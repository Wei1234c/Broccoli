# coding: utf-8

# import os
# import sys
import time
import threading

# sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'hardware')))
# sys.path.append(os.path.abspath(os.path.join(os.path.pardir, 'node')))

import node


class Client(threading.Thread):
    
    def __init__(self):        
        super().__init__(name = 'Client', daemon = True)
        self.node = node.Node()
        self.status = self.node.broker.status
        self.node.broker.is_client = True
        self.sync_file = self.node.broker.sync_file
        self.reset_workers = self.node.broker.reset_workers
        
    def request(self, receiver, message):
        try:
            message['receiver'] = receiver
            return self.node.request(**message)
        except Exception as e:
            print(e)

    def run(self):
        self.node.run()
       
    def stop(self):
        self.node.stop()


if __name__ == '__main__':

    the_client = Client()
    the_client.start()
    while not the_client.status['Is connected']:
        time.sleep(1)
        print('Node not ready yet.')

    ## reset workers
    # the_client.reset_workers()
    # time.sleep(15)

    # sync_file
    the_client.sync_file('tasks.py', load_as_tasks = True)

    from canvas import *
    import tasks

    def test1():
        count = 10

        # s = tasks.add.s(x = 3, y = 8)
        # s.set_routing_key('NodeMCU_b4e62d890c49')
        # result = s.apply_async()
        # result = tasks.add.apply_async(x = 3, y = 8)
        # print('******* result is: ', result.get())

        # async_results = [tasks.mul.s(x = n, y = n+1).apply_async() for n in range(count)]
        # results = [async_result.get() for async_result in async_results]
        # return results
        # result_set = ResultSet(async_results)
        # return result_set.get()

        gp = group([tasks.mul.s(n, n+1) for n in range(count)])
        results = gp.get()
        return  results

    print('********** result:\n', test1(), '\n**********')


    def test2():
        import word_count
        return word_count.count_words('test.txt')

    # words_count, counts = test2()
    # print('********** result:\nwords count: {}\n\n{}\n**********'.format(words_count, counts[:10]))


    def test3():
        count = 10
        # gp = tasks.xsum.map([(n, n+1) for n in range(count)])
        # gp = tasks.xsum.map(list(zip(range(10), range(10))))
        # gp = tasks.xsum.map([list(range(10)), list(range(50)), list(range(100))])
        # gp = tasks.xsum.map([list(range(10)), list(range(100))])
        gp = tasks.add.starmap(list(zip(range(10), range(10))))
        results = gp.get()
        return  results

    # print('********** result:\n', test3(), '\n**********')


    def test4():
        ch = chain(tasks.add.s(4, 4), tasks.mul.s(8), tasks.mul.s(10))
        results = ch.get()
        return  results

    # print('********** result:\n', test4(), '\n**********')


    def test5():
        count = 100

        callback = tasks.xsum.s()
        header = [tasks.add.s(i, i) for i in range(count)]
        async_result = chord(header)(callback)
        results = async_result.get()

        # async_result = chord([tasks.add.s(i, i) for i in range(count)])(tasks.xsum.s())
        # results = async_result.get()
        return  results

    # print('********** result:\n', test5(), '\n**********')


    def test6():
        ck = tasks.add.chunks(list(zip(range(101), range(101))), 10)
        async_result = ck.apply_async()
        results = async_result.get()

        # async_result = chord([tasks.add.s(i, i) for i in range(count)])(tasks.xsum.s())
        # results = async_result.get()
        return  results

    # print('********** result:\n', test6(), '\n**********')
    

    time.sleep(3)
