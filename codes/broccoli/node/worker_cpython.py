# coding: utf-8

import datetime
import worker


class Worker(worker.Worker):

    count = 0

    # Object control
    def __init__(self, server_address, server_port):
        super().__init__(server_address, server_port)
        def next_count():
            Worker.count += 1
            return Worker.count
        self.now = lambda : '{} {}'.format(datetime.datetime.now(), next_count())


    # code book_______________________
    def set_default_code_book(self):
        code_book = {'read GPIOs': self.read_GPIOs,
                     'write GPIOs': self.write_GPIOs,
                     'blink led': self.blink_led}      
        self.set_code_book(code_book)


    # Specialized functions___________
    def read_GPIOs(self, pins): 
        return 'Not applicable.'


    def write_GPIOs(self, pins_and_values):
        return 'Not applicable.'


    def blink_led(self, times = 1, on_seconds = 0.1, off_seconds = 0.1, forever = False):
        return 'Not applicable.'
