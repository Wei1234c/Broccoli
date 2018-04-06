import celery
from celery import task

# docker run -d -p 6379:6379 --net=host --name=redis --volume=/data:/data hypriot/rpi-redis

celery.app.base.Celery.send_task
from celery.app.task import Task
celery.canvas.Signature
celery.canvas.group
celery.app.task.Task.apply_async
celery.local.PromiseProxy
# celery.app.task.AsyncResult

from celery.result import ResultBase
from celery.result import AsyncResult
from celery.result import ResultSet
from celery.result import GroupResult
# celery.result
# app = celery.app()
# celery.worker.request
from celery.worker.request import Request
from celery import group



@task
def f():
    return 'hello'

# from celery import app

print(f.s()())







class Context_test:
    """Task request variables (Task.request)."""

    logfile = None
    loglevel = None
    hostname = None
    id = None
    args = None
    kwargs = None
    retries = 0
    eta = None
    expires = None
    is_eager = False
    headers = None
    delivery_info = None
    reply_to = None
    root_id = None
    parent_id = None
    correlation_id = None
    taskset = None   # compat alias to group
    group = None
    chord = None
    chain = None
    utc = None
    called_directly = True
    callbacks = None
    errbacks = None
    timelimit = None
    origin = None
    _children = None   # see property
    _protected = 0

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def clear(self):
        return self.__dict__.clear()

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __repr__(self):
        return '<Context: {0!r}>'.format(vars(self))

    def as_execution_options(self):
        limit_hard, limit_soft = self.timelimit or (None, None)
        return {
            'task_id': self.id,
            'root_id': self.root_id,
            'parent_id': self.parent_id,
            'group_id': self.group,
            'chord': self.chord,
            'chain': self.chain,
            'link': self.callbacks,
            'link_error': self.errbacks,
            'expires': self.expires,
            'soft_time_limit': limit_soft,
            'time_limit': limit_hard,
            'headers': self.headers,
            'retries': self.retries,
            'reply_to': self.reply_to,
            'origin': self.origin,
        }

    @property
    def children(self):
        # children must be an empy list for every thread
        if self._children is None:
            self._children = []
        return self._children


# task_message(headers={'lang': 'py', 'task': '__main__.mapper', 'id': '1946a678-2709-4bf2-b163-ed8bac0c9008',
#                       'eta': None, 'expires': None, 'group': None, 'retries': 0, 'timelimit': [None, None],
#                       'root_id': '1946a678-2709-4bf2-b163-ed8bac0c9008', 'parent_id': None,
#                       'argsrepr': "('Aesop's',)", 'kwargsrepr': '{}', 'origin': 'gen14632@DESKTOP-M4SP11C'},
#              properties={'correlation_id': '1946a678-2709-4bf2-b163-ed8bac0c9008',
#                          'reply_to': '09f182a6-d719-3c46-a7fb-07e6208e9b81'},
#              body=(("Aesop's",), {}, {'callbacks': None, 'errbacks': None, 'chain': None, 'chord': None}),
#              sent_event=None)


# celery.app.base
#
# send_task(self, name, args=None, kwargs=None, countdown=None,
#           eta=None, task_id=None, producer=None, connection=None,
#           router=None, result_cls=None, expires=None,
#           publisher=None, link=None, link_error=None,
#           add_to_parent=True, group_id=None, retries=0, chord=None,
#           reply_to=None, time_limit=None, soft_time_limit=None,
#           root_id=None, parent_id=None, route_name=None,
#           shadow=None, chain=None, task_type=None, **options):
# """Send task by name.
#
# Supports the same arguments as :meth:`@-Task.apply_async`.
#
# Arguments:
#     name (str): Name of task to call (e.g., `"tasks.add"`).
#     result_cls (~@AsyncResult): Specify custom result class.
# """
# parent = have_parent = None
# amqp = self.amqp
# task_id = task_id or uuid()
# producer = producer or publisher  # XXX compat
# router = router or amqp.router
# conf = self.conf
# if conf.task_always_eager:  # pragma: no cover
#     warnings.warn(AlwaysEagerIgnored(
#         'task_always_eager has no effect on send_task',
#     ), stacklevel=2)
# options = router.route(
#     options, route_name or name, args, kwargs, task_type)
#
# if not root_id or not parent_id:
#     parent = self.current_worker_task
#     if parent:
#         if not root_id:
#             root_id = parent.request.root_id or parent.request.id
#         if not parent_id:
#             parent_id = parent.request.id
#
# message = amqp.create_task_message(
#     task_id, name, args, kwargs, countdown, eta, group_id,
#     expires, retries, chord,
#     maybe_list(link), maybe_list(link_error),
#     reply_to or self.oid, time_limit, soft_time_limit,
#     self.conf.task_send_sent_event,
#     root_id, parent_id, shadow, chain,
# )
#
# if connection:
#     producer = amqp.Producer(connection, auto_declare=False)
# with self.producer_or_acquire(producer) as P:
#     with P.connection._reraise_as_library_errors():
#         self.backend.on_task_call(P, task_id)
#         amqp.send_task_message(P, name, message, **options)
# result = (result_cls or self.AsyncResult)(task_id)