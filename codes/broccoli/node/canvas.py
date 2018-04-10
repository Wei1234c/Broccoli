import cluster_node as node


broker = node.Node.broker

class Signature:

    def __init__(self, task, *args, **kargs):
        self.task = task
        self.routing_key = broker.broadcasting_channel
        self.delay = self.apply_async
        self.message = {'message_type': 'function',
                        'function': '{}.{}'.format(self.task._f.__module__,
                                                   self.task._f.__name__),
                        'args': args,
                        'kwargs': kargs,
                        'need_result': True}

    def append_arg(self, arg):
        self.message['args'] += (arg,)
        return self

    def set_routing_key(self, key):
        self.routing_key = key
        return self

    def apply_async(self):
        return broker.put_task(self, routing_key=self.routing_key)


class Task:

    def __init__(self, f):
        self._f = f
        self.__name__ = f.__name__
        self.signature = self.gen_signature
        self.s = self.signature
        self.delay = self.apply_async

    def gen_signature(self, *args, **kargs):
        return Signature(self, *args, **kargs)

    def __call__(self, *args, **kargs):
        return self._f(*args, **kargs)

    def apply_async(self, *args, **kargs):
        signature = self.s(*args, **kargs)
        return signature.apply_async()

    def map(self, args_list):
        return xmap(self, args_list)

    def starmap(self, args_list):
        return xstarmap(self, args_list)

    def chunks(self, args_list, bins):
        return chunks(self, args_list, bins)


class ResultSet:

    def __init__(self, async_results):
        self.async_results = async_results

    def get(self):
        return [async_result.get() for async_result in self.async_results]


class group:

    def __init__(self, signatures):
        self.signatures = signatures
        self.result_set = None

    def __call__(self):
        self.result_set = ResultSet([signature.apply_async() for signature in self.signatures])
        return self.result_set

    def apply_async(self):
        return self.__call__()

    def get(self):
        if self.result_set is None:
            self.apply_async()
        return self.result_set.get()


class xmap(group):

    def __init__(self, task, args_list):
        super().__init__([task.s(args) for args in args_list])


class xstarmap(group):

    def __init__(self, task, args_list):
        super().__init__([task.s(*args) for args in args_list])


class chunks:

    def __init__(self, task, args_list, bins):
        args_list_chunks = self._chunks(args_list, bins)
        self.groups = [group([task.s(*args) for args in args_list]) for args_list in args_list_chunks]
        self.result_set = None

    def _chunks(self, the_list, bins):
        length = len(the_list)
        quotient = length // bins
        remainder = length % bins
        start = 0

        for r in range(bins):
            end = start + quotient + (1 if remainder > 0 else 0)
            yield the_list[start:end]
            start = end
            remainder -= 1

    def __call__(self):
        self.result_set = [group.apply_async() for group in self.groups]
        return self

    def apply_async(self):
        return self.__call__()

    def get(self):
        if self.result_set is None:
            self.apply_async()
        return [async_result.get() for async_result in self.result_set]


class chain:

    def __init__(self, *signatures):
        self.signatures = signatures
        self.async_result = None

    def __call__(self):
        async_result = self.signatures[0].apply_async()

        for signature in self.signatures[1:]:
            result = async_result.get()
            if result:
                signature.append_arg(result)
            async_result = signature.apply_async()

        self.async_result = async_result
        return async_result

    def apply_async(self):
        return self.__call__()

    def get(self):
        if self.async_result is None:
            self.apply_async()
        return self.async_result.get()


class chord():

    def __init__(self, signatures):
        self.group = group(signatures)

    def __call__(self, signature):
        async_result = signature.append_arg(self.get()).apply_async()
        return async_result

    def apply_async(self, signature):
        return self.__call__(signature)

    def get(self):
        return self.group.get()
