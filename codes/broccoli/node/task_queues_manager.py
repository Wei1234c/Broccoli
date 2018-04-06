import time
import queue_manager


class Queue_manager(queue_manager.Queue_manager):

    def __init__(self, key_name = 'task_id'):
        queue_manager.Queue_manager.__init__(self, key_name)
        self.enqueue_task = self.append_request_message
        self.dequeue_result = self.pop_received_message


    def remain_tasks_count(self):
        return len(self._message_queue_out)


    def enqueue_result(self, message):
        super().append_received_message(message)
        super().pop_received_message()


    def dequeue_task(self):
        return (self._message_queue_out.pop(0), self.remain_tasks_count()) if self.remain_tasks_count() > 0 else \
               (None, 0)
