# coding: utf-8

import time
import config_mqtt


class Asynch_result:
        
    def __init__(self, id, requests, yield_to):
        self.id = id
        self._requests_need_result = requests
        self.yield_to = yield_to
        self.ready = False
        self.successful = False
        

    def is_ready(self):
        request = self._requests_need_result.get(self.id)

        if request:
            if request.get('is_replied'):
                self.ready = True
        else:
            raise Exception('No such request with id {}'.format(self.id))

        return self.ready


    def get(self, timeout = config_mqtt.ASYNCH_RESULT_TIMEOUT):
        # time.sleep(config_mqtt.ASYNCH_RESULT_WAIT_BEFORE_GET)
        start_time = time.time()

        while True:
            current_time = time.time()

            if self.is_ready():
                self.successful = True
                request = self._requests_need_result.get(self.id)
                result = request.get('result')
                self._requests_need_result.pop(self.id)
                return result
            else:
                if current_time - start_time > timeout:  # timeout
                    self.ready = True
                    self._requests_need_result.pop(self.id)
                    err_msg = 'Timeout: no result returned for request with id {}'.format(self.id)
                    # raise Exception(err_msg)
                    print(err_msg)
                    return None
                else:
                    self.yield_to()