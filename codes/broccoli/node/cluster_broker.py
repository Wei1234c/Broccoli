import os
import config_mqtt
import task_queues_manager
import asynch_result


if config_mqtt.IS_MICROPYTHON:
    import worker_upython as worker_impl
else:
    import worker_cpython as worker_impl


class Broker(worker_impl.Worker):

    DEFAULT_CHANNEL = config_mqtt.SERVER_NAME

    def __init__(self, server_address, server_port):
        worker_impl.Worker.__init__(self, server_address, server_port)
        self.is_client = False
        self.broadcasting_channel = Broker.DEFAULT_CHANNEL
        self.task_queues_manager = task_queues_manager.Queue_manager()
        self.enqueue_task = self.task_queues_manager.enqueue_task
        self.enqueue_result = self.task_queues_manager.enqueue_result
        self.dequeue_task = self.task_queues_manager.dequeue_task


    def broadcast(self, message):
        message['receiver'] = self.broadcasting_channel
        self.request(message)


    def reset_workers(self):
        message = {'message_type': 'exec',
                   'to_exec': 'import machine;machine.reset()'}
        self.broadcast(message)


    def sync_file(self, file, load_as_tasks = False):
        with open(file) as f:
            content = f.read()

        message = {'message_type': 'file',
                   'kwargs': {'filename': os.path.basename(file),
                              'file':content,
                              'load_as_tasks': load_as_tasks}}
        self.broadcast(message)


    def put_task(self, signature, routing_key = DEFAULT_CHANNEL):
        message = self.create_task_message(signature)
        remain_tasks_count = self.task_queues_manager.remain_tasks_count()
        self.enqueue_task(message)
        if remain_tasks_count == 0:  # call for help only if this is the first one.
            self.call_for_help(routing_key)

        async_result = None
        if message.get('need_result'):
            async_result = asynch_result.Asynch_result(message.get('task_id'),
                                                       self.task_queues_manager._requests_need_result,
                                                       self.receive_one_cycle)
        return async_result


    def create_task_message(self, signature):
        message = signature.message
        time_stamp = str(self.now())
        message['message_id'] = time_stamp
        message['sender'] = self.name
        message['reply_to'] = self.name
        message['result'] = None
        message['correlation_id'] = time_stamp
        message['task_id'] = time_stamp
        message = self.format_message(**message)
        return message


    def call_for_help(self, routing_key = DEFAULT_CHANNEL):
        message= {'receiver': routing_key,
                  'message_type': 'function',
                  'function': 'fetch_task',
                  'kwargs': {'broker': self.name}}
        self.request(message)


    def fetch_task(self, broker):
        # if not self.is_client:
        if self.name != broker:
            remain_tasks_count = 1

            while remain_tasks_count > 0:
                # fetch_task
                message= {'receiver': broker,
                          'message_type': 'function',
                          'function': 'dequeue_task',
                          'need_result': True}
                msg, asynch_result = self.request(message)

                task = None
                result = asynch_result.get()
                if result:
                    task, remain_tasks_count = result
                self.blink_led(on_seconds=0.003, off_seconds=0.001)

                if task:
                    print('\ntask:', task)
                    self.consume_task(task)


    def consume_task(self, task):

        # do task
        message, message_string = self.do(task)
        print('reply_message:', message)

        # reply result
        try:
            if message and message.get('need_result'):
                time_stamp = str(self.now())
                reply_message = self.format_message(message_id=time_stamp,
                                                    sender=self.name,
                                                    receiver=message.get('sender'),
                                                    message_type='function',
                                                    function='enqueue_result',
                                                    kwargs={'message': message},
                                                    reply_to=self.name,
                                                    correlation_id=time_stamp)

                print('\nProcessed result:\n{0}\n'.format(self.get_OrderedDict(reply_message)))
                self.send_message(reply_message)

        except Exception as e:
            print(e, 'Fail to return result.')
