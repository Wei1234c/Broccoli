
# mini cluster of ESP32 - test

ref: [Celery Canvas](http://docs.celeryproject.org/en/latest/userguide/canvas.html)

The 'private' folder contains 'config_mqtt.py' with my private MQTT broker address and settings.  
For those who want to test this, please:  
- Upload all *.py found in this [repo.](https://github.com/Wei1234c/MQTT_bridged_workers) to ESP32's '/' folder.
- Copy all *.py found in this [repo.](https://github.com/Wei1234c/MQTT_bridged_workers) to a '...external/mqtt_network' folder in you local machine.
- UPload all *.py found in this repo. to ESP32's '/' folder.
- Config your copy of 'config_mqtt.py' in 'config' folder.
- Comment out the line with '... 'external', 'private' ...'.
- make sure the line with '... 'external', 'mqtt_network' ...' can refer to those *.py file you copy from this [repo.](https://github.com/Wei1234c/MQTT_bridged_workers).

### Imports


```python
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join('..', '..', '..', 'external', 'private')))
sys.path.append(os.path.abspath(os.path.join('..', '..', '..', 'external', 'amd64')))
sys.path.append(os.path.abspath(os.path.join('..', '..', 'codes', 'broccoli', 'client')))
sys.path.append(os.path.abspath(os.path.join('..', '..', 'codes', 'broccoli', 'config')))
sys.path.append(os.path.abspath(os.path.join('..', '..', 'codes', 'broccoli', 'node')))
sys.path.append(os.path.abspath(os.path.join('..', '..', '..', 'external', 'mqtt_network')))

import client
from collections import OrderedDict

from canvas import *
import tasks
```

### Start client
啟動 client 物件。  

在本機上有一個 Broker 物件，負責：
- 管理本機上的 task queue
- 接受使用者發出的運算要求，並將之排入本機上的 task queue
- 通知遠端的 workers 協助處理 tasks
- 將工作發送給 workers 做處理
- 收集 workers 傳回的運算結果
- 將運算結果整合之後，傳回給使用者

而我們透過 client 物件來與 Broker 物件溝通


```python
the_client = client.Client()
the_client.start()

while not the_client.status['Is connected']:            
    time.sleep(1)
    print('Node not ready yet.')
```

    
    Sending 281 bytes
    Message:
    OrderedDict([('command', 'set connection name'), ('correlation_id', '2018-04-10 16:27:46.072660 1'), ('kwargs', {'name': 'Wei-Legion'}), ('message_id', '2018-04-10 16:27:46.072660 1'), ('message_type', 'command'), ('need_result', True), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    [Connected: ('123.240.210.68', 1883)]
    [Listen to messages]
    Node not ready yet.
    

### Reset workers
如果需要確保 workers 的狀態都一致，或者需要重新 depoly Python module files 到 workers 上面去，可以發送指令給遠端的 workers，要求做 reboot 回到最初的狀態。


```python
the_client.reset_workers()
time.sleep(15)  # wait until workers ready.
```

    
    Sending 236 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:27:46.891780 10'), ('message_id', '2018-04-10 16:27:46.891780 10'), ('message_type', 'exec'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion'), ('to_exec', 'import machine;machine.reset()')])
    
    
    Data received: 236 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:27:46.891780 10'), ('message_id', '2018-04-10 16:27:46.891780 10'), ('message_type', 'exec'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion'), ('to_exec', 'import machine;machine.reset()')])
    
    No module named 'machine'
    
    Data received: 257 bytes
    Message:
    OrderedDict([('command', 'set connection name'), ('correlation_id', '6580'), ('kwargs', {'name': 'ESP32_b4e62d8904d1'}), ('message_id', '6580'), ('message_type', 'command'), ('need_result', True), ('receiver', 'Hub'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 257 bytes
    Message:
    OrderedDict([('command', 'set connection name'), ('correlation_id', '6544'), ('kwargs', {'name': 'ESP32_b4e62d891439'}), ('message_id', '6544'), ('message_type', 'command'), ('need_result', True), ('receiver', 'Hub'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 257 bytes
    Message:
    OrderedDict([('command', 'set connection name'), ('correlation_id', '6654'), ('kwargs', {'name': 'ESP32_b4e62d890c49'}), ('message_id', '6654'), ('message_type', 'command'), ('need_result', True), ('receiver', 'Hub'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    

### Upload tasks module file
Reboot 之後的 workers 只有最基本的功能，如果我們需要 workers 執行額外的功能 (functions)，則需要先將定義這些 functions 的 module 檔案上傳給 workers 並且要求它們 import。  

例如： 我們上傳給每一個 worker 一個`tasks.py`的檔案，其中定義幾個 functions:
```
from canvas import Task

@Task
def add(x, y, op=None):
    return op(x, y) if op else x + y

@Task
def xsum(x):
    return sum(x)

@Task
def mul(x, y, op=None):
    return op(x, y) if op else x * y

@Task
def mapper(word):
    return (word, 1) if len(word) > 3 else None

```

Workers 收到這個`tasks.py`檔案之後，會做`import tasks`的動作，所以就可以呼叫 tasks.add() 這個 function。


```python
tasks_file = os.path.join('..', '..', 'codes', 'broccoli', 'client', 'tasks.py')
the_client.sync_file(tasks_file, load_as_tasks = True)
```

    
    Sending 550 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:01.949386 23'), ('kwargs', {'filename': 'tasks.py', 'file': 'from canvas import Task\n\n@Task\ndef add(x, y, op=None):\n    return op(x, y) if op else x + y\n\n@Task\ndef xsum(x):\n    return sum(x)\n\n@Task\ndef mul(x, y, op=None):\n    return op(x, y) if op else x * y\n\n@Task\ndef mapper(word):\n    return (word, 1) if len(word) > 3 else None\n', 'load_as_tasks': True}), ('message_id', '2018-04-10 16:28:01.949386 23'), ('message_type', 'file'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    

<font color='blue'>
## DEMOs

### Chains
Celery [Chains](http://docs.celeryproject.org/en/latest/userguide/canvas.html#chains) 的主要作用是把多個運算**串聯**起來，前一個運算的結果是下一個運算的參數，這樣就可以組成一個完整的運算過程，例如下例中用`chain`組成一個 ((4+4) * 8) * 10  = 640 的計算過程
```
>>> # (4 + 4) * 8 * 10
>>> res = chain(add.s(4, 4), mul.s(8), mul.s(10))
proj.tasks.add(4, 4) | proj.tasks.mul(8) | proj.tasks.mul(10)

>>> res = chain(add.s(4, 4), mul.s(8), mul.s(10))()
>>> res.get()
640
```

我們可以在 ESP32 cluster 上面也做同樣的事情：


```python
ch = chain(tasks.add.s(4, 4), tasks.mul.s(8), tasks.mul.s(10))
ch.get()
```

    
    Sending 257 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:01.993466 27'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:01.993466 27'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 550 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:01.949386 23'), ('kwargs', {'filename': 'tasks.py', 'file': 'from canvas import Task\n\n@Task\ndef add(x, y, op=None):\n    return op(x, y) if op else x + y\n\n@Task\ndef xsum(x):\n    return sum(x)\n\n@Task\ndef mul(x, y, op=None):\n    return op(x, y) if op else x * y\n\n@Task\ndef mapper(word):\n    return (word, 1) if len(word) > 3 else None\n', 'load_as_tasks': True}), ('message_id', '2018-04-10 16:28:01.949386 23'), ('message_type', 'file'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 257 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:01.993466 27'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:01.993466 27'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '14236'), ('function', 'dequeue_task'), ('message_id', '14236'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '14236'), ('message_id', '2018-04-10 16:28:03.120213 132'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:01.993466 26', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:01.993466 26', 'task_id': '2018-04-10 16:28:01.993466 26'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 484 bytes
    Message:
    OrderedDict([('correlation_id', '14236'), ('message_id', '2018-04-10 16:28:03.120213 132'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:01.993466 26', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:01.993466 26', 'task_id': '2018-04-10 16:28:01.993466 26'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '14170'), ('function', 'dequeue_task'), ('message_id', '14170'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '14170'), ('message_id', '2018-04-10 16:28:03.407476 153'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    Message:
    OrderedDict([('correlation_id', '14170'), ('message_id', '2018-04-10 16:28:03.407476 153'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '14107'), ('function', 'dequeue_task'), ('message_id', '14107'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '14107'), ('message_id', '2018-04-10 16:28:03.523787 161'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    Message:
    OrderedDict([('correlation_id', '14107'), ('message_id', '2018-04-10 16:28:03.523787 161'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 518 bytes
    Message:
    OrderedDict([('correlation_id', '14934'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 8, 'function': 'tasks.add', 'args': [4, 4], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:01.993466 26', 'message_type': 'result', 'task_id': '2018-04-10 16:28:01.993466 26', 'correlation_id': '2018-04-10 16:28:01.993466 26', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '14934'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Sending 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:03.811550 185'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:03.811550 185'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:03.811550 185'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:03.811550 185'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '15547'), ('function', 'dequeue_task'), ('message_id', '15547'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '15547'), ('message_id', '2018-04-10 16:28:04.314388 217'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:03.811550 184', 'function': 'tasks.mul', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:03.811550 184', 'task_id': '2018-04-10 16:28:03.811550 184'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '15547'), ('message_id', '2018-04-10 16:28:04.314388 217'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:03.811550 184', 'function': 'tasks.mul', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:03.811550 184', 'task_id': '2018-04-10 16:28:03.811550 184'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '15460'), ('function', 'dequeue_task'), ('message_id', '15460'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '15460'), ('message_id', '2018-04-10 16:28:04.474815 229'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '15432'), ('function', 'dequeue_task'), ('message_id', '15432'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '15432'), ('message_id', '2018-04-10 16:28:04.514921 232'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    Message:
    OrderedDict([('correlation_id', '15432'), ('message_id', '2018-04-10 16:28:04.514921 232'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '15460'), ('message_id', '2018-04-10 16:28:04.474815 229'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 522 bytes
    Message:
    OrderedDict([('correlation_id', '16078'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 64, 'function': 'tasks.mul', 'args': [8, 8], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:03.811550 184', 'message_type': 'result', 'task_id': '2018-04-10 16:28:03.811550 184', 'correlation_id': '2018-04-10 16:28:03.811550 184', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '16078'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Sending 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:04.959102 271'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:04.959102 271'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:04.959102 271'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:04.959102 271'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '16689'), ('function', 'dequeue_task'), ('message_id', '16689'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '16689'), ('message_id', '2018-04-10 16:28:05.554686 315'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:04.959102 270', 'function': 'tasks.mul', 'args': (10, 64), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:04.959102 270', 'task_id': '2018-04-10 16:28:04.959102 270'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Sending 489 bytes
    
    Message:
    OrderedDict([('correlation_id', '16615'), ('function', 'dequeue_task'), ('message_id', '16615'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    Message:
    OrderedDict([('correlation_id', '16689'), ('message_id', '2018-04-10 16:28:05.554686 315'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:04.959102 270', 'function': 'tasks.mul', 'args': (10, 64), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:04.959102 270', 'task_id': '2018-04-10 16:28:04.959102 270'}, 0)), ('sender', 'Wei-Legion')])
    
    
    
    Processed result:
    OrderedDict([('correlation_id', '16615'), ('message_id', '2018-04-10 16:28:05.603315 318'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    Message:
    OrderedDict([('correlation_id', '16615'), ('message_id', '2018-04-10 16:28:05.603315 318'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '16578'), ('function', 'dequeue_task'), ('message_id', '16578'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '16578'), ('message_id', '2018-04-10 16:28:05.845960 336'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    Message:
    OrderedDict([('correlation_id', '16578'), ('message_id', '2018-04-10 16:28:05.845960 336'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '17605'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 640, 'function': 'tasks.mul', 'args': [10, 64], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:04.959102 270', 'message_type': 'result', 'task_id': '2018-04-10 16:28:04.959102 270', 'correlation_id': '2018-04-10 16:28:04.959102 270', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '17605'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    




    640



### Groups
Celery [Groups](http://docs.celeryproject.org/en/latest/userguide/canvas.html#groups) 的主要作用是把多個運算**併聯**起來，把很多同質性的運算同時發送給許多遠端的 workers 協助處理，再收集 workers 傳回來的結果彙整成為一個結果集，例如下例中用`group`同時計算 (2+2) 和 (4+4)，結果是 [4, 8]
```
>>> from celery import group
>>> from proj.tasks import add

>>> group(add.s(2, 2), add.s(4, 4))
(proj.tasks.add(2, 2), proj.tasks.add(4, 4))  

>>> g = group(add.s(2, 2), add.s(4, 4))
>>> res = g()
>>> res.get()
[4, 8]
```
我們可以在 ESP32 cluster 上面也做同樣的事情：


```python
gp = group([tasks.add.s(2, 2), tasks.add.s(4, 4)])
gp.get()
```

    
    Sending 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:06.453074 383'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:06.453074 383'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:06.453074 383'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:06.453074 383'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '18108'), ('function', 'dequeue_task'), ('message_id', '18108'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '18108'), ('message_id', '2018-04-10 16:28:06.927423 425'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:06.453074 382', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:06.453074 382', 'task_id': '2018-04-10 16:28:06.453074 382'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '18108'), ('message_id', '2018-04-10 16:28:06.927423 425'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:06.453074 382', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:06.453074 382', 'task_id': '2018-04-10 16:28:06.453074 382'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '18068'), ('function', 'dequeue_task'), ('message_id', '18068'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '18068'), ('message_id', '2018-04-10 16:28:07.126061 445'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:06.494685 386', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:06.494685 386', 'task_id': '2018-04-10 16:28:06.494685 386'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '18068'), ('message_id', '2018-04-10 16:28:07.126061 445'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:06.494685 386', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:06.494685 386', 'task_id': '2018-04-10 16:28:06.494685 386'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '18184'), ('function', 'dequeue_task'), ('message_id', '18184'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '18184'), ('message_id', '2018-04-10 16:28:07.224939 454'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    Message:
    OrderedDict([('correlation_id', '18184'), ('message_id', '2018-04-10 16:28:07.224939 454'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '18607'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 4, 'function': 'tasks.add', 'args': [2, 2], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:06.453074 382', 'message_type': 'result', 'task_id': '2018-04-10 16:28:06.453074 382', 'correlation_id': '2018-04-10 16:28:06.453074 382', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '18607'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '18710'), ('function', 'dequeue_task'), ('message_id', '18710'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '18710'), ('message_id', '2018-04-10 16:28:07.591667 492'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    Message:
    OrderedDict([('correlation_id', '18710'), ('message_id', '2018-04-10 16:28:07.591667 492'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '18771'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 8, 'function': 'tasks.add', 'args': [4, 4], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:06.494685 386', 'message_type': 'result', 'task_id': '2018-04-10 16:28:06.494685 386', 'correlation_id': '2018-04-10 16:28:06.494685 386', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '18771'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    




    [4, 8]



我們可以用 iterators:
```
>>> group(add.s(i, i) for i in xrange(10))()
```


```python
gp = group([tasks.add.s(i, i) for i in range(10)])
gp.get()
```

    
    Sending 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:07.710611 506'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:07.710611 506'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:07.710611 506'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:07.710611 506'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '19420'), ('function', 'dequeue_task'), ('message_id', '19420'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '19420'), ('message_id', '2018-04-10 16:28:08.237606 569'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.710611 505', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.710611 505', 'task_id': '2018-04-10 16:28:07.710611 505'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '19420'), ('message_id', '2018-04-10 16:28:08.237606 569'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.710611 505', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.710611 505', 'task_id': '2018-04-10 16:28:07.710611 505'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '19496'), ('function', 'dequeue_task'), ('message_id', '19496'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '19496'), ('message_id', '2018-04-10 16:28:08.377966 583'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 509', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 509', 'task_id': '2018-04-10 16:28:07.735680 509'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '19401'), ('function', 'dequeue_task'), ('message_id', '19401'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '19401'), ('message_id', '2018-04-10 16:28:08.406543 586'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 510', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 510', 'task_id': '2018-04-10 16:28:07.735680 510'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '19401'), ('message_id', '2018-04-10 16:28:08.406543 586'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 510', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 510', 'task_id': '2018-04-10 16:28:07.735680 510'}, 7)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '19496'), ('message_id', '2018-04-10 16:28:08.377966 583'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 509', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 509', 'task_id': '2018-04-10 16:28:07.735680 509'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '19924'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 0, 'function': 'tasks.add', 'args': [0, 0], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.710611 505', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.710611 505', 'correlation_id': '2018-04-10 16:28:07.710611 505', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '19924'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '20026'), ('function', 'dequeue_task'), ('message_id', '20026'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '20026'), ('message_id', '2018-04-10 16:28:08.926870 640'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 511', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 511', 'task_id': '2018-04-10 16:28:07.735680 511'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '20026'), ('message_id', '2018-04-10 16:28:08.926870 640'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 511', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 511', 'task_id': '2018-04-10 16:28:07.735680 511'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '20127'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 2, 'function': 'tasks.add', 'args': [1, 1], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.735680 509', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.735680 509', 'correlation_id': '2018-04-10 16:28:07.735680 509', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '20127'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '20230'), ('function', 'dequeue_task'), ('message_id', '20230'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '20230'), ('message_id', '2018-04-10 16:28:09.218173 669'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 512', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 512', 'task_id': '2018-04-10 16:28:07.735680 512'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '20230'), ('message_id', '2018-04-10 16:28:09.218173 669'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 512', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 512', 'task_id': '2018-04-10 16:28:07.735680 512'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '20120'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 4, 'function': 'tasks.add', 'args': [2, 2], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.735680 510', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.735680 510', 'correlation_id': '2018-04-10 16:28:07.735680 510', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '20120'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '20224'), ('function', 'dequeue_task'), ('message_id', '20224'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '20224'), ('message_id', '2018-04-10 16:28:09.378158 684'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 513', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 513', 'task_id': '2018-04-10 16:28:07.735680 513'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '20224'), ('message_id', '2018-04-10 16:28:09.378158 684'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 513', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 513', 'task_id': '2018-04-10 16:28:07.735680 513'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '20608'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 6, 'function': 'tasks.add', 'args': [3, 3], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.735680 511', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.735680 511', 'correlation_id': '2018-04-10 16:28:07.735680 511', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '20608'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '20711'), ('function', 'dequeue_task'), ('message_id', '20711'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '20711'), ('message_id', '2018-04-10 16:28:09.574093 703'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 514', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 514', 'task_id': '2018-04-10 16:28:07.735680 514'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '20711'), ('message_id', '2018-04-10 16:28:09.574093 703'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 514', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 514', 'task_id': '2018-04-10 16:28:07.735680 514'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '21105'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 8, 'function': 'tasks.add', 'args': [4, 4], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.735680 512', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.735680 512', 'correlation_id': '2018-04-10 16:28:07.735680 512', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '21105'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '21208'), ('function', 'dequeue_task'), ('message_id', '21208'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '21208'), ('message_id', '2018-04-10 16:28:10.097152 759'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 515', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 515', 'task_id': '2018-04-10 16:28:07.735680 515'}, 2)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    
    Data received: 522 bytes
    Message:
    OrderedDict([('correlation_id', '21051'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 10, 'function': 'tasks.add', 'args': [5, 5], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.735680 513', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.735680 513', 'correlation_id': '2018-04-10 16:28:07.735680 513', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '21051'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    Message:
    OrderedDict([('correlation_id', '21208'), ('message_id', '2018-04-10 16:28:10.097152 759'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 515', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 515', 'task_id': '2018-04-10 16:28:07.735680 515'}, 2)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '21157'), ('function', 'dequeue_task'), ('message_id', '21157'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '21157'), ('message_id', '2018-04-10 16:28:10.177528 766'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 516', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 516', 'task_id': '2018-04-10 16:28:07.735680 516'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '21157'), ('message_id', '2018-04-10 16:28:10.177528 766'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 516', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 516', 'task_id': '2018-04-10 16:28:07.735680 516'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Data received: 522 bytes
    Message:
    OrderedDict([('correlation_id', '21279'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 12, 'function': 'tasks.add', 'args': [6, 6], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.735680 514', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.735680 514', 'correlation_id': '2018-04-10 16:28:07.735680 514', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '21279'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '21382'), ('function', 'dequeue_task'), ('message_id', '21382'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '21382'), ('message_id', '2018-04-10 16:28:10.464677 796'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 517', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 517', 'task_id': '2018-04-10 16:28:07.735680 517'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '21382'), ('message_id', '2018-04-10 16:28:10.464677 796'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:07.735680 517', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:07.735680 517', 'task_id': '2018-04-10 16:28:07.735680 517'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 522 bytes
    Message:
    OrderedDict([('correlation_id', '21893'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 14, 'function': 'tasks.add', 'args': [7, 7], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.735680 515', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.735680 515', 'correlation_id': '2018-04-10 16:28:07.735680 515', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '21893'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '21997'), ('function', 'dequeue_task'), ('message_id', '21997'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '21997'), ('message_id', '2018-04-10 16:28:10.971447 850'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    Message:
    OrderedDict([('correlation_id', '21997'), ('message_id', '2018-04-10 16:28:10.971447 850'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 522 bytes
    Message:
    OrderedDict([('correlation_id', '21872'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 16, 'function': 'tasks.add', 'args': [8, 8], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.735680 516', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.735680 516', 'correlation_id': '2018-04-10 16:28:07.735680 516', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '21872'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '21976'), ('function', 'dequeue_task'), ('message_id', '21976'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '21976'), ('message_id', '2018-04-10 16:28:11.208156 874'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 206 bytes
    
    Data received: 522 bytes
    Message:
    OrderedDict([('correlation_id', '22180'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 18, 'function': 'tasks.add', 'args': [9, 9], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:07.735680 517', 'message_type': 'result', 'task_id': '2018-04-10 16:28:07.735680 517', 'correlation_id': '2018-04-10 16:28:07.735680 517', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '22180'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    Message:
    OrderedDict([('correlation_id', '21976'), ('message_id', '2018-04-10 16:28:11.208156 874'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    




    [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]



### Chords
Celery [Chords](http://docs.celeryproject.org/en/latest/userguide/canvas.html#chords) 的主要作用是由兩段運算所組成的，第一段是一個`Groups`運算，其運算的結果會傳給第二段中的運算，作為其運算所需的參數。  

其作用可以用以下的例子來說明，`header`運算的結果會傳給`callback`做進一步的處理：
```
>>> callback = tsum.s()
>>> header = [add.s(i, i) for i in range(10)]
>>> result = chord(header)(callback)
>>> result.get()
90
```
我們可以在 ESP32 cluster 上面也做同樣的事情：


```python
callback = tasks.xsum.s()
header = [tasks.add.s(i, i) for i in range(10)]
async_result = chord(header)(callback)
async_result.get()
```

    
    Sending 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:11.255298 880'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:11.255298 880'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 259 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:11.255298 880'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:11.255298 880'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '23008'), ('function', 'dequeue_task'), ('message_id', '23008'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '23008'), ('message_id', '2018-04-10 16:28:11.725665 935'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.255298 879', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.255298 879', 'task_id': '2018-04-10 16:28:11.255298 879'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '23008'), ('message_id', '2018-04-10 16:28:11.725665 935'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.255298 879', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.255298 879', 'task_id': '2018-04-10 16:28:11.255298 879'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '22936'), ('function', 'dequeue_task'), ('message_id', '22936'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '22936'), ('message_id', '2018-04-10 16:28:11.867046 949'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 883', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 883', 'task_id': '2018-04-10 16:28:11.280351 883'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '22936'), ('message_id', '2018-04-10 16:28:11.867046 949'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 883', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 883', 'task_id': '2018-04-10 16:28:11.280351 883'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '22975'), ('function', 'dequeue_task'), ('message_id', '22975'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '22975'), ('message_id', '2018-04-10 16:28:12.043101 967'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 884', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 884', 'task_id': '2018-04-10 16:28:11.280351 884'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Sending 487 bytes
    Message:
    OrderedDict([('correlation_id', '22975'), ('message_id', '2018-04-10 16:28:12.043101 967'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 884', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 884', 'task_id': '2018-04-10 16:28:11.280351 884'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '23723'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 0, 'function': 'tasks.add', 'args': [0, 0], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.255298 879', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.255298 879', 'correlation_id': '2018-04-10 16:28:11.255298 879', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '23723'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '23828'), ('function', 'dequeue_task'), ('message_id', '23828'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '23828'), ('message_id', '2018-04-10 16:28:12.734796 1041'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 885', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 885', 'task_id': '2018-04-10 16:28:11.280351 885'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Sending 488 bytes
    Message:
    OrderedDict([('correlation_id', '23828'), ('message_id', '2018-04-10 16:28:12.734796 1041'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 885', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 885', 'task_id': '2018-04-10 16:28:11.280351 885'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '23887'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 2, 'function': 'tasks.add', 'args': [1, 1], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.280351 883', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.280351 883', 'correlation_id': '2018-04-10 16:28:11.280351 883', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '23887'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '23990'), ('function', 'dequeue_task'), ('message_id', '23990'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '23990'), ('message_id', '2018-04-10 16:28:12.925157 1060'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 886', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 886', 'task_id': '2018-04-10 16:28:11.280351 886'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Sending 488 bytes
    Message:
    OrderedDict([('correlation_id', '23990'), ('message_id', '2018-04-10 16:28:12.925157 1060'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 886', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 886', 'task_id': '2018-04-10 16:28:11.280351 886'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '23847'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 4, 'function': 'tasks.add', 'args': [2, 2], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.280351 884', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.280351 884', 'correlation_id': '2018-04-10 16:28:11.280351 884', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '23847'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '23951'), ('function', 'dequeue_task'), ('message_id', '23951'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '23951'), ('message_id', '2018-04-10 16:28:13.202991 1087'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 887', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 887', 'task_id': '2018-04-10 16:28:11.280351 887'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Sending 488 bytes
    Message:
    OrderedDict([('correlation_id', '23951'), ('message_id', '2018-04-10 16:28:13.202991 1087'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 887', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 887', 'task_id': '2018-04-10 16:28:11.280351 887'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '24535'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 6, 'function': 'tasks.add', 'args': [3, 3], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.280351 885', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.280351 885', 'correlation_id': '2018-04-10 16:28:11.280351 885', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '24535'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '24638'), ('function', 'dequeue_task'), ('message_id', '24638'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '24638'), ('message_id', '2018-04-10 16:28:13.533323 1121'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 888', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 888', 'task_id': '2018-04-10 16:28:11.280351 888'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Sending 488 bytes
    Message:
    OrderedDict([('correlation_id', '24638'), ('message_id', '2018-04-10 16:28:13.533323 1121'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 888', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 888', 'task_id': '2018-04-10 16:28:11.280351 888'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Data received: 521 bytes
    Message:
    OrderedDict([('correlation_id', '24889'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 8, 'function': 'tasks.add', 'args': [4, 4], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.280351 886', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.280351 886', 'correlation_id': '2018-04-10 16:28:11.280351 886', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '24889'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '24994'), ('function', 'dequeue_task'), ('message_id', '24994'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '24994'), ('message_id', '2018-04-10 16:28:14.027757 1174'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 889', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 889', 'task_id': '2018-04-10 16:28:11.280351 889'}, 2)), ('sender', 'Wei-Legion')])
    
    
    Sending 488 bytes
    Data received: 522 bytes
    
    Message:
    OrderedDict([('correlation_id', '24994'), ('message_id', '2018-04-10 16:28:14.027757 1174'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 889', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 889', 'task_id': '2018-04-10 16:28:11.280351 889'}, 2)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '24974'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 10, 'function': 'tasks.add', 'args': [5, 5], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.280351 887', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.280351 887', 'correlation_id': '2018-04-10 16:28:11.280351 887', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '24974'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '25077'), ('function', 'dequeue_task'), ('message_id', '25077'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '25077'), ('message_id', '2018-04-10 16:28:14.130043 1183'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 890', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 890', 'task_id': '2018-04-10 16:28:11.280351 890'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Sending 488 bytes
    Message:
    OrderedDict([('correlation_id', '25077'), ('message_id', '2018-04-10 16:28:14.130043 1183'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 890', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 890', 'task_id': '2018-04-10 16:28:11.280351 890'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Data received: 522 bytes
    Message:
    OrderedDict([('correlation_id', '25344'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 12, 'function': 'tasks.add', 'args': [6, 6], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.280351 888', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.280351 888', 'correlation_id': '2018-04-10 16:28:11.280351 888', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '25344'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '25446'), ('function', 'dequeue_task'), ('message_id', '25446'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '25446'), ('message_id', '2018-04-10 16:28:14.388242 1209'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 891', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 891', 'task_id': '2018-04-10 16:28:11.280351 891'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 488 bytes
    Message:
    OrderedDict([('correlation_id', '25446'), ('message_id', '2018-04-10 16:28:14.388242 1209'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:11.280351 891', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:11.280351 891', 'task_id': '2018-04-10 16:28:11.280351 891'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 522 bytes
    Message:
    OrderedDict([('correlation_id', '25845'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 14, 'function': 'tasks.add', 'args': [7, 7], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.280351 889', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.280351 889', 'correlation_id': '2018-04-10 16:28:11.280351 889', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '25845'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '25949'), ('function', 'dequeue_task'), ('message_id', '25949'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '25949'), ('message_id', '2018-04-10 16:28:14.846368 1259'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '25949'), ('message_id', '2018-04-10 16:28:14.846368 1259'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 522 bytes
    Message:
    OrderedDict([('correlation_id', '25808'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 16, 'function': 'tasks.add', 'args': [8, 8], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.280351 890', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.280351 890', 'correlation_id': '2018-04-10 16:28:11.280351 890', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '25808'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '25911'), ('function', 'dequeue_task'), ('message_id', '25911'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '25911'), ('message_id', '2018-04-10 16:28:15.049407 1279'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    Data received: 522 bytes
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '26203'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 18, 'function': 'tasks.add', 'args': [9, 9], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:11.280351 891', 'message_type': 'result', 'task_id': '2018-04-10 16:28:11.280351 891', 'correlation_id': '2018-04-10 16:28:11.280351 891', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '26203'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    Message:
    OrderedDict([('correlation_id', '25911'), ('message_id', '2018-04-10 16:28:15.049407 1279'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:15.093201 1285'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:15.093201 1285'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:15.093201 1285'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:15.093201 1285'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '26776'), ('function', 'dequeue_task'), ('message_id', '26776'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '26776'), ('message_id', '2018-04-10 16:28:15.645344 1344'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:15.093201 1284', 'function': 'tasks.xsum', 'args': ([0, 2, 4, 6, 8, 10, 12, 14, 16, 18],), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:15.093201 1284', 'task_id': '2018-04-10 16:28:15.093201 1284'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 523 bytes
    Message:
    OrderedDict([('correlation_id', '26776'), ('message_id', '2018-04-10 16:28:15.645344 1344'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:15.093201 1284', 'function': 'tasks.xsum', 'args': ([0, 2, 4, 6, 8, 10, 12, 14, 16, 18],), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:15.093201 1284', 'task_id': '2018-04-10 16:28:15.093201 1284'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '26850'), ('function', 'dequeue_task'), ('message_id', '26850'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '26850'), ('message_id', '2018-04-10 16:28:15.745628 1354'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '26850'), ('message_id', '2018-04-10 16:28:15.745628 1354'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '26737'), ('function', 'dequeue_task'), ('message_id', '26737'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '26737'), ('message_id', '2018-04-10 16:28:15.784209 1357'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '26737'), ('message_id', '2018-04-10 16:28:15.784209 1357'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 557 bytes
    Message:
    OrderedDict([('correlation_id', '27460'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 90, 'function': 'tasks.xsum', 'args': [[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:15.093201 1284', 'message_type': 'result', 'task_id': '2018-04-10 16:28:15.093201 1284', 'correlation_id': '2018-04-10 16:28:15.093201 1284', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '27460'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    




    90



上述的運算可以直接寫成：
```
chord(add.s(i, i) for i in xrange(10))(tsum.s()).get()
```
我們可以在 ESP32 cluster 上面也做同樣的事情：


```python
async_result = chord([tasks.add.s(i, i) for i in range(10)])(tasks.xsum.s())
async_result.get()
```

    
    Sending 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:16.294612 1415'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:16.294612 1415'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:16.294612 1415'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:16.294612 1415'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '28022'), ('function', 'dequeue_task'), ('message_id', '28022'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '28022'), ('message_id', '2018-04-10 16:28:16.886740 1484'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.294612 1414', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.294612 1414', 'task_id': '2018-04-10 16:28:16.294612 1414'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '27944'), ('function', 'dequeue_task'), ('message_id', '27944'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '27944'), ('message_id', '2018-04-10 16:28:16.915329 1487'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1418', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1418', 'task_id': '2018-04-10 16:28:16.319680 1418'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '27944'), ('message_id', '2018-04-10 16:28:16.915329 1487'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1418', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1418', 'task_id': '2018-04-10 16:28:16.319680 1418'}, 8)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '28022'), ('message_id', '2018-04-10 16:28:16.886740 1484'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.294612 1414', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.294612 1414', 'task_id': '2018-04-10 16:28:16.294612 1414'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '27906'), ('function', 'dequeue_task'), ('message_id', '27906'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '27906'), ('message_id', '2018-04-10 16:28:16.970231 1491'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1419', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1419', 'task_id': '2018-04-10 16:28:16.319680 1419'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '27906'), ('message_id', '2018-04-10 16:28:16.970231 1491'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1419', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1419', 'task_id': '2018-04-10 16:28:16.319680 1419'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '28732'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 2, 'function': 'tasks.add', 'args': [1, 1], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.319680 1418', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.319680 1418', 'correlation_id': '2018-04-10 16:28:16.319680 1418', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '28732'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '28835'), ('function', 'dequeue_task'), ('message_id', '28835'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '28835'), ('message_id', '2018-04-10 16:28:17.761961 1576'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1420', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1420', 'task_id': '2018-04-10 16:28:16.319680 1420'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '28697'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 4, 'function': 'tasks.add', 'args': [2, 2], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.319680 1419', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.319680 1419', 'correlation_id': '2018-04-10 16:28:16.319680 1419', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '28697'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    Message:
    OrderedDict([('correlation_id', '28835'), ('message_id', '2018-04-10 16:28:17.761961 1576'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1420', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1420', 'task_id': '2018-04-10 16:28:16.319680 1420'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '28800'), ('function', 'dequeue_task'), ('message_id', '28800'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '28800'), ('message_id', '2018-04-10 16:28:17.852821 1584'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1421', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1421', 'task_id': '2018-04-10 16:28:16.319680 1421'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '28800'), ('message_id', '2018-04-10 16:28:17.852821 1584'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1421', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1421', 'task_id': '2018-04-10 16:28:16.319680 1421'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '28680'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 0, 'function': 'tasks.add', 'args': [0, 0], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.294612 1414', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.294612 1414', 'correlation_id': '2018-04-10 16:28:16.294612 1414', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '28680'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '28784'), ('function', 'dequeue_task'), ('message_id', '28784'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '28784'), ('message_id', '2018-04-10 16:28:18.057257 1603'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1422', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1422', 'task_id': '2018-04-10 16:28:16.319680 1422'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '28784'), ('message_id', '2018-04-10 16:28:18.057257 1603'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1422', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1422', 'task_id': '2018-04-10 16:28:16.319680 1422'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '29448'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 6, 'function': 'tasks.add', 'args': [3, 3], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.319680 1420', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.319680 1420', 'correlation_id': '2018-04-10 16:28:16.319680 1420', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '29448'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '29552'), ('function', 'dequeue_task'), ('message_id', '29552'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '29552'), ('message_id', '2018-04-10 16:28:18.357310 1634'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1423', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1423', 'task_id': '2018-04-10 16:28:16.319680 1423'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '29552'), ('message_id', '2018-04-10 16:28:18.357310 1634'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1423', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1423', 'task_id': '2018-04-10 16:28:16.319680 1423'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '29593'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 8, 'function': 'tasks.add', 'args': [4, 4], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.319680 1421', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.319680 1421', 'correlation_id': '2018-04-10 16:28:16.319680 1421', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '29593'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '29696'), ('function', 'dequeue_task'), ('message_id', '29696'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '29696'), ('message_id', '2018-04-10 16:28:18.530949 1651'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1424', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1424', 'task_id': '2018-04-10 16:28:16.319680 1424'}, 2)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '29696'), ('message_id', '2018-04-10 16:28:18.530949 1651'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.319680 1424', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.319680 1424', 'task_id': '2018-04-10 16:28:16.319680 1424'}, 2)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '29789'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 10, 'function': 'tasks.add', 'args': [5, 5], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.319680 1422', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.319680 1422', 'correlation_id': '2018-04-10 16:28:16.319680 1422', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '29789'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '29893'), ('function', 'dequeue_task'), ('message_id', '29893'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '29893'), ('message_id', '2018-04-10 16:28:18.719531 1670'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.320181 1425', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.320181 1425', 'task_id': '2018-04-10 16:28:16.320181 1425'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '29893'), ('message_id', '2018-04-10 16:28:18.719531 1670'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.320181 1425', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.320181 1425', 'task_id': '2018-04-10 16:28:16.320181 1425'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '30038'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 12, 'function': 'tasks.add', 'args': [6, 6], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.319680 1423', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.319680 1423', 'correlation_id': '2018-04-10 16:28:16.319680 1423', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '30038'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '30142'), ('function', 'dequeue_task'), ('message_id', '30142'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '30142'), ('message_id', '2018-04-10 16:28:19.075878 1707'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.320181 1426', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.320181 1426', 'task_id': '2018-04-10 16:28:16.320181 1426'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '30142'), ('message_id', '2018-04-10 16:28:19.075878 1707'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:16.320181 1426', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:16.320181 1426', 'task_id': '2018-04-10 16:28:16.320181 1426'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '30288'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 14, 'function': 'tasks.add', 'args': [7, 7], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.319680 1424', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.319680 1424', 'correlation_id': '2018-04-10 16:28:16.319680 1424', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '30288'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '30393'), ('function', 'dequeue_task'), ('message_id', '30393'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '30393'), ('message_id', '2018-04-10 16:28:19.872172 1796'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '30393'), ('message_id', '2018-04-10 16:28:19.872172 1796'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '31022'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 16, 'function': 'tasks.add', 'args': [8, 8], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.320181 1425', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.320181 1425', 'correlation_id': '2018-04-10 16:28:16.320181 1425', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '31022'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '31126'), ('function', 'dequeue_task'), ('message_id', '31126'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '31126'), ('message_id', '2018-04-10 16:28:20.104182 1819'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '31126'), ('message_id', '2018-04-10 16:28:20.104182 1819'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '31169'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 18, 'function': 'tasks.add', 'args': [9, 9], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:16.320181 1426', 'message_type': 'result', 'task_id': '2018-04-10 16:28:16.320181 1426', 'correlation_id': '2018-04-10 16:28:16.320181 1426', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '31169'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Sending 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:20.199888 1830'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:20.199888 1830'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:20.199888 1830'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:20.199888 1830'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '31818'), ('function', 'dequeue_task'), ('message_id', '31818'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '31818'), ('message_id', '2018-04-10 16:28:20.689503 1882'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:20.199888 1829', 'function': 'tasks.xsum', 'args': ([0, 2, 4, 6, 8, 10, 12, 14, 16, 18],), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:20.199888 1829', 'task_id': '2018-04-10 16:28:20.199888 1829'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 523 bytes
    Message:
    OrderedDict([('correlation_id', '31818'), ('message_id', '2018-04-10 16:28:20.689503 1882'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:20.199888 1829', 'function': 'tasks.xsum', 'args': ([0, 2, 4, 6, 8, 10, 12, 14, 16, 18],), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:20.199888 1829', 'task_id': '2018-04-10 16:28:20.199888 1829'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '31778'), ('function', 'dequeue_task'), ('message_id', '31778'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '31778'), ('message_id', '2018-04-10 16:28:20.848381 1898'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '31778'), ('message_id', '2018-04-10 16:28:20.848381 1898'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '32448'), ('function', 'dequeue_task'), ('message_id', '32448'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '32448'), ('message_id', '2018-04-10 16:28:21.242869 1940'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '32448'), ('message_id', '2018-04-10 16:28:21.242869 1940'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 557 bytes
    Message:
    OrderedDict([('correlation_id', '32536'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 90, 'function': 'tasks.xsum', 'args': [[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:20.199888 1829', 'message_type': 'result', 'task_id': '2018-04-10 16:28:20.199888 1829', 'correlation_id': '2018-04-10 16:28:20.199888 1829', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '32536'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    




    90



### Map & Starmap
Celery [Map & Starmap](http://docs.celeryproject.org/en/latest/userguide/canvas.html#map-starmap) 的主要作用和 Python 中的`map`指令一樣，會對一個 list 中的每個 element 做指定的運算，例如下例會分別對`range(10)`,`range(100)`做`sum`運算：
```
>>> ~xsum.map([range(10), range(100)])
[45, 4950]
```
我們可以在 ESP32 cluster 上面也做同樣的事情，但是須先使用`list()`對`range`物件做展開：


```python
gp = tasks.xsum.map([list(range(10)), list(range(100))])
gp.get()
```

    
    Sending 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:21.407229 1959'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:21.407229 1959'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:21.407229 1959'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:21.407229 1959'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '33059'), ('function', 'dequeue_task'), ('message_id', '33059'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '33059'), ('message_id', '2018-04-10 16:28:21.873090 2007'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:21.407229 1958', 'function': 'tasks.xsum', 'args': ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:21.407229 1958', 'task_id': '2018-04-10 16:28:21.407229 1958'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Sending 518 bytes
    Message:
    OrderedDict([('correlation_id', '33059'), ('message_id', '2018-04-10 16:28:21.873090 2007'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:21.407229 1958', 'function': 'tasks.xsum', 'args': ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9],), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:21.407229 1958', 'task_id': '2018-04-10 16:28:21.407229 1958'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '33018'), ('function', 'dequeue_task'), ('message_id', '33018'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '33018'), ('message_id', '2018-04-10 16:28:21.970894 2017'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:21.432295 1962', 'function': 'tasks.xsum', 'args': ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:21.432295 1962', 'task_id': '2018-04-10 16:28:21.432295 1962'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 878 bytes
    Message:
    OrderedDict([('correlation_id', '33018'), ('message_id', '2018-04-10 16:28:21.970894 2017'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:21.432295 1962', 'function': 'tasks.xsum', 'args': ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:21.432295 1962', 'task_id': '2018-04-10 16:28:21.432295 1962'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '33211'), ('function', 'dequeue_task'), ('message_id', '33211'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '33211'), ('message_id', '2018-04-10 16:28:22.007378 2020'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '33211'), ('message_id', '2018-04-10 16:28:22.007378 2020'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 552 bytes
    Message:
    OrderedDict([('correlation_id', '33576'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 45, 'function': 'tasks.xsum', 'args': [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:21.407229 1958', 'message_type': 'result', 'task_id': '2018-04-10 16:28:21.407229 1958', 'correlation_id': '2018-04-10 16:28:21.407229 1958', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '33576'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '33687'), ('function', 'dequeue_task'), ('message_id', '33687'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '33687'), ('message_id', '2018-04-10 16:28:22.568614 2078'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '33687'), ('message_id', '2018-04-10 16:28:22.568614 2078'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 914 bytes
    Message:
    OrderedDict([('correlation_id', '33795'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 4950, 'function': 'tasks.xsum', 'args': [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:21.432295 1962', 'message_type': 'result', 'task_id': '2018-04-10 16:28:21.432295 1962', 'correlation_id': '2018-04-10 16:28:21.432295 1962', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '33795'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    




    [45, 4950]



`starmap`的作用和`map`指令一樣，會對一個 list 中的每個 element 做指定的運算，只是會先做 star展開，將一個`list`展開成為 positional arguments：
```
>>> ~add.starmap(zip(range(10), range(10)))
[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```
我們可以在 ESP32 cluster 上面也做同樣的事情，但是須先使用`list()`對`zip`物件做展開：


```python
gp = tasks.add.starmap(list(zip(range(10), range(10))))
gp.get()
```

    
    Sending 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:22.764440 2100'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:22.764440 2100'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:22.764440 2100'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:22.764440 2100'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '34380'), ('function', 'dequeue_task'), ('message_id', '34380'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '34380'), ('message_id', '2018-04-10 16:28:23.185341 2149'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.764440 2099', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.764440 2099', 'task_id': '2018-04-10 16:28:22.764440 2099'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '34380'), ('message_id', '2018-04-10 16:28:23.185341 2149'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.764440 2099', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.764440 2099', 'task_id': '2018-04-10 16:28:22.764440 2099'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '34454'), ('function', 'dequeue_task'), ('message_id', '34454'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '34454'), ('message_id', '2018-04-10 16:28:23.345767 2164'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2102', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2102', 'task_id': '2018-04-10 16:28:22.786999 2102'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '34454'), ('message_id', '2018-04-10 16:28:23.345767 2164'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2102', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2102', 'task_id': '2018-04-10 16:28:22.786999 2102'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '34343'), ('function', 'dequeue_task'), ('message_id', '34343'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '34343'), ('message_id', '2018-04-10 16:28:23.463306 2175'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2103', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2103', 'task_id': '2018-04-10 16:28:22.786999 2103'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '34343'), ('message_id', '2018-04-10 16:28:23.463306 2175'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2103', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2103', 'task_id': '2018-04-10 16:28:22.786999 2103'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '34859'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 0, 'function': 'tasks.add', 'args': [0, 0], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.764440 2099', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.764440 2099', 'correlation_id': '2018-04-10 16:28:22.764440 2099', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '34859'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '34963'), ('function', 'dequeue_task'), ('message_id', '34963'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '34963'), ('message_id', '2018-04-10 16:28:23.850786 2214'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2104', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2104', 'task_id': '2018-04-10 16:28:22.786999 2104'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '34963'), ('message_id', '2018-04-10 16:28:23.850786 2214'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2104', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2104', 'task_id': '2018-04-10 16:28:22.786999 2104'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '35228'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 2, 'function': 'tasks.add', 'args': [1, 1], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.786999 2102', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.786999 2102', 'correlation_id': '2018-04-10 16:28:22.786999 2102', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '35228'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '35333'), ('function', 'dequeue_task'), ('message_id', '35333'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '35333'), ('message_id', '2018-04-10 16:28:24.157139 2244'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2105', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2105', 'task_id': '2018-04-10 16:28:22.786999 2105'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '35333'), ('message_id', '2018-04-10 16:28:24.157139 2244'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2105', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2105', 'task_id': '2018-04-10 16:28:22.786999 2105'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '35208'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 4, 'function': 'tasks.add', 'args': [2, 2], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.786999 2103', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.786999 2103', 'correlation_id': '2018-04-10 16:28:22.786999 2103', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '35208'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '35311'), ('function', 'dequeue_task'), ('message_id', '35311'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '35311'), ('message_id', '2018-04-10 16:28:24.441387 2273'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2106', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2106', 'task_id': '2018-04-10 16:28:22.786999 2106'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '35311'), ('message_id', '2018-04-10 16:28:24.441387 2273'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2106', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2106', 'task_id': '2018-04-10 16:28:22.786999 2106'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '35545'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 6, 'function': 'tasks.add', 'args': [3, 3], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.786999 2104', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.786999 2104', 'correlation_id': '2018-04-10 16:28:22.786999 2104', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '35545'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '35649'), ('function', 'dequeue_task'), ('message_id', '35649'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '35649'), ('message_id', '2018-04-10 16:28:24.602280 2288'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2107', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2107', 'task_id': '2018-04-10 16:28:22.786999 2107'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '35649'), ('message_id', '2018-04-10 16:28:24.602280 2288'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2107', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2107', 'task_id': '2018-04-10 16:28:22.786999 2107'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '36094'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 8, 'function': 'tasks.add', 'args': [4, 4], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.786999 2105', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.786999 2105', 'correlation_id': '2018-04-10 16:28:22.786999 2105', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '36094'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '36197'), ('function', 'dequeue_task'), ('message_id', '36197'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '36197'), ('message_id', '2018-04-10 16:28:25.013487 2331'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2108', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2108', 'task_id': '2018-04-10 16:28:22.786999 2108'}, 2)), ('sender', 'Wei-Legion')])
    
    Data received: 525 bytes
    
    Sending 491 bytes
    
    Message:
    OrderedDict([('correlation_id', '36136'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 10, 'function': 'tasks.add', 'args': [5, 5], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.786999 2106', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.786999 2106', 'correlation_id': '2018-04-10 16:28:22.786999 2106', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '36136'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    Message:
    OrderedDict([('correlation_id', '36197'), ('message_id', '2018-04-10 16:28:25.013487 2331'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2108', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2108', 'task_id': '2018-04-10 16:28:22.786999 2108'}, 2)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '36240'), ('function', 'dequeue_task'), ('message_id', '36240'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '36240'), ('message_id', '2018-04-10 16:28:25.171383 2346'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2109', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2109', 'task_id': '2018-04-10 16:28:22.786999 2109'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '36240'), ('message_id', '2018-04-10 16:28:25.171383 2346'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2109', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2109', 'task_id': '2018-04-10 16:28:22.786999 2109'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '36430'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 12, 'function': 'tasks.add', 'args': [6, 6], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.786999 2107', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.786999 2107', 'correlation_id': '2018-04-10 16:28:22.786999 2107', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '36430'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '36533'), ('function', 'dequeue_task'), ('message_id', '36533'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '36533'), ('message_id', '2018-04-10 16:28:25.387372 2368'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2110', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2110', 'task_id': '2018-04-10 16:28:22.786999 2110'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 491 bytes
    Message:
    OrderedDict([('correlation_id', '36533'), ('message_id', '2018-04-10 16:28:25.387372 2368'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:22.786999 2110', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:22.786999 2110', 'task_id': '2018-04-10 16:28:22.786999 2110'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '36916'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 14, 'function': 'tasks.add', 'args': [7, 7], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.786999 2108', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.786999 2108', 'correlation_id': '2018-04-10 16:28:22.786999 2108', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '36916'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '37019'), ('function', 'dequeue_task'), ('message_id', '37019'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '37019'), ('message_id', '2018-04-10 16:28:25.792885 2411'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '37019'), ('message_id', '2018-04-10 16:28:25.792885 2411'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '36859'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 16, 'function': 'tasks.add', 'args': [8, 8], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.786999 2109', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.786999 2109', 'correlation_id': '2018-04-10 16:28:22.786999 2109', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '36859'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '36963'), ('function', 'dequeue_task'), ('message_id', '36963'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '36963'), ('message_id', '2018-04-10 16:28:25.948297 2426'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '36963'), ('message_id', '2018-04-10 16:28:25.948297 2426'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '37089'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 18, 'function': 'tasks.add', 'args': [9, 9], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:22.786999 2110', 'message_type': 'result', 'task_id': '2018-04-10 16:28:22.786999 2110', 'correlation_id': '2018-04-10 16:28:22.786999 2110', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '37089'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    




    [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]



### Chunks
Celery [Chunks](http://docs.celeryproject.org/en/latest/userguide/canvas.html#chunks) 的主要作用是把一大串的資料切成指定的份數，分發給遠端的 workers 協處處理，例如：
```
>>> res = add.chunks(zip(range(100), range(100)), 10)()
>>> res.get()
[[0, 2, 4, 6, 8, 10, 12, 14, 16, 18],
 [20, 22, 24, 26, 28, 30, 32, 34, 36, 38],
 [40, 42, 44, 46, 48, 50, 52, 54, 56, 58],
 [60, 62, 64, 66, 68, 70, 72, 74, 76, 78],
 [80, 82, 84, 86, 88, 90, 92, 94, 96, 98],
 [100, 102, 104, 106, 108, 110, 112, 114, 116, 118],
 [120, 122, 124, 126, 128, 130, 132, 134, 136, 138],
 [140, 142, 144, 146, 148, 150, 152, 154, 156, 158],
 [160, 162, 164, 166, 168, 170, 172, 174, 176, 178],
 [180, 182, 184, 186, 188, 190, 192, 194, 196, 198]]
```
我們可以在 ESP32 cluster 上面也做同樣的事情，但是須先使用`list()`對`zip`物件做展開：


```python
ck = tasks.add.chunks(list(zip(range(100), range(100))), 10)
async_result = ck()
async_result.get()
```

    
    Sending 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:26.061545 2439'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:26.061545 2439'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:26.061545 2439'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:26.061545 2439'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '37766'), ('function', 'dequeue_task'), ('message_id', '37766'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '37766'), ('message_id', '2018-04-10 16:28:26.670350 2599'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.061545 2438', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.061545 2438', 'task_id': '2018-04-10 16:28:26.061545 2438'}, 99)), ('sender', 'Wei-Legion')])
    
    
    Sending 492 bytes
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '37839'), ('function', 'dequeue_task'), ('message_id', '37839'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '37839'), ('message_id', '2018-04-10 16:28:26.698424 2602'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2441', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2441', 'task_id': '2018-04-10 16:28:26.074580 2441'}, 98)), ('sender', 'Wei-Legion')])
    
    
    Sending 492 bytes
    Message:
    OrderedDict([('correlation_id', '37839'), ('message_id', '2018-04-10 16:28:26.698424 2602'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2441', 'function': 'tasks.add', 'args': (1, 1), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2441', 'task_id': '2018-04-10 16:28:26.074580 2441'}, 98)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '37766'), ('message_id', '2018-04-10 16:28:26.670350 2599'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.061545 2438', 'function': 'tasks.add', 'args': (0, 0), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.061545 2438', 'task_id': '2018-04-10 16:28:26.061545 2438'}, 99)), ('sender', 'Wei-Legion')])
    
    Data received: 219 bytes
    
    Message:
    OrderedDict([('correlation_id', '37775'), ('function', 'dequeue_task'), ('message_id', '37775'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '37775'), ('message_id', '2018-04-10 16:28:26.737964 2604'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2442', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2442', 'task_id': '2018-04-10 16:28:26.074580 2442'}, 97)), ('sender', 'Wei-Legion')])
    
    
    Sending 492 bytes
    Message:
    OrderedDict([('correlation_id', '37775'), ('message_id', '2018-04-10 16:28:26.737964 2604'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2442', 'function': 'tasks.add', 'args': (2, 2), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2442', 'task_id': '2018-04-10 16:28:26.074580 2442'}, 97)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '38367'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 0, 'function': 'tasks.add', 'args': [0, 0], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.061545 2438', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.061545 2438', 'correlation_id': '2018-04-10 16:28:26.061545 2438', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '38367'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '38471'), ('function', 'dequeue_task'), ('message_id', '38471'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '38471'), ('message_id', '2018-04-10 16:28:27.367684 2668'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2443', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2443', 'task_id': '2018-04-10 16:28:26.074580 2443'}, 96)), ('sender', 'Wei-Legion')])
    
    
    Sending 492 bytes
    Message:
    OrderedDict([('correlation_id', '38471'), ('message_id', '2018-04-10 16:28:27.367684 2668'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2443', 'function': 'tasks.add', 'args': (3, 3), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2443', 'task_id': '2018-04-10 16:28:26.074580 2443'}, 96)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '38611'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 2, 'function': 'tasks.add', 'args': [1, 1], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2441', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2441', 'correlation_id': '2018-04-10 16:28:26.074580 2441', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '38611'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '38715'), ('function', 'dequeue_task'), ('message_id', '38715'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '38715'), ('message_id', '2018-04-10 16:28:27.621004 2693'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2444', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2444', 'task_id': '2018-04-10 16:28:26.074580 2444'}, 95)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    
    Sending 492 bytes
    Message:
    OrderedDict([('correlation_id', '38497'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 4, 'function': 'tasks.add', 'args': [2, 2], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2442', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2442', 'correlation_id': '2018-04-10 16:28:26.074580 2442', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '38497'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    Message:
    OrderedDict([('correlation_id', '38715'), ('message_id', '2018-04-10 16:28:27.621004 2693'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2444', 'function': 'tasks.add', 'args': (4, 4), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2444', 'task_id': '2018-04-10 16:28:26.074580 2444'}, 95)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '38601'), ('function', 'dequeue_task'), ('message_id', '38601'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '38601'), ('message_id', '2018-04-10 16:28:27.715802 2701'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2445', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2445', 'task_id': '2018-04-10 16:28:26.074580 2445'}, 94)), ('sender', 'Wei-Legion')])
    
    
    Sending 492 bytes
    Message:
    OrderedDict([('correlation_id', '38601'), ('message_id', '2018-04-10 16:28:27.715802 2701'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2445', 'function': 'tasks.add', 'args': (5, 5), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2445', 'task_id': '2018-04-10 16:28:26.074580 2445'}, 94)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '39207'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 6, 'function': 'tasks.add', 'args': [3, 3], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2443', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2443', 'correlation_id': '2018-04-10 16:28:26.074580 2443', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '39207'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '39311'), ('function', 'dequeue_task'), ('message_id', '39311'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '39311'), ('message_id', '2018-04-10 16:28:28.266456 2758'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2446', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2446', 'task_id': '2018-04-10 16:28:26.074580 2446'}, 93)), ('sender', 'Wei-Legion')])
    
    
    Sending 492 bytes
    Message:
    OrderedDict([('correlation_id', '39311'), ('message_id', '2018-04-10 16:28:28.266456 2758'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2446', 'function': 'tasks.add', 'args': (6, 6), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2446', 'task_id': '2018-04-10 16:28:26.074580 2446'}, 93)), ('sender', 'Wei-Legion')])
    
    
    Data received: 524 bytes
    Message:
    OrderedDict([('correlation_id', '39480'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 8, 'function': 'tasks.add', 'args': [4, 4], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2444', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2444', 'correlation_id': '2018-04-10 16:28:26.074580 2444', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '39480'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '39584'), ('function', 'dequeue_task'), ('message_id', '39584'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '39584'), ('message_id', '2018-04-10 16:28:28.446955 2775'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2447', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2447', 'task_id': '2018-04-10 16:28:26.074580 2447'}, 92)), ('sender', 'Wei-Legion')])
    
    
    Sending 492 bytes
    Message:
    OrderedDict([('correlation_id', '39584'), ('message_id', '2018-04-10 16:28:28.446955 2775'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2447', 'function': 'tasks.add', 'args': (7, 7), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2447', 'task_id': '2018-04-10 16:28:26.074580 2447'}, 92)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '39529'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 10, 'function': 'tasks.add', 'args': [5, 5], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2445', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2445', 'correlation_id': '2018-04-10 16:28:26.074580 2445', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '39529'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '39634'), ('function', 'dequeue_task'), ('message_id', '39634'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '39634'), ('message_id', '2018-04-10 16:28:28.773304 2808'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2448', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2448', 'task_id': '2018-04-10 16:28:26.074580 2448'}, 91)), ('sender', 'Wei-Legion')])
    
    
    Sending 492 bytes
    Message:
    OrderedDict([('correlation_id', '39634'), ('message_id', '2018-04-10 16:28:28.773304 2808'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2448', 'function': 'tasks.add', 'args': (8, 8), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2448', 'task_id': '2018-04-10 16:28:26.074580 2448'}, 91)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '40042'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 12, 'function': 'tasks.add', 'args': [6, 6], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2446', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2446', 'correlation_id': '2018-04-10 16:28:26.074580 2446', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '40042'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '40148'), ('function', 'dequeue_task'), ('message_id', '40148'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '40148'), ('message_id', '2018-04-10 16:28:29.125348 2843'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2449', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2449', 'task_id': '2018-04-10 16:28:26.074580 2449'}, 90)), ('sender', 'Wei-Legion')])
    
    
    Sending 492 bytes
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '40410'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 14, 'function': 'tasks.add', 'args': [7, 7], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2447', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2447', 'correlation_id': '2018-04-10 16:28:26.074580 2447', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '40410'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    Message:
    OrderedDict([('correlation_id', '40148'), ('message_id', '2018-04-10 16:28:29.125348 2843'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2449', 'function': 'tasks.add', 'args': (9, 9), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2449', 'task_id': '2018-04-10 16:28:26.074580 2449'}, 90)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '40516'), ('function', 'dequeue_task'), ('message_id', '40516'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '40516'), ('message_id', '2018-04-10 16:28:29.397424 2870'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2450', 'function': 'tasks.add', 'args': (10, 10), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2450', 'task_id': '2018-04-10 16:28:26.074580 2450'}, 89)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '40516'), ('message_id', '2018-04-10 16:28:29.397424 2870'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2450', 'function': 'tasks.add', 'args': (10, 10), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2450', 'task_id': '2018-04-10 16:28:26.074580 2450'}, 89)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '40449'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 16, 'function': 'tasks.add', 'args': [8, 8], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2448', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2448', 'correlation_id': '2018-04-10 16:28:26.074580 2448', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '40449'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '40553'), ('function', 'dequeue_task'), ('message_id', '40553'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '40553'), ('message_id', '2018-04-10 16:28:29.670693 2897'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2451', 'function': 'tasks.add', 'args': (11, 11), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2451', 'task_id': '2018-04-10 16:28:26.074580 2451'}, 88)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '40553'), ('message_id', '2018-04-10 16:28:29.670693 2897'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.074580 2451', 'function': 'tasks.add', 'args': (11, 11), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.074580 2451', 'task_id': '2018-04-10 16:28:26.074580 2451'}, 88)), ('sender', 'Wei-Legion')])
    
    
    Data received: 525 bytes
    Message:
    OrderedDict([('correlation_id', '40850'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 18, 'function': 'tasks.add', 'args': [9, 9], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2449', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2449', 'correlation_id': '2018-04-10 16:28:26.074580 2449', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '40850'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '40955'), ('function', 'dequeue_task'), ('message_id', '40955'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '40955'), ('message_id', '2018-04-10 16:28:30.035758 2934'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2452', 'function': 'tasks.add', 'args': (12, 12), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2452', 'task_id': '2018-04-10 16:28:26.075081 2452'}, 87)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '40955'), ('message_id', '2018-04-10 16:28:30.035758 2934'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2452', 'function': 'tasks.add', 'args': (12, 12), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2452', 'task_id': '2018-04-10 16:28:26.075081 2452'}, 87)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '41608'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 20, 'function': 'tasks.add', 'args': [10, 10], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2450', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2450', 'correlation_id': '2018-04-10 16:28:26.074580 2450', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '41608'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '41712'), ('function', 'dequeue_task'), ('message_id', '41712'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '41712'), ('message_id', '2018-04-10 16:28:30.660598 2997'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2453', 'function': 'tasks.add', 'args': (13, 13), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2453', 'task_id': '2018-04-10 16:28:26.075081 2453'}, 86)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '41712'), ('message_id', '2018-04-10 16:28:30.660598 2997'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2453', 'function': 'tasks.add', 'args': (13, 13), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2453', 'task_id': '2018-04-10 16:28:26.075081 2453'}, 86)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '41577'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 22, 'function': 'tasks.add', 'args': [11, 11], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.074580 2451', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.074580 2451', 'correlation_id': '2018-04-10 16:28:26.074580 2451', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '41577'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '41681'), ('function', 'dequeue_task'), ('message_id', '41681'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '41681'), ('message_id', '2018-04-10 16:28:30.918322 3019'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2454', 'function': 'tasks.add', 'args': (14, 14), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2454', 'task_id': '2018-04-10 16:28:26.075081 2454'}, 85)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '41681'), ('message_id', '2018-04-10 16:28:30.918322 3019'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2454', 'function': 'tasks.add', 'args': (14, 14), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2454', 'task_id': '2018-04-10 16:28:26.075081 2454'}, 85)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '41731'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 24, 'function': 'tasks.add', 'args': [12, 12], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2452', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2452', 'correlation_id': '2018-04-10 16:28:26.075081 2452', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '41731'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '41834'), ('function', 'dequeue_task'), ('message_id', '41834'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '41834'), ('message_id', '2018-04-10 16:28:31.116220 3036'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2455', 'function': 'tasks.add', 'args': (15, 15), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2455', 'task_id': '2018-04-10 16:28:26.075081 2455'}, 84)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '41834'), ('message_id', '2018-04-10 16:28:31.116220 3036'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2455', 'function': 'tasks.add', 'args': (15, 15), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2455', 'task_id': '2018-04-10 16:28:26.075081 2455'}, 84)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '42454'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 26, 'function': 'tasks.add', 'args': [13, 13], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2453', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2453', 'correlation_id': '2018-04-10 16:28:26.075081 2453', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '42454'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '42557'), ('function', 'dequeue_task'), ('message_id', '42557'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '42557'), ('message_id', '2018-04-10 16:28:31.506863 3074'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2456', 'function': 'tasks.add', 'args': (16, 16), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2456', 'task_id': '2018-04-10 16:28:26.075081 2456'}, 83)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '42557'), ('message_id', '2018-04-10 16:28:31.506863 3074'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2456', 'function': 'tasks.add', 'args': (16, 16), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2456', 'task_id': '2018-04-10 16:28:26.075081 2456'}, 83)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '42679'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 28, 'function': 'tasks.add', 'args': [14, 14], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2454', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2454', 'correlation_id': '2018-04-10 16:28:26.075081 2454', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '42679'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '42784'), ('function', 'dequeue_task'), ('message_id', '42784'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '42784'), ('message_id', '2018-04-10 16:28:31.735972 3096'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2457', 'function': 'tasks.add', 'args': (17, 17), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2457', 'task_id': '2018-04-10 16:28:26.075081 2457'}, 82)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '42784'), ('message_id', '2018-04-10 16:28:31.735972 3096'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2457', 'function': 'tasks.add', 'args': (17, 17), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2457', 'task_id': '2018-04-10 16:28:26.075081 2457'}, 82)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '42878'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 30, 'function': 'tasks.add', 'args': [15, 15], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2455', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2455', 'correlation_id': '2018-04-10 16:28:26.075081 2455', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '42878'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '42982'), ('function', 'dequeue_task'), ('message_id', '42982'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '42982'), ('message_id', '2018-04-10 16:28:31.976111 3119'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2458', 'function': 'tasks.add', 'args': (18, 18), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2458', 'task_id': '2018-04-10 16:28:26.075081 2458'}, 81)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '43282'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 32, 'function': 'tasks.add', 'args': [16, 16], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2456', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2456', 'correlation_id': '2018-04-10 16:28:26.075081 2456', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '43282'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    Message:
    OrderedDict([('correlation_id', '42982'), ('message_id', '2018-04-10 16:28:31.976111 3119'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2458', 'function': 'tasks.add', 'args': (18, 18), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2458', 'task_id': '2018-04-10 16:28:26.075081 2458'}, 81)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '43388'), ('function', 'dequeue_task'), ('message_id', '43388'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '43388'), ('message_id', '2018-04-10 16:28:32.139833 3134'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2459', 'function': 'tasks.add', 'args': (19, 19), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2459', 'task_id': '2018-04-10 16:28:26.075081 2459'}, 80)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '43388'), ('message_id', '2018-04-10 16:28:32.139833 3134'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2459', 'function': 'tasks.add', 'args': (19, 19), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2459', 'task_id': '2018-04-10 16:28:26.075081 2459'}, 80)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '43366'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 34, 'function': 'tasks.add', 'args': [17, 17], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2457', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2457', 'correlation_id': '2018-04-10 16:28:26.075081 2457', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '43366'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '43473'), ('function', 'dequeue_task'), ('message_id', '43473'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '43473'), ('message_id', '2018-04-10 16:28:32.296145 3149'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2460', 'function': 'tasks.add', 'args': (20, 20), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2460', 'task_id': '2018-04-10 16:28:26.075081 2460'}, 79)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '43473'), ('message_id', '2018-04-10 16:28:32.296145 3149'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2460', 'function': 'tasks.add', 'args': (20, 20), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2460', 'task_id': '2018-04-10 16:28:26.075081 2460'}, 79)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '43648'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 36, 'function': 'tasks.add', 'args': [18, 18], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2458', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2458', 'correlation_id': '2018-04-10 16:28:26.075081 2458', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '43648'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '43752'), ('function', 'dequeue_task'), ('message_id', '43752'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '43752'), ('message_id', '2018-04-10 16:28:32.580859 3177'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2461', 'function': 'tasks.add', 'args': (21, 21), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2461', 'task_id': '2018-04-10 16:28:26.075081 2461'}, 78)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '43752'), ('message_id', '2018-04-10 16:28:32.580859 3177'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2461', 'function': 'tasks.add', 'args': (21, 21), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2461', 'task_id': '2018-04-10 16:28:26.075081 2461'}, 78)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '43923'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 38, 'function': 'tasks.add', 'args': [19, 19], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2459', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2459', 'correlation_id': '2018-04-10 16:28:26.075081 2459', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '43923'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '44027'), ('function', 'dequeue_task'), ('message_id', '44027'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '44027'), ('message_id', '2018-04-10 16:28:32.846826 3203'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2462', 'function': 'tasks.add', 'args': (22, 22), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2462', 'task_id': '2018-04-10 16:28:26.075081 2462'}, 77)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '44027'), ('message_id', '2018-04-10 16:28:32.846826 3203'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2462', 'function': 'tasks.add', 'args': (22, 22), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2462', 'task_id': '2018-04-10 16:28:26.075081 2462'}, 77)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '43979'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 40, 'function': 'tasks.add', 'args': [20, 20], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2460', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2460', 'correlation_id': '2018-04-10 16:28:26.075081 2460', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '43979'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '44082'), ('function', 'dequeue_task'), ('message_id', '44082'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '44082'), ('message_id', '2018-04-10 16:28:33.031756 3221'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2463', 'function': 'tasks.add', 'args': (23, 23), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2463', 'task_id': '2018-04-10 16:28:26.075081 2463'}, 76)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '44082'), ('message_id', '2018-04-10 16:28:33.031756 3221'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2463', 'function': 'tasks.add', 'args': (23, 23), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2463', 'task_id': '2018-04-10 16:28:26.075081 2463'}, 76)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '44247'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 42, 'function': 'tasks.add', 'args': [21, 21], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2461', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2461', 'correlation_id': '2018-04-10 16:28:26.075081 2461', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '44247'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '44352'), ('function', 'dequeue_task'), ('message_id', '44352'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '44352'), ('message_id', '2018-04-10 16:28:33.220847 3239'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2464', 'function': 'tasks.add', 'args': (24, 24), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2464', 'task_id': '2018-04-10 16:28:26.075081 2464'}, 75)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '44352'), ('message_id', '2018-04-10 16:28:33.220847 3239'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2464', 'function': 'tasks.add', 'args': (24, 24), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2464', 'task_id': '2018-04-10 16:28:26.075081 2464'}, 75)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '44732'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 44, 'function': 'tasks.add', 'args': [22, 22], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2462', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2462', 'correlation_id': '2018-04-10 16:28:26.075081 2462', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '44732'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '44836'), ('function', 'dequeue_task'), ('message_id', '44836'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '44836'), ('message_id', '2018-04-10 16:28:33.645263 3283'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2465', 'function': 'tasks.add', 'args': (25, 25), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2465', 'task_id': '2018-04-10 16:28:26.075081 2465'}, 74)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '44836'), ('message_id', '2018-04-10 16:28:33.645263 3283'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2465', 'function': 'tasks.add', 'args': (25, 25), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2465', 'task_id': '2018-04-10 16:28:26.075081 2465'}, 74)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '44699'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 46, 'function': 'tasks.add', 'args': [23, 23], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2463', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2463', 'correlation_id': '2018-04-10 16:28:26.075081 2463', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '44699'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '44805'), ('function', 'dequeue_task'), ('message_id', '44805'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '44805'), ('message_id', '2018-04-10 16:28:33.798780 3297'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2466', 'function': 'tasks.add', 'args': (26, 26), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2466', 'task_id': '2018-04-10 16:28:26.075081 2466'}, 73)), ('sender', 'Wei-Legion')])
    
    Data received: 527 bytes
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '44805'), ('message_id', '2018-04-10 16:28:33.798780 3297'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2466', 'function': 'tasks.add', 'args': (26, 26), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2466', 'task_id': '2018-04-10 16:28:26.075081 2466'}, 73)), ('sender', 'Wei-Legion')])
    
    
    Message:
    OrderedDict([('correlation_id', '44903'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 48, 'function': 'tasks.add', 'args': [24, 24], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2464', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2464', 'correlation_id': '2018-04-10 16:28:26.075081 2464', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '44903'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '45007'), ('function', 'dequeue_task'), ('message_id', '45007'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '45007'), ('message_id', '2018-04-10 16:28:34.040687 3321'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2467', 'function': 'tasks.add', 'args': (27, 27), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2467', 'task_id': '2018-04-10 16:28:26.075081 2467'}, 72)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '45007'), ('message_id', '2018-04-10 16:28:34.040687 3321'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2467', 'function': 'tasks.add', 'args': (27, 27), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2467', 'task_id': '2018-04-10 16:28:26.075081 2467'}, 72)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '45446'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 50, 'function': 'tasks.add', 'args': [25, 25], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2465', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2465', 'correlation_id': '2018-04-10 16:28:26.075081 2465', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '45446'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '45550'), ('function', 'dequeue_task'), ('message_id', '45550'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '45550'), ('message_id', '2018-04-10 16:28:34.398766 3357'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2468', 'function': 'tasks.add', 'args': (28, 28), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2468', 'task_id': '2018-04-10 16:28:26.075081 2468'}, 71)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '45550'), ('message_id', '2018-04-10 16:28:34.398766 3357'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2468', 'function': 'tasks.add', 'args': (28, 28), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2468', 'task_id': '2018-04-10 16:28:26.075081 2468'}, 71)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '45720'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 52, 'function': 'tasks.add', 'args': [26, 26], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2466', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2466', 'correlation_id': '2018-04-10 16:28:26.075081 2466', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '45720'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '45824'), ('function', 'dequeue_task'), ('message_id', '45824'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '45824'), ('message_id', '2018-04-10 16:28:34.692045 3385'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2469', 'function': 'tasks.add', 'args': (29, 29), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2469', 'task_id': '2018-04-10 16:28:26.075081 2469'}, 70)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '45824'), ('message_id', '2018-04-10 16:28:34.692045 3385'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2469', 'function': 'tasks.add', 'args': (29, 29), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2469', 'task_id': '2018-04-10 16:28:26.075081 2469'}, 70)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '45889'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 54, 'function': 'tasks.add', 'args': [27, 27], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2467', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2467', 'correlation_id': '2018-04-10 16:28:26.075081 2467', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '45889'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '45993'), ('function', 'dequeue_task'), ('message_id', '45993'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '45993'), ('message_id', '2018-04-10 16:28:34.898078 3405'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2470', 'function': 'tasks.add', 'args': (30, 30), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2470', 'task_id': '2018-04-10 16:28:26.075081 2470'}, 69)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '45993'), ('message_id', '2018-04-10 16:28:34.898078 3405'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2470', 'function': 'tasks.add', 'args': (30, 30), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2470', 'task_id': '2018-04-10 16:28:26.075081 2470'}, 69)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '46165'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 56, 'function': 'tasks.add', 'args': [28, 28], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2468', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2468', 'correlation_id': '2018-04-10 16:28:26.075081 2468', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '46165'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '46269'), ('function', 'dequeue_task'), ('message_id', '46269'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '46269'), ('message_id', '2018-04-10 16:28:35.108554 3425'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2471', 'function': 'tasks.add', 'args': (31, 31), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2471', 'task_id': '2018-04-10 16:28:26.075081 2471'}, 68)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '46269'), ('message_id', '2018-04-10 16:28:35.108554 3425'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2471', 'function': 'tasks.add', 'args': (31, 31), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2471', 'task_id': '2018-04-10 16:28:26.075081 2471'}, 68)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '46362'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 58, 'function': 'tasks.add', 'args': [29, 29], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2469', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2469', 'correlation_id': '2018-04-10 16:28:26.075081 2469', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '46362'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '46467'), ('function', 'dequeue_task'), ('message_id', '46467'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '46467'), ('message_id', '2018-04-10 16:28:35.447206 3459'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2472', 'function': 'tasks.add', 'args': (32, 32), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2472', 'task_id': '2018-04-10 16:28:26.075081 2472'}, 67)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '46467'), ('message_id', '2018-04-10 16:28:35.447206 3459'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2472', 'function': 'tasks.add', 'args': (32, 32), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2472', 'task_id': '2018-04-10 16:28:26.075081 2472'}, 67)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '46608'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 60, 'function': 'tasks.add', 'args': [30, 30], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2470', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2470', 'correlation_id': '2018-04-10 16:28:26.075081 2470', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '46608'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '46712'), ('function', 'dequeue_task'), ('message_id', '46712'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '46712'), ('message_id', '2018-04-10 16:28:35.721418 3486'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2473', 'function': 'tasks.add', 'args': (33, 33), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2473', 'task_id': '2018-04-10 16:28:26.075081 2473'}, 66)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '46712'), ('message_id', '2018-04-10 16:28:35.721418 3486'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2473', 'function': 'tasks.add', 'args': (33, 33), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2473', 'task_id': '2018-04-10 16:28:26.075081 2473'}, 66)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '46884'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 62, 'function': 'tasks.add', 'args': [31, 31], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2471', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2471', 'correlation_id': '2018-04-10 16:28:26.075081 2471', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '46884'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '46988'), ('function', 'dequeue_task'), ('message_id', '46988'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '46988'), ('message_id', '2018-04-10 16:28:35.913097 3505'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2474', 'function': 'tasks.add', 'args': (34, 34), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2474', 'task_id': '2018-04-10 16:28:26.075081 2474'}, 65)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '46988'), ('message_id', '2018-04-10 16:28:35.913097 3505'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2474', 'function': 'tasks.add', 'args': (34, 34), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2474', 'task_id': '2018-04-10 16:28:26.075081 2474'}, 65)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '47249'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 64, 'function': 'tasks.add', 'args': [32, 32], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2472', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2472', 'correlation_id': '2018-04-10 16:28:26.075081 2472', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '47249'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '47352'), ('function', 'dequeue_task'), ('message_id', '47352'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '47352'), ('message_id', '2018-04-10 16:28:36.290606 3543'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2475', 'function': 'tasks.add', 'args': (35, 35), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2475', 'task_id': '2018-04-10 16:28:26.075081 2475'}, 64)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '47418'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 66, 'function': 'tasks.add', 'args': [33, 33], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2473', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2473', 'correlation_id': '2018-04-10 16:28:26.075081 2473', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '47418'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    Message:
    OrderedDict([('correlation_id', '47352'), ('message_id', '2018-04-10 16:28:36.290606 3543'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2475', 'function': 'tasks.add', 'args': (35, 35), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2475', 'task_id': '2018-04-10 16:28:26.075081 2475'}, 64)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '47524'), ('function', 'dequeue_task'), ('message_id', '47524'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '47524'), ('message_id', '2018-04-10 16:28:36.417685 3554'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2476', 'function': 'tasks.add', 'args': (36, 36), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2476', 'task_id': '2018-04-10 16:28:26.075081 2476'}, 63)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '47524'), ('message_id', '2018-04-10 16:28:36.417685 3554'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2476', 'function': 'tasks.add', 'args': (36, 36), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2476', 'task_id': '2018-04-10 16:28:26.075081 2476'}, 63)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '47762'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 68, 'function': 'tasks.add', 'args': [34, 34], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2474', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2474', 'correlation_id': '2018-04-10 16:28:26.075081 2474', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '47762'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '47865'), ('function', 'dequeue_task'), ('message_id', '47865'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '47865'), ('message_id', '2018-04-10 16:28:36.626295 3574'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2477', 'function': 'tasks.add', 'args': (37, 37), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2477', 'task_id': '2018-04-10 16:28:26.075081 2477'}, 62)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '47865'), ('message_id', '2018-04-10 16:28:36.626295 3574'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2477', 'function': 'tasks.add', 'args': (37, 37), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2477', 'task_id': '2018-04-10 16:28:26.075081 2477'}, 62)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '47909'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 70, 'function': 'tasks.add', 'args': [35, 35], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2475', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2475', 'correlation_id': '2018-04-10 16:28:26.075081 2475', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '47909'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '48013'), ('function', 'dequeue_task'), ('message_id', '48013'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '48013'), ('message_id', '2018-04-10 16:28:37.002689 3613'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2478', 'function': 'tasks.add', 'args': (38, 38), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2478', 'task_id': '2018-04-10 16:28:26.075081 2478'}, 61)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '48013'), ('message_id', '2018-04-10 16:28:37.002689 3613'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2478', 'function': 'tasks.add', 'args': (38, 38), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2478', 'task_id': '2018-04-10 16:28:26.075081 2478'}, 61)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '48090'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 72, 'function': 'tasks.add', 'args': [36, 36], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2476', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2476', 'correlation_id': '2018-04-10 16:28:26.075081 2476', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '48090'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '48194'), ('function', 'dequeue_task'), ('message_id', '48194'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '48194'), ('message_id', '2018-04-10 16:28:37.170161 3629'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2479', 'function': 'tasks.add', 'args': (39, 39), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2479', 'task_id': '2018-04-10 16:28:26.075081 2479'}, 60)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '48194'), ('message_id', '2018-04-10 16:28:37.170161 3629'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2479', 'function': 'tasks.add', 'args': (39, 39), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2479', 'task_id': '2018-04-10 16:28:26.075081 2479'}, 60)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '48404'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 74, 'function': 'tasks.add', 'args': [37, 37], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2477', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2477', 'correlation_id': '2018-04-10 16:28:26.075081 2477', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '48404'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '48510'), ('function', 'dequeue_task'), ('message_id', '48510'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '48510'), ('message_id', '2018-04-10 16:28:37.443516 3655'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2480', 'function': 'tasks.add', 'args': (40, 40), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2480', 'task_id': '2018-04-10 16:28:26.075081 2480'}, 59)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '48510'), ('message_id', '2018-04-10 16:28:37.443516 3655'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2480', 'function': 'tasks.add', 'args': (40, 40), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2480', 'task_id': '2018-04-10 16:28:26.075081 2480'}, 59)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '48650'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 76, 'function': 'tasks.add', 'args': [38, 38], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2478', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2478', 'correlation_id': '2018-04-10 16:28:26.075081 2478', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '48650'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '48755'), ('function', 'dequeue_task'), ('message_id', '48755'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '48755'), ('message_id', '2018-04-10 16:28:37.735376 3684'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2481', 'function': 'tasks.add', 'args': (41, 41), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2481', 'task_id': '2018-04-10 16:28:26.075081 2481'}, 58)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '48755'), ('message_id', '2018-04-10 16:28:37.735376 3684'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2481', 'function': 'tasks.add', 'args': (41, 41), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2481', 'task_id': '2018-04-10 16:28:26.075081 2481'}, 58)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '48848'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 78, 'function': 'tasks.add', 'args': [39, 39], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2479', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2479', 'correlation_id': '2018-04-10 16:28:26.075081 2479', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '48848'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '48954'), ('function', 'dequeue_task'), ('message_id', '48954'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '48954'), ('message_id', '2018-04-10 16:28:37.963758 3706'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2482', 'function': 'tasks.add', 'args': (42, 42), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2482', 'task_id': '2018-04-10 16:28:26.075081 2482'}, 57)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '48954'), ('message_id', '2018-04-10 16:28:37.963758 3706'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2482', 'function': 'tasks.add', 'args': (42, 42), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2482', 'task_id': '2018-04-10 16:28:26.075081 2482'}, 57)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '49202'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 80, 'function': 'tasks.add', 'args': [40, 40], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2480', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2480', 'correlation_id': '2018-04-10 16:28:26.075081 2480', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '49202'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '49306'), ('function', 'dequeue_task'), ('message_id', '49306'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '49306'), ('message_id', '2018-04-10 16:28:38.193801 3729'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2483', 'function': 'tasks.add', 'args': (43, 43), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2483', 'task_id': '2018-04-10 16:28:26.075081 2483'}, 56)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '49306'), ('message_id', '2018-04-10 16:28:38.193801 3729'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2483', 'function': 'tasks.add', 'args': (43, 43), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2483', 'task_id': '2018-04-10 16:28:26.075081 2483'}, 56)), ('sender', 'Wei-Legion')])
    
    Data received: 527 bytes
    
    Message:
    OrderedDict([('correlation_id', '49374'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 82, 'function': 'tasks.add', 'args': [41, 41], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2481', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2481', 'correlation_id': '2018-04-10 16:28:26.075081 2481', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '49374'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '49477'), ('function', 'dequeue_task'), ('message_id', '49477'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '49477'), ('message_id', '2018-04-10 16:28:38.432935 3752'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2484', 'function': 'tasks.add', 'args': (44, 44), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2484', 'task_id': '2018-04-10 16:28:26.075081 2484'}, 55)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '49477'), ('message_id', '2018-04-10 16:28:38.432935 3752'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2484', 'function': 'tasks.add', 'args': (44, 44), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2484', 'task_id': '2018-04-10 16:28:26.075081 2484'}, 55)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '49783'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 84, 'function': 'tasks.add', 'args': [42, 42], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2482', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2482', 'correlation_id': '2018-04-10 16:28:26.075081 2482', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '49783'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '49887'), ('function', 'dequeue_task'), ('message_id', '49887'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '49887'), ('message_id', '2018-04-10 16:28:38.743943 3783'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2485', 'function': 'tasks.add', 'args': (45, 45), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2485', 'task_id': '2018-04-10 16:28:26.075081 2485'}, 54)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '49887'), ('message_id', '2018-04-10 16:28:38.743943 3783'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2485', 'function': 'tasks.add', 'args': (45, 45), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2485', 'task_id': '2018-04-10 16:28:26.075081 2485'}, 54)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '49963'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 86, 'function': 'tasks.add', 'args': [43, 43], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2483', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2483', 'correlation_id': '2018-04-10 16:28:26.075081 2483', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '49963'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '50067'), ('function', 'dequeue_task'), ('message_id', '50067'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '50067'), ('message_id', '2018-04-10 16:28:38.942881 3802'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2486', 'function': 'tasks.add', 'args': (46, 46), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2486', 'task_id': '2018-04-10 16:28:26.075081 2486'}, 53)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '50067'), ('message_id', '2018-04-10 16:28:38.942881 3802'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2486', 'function': 'tasks.add', 'args': (46, 46), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2486', 'task_id': '2018-04-10 16:28:26.075081 2486'}, 53)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '50091'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 88, 'function': 'tasks.add', 'args': [44, 44], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2484', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2484', 'correlation_id': '2018-04-10 16:28:26.075081 2484', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '50091'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '50194'), ('function', 'dequeue_task'), ('message_id', '50194'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '50194'), ('message_id', '2018-04-10 16:28:39.099435 3816'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2487', 'function': 'tasks.add', 'args': (47, 47), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2487', 'task_id': '2018-04-10 16:28:26.075081 2487'}, 52)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '50194'), ('message_id', '2018-04-10 16:28:39.099435 3816'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2487', 'function': 'tasks.add', 'args': (47, 47), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2487', 'task_id': '2018-04-10 16:28:26.075081 2487'}, 52)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '50552'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 90, 'function': 'tasks.add', 'args': [45, 45], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2485', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2485', 'correlation_id': '2018-04-10 16:28:26.075081 2485', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '50552'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '50656'), ('function', 'dequeue_task'), ('message_id', '50656'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '50656'), ('message_id', '2018-04-10 16:28:39.604704 3868'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2488', 'function': 'tasks.add', 'args': (48, 48), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2488', 'task_id': '2018-04-10 16:28:26.075081 2488'}, 51)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '50656'), ('message_id', '2018-04-10 16:28:39.604704 3868'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2488', 'function': 'tasks.add', 'args': (48, 48), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2488', 'task_id': '2018-04-10 16:28:26.075081 2488'}, 51)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '50763'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 92, 'function': 'tasks.add', 'args': [46, 46], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2486', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2486', 'correlation_id': '2018-04-10 16:28:26.075081 2486', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '50763'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '50870'), ('function', 'dequeue_task'), ('message_id', '50870'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '50870'), ('message_id', '2018-04-10 16:28:39.944471 3902'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2489', 'function': 'tasks.add', 'args': (49, 49), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2489', 'task_id': '2018-04-10 16:28:26.075081 2489'}, 50)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '50870'), ('message_id', '2018-04-10 16:28:39.944471 3902'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2489', 'function': 'tasks.add', 'args': (49, 49), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2489', 'task_id': '2018-04-10 16:28:26.075081 2489'}, 50)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '50832'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 94, 'function': 'tasks.add', 'args': [47, 47], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2487', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2487', 'correlation_id': '2018-04-10 16:28:26.075081 2487', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '50832'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '50936'), ('function', 'dequeue_task'), ('message_id', '50936'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '50936'), ('message_id', '2018-04-10 16:28:40.216250 3929'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2490', 'function': 'tasks.add', 'args': (50, 50), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2490', 'task_id': '2018-04-10 16:28:26.075081 2490'}, 49)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '50936'), ('message_id', '2018-04-10 16:28:40.216250 3929'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2490', 'function': 'tasks.add', 'args': (50, 50), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2490', 'task_id': '2018-04-10 16:28:26.075081 2490'}, 49)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '51489'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 96, 'function': 'tasks.add', 'args': [48, 48], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2488', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2488', 'correlation_id': '2018-04-10 16:28:26.075081 2488', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '51489'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '51593'), ('function', 'dequeue_task'), ('message_id', '51593'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '51593'), ('message_id', '2018-04-10 16:28:40.506349 3958'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2491', 'function': 'tasks.add', 'args': (51, 51), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2491', 'task_id': '2018-04-10 16:28:26.075081 2491'}, 48)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '51593'), ('message_id', '2018-04-10 16:28:40.506349 3958'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2491', 'function': 'tasks.add', 'args': (51, 51), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2491', 'task_id': '2018-04-10 16:28:26.075081 2491'}, 48)), ('sender', 'Wei-Legion')])
    
    
    Data received: 527 bytes
    Message:
    OrderedDict([('correlation_id', '51846'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 98, 'function': 'tasks.add', 'args': [49, 49], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2489', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2489', 'correlation_id': '2018-04-10 16:28:26.075081 2489', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '51846'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '51950'), ('function', 'dequeue_task'), ('message_id', '51950'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '51950'), ('message_id', '2018-04-10 16:28:40.728928 3980'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2492', 'function': 'tasks.add', 'args': (52, 52), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2492', 'task_id': '2018-04-10 16:28:26.075081 2492'}, 47)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    
    Sending 494 bytesMessage:
    OrderedDict([('correlation_id', '51855'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 100, 'function': 'tasks.add', 'args': [50, 50], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2490', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2490', 'correlation_id': '2018-04-10 16:28:26.075081 2490', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '51855'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Message:
    OrderedDict([('correlation_id', '51950'), ('message_id', '2018-04-10 16:28:40.728928 3980'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2492', 'function': 'tasks.add', 'args': (52, 52), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2492', 'task_id': '2018-04-10 16:28:26.075081 2492'}, 47)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '51959'), ('function', 'dequeue_task'), ('message_id', '51959'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '51959'), ('message_id', '2018-04-10 16:28:40.837818 3990'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2493', 'function': 'tasks.add', 'args': (53, 53), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2493', 'task_id': '2018-04-10 16:28:26.075081 2493'}, 46)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '51959'), ('message_id', '2018-04-10 16:28:40.837818 3990'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2493', 'function': 'tasks.add', 'args': (53, 53), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2493', 'task_id': '2018-04-10 16:28:26.075081 2493'}, 46)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '52169'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 102, 'function': 'tasks.add', 'args': [51, 51], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2491', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2491', 'correlation_id': '2018-04-10 16:28:26.075081 2491', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '52169'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '52273'), ('function', 'dequeue_task'), ('message_id', '52273'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '52273'), ('message_id', '2018-04-10 16:28:41.122105 4018'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2494', 'function': 'tasks.add', 'args': (54, 54), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2494', 'task_id': '2018-04-10 16:28:26.075081 2494'}, 45)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '52273'), ('message_id', '2018-04-10 16:28:41.122105 4018'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2494', 'function': 'tasks.add', 'args': (54, 54), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2494', 'task_id': '2018-04-10 16:28:26.075081 2494'}, 45)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '52515'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 104, 'function': 'tasks.add', 'args': [52, 52], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2492', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2492', 'correlation_id': '2018-04-10 16:28:26.075081 2492', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '52515'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '52620'), ('function', 'dequeue_task'), ('message_id', '52620'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '52620'), ('message_id', '2018-04-10 16:28:41.410455 4047'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2495', 'function': 'tasks.add', 'args': (55, 55), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2495', 'task_id': '2018-04-10 16:28:26.075081 2495'}, 44)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '52620'), ('message_id', '2018-04-10 16:28:41.410455 4047'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2495', 'function': 'tasks.add', 'args': (55, 55), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2495', 'task_id': '2018-04-10 16:28:26.075081 2495'}, 44)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '52489'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 106, 'function': 'tasks.add', 'args': [53, 53], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2493', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2493', 'correlation_id': '2018-04-10 16:28:26.075081 2493', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '52489'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '52595'), ('function', 'dequeue_task'), ('message_id', '52595'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '52595'), ('message_id', '2018-04-10 16:28:41.713205 4077'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2496', 'function': 'tasks.add', 'args': (56, 56), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2496', 'task_id': '2018-04-10 16:28:26.075081 2496'}, 43)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '52808'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 108, 'function': 'tasks.add', 'args': [54, 54], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2494', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2494', 'correlation_id': '2018-04-10 16:28:26.075081 2494', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '52808'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    Message:
    OrderedDict([('correlation_id', '52595'), ('message_id', '2018-04-10 16:28:41.713205 4077'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2496', 'function': 'tasks.add', 'args': (56, 56), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2496', 'task_id': '2018-04-10 16:28:26.075081 2496'}, 43)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '52912'), ('function', 'dequeue_task'), ('message_id', '52912'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '52912'), ('message_id', '2018-04-10 16:28:41.793486 4083'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2497', 'function': 'tasks.add', 'args': (57, 57), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2497', 'task_id': '2018-04-10 16:28:26.075081 2497'}, 42)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '52912'), ('message_id', '2018-04-10 16:28:41.793486 4083'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2497', 'function': 'tasks.add', 'args': (57, 57), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2497', 'task_id': '2018-04-10 16:28:26.075081 2497'}, 42)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '53155'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 110, 'function': 'tasks.add', 'args': [55, 55], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2495', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2495', 'correlation_id': '2018-04-10 16:28:26.075081 2495', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '53155'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '53260'), ('function', 'dequeue_task'), ('message_id', '53260'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '53260'), ('message_id', '2018-04-10 16:28:42.103061 4114'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2498', 'function': 'tasks.add', 'args': (58, 58), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2498', 'task_id': '2018-04-10 16:28:26.075081 2498'}, 41)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '53260'), ('message_id', '2018-04-10 16:28:42.103061 4114'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2498', 'function': 'tasks.add', 'args': (58, 58), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2498', 'task_id': '2018-04-10 16:28:26.075081 2498'}, 41)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '53345'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 112, 'function': 'tasks.add', 'args': [56, 56], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2496', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2496', 'correlation_id': '2018-04-10 16:28:26.075081 2496', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '53345'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '53480'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 114, 'function': 'tasks.add', 'args': [57, 57], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2497', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2497', 'correlation_id': '2018-04-10 16:28:26.075081 2497', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '53480'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '53584'), ('function', 'dequeue_task'), ('message_id', '53584'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '53584'), ('message_id', '2018-04-10 16:28:42.420207 4145'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2499', 'function': 'tasks.add', 'args': (59, 59), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2499', 'task_id': '2018-04-10 16:28:26.075081 2499'}, 40)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '53584'), ('message_id', '2018-04-10 16:28:42.420207 4145'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2499', 'function': 'tasks.add', 'args': (59, 59), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2499', 'task_id': '2018-04-10 16:28:26.075081 2499'}, 40)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '53450'), ('function', 'dequeue_task'), ('message_id', '53450'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '53450'), ('message_id', '2018-04-10 16:28:42.486738 4151'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2500', 'function': 'tasks.add', 'args': (60, 60), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2500', 'task_id': '2018-04-10 16:28:26.075081 2500'}, 39)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '53450'), ('message_id', '2018-04-10 16:28:42.486738 4151'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2500', 'function': 'tasks.add', 'args': (60, 60), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2500', 'task_id': '2018-04-10 16:28:26.075081 2500'}, 39)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '53887'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 116, 'function': 'tasks.add', 'args': [58, 58], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2498', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2498', 'correlation_id': '2018-04-10 16:28:26.075081 2498', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '53887'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '53991'), ('function', 'dequeue_task'), ('message_id', '53991'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '53991'), ('message_id', '2018-04-10 16:28:42.853165 4188'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2501', 'function': 'tasks.add', 'args': (61, 61), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2501', 'task_id': '2018-04-10 16:28:26.075081 2501'}, 38)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '53991'), ('message_id', '2018-04-10 16:28:42.853165 4188'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2501', 'function': 'tasks.add', 'args': (61, 61), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2501', 'task_id': '2018-04-10 16:28:26.075081 2501'}, 38)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '54133'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 118, 'function': 'tasks.add', 'args': [59, 59], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2499', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2499', 'correlation_id': '2018-04-10 16:28:26.075081 2499', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '54133'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '54237'), ('function', 'dequeue_task'), ('message_id', '54237'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '54237'), ('message_id', '2018-04-10 16:28:43.133379 4216'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2502', 'function': 'tasks.add', 'args': (62, 62), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2502', 'task_id': '2018-04-10 16:28:26.075081 2502'}, 37)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '54237'), ('message_id', '2018-04-10 16:28:43.133379 4216'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2502', 'function': 'tasks.add', 'args': (62, 62), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2502', 'task_id': '2018-04-10 16:28:26.075081 2502'}, 37)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '54209'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 120, 'function': 'tasks.add', 'args': [60, 60], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2500', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2500', 'correlation_id': '2018-04-10 16:28:26.075081 2500', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '54209'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '54315'), ('function', 'dequeue_task'), ('message_id', '54315'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '54315'), ('message_id', '2018-04-10 16:28:43.313651 4233'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2503', 'function': 'tasks.add', 'args': (63, 63), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2503', 'task_id': '2018-04-10 16:28:26.075081 2503'}, 36)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '54315'), ('message_id', '2018-04-10 16:28:43.313651 4233'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2503', 'function': 'tasks.add', 'args': (63, 63), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2503', 'task_id': '2018-04-10 16:28:26.075081 2503'}, 36)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '54604'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 122, 'function': 'tasks.add', 'args': [61, 61], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2501', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2501', 'correlation_id': '2018-04-10 16:28:26.075081 2501', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '54604'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '54708'), ('function', 'dequeue_task'), ('message_id', '54708'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '54708'), ('message_id', '2018-04-10 16:28:43.594291 4261'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2504', 'function': 'tasks.add', 'args': (64, 64), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2504', 'task_id': '2018-04-10 16:28:26.075081 2504'}, 35)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '54708'), ('message_id', '2018-04-10 16:28:43.594291 4261'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2504', 'function': 'tasks.add', 'args': (64, 64), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2504', 'task_id': '2018-04-10 16:28:26.075081 2504'}, 35)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '54891'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 124, 'function': 'tasks.add', 'args': [62, 62], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2502', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2502', 'correlation_id': '2018-04-10 16:28:26.075081 2502', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '54891'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '54998'), ('function', 'dequeue_task'), ('message_id', '54998'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '54998'), ('message_id', '2018-04-10 16:28:43.844156 4286'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2505', 'function': 'tasks.add', 'args': (65, 65), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2505', 'task_id': '2018-04-10 16:28:26.075081 2505'}, 34)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '54998'), ('message_id', '2018-04-10 16:28:43.844156 4286'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2505', 'function': 'tasks.add', 'args': (65, 65), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2505', 'task_id': '2018-04-10 16:28:26.075081 2505'}, 34)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '54964'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 126, 'function': 'tasks.add', 'args': [63, 63], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2503', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2503', 'correlation_id': '2018-04-10 16:28:26.075081 2503', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '54964'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '55069'), ('function', 'dequeue_task'), ('message_id', '55069'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '55069'), ('message_id', '2018-04-10 16:28:44.163884 4318'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2506', 'function': 'tasks.add', 'args': (66, 66), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2506', 'task_id': '2018-04-10 16:28:26.075081 2506'}, 33)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '55069'), ('message_id', '2018-04-10 16:28:44.163884 4318'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2506', 'function': 'tasks.add', 'args': (66, 66), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2506', 'task_id': '2018-04-10 16:28:26.075081 2506'}, 33)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '55391'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 128, 'function': 'tasks.add', 'args': [64, 64], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2504', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2504', 'correlation_id': '2018-04-10 16:28:26.075081 2504', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '55391'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '55495'), ('function', 'dequeue_task'), ('message_id', '55495'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '55495'), ('message_id', '2018-04-10 16:28:44.422592 4343'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2507', 'function': 'tasks.add', 'args': (67, 67), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2507', 'task_id': '2018-04-10 16:28:26.075081 2507'}, 32)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '55495'), ('message_id', '2018-04-10 16:28:44.422592 4343'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075081 2507', 'function': 'tasks.add', 'args': (67, 67), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075081 2507', 'task_id': '2018-04-10 16:28:26.075081 2507'}, 32)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '55564'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 130, 'function': 'tasks.add', 'args': [65, 65], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2505', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2505', 'correlation_id': '2018-04-10 16:28:26.075081 2505', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '55564'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '55669'), ('function', 'dequeue_task'), ('message_id', '55669'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '55669'), ('message_id', '2018-04-10 16:28:44.651505 4365'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2508', 'function': 'tasks.add', 'args': (68, 68), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2508', 'task_id': '2018-04-10 16:28:26.075581 2508'}, 31)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '55669'), ('message_id', '2018-04-10 16:28:44.651505 4365'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2508', 'function': 'tasks.add', 'args': (68, 68), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2508', 'task_id': '2018-04-10 16:28:26.075581 2508'}, 31)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '55934'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 132, 'function': 'tasks.add', 'args': [66, 66], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2506', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2506', 'correlation_id': '2018-04-10 16:28:26.075081 2506', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '55934'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '56037'), ('function', 'dequeue_task'), ('message_id', '56037'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '56037'), ('message_id', '2018-04-10 16:28:44.917410 4391'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2509', 'function': 'tasks.add', 'args': (69, 69), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2509', 'task_id': '2018-04-10 16:28:26.075581 2509'}, 30)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '56037'), ('message_id', '2018-04-10 16:28:44.917410 4391'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2509', 'function': 'tasks.add', 'args': (69, 69), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2509', 'task_id': '2018-04-10 16:28:26.075581 2509'}, 30)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '56195'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 134, 'function': 'tasks.add', 'args': [67, 67], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075081 2507', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075081 2507', 'correlation_id': '2018-04-10 16:28:26.075081 2507', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '56195'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '56301'), ('function', 'dequeue_task'), ('message_id', '56301'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '56301'), ('message_id', '2018-04-10 16:28:45.152671 4414'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2510', 'function': 'tasks.add', 'args': (70, 70), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2510', 'task_id': '2018-04-10 16:28:26.075581 2510'}, 29)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '56301'), ('message_id', '2018-04-10 16:28:45.152671 4414'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2510', 'function': 'tasks.add', 'args': (70, 70), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2510', 'task_id': '2018-04-10 16:28:26.075581 2510'}, 29)), ('sender', 'Wei-Legion')])
    
    
    Message:
    OrderedDict([('correlation_id', '56331'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 136, 'function': 'tasks.add', 'args': [68, 68], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2508', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2508', 'correlation_id': '2018-04-10 16:28:26.075581 2508', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '56331'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '56435'), ('function', 'dequeue_task'), ('message_id', '56435'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '56435'), ('message_id', '2018-04-10 16:28:45.292129 4427'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2511', 'function': 'tasks.add', 'args': (71, 71), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2511', 'task_id': '2018-04-10 16:28:26.075581 2511'}, 28)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '56435'), ('message_id', '2018-04-10 16:28:45.292129 4427'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2511', 'function': 'tasks.add', 'args': (71, 71), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2511', 'task_id': '2018-04-10 16:28:26.075581 2511'}, 28)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '56572'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 138, 'function': 'tasks.add', 'args': [69, 69], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2509', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2509', 'correlation_id': '2018-04-10 16:28:26.075581 2509', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '56572'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '56675'), ('function', 'dequeue_task'), ('message_id', '56675'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '56675'), ('message_id', '2018-04-10 16:28:45.678629 4460'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2512', 'function': 'tasks.add', 'args': (72, 72), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2512', 'task_id': '2018-04-10 16:28:26.075581 2512'}, 27)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '56675'), ('message_id', '2018-04-10 16:28:45.678629 4460'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2512', 'function': 'tasks.add', 'args': (72, 72), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2512', 'task_id': '2018-04-10 16:28:26.075581 2512'}, 27)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '57093'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 140, 'function': 'tasks.add', 'args': [70, 70], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2510', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2510', 'correlation_id': '2018-04-10 16:28:26.075581 2510', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '57093'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '57197'), ('function', 'dequeue_task'), ('message_id', '57197'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '57197'), ('message_id', '2018-04-10 16:28:46.211408 4508'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2513', 'function': 'tasks.add', 'args': (73, 73), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2513', 'task_id': '2018-04-10 16:28:26.075581 2513'}, 26)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Sending 494 bytes
    
    Message:
    OrderedDict([('correlation_id', '57095'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 142, 'function': 'tasks.add', 'args': [71, 71], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2511', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2511', 'correlation_id': '2018-04-10 16:28:26.075581 2511', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '57095'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    Message:
    OrderedDict([('correlation_id', '57197'), ('message_id', '2018-04-10 16:28:46.211408 4508'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2513', 'function': 'tasks.add', 'args': (73, 73), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2513', 'task_id': '2018-04-10 16:28:26.075581 2513'}, 26)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '57198'), ('function', 'dequeue_task'), ('message_id', '57198'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '57198'), ('message_id', '2018-04-10 16:28:46.430491 4521'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2514', 'function': 'tasks.add', 'args': (74, 74), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2514', 'task_id': '2018-04-10 16:28:26.075581 2514'}, 25)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Sending 494 bytes
    
    Message:
    OrderedDict([('correlation_id', '57198'), ('message_id', '2018-04-10 16:28:46.430491 4521'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2514', 'function': 'tasks.add', 'args': (74, 74), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2514', 'task_id': '2018-04-10 16:28:26.075581 2514'}, 25)), ('sender', 'Wei-Legion')])
    Message:
    OrderedDict([('correlation_id', '57403'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 144, 'function': 'tasks.add', 'args': [72, 72], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2512', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2512', 'correlation_id': '2018-04-10 16:28:26.075581 2512', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '57403'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '57509'), ('function', 'dequeue_task'), ('message_id', '57509'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '57509'), ('message_id', '2018-04-10 16:28:46.588411 4531'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2515', 'function': 'tasks.add', 'args': (75, 75), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2515', 'task_id': '2018-04-10 16:28:26.075581 2515'}, 24)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '57509'), ('message_id', '2018-04-10 16:28:46.588411 4531'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2515', 'function': 'tasks.add', 'args': (75, 75), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2515', 'task_id': '2018-04-10 16:28:26.075581 2515'}, 24)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '58165'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 146, 'function': 'tasks.add', 'args': [73, 73], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2513', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2513', 'correlation_id': '2018-04-10 16:28:26.075581 2513', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '58165'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '58269'), ('function', 'dequeue_task'), ('message_id', '58269'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '58269'), ('message_id', '2018-04-10 16:28:47.049637 4564'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2516', 'function': 'tasks.add', 'args': (76, 76), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2516', 'task_id': '2018-04-10 16:28:26.075581 2516'}, 23)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '58269'), ('message_id', '2018-04-10 16:28:47.049637 4564'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2516', 'function': 'tasks.add', 'args': (76, 76), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2516', 'task_id': '2018-04-10 16:28:26.075581 2516'}, 23)), ('sender', 'Wei-Legion')])
    Message:
    OrderedDict([('correlation_id', '58249'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 148, 'function': 'tasks.add', 'args': [74, 74], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2514', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2514', 'correlation_id': '2018-04-10 16:28:26.075581 2514', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '58249'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '58353'), ('function', 'dequeue_task'), ('message_id', '58353'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '58353'), ('message_id', '2018-04-10 16:28:47.315845 4581'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2517', 'function': 'tasks.add', 'args': (77, 77), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2517', 'task_id': '2018-04-10 16:28:26.075581 2517'}, 22)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '58353'), ('message_id', '2018-04-10 16:28:47.315845 4581'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2517', 'function': 'tasks.add', 'args': (77, 77), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2517', 'task_id': '2018-04-10 16:28:26.075581 2517'}, 22)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '58291'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 150, 'function': 'tasks.add', 'args': [75, 75], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2515', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2515', 'correlation_id': '2018-04-10 16:28:26.075581 2515', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '58291'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '58396'), ('function', 'dequeue_task'), ('message_id', '58396'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '58396'), ('message_id', '2018-04-10 16:28:47.706383 4607'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2518', 'function': 'tasks.add', 'args': (78, 78), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2518', 'task_id': '2018-04-10 16:28:26.075581 2518'}, 21)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Sending 494 bytes
    
    Message:
    OrderedDict([('correlation_id', '58396'), ('message_id', '2018-04-10 16:28:47.706383 4607'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2518', 'function': 'tasks.add', 'args': (78, 78), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2518', 'task_id': '2018-04-10 16:28:26.075581 2518'}, 21)), ('sender', 'Wei-Legion')])
    Message:
    OrderedDict([('correlation_id', '58893'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 152, 'function': 'tasks.add', 'args': [76, 76], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2516', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2516', 'correlation_id': '2018-04-10 16:28:26.075581 2516', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '58893'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '58998'), ('function', 'dequeue_task'), ('message_id', '58998'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '58998'), ('message_id', '2018-04-10 16:28:48.025509 4635'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2519', 'function': 'tasks.add', 'args': (79, 79), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2519', 'task_id': '2018-04-10 16:28:26.075581 2519'}, 20)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '58998'), ('message_id', '2018-04-10 16:28:48.025509 4635'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2519', 'function': 'tasks.add', 'args': (79, 79), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2519', 'task_id': '2018-04-10 16:28:26.075581 2519'}, 20)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '59041'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 154, 'function': 'tasks.add', 'args': [77, 77], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2517', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2517', 'correlation_id': '2018-04-10 16:28:26.075581 2517', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '59041'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '59144'), ('function', 'dequeue_task'), ('message_id', '59144'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '59144'), ('message_id', '2018-04-10 16:28:48.184129 4650'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2520', 'function': 'tasks.add', 'args': (80, 80), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2520', 'task_id': '2018-04-10 16:28:26.075581 2520'}, 19)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '59144'), ('message_id', '2018-04-10 16:28:48.184129 4650'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2520', 'function': 'tasks.add', 'args': (80, 80), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2520', 'task_id': '2018-04-10 16:28:26.075581 2520'}, 19)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '59460'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 156, 'function': 'tasks.add', 'args': [78, 78], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2518', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2518', 'correlation_id': '2018-04-10 16:28:26.075581 2518', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '59460'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '59566'), ('function', 'dequeue_task'), ('message_id', '59566'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '59566'), ('message_id', '2018-04-10 16:28:48.589752 4691'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2521', 'function': 'tasks.add', 'args': (81, 81), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2521', 'task_id': '2018-04-10 16:28:26.075581 2521'}, 18)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '59764'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 158, 'function': 'tasks.add', 'args': [79, 79], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2519', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2519', 'correlation_id': '2018-04-10 16:28:26.075581 2519', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '59764'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    Message:
    OrderedDict([('correlation_id', '59566'), ('message_id', '2018-04-10 16:28:48.589752 4691'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2521', 'function': 'tasks.add', 'args': (81, 81), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2521', 'task_id': '2018-04-10 16:28:26.075581 2521'}, 18)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '59870'), ('function', 'dequeue_task'), ('message_id', '59870'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '59870'), ('message_id', '2018-04-10 16:28:48.683974 4698'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2522', 'function': 'tasks.add', 'args': (82, 82), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2522', 'task_id': '2018-04-10 16:28:26.075581 2522'}, 17)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '59870'), ('message_id', '2018-04-10 16:28:48.683974 4698'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2522', 'function': 'tasks.add', 'args': (82, 82), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2522', 'task_id': '2018-04-10 16:28:26.075581 2522'}, 17)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '59861'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 160, 'function': 'tasks.add', 'args': [80, 80], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2520', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2520', 'correlation_id': '2018-04-10 16:28:26.075581 2520', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '59861'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '59965'), ('function', 'dequeue_task'), ('message_id', '59965'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '59965'), ('message_id', '2018-04-10 16:28:48.979789 4726'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2523', 'function': 'tasks.add', 'args': (83, 83), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2523', 'task_id': '2018-04-10 16:28:26.075581 2523'}, 16)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '59965'), ('message_id', '2018-04-10 16:28:48.979789 4726'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2523', 'function': 'tasks.add', 'args': (83, 83), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2523', 'task_id': '2018-04-10 16:28:26.075581 2523'}, 16)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '60306'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 162, 'function': 'tasks.add', 'args': [81, 81], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2521', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2521', 'correlation_id': '2018-04-10 16:28:26.075581 2521', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '60306'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '60411'), ('function', 'dequeue_task'), ('message_id', '60411'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '60411'), ('message_id', '2018-04-10 16:28:50.166903 4815'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2524', 'function': 'tasks.add', 'args': (84, 84), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2524', 'task_id': '2018-04-10 16:28:26.075581 2524'}, 15)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '60411'), ('message_id', '2018-04-10 16:28:50.166903 4815'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2524', 'function': 'tasks.add', 'args': (84, 84), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2524', 'task_id': '2018-04-10 16:28:26.075581 2524'}, 15)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '60449'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 164, 'function': 'tasks.add', 'args': [82, 82], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2522', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2522', 'correlation_id': '2018-04-10 16:28:26.075581 2522', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '60449'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '60552'), ('function', 'dequeue_task'), ('message_id', '60552'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '60552'), ('message_id', '2018-04-10 16:28:50.401026 4829'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2525', 'function': 'tasks.add', 'args': (85, 85), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2525', 'task_id': '2018-04-10 16:28:26.075581 2525'}, 14)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '60806'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 166, 'function': 'tasks.add', 'args': [83, 83], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2523', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2523', 'correlation_id': '2018-04-10 16:28:26.075581 2523', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '60806'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    Message:
    OrderedDict([('correlation_id', '60552'), ('message_id', '2018-04-10 16:28:50.401026 4829'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2525', 'function': 'tasks.add', 'args': (85, 85), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2525', 'task_id': '2018-04-10 16:28:26.075581 2525'}, 14)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '60910'), ('function', 'dequeue_task'), ('message_id', '60910'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '60910'), ('message_id', '2018-04-10 16:28:50.606572 4841'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2526', 'function': 'tasks.add', 'args': (86, 86), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2526', 'task_id': '2018-04-10 16:28:26.075581 2526'}, 13)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '60910'), ('message_id', '2018-04-10 16:28:50.606572 4841'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2526', 'function': 'tasks.add', 'args': (86, 86), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2526', 'task_id': '2018-04-10 16:28:26.075581 2526'}, 13)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '62644'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 168, 'function': 'tasks.add', 'args': [84, 84], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2524', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2524', 'correlation_id': '2018-04-10 16:28:26.075581 2524', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '62644'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '62749'), ('function', 'dequeue_task'), ('message_id', '62749'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '62749'), ('message_id', '2018-04-10 16:28:51.748306 4934'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2527', 'function': 'tasks.add', 'args': (87, 87), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2527', 'task_id': '2018-04-10 16:28:26.075581 2527'}, 12)), ('sender', 'Wei-Legion')])
    
    Data received: 528 bytes
    
    Sending 494 bytes
    
    Message:
    OrderedDict([('correlation_id', '62749'), ('message_id', '2018-04-10 16:28:51.748306 4934'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2527', 'function': 'tasks.add', 'args': (87, 87), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2527', 'task_id': '2018-04-10 16:28:26.075581 2527'}, 12)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '62826'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 170, 'function': 'tasks.add', 'args': [85, 85], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2525', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2525', 'correlation_id': '2018-04-10 16:28:26.075581 2525', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '62826'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '62930'), ('function', 'dequeue_task'), ('message_id', '62930'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '62930'), ('message_id', '2018-04-10 16:28:51.898213 4947'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2528', 'function': 'tasks.add', 'args': (88, 88), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2528', 'task_id': '2018-04-10 16:28:26.075581 2528'}, 11)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '62930'), ('message_id', '2018-04-10 16:28:51.898213 4947'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2528', 'function': 'tasks.add', 'args': (88, 88), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2528', 'task_id': '2018-04-10 16:28:26.075581 2528'}, 11)), ('sender', 'Wei-Legion')])
    
    Data received: 528 bytes
    
    Message:
    OrderedDict([('correlation_id', '62752'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 172, 'function': 'tasks.add', 'args': [86, 86], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2526', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2526', 'correlation_id': '2018-04-10 16:28:26.075581 2526', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '62752'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '62856'), ('function', 'dequeue_task'), ('message_id', '62856'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '62856'), ('message_id', '2018-04-10 16:28:51.998681 4955'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2529', 'function': 'tasks.add', 'args': (89, 89), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2529', 'task_id': '2018-04-10 16:28:26.075581 2529'}, 10)), ('sender', 'Wei-Legion')])
    
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '62856'), ('message_id', '2018-04-10 16:28:51.998681 4955'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2529', 'function': 'tasks.add', 'args': (89, 89), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2529', 'task_id': '2018-04-10 16:28:26.075581 2529'}, 10)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '63531'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 174, 'function': 'tasks.add', 'args': [87, 87], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2527', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2527', 'correlation_id': '2018-04-10 16:28:26.075581 2527', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '63531'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '63634'), ('function', 'dequeue_task'), ('message_id', '63634'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '63634'), ('message_id', '2018-04-10 16:28:52.528946 5008'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2530', 'function': 'tasks.add', 'args': (90, 90), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2530', 'task_id': '2018-04-10 16:28:26.075581 2530'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Sending 493 bytes
    Message:
    OrderedDict([('correlation_id', '63634'), ('message_id', '2018-04-10 16:28:52.528946 5008'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2530', 'function': 'tasks.add', 'args': (90, 90), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2530', 'task_id': '2018-04-10 16:28:26.075581 2530'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '63726'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 176, 'function': 'tasks.add', 'args': [88, 88], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2528', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2528', 'correlation_id': '2018-04-10 16:28:26.075581 2528', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '63726'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '63830'), ('function', 'dequeue_task'), ('message_id', '63830'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '63830'), ('message_id', '2018-04-10 16:28:52.730017 5026'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2531', 'function': 'tasks.add', 'args': (91, 91), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2531', 'task_id': '2018-04-10 16:28:26.075581 2531'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Sending 493 bytes
    Message:
    OrderedDict([('correlation_id', '63830'), ('message_id', '2018-04-10 16:28:52.730017 5026'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2531', 'function': 'tasks.add', 'args': (91, 91), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2531', 'task_id': '2018-04-10 16:28:26.075581 2531'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '63778'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 178, 'function': 'tasks.add', 'args': [89, 89], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2529', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2529', 'correlation_id': '2018-04-10 16:28:26.075581 2529', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '63778'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '63880'), ('function', 'dequeue_task'), ('message_id', '63880'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '63880'), ('message_id', '2018-04-10 16:28:52.908742 5043'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2532', 'function': 'tasks.add', 'args': (92, 92), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2532', 'task_id': '2018-04-10 16:28:26.075581 2532'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Sending 493 bytes
    Message:
    OrderedDict([('correlation_id', '63880'), ('message_id', '2018-04-10 16:28:52.908742 5043'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2532', 'function': 'tasks.add', 'args': (92, 92), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2532', 'task_id': '2018-04-10 16:28:26.075581 2532'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '64296'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 180, 'function': 'tasks.add', 'args': [90, 90], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2530', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2530', 'correlation_id': '2018-04-10 16:28:26.075581 2530', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '64296'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '64400'), ('function', 'dequeue_task'), ('message_id', '64400'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '64400'), ('message_id', '2018-04-10 16:28:53.342558 5086'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2533', 'function': 'tasks.add', 'args': (93, 93), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2533', 'task_id': '2018-04-10 16:28:26.075581 2533'}, 6)), ('sender', 'Wei-Legion')])
    
    Data received: 528 bytes
    
    Sending 493 bytes
    Message:
    OrderedDict([('correlation_id', '64400'), ('message_id', '2018-04-10 16:28:53.342558 5086'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2533', 'function': 'tasks.add', 'args': (93, 93), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2533', 'task_id': '2018-04-10 16:28:26.075581 2533'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Message:
    OrderedDict([('correlation_id', '64491'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 182, 'function': 'tasks.add', 'args': [91, 91], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2531', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2531', 'correlation_id': '2018-04-10 16:28:26.075581 2531', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '64491'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '64597'), ('function', 'dequeue_task'), ('message_id', '64597'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '64597'), ('message_id', '2018-04-10 16:28:53.445236 5095'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2534', 'function': 'tasks.add', 'args': (94, 94), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2534', 'task_id': '2018-04-10 16:28:26.075581 2534'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Sending 493 bytes
    Message:
    OrderedDict([('correlation_id', '64597'), ('message_id', '2018-04-10 16:28:53.445236 5095'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2534', 'function': 'tasks.add', 'args': (94, 94), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2534', 'task_id': '2018-04-10 16:28:26.075581 2534'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '64609'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 184, 'function': 'tasks.add', 'args': [92, 92], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2532', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2532', 'correlation_id': '2018-04-10 16:28:26.075581 2532', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '64609'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '64715'), ('function', 'dequeue_task'), ('message_id', '64715'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '64715'), ('message_id', '2018-04-10 16:28:53.578416 5107'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2535', 'function': 'tasks.add', 'args': (95, 95), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2535', 'task_id': '2018-04-10 16:28:26.075581 2535'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Sending 493 bytes
    Message:
    OrderedDict([('correlation_id', '64715'), ('message_id', '2018-04-10 16:28:53.578416 5107'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2535', 'function': 'tasks.add', 'args': (95, 95), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2535', 'task_id': '2018-04-10 16:28:26.075581 2535'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '65267'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 188, 'function': 'tasks.add', 'args': [94, 94], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2534', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2534', 'correlation_id': '2018-04-10 16:28:26.075581 2534', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '65267'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '65370'), ('function', 'dequeue_task'), ('message_id', '65370'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '65370'), ('message_id', '2018-04-10 16:28:54.233880 5178'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2536', 'function': 'tasks.add', 'args': (96, 96), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2536', 'task_id': '2018-04-10 16:28:26.075581 2536'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Sending 493 bytes
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '65131'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 186, 'function': 'tasks.add', 'args': [93, 93], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2533', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2533', 'correlation_id': '2018-04-10 16:28:26.075581 2533', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '65131'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    Message:
    OrderedDict([('correlation_id', '65370'), ('message_id', '2018-04-10 16:28:54.233880 5178'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2536', 'function': 'tasks.add', 'args': (96, 96), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2536', 'task_id': '2018-04-10 16:28:26.075581 2536'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '65236'), ('function', 'dequeue_task'), ('message_id', '65236'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '65236'), ('message_id', '2018-04-10 16:28:54.377455 5191'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2537', 'function': 'tasks.add', 'args': (97, 97), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2537', 'task_id': '2018-04-10 16:28:26.075581 2537'}, 2)), ('sender', 'Wei-Legion')])
    
    
    Sending 493 bytes
    Message:
    OrderedDict([('correlation_id', '65236'), ('message_id', '2018-04-10 16:28:54.377455 5191'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2537', 'function': 'tasks.add', 'args': (97, 97), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2537', 'task_id': '2018-04-10 16:28:26.075581 2537'}, 2)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '65294'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 190, 'function': 'tasks.add', 'args': [95, 95], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2535', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2535', 'correlation_id': '2018-04-10 16:28:26.075581 2535', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '65294'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '65397'), ('function', 'dequeue_task'), ('message_id', '65397'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '65397'), ('message_id', '2018-04-10 16:28:54.490881 5201'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2538', 'function': 'tasks.add', 'args': (98, 98), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2538', 'task_id': '2018-04-10 16:28:26.075581 2538'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Sending 493 bytes
    Message:
    OrderedDict([('correlation_id', '65397'), ('message_id', '2018-04-10 16:28:54.490881 5201'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2538', 'function': 'tasks.add', 'args': (98, 98), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2538', 'task_id': '2018-04-10 16:28:26.075581 2538'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '65976'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 192, 'function': 'tasks.add', 'args': [96, 96], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2536', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2536', 'correlation_id': '2018-04-10 16:28:26.075581 2536', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '65976'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '66080'), ('function', 'dequeue_task'), ('message_id', '66080'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '66080'), ('message_id', '2018-04-10 16:28:55.003950 5255'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2539', 'function': 'tasks.add', 'args': (99, 99), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2539', 'task_id': '2018-04-10 16:28:26.075581 2539'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 493 bytes
    Message:
    OrderedDict([('correlation_id', '66080'), ('message_id', '2018-04-10 16:28:55.003950 5255'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:26.075581 2539', 'function': 'tasks.add', 'args': (99, 99), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:26.075581 2539', 'task_id': '2018-04-10 16:28:26.075581 2539'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '66173'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 194, 'function': 'tasks.add', 'args': [97, 97], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2537', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2537', 'correlation_id': '2018-04-10 16:28:26.075581 2537', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '66173'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '66277'), ('function', 'dequeue_task'), ('message_id', '66277'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '66277'), ('message_id', '2018-04-10 16:28:55.269155 5280'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '66337'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 196, 'function': 'tasks.add', 'args': [98, 98], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2538', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2538', 'correlation_id': '2018-04-10 16:28:26.075581 2538', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '66337'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    Message:
    OrderedDict([('correlation_id', '66277'), ('message_id', '2018-04-10 16:28:55.269155 5280'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '66442'), ('function', 'dequeue_task'), ('message_id', '66442'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '66442'), ('message_id', '2018-04-10 16:28:55.340523 5285'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '66442'), ('message_id', '2018-04-10 16:28:55.340523 5285'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 528 bytes
    Message:
    OrderedDict([('correlation_id', '66765'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': 198, 'function': 'tasks.add', 'args': [99, 99], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:26.075581 2539', 'message_type': 'result', 'task_id': '2018-04-10 16:28:26.075581 2539', 'correlation_id': '2018-04-10 16:28:26.075581 2539', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '66765'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    




    [[0, 2, 4, 6, 8, 10, 12, 14, 16, 18],
     [20, 22, 24, 26, 28, 30, 32, 34, 36, 38],
     [40, 42, 44, 46, 48, 50, 52, 54, 56, 58],
     [60, 62, 64, 66, 68, 70, 72, 74, 76, 78],
     [80, 82, 84, 86, 88, 90, 92, 94, 96, 98],
     [100, 102, 104, 106, 108, 110, 112, 114, 116, 118],
     [120, 122, 124, 126, 128, 130, 132, 134, 136, 138],
     [140, 142, 144, 146, 148, 150, 152, 154, 156, 158],
     [160, 162, 164, 166, 168, 170, 172, 174, 176, 178],
     [180, 182, 184, 186, 188, 190, 192, 194, 196, 198]]



### Word Count
最後我們以 Hadoop 領域中的 "Hello World" 範例 "Word Count" 來測試。  

我們會把一個文字檔的內容拆解成 words 並將每個 word 發送給 workers 處理，workers 要做的主要是一個`mapper`處理：
```
def mapper(word):
    return (word, 1) if len(word) > 3 else None
```
worker 會將處理的結果傳回來，client 這邊會有一個`reduce`function 將結果彙整。  

我們可以在 ESP32 cluster 上面這樣做：


```python
import word_count

text_file = os.path.join('..', '..', 'codes', 'broccoli', 'client', 'test.txt')
words_count, counts = word_count.count_words(text_file)
print('********** result:\nwords count: {}\n\n{}\n**********'.format(words_count, counts[:10]))
```

    
    Sending 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:55.691248 5322'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:55.691248 5322'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 261 bytes
    Message:
    OrderedDict([('correlation_id', '2018-04-10 16:28:55.691248 5322'), ('function', 'fetch_task'), ('kwargs', {'broker': 'Wei-Legion'}), ('message_id', '2018-04-10 16:28:55.691248 5322'), ('message_type', 'function'), ('receiver', 'Hub'), ('reply_to', 'Wei-Legion'), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '67257'), ('function', 'dequeue_task'), ('message_id', '67257'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '67257'), ('message_id', '2018-04-10 16:28:56.084692 5450'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.691248 5321', 'function': 'tasks.mapper', 'args': ("Aesop's",), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.691248 5321', 'task_id': '2018-04-10 16:28:55.691248 5321'}, 93)), ('sender', 'Wei-Legion')])
    
    
    Sending 500 bytes
    Message:
    OrderedDict([('correlation_id', '67257'), ('message_id', '2018-04-10 16:28:56.084692 5450'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.691248 5321', 'function': 'tasks.mapper', 'args': ("Aesop's",), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.691248 5321', 'task_id': '2018-04-10 16:28:55.691248 5321'}, 93)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '67371'), ('function', 'dequeue_task'), ('message_id', '67371'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '67371'), ('message_id', '2018-04-10 16:28:56.222800 5463'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5325', 'function': 'tasks.mapper', 'args': ('Fables',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5325', 'task_id': '2018-04-10 16:28:55.715814 5325'}, 92)), ('sender', 'Wei-Legion')])
    
    
    Sending 499 bytes
    Message:
    OrderedDict([('correlation_id', '67371'), ('message_id', '2018-04-10 16:28:56.222800 5463'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5325', 'function': 'tasks.mapper', 'args': ('Fables',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5325', 'task_id': '2018-04-10 16:28:55.715814 5325'}, 92)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '67361'), ('function', 'dequeue_task'), ('message_id', '67361'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '67361'), ('message_id', '2018-04-10 16:28:56.317581 5471'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5326', 'function': 'tasks.mapper', 'args': ('Translated',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5326', 'task_id': '2018-04-10 16:28:55.715814 5326'}, 91)), ('sender', 'Wei-Legion')])
    
    
    Sending 503 bytes
    Message:
    OrderedDict([('correlation_id', '67361'), ('message_id', '2018-04-10 16:28:56.317581 5471'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5326', 'function': 'tasks.mapper', 'args': ('Translated',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5326', 'task_id': '2018-04-10 16:28:55.715814 5326'}, 91)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '67736'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ["Aesop's", 1], 'function': 'tasks.mapper', 'args': ["Aesop's"], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.691248 5321', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.691248 5321', 'correlation_id': '2018-04-10 16:28:55.691248 5321', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '67736'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '67843'), ('function', 'dequeue_task'), ('message_id', '67843'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '67843'), ('message_id', '2018-04-10 16:28:56.794943 5504'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5327', 'function': 'tasks.mapper', 'args': ('by',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5327', 'task_id': '2018-04-10 16:28:55.715814 5327'}, 90)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '67843'), ('message_id', '2018-04-10 16:28:56.794943 5504'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5327', 'function': 'tasks.mapper', 'args': ('by',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5327', 'task_id': '2018-04-10 16:28:55.715814 5327'}, 90)), ('sender', 'Wei-Legion')])
    
    
    Data received: 543 bytes
    Message:
    OrderedDict([('correlation_id', '67965'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Fables', 1], 'function': 'tasks.mapper', 'args': ['Fables'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5325', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5325', 'correlation_id': '2018-04-10 16:28:55.715814 5325', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '67965'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '68073'), ('function', 'dequeue_task'), ('message_id', '68073'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '68073'), ('message_id', '2018-04-10 16:28:57.167434 5523'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5328', 'function': 'tasks.mapper', 'args': ('George',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5328', 'task_id': '2018-04-10 16:28:55.715814 5328'}, 89)), ('sender', 'Wei-Legion')])
    
    
    Sending 499 bytes
    
    Data received: 551 bytesMessage:
    OrderedDict([('correlation_id', '68073'), ('message_id', '2018-04-10 16:28:57.167434 5523'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5328', 'function': 'tasks.mapper', 'args': ('George',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5328', 'task_id': '2018-04-10 16:28:55.715814 5328'}, 89)), ('sender', 'Wei-Legion')])
    
    
    Message:
    OrderedDict([('correlation_id', '67991'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Translated', 1], 'function': 'tasks.mapper', 'args': ['Translated'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5326', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5326', 'correlation_id': '2018-04-10 16:28:55.715814 5326', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '67991'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '68100'), ('function', 'dequeue_task'), ('message_id', '68100'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '68100'), ('message_id', '2018-04-10 16:28:57.518367 5544'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5329', 'function': 'tasks.mapper', 'args': ('Fyler',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5329', 'task_id': '2018-04-10 16:28:55.715814 5329'}, 88)), ('sender', 'Wei-Legion')])
    
    
    Sending 498 bytes
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '68612'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['by'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5327', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5327', 'correlation_id': '2018-04-10 16:28:55.715814 5327', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '68612'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    Message:
    OrderedDict([('correlation_id', '68100'), ('message_id', '2018-04-10 16:28:57.518367 5544'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5329', 'function': 'tasks.mapper', 'args': ('Fyler',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5329', 'task_id': '2018-04-10 16:28:55.715814 5329'}, 88)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '68717'), ('function', 'dequeue_task'), ('message_id', '68717'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '68717'), ('message_id', '2018-04-10 16:28:57.761012 5558'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5330', 'function': 'tasks.mapper', 'args': ('Townsend',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5330', 'task_id': '2018-04-10 16:28:55.715814 5330'}, 87)), ('sender', 'Wei-Legion')])
    
    
    Sending 501 bytes
    Message:
    OrderedDict([('correlation_id', '68717'), ('message_id', '2018-04-10 16:28:57.761012 5558'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5330', 'function': 'tasks.mapper', 'args': ('Townsend',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5330', 'task_id': '2018-04-10 16:28:55.715814 5330'}, 87)), ('sender', 'Wei-Legion')])
    
    
    Data received: 543 bytes
    Message:
    OrderedDict([('correlation_id', '69263'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['George', 1], 'function': 'tasks.mapper', 'args': ['George'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5328', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5328', 'correlation_id': '2018-04-10 16:28:55.715814 5328', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '69263'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '69370'), ('function', 'dequeue_task'), ('message_id', '69370'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '69370'), ('message_id', '2018-04-10 16:28:58.393694 5598'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5331', 'function': 'tasks.mapper', 'args': ('The',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5331', 'task_id': '2018-04-10 16:28:55.715814 5331'}, 86)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    
    Data received: 541 bytes
    Message:
    OrderedDict([('correlation_id', '69295'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Fyler', 1], 'function': 'tasks.mapper', 'args': ['Fyler'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5329', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5329', 'correlation_id': '2018-04-10 16:28:55.715814 5329', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '69295'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    Message:
    OrderedDict([('correlation_id', '69370'), ('message_id', '2018-04-10 16:28:58.393694 5598'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5331', 'function': 'tasks.mapper', 'args': ('The',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5331', 'task_id': '2018-04-10 16:28:55.715814 5331'}, 86)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '69401'), ('function', 'dequeue_task'), ('message_id', '69401'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '69401'), ('message_id', '2018-04-10 16:28:58.573674 5608'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5332', 'function': 'tasks.mapper', 'args': ('Wolf',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5332', 'task_id': '2018-04-10 16:28:55.715814 5332'}, 85)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '69401'), ('message_id', '2018-04-10 16:28:58.573674 5608'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5332', 'function': 'tasks.mapper', 'args': ('Wolf',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5332', 'task_id': '2018-04-10 16:28:55.715814 5332'}, 85)), ('sender', 'Wei-Legion')])
    
    
    Data received: 547 bytes
    Message:
    OrderedDict([('correlation_id', '69534'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Townsend', 1], 'function': 'tasks.mapper', 'args': ['Townsend'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5330', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5330', 'correlation_id': '2018-04-10 16:28:55.715814 5330', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '69534'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '69642'), ('function', 'dequeue_task'), ('message_id', '69642'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '69642'), ('message_id', '2018-04-10 16:28:59.125140 5642'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5333', 'function': 'tasks.mapper', 'args': ('and',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5333', 'task_id': '2018-04-10 16:28:55.715814 5333'}, 84)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    
    Data received: 531 bytesMessage:
    OrderedDict([('correlation_id', '69642'), ('message_id', '2018-04-10 16:28:59.125140 5642'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5333', 'function': 'tasks.mapper', 'args': ('and',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5333', 'task_id': '2018-04-10 16:28:55.715814 5333'}, 84)), ('sender', 'Wei-Legion')])
    
    
    Message:
    OrderedDict([('correlation_id', '70170'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['The'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5331', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5331', 'correlation_id': '2018-04-10 16:28:55.715814 5331', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '70170'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '70276'), ('function', 'dequeue_task'), ('message_id', '70276'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '70276'), ('message_id', '2018-04-10 16:28:59.437971 5659'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5334', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5334', 'task_id': '2018-04-10 16:28:55.715814 5334'}, 83)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Data received: 539 bytes
    
    Message:
    OrderedDict([('correlation_id', '70276'), ('message_id', '2018-04-10 16:28:59.437971 5659'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5334', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5334', 'task_id': '2018-04-10 16:28:55.715814 5334'}, 83)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '70615'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Wolf', 1], 'function': 'tasks.mapper', 'args': ['Wolf'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5332', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5332', 'correlation_id': '2018-04-10 16:28:55.715814 5332', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '70615'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '70720'), ('function', 'dequeue_task'), ('message_id', '70720'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '70720'), ('message_id', '2018-04-10 16:28:59.731752 5674'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5335', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5335', 'task_id': '2018-04-10 16:28:55.715814 5335'}, 82)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '70720'), ('message_id', '2018-04-10 16:28:59.731752 5674'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5335', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5335', 'task_id': '2018-04-10 16:28:55.715814 5335'}, 82)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '71095'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['and'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5333', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5333', 'correlation_id': '2018-04-10 16:28:55.715814 5333', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '71095'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '71199'), ('function', 'dequeue_task'), ('message_id', '71199'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '71199'), ('message_id', '2018-04-10 16:29:00.395015 5715'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5336', 'function': 'tasks.mapper', 'args': ('WOLF',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5336', 'task_id': '2018-04-10 16:28:55.715814 5336'}, 81)), ('sender', 'Wei-Legion')])
    
    Data received: 531 bytes
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '71484'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['the'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5334', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5334', 'correlation_id': '2018-04-10 16:28:55.715814 5334', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '71484'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    Message:
    OrderedDict([('correlation_id', '71199'), ('message_id', '2018-04-10 16:29:00.395015 5715'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5336', 'function': 'tasks.mapper', 'args': ('WOLF',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5336', 'task_id': '2018-04-10 16:28:55.715814 5336'}, 81)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '71589'), ('function', 'dequeue_task'), ('message_id', '71589'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '71589'), ('message_id', '2018-04-10 16:29:00.659217 5732'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5337', 'function': 'tasks.mapper', 'args': ('meeting',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5337', 'task_id': '2018-04-10 16:28:55.715814 5337'}, 80)), ('sender', 'Wei-Legion')])
    
    
    Sending 500 bytes
    Message:
    OrderedDict([('correlation_id', '71589'), ('message_id', '2018-04-10 16:29:00.659217 5732'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5337', 'function': 'tasks.mapper', 'args': ('meeting',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5337', 'task_id': '2018-04-10 16:28:55.715814 5337'}, 80)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '71738'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Lamb', 1], 'function': 'tasks.mapper', 'args': ['Lamb'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5335', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5335', 'correlation_id': '2018-04-10 16:28:55.715814 5335', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '71738'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '71843'), ('function', 'dequeue_task'), ('message_id', '71843'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '71843'), ('message_id', '2018-04-10 16:29:00.870759 5750'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5338', 'function': 'tasks.mapper', 'args': ('with',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5338', 'task_id': '2018-04-10 16:28:55.715814 5338'}, 79)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '71843'), ('message_id', '2018-04-10 16:29:00.870759 5750'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5338', 'function': 'tasks.mapper', 'args': ('with',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5338', 'task_id': '2018-04-10 16:28:55.715814 5338'}, 79)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '72293'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['WOLF', 1], 'function': 'tasks.mapper', 'args': ['WOLF'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5336', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5336', 'correlation_id': '2018-04-10 16:28:55.715814 5336', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '72293'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '72400'), ('function', 'dequeue_task'), ('message_id', '72400'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '72400'), ('message_id', '2018-04-10 16:29:01.381116 5794'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5339', 'function': 'tasks.mapper', 'args': ('a',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5339', 'task_id': '2018-04-10 16:28:55.715814 5339'}, 78)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '72458'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['meeting', 1], 'function': 'tasks.mapper', 'args': ['meeting'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5337', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5337', 'correlation_id': '2018-04-10 16:28:55.715814 5337', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '72458'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '72400'), ('message_id', '2018-04-10 16:29:01.381116 5794'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5339', 'function': 'tasks.mapper', 'args': ('a',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5339', 'task_id': '2018-04-10 16:28:55.715814 5339'}, 78)), ('sender', 'Wei-Legion')])
    
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '72566'), ('function', 'dequeue_task'), ('message_id', '72566'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '72566'), ('message_id', '2018-04-10 16:29:01.558623 5809'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5340', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5340', 'task_id': '2018-04-10 16:28:55.715814 5340'}, 77)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '72566'), ('message_id', '2018-04-10 16:29:01.558623 5809'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5340', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5340', 'task_id': '2018-04-10 16:28:55.715814 5340'}, 77)), ('sender', 'Wei-Legion')])
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '72569'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['with', 1], 'function': 'tasks.mapper', 'args': ['with'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5338', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5338', 'correlation_id': '2018-04-10 16:28:55.715814 5338', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '72569'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    
    Message:
    OrderedDict([('correlation_id', '72675'), ('function', 'dequeue_task'), ('message_id', '72675'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '72675'), ('message_id', '2018-04-10 16:29:01.630772 5814'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5341', 'function': 'tasks.mapper', 'args': ('astray',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5341', 'task_id': '2018-04-10 16:28:55.715814 5341'}, 76)), ('sender', 'Wei-Legion')])
    
    
    Sending 499 bytes
    Message:
    OrderedDict([('correlation_id', '72675'), ('message_id', '2018-04-10 16:29:01.630772 5814'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5341', 'function': 'tasks.mapper', 'args': ('astray',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5341', 'task_id': '2018-04-10 16:28:55.715814 5341'}, 76)), ('sender', 'Wei-Legion')])
    
    
    Data received: 529 bytes
    Message:
    OrderedDict([('correlation_id', '73209'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['a'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5339', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5339', 'correlation_id': '2018-04-10 16:28:55.715814 5339', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '73209'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '73314'), ('function', 'dequeue_task'), ('message_id', '73314'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '73314'), ('message_id', '2018-04-10 16:29:02.193059 5870'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5342', 'function': 'tasks.mapper', 'args': ('from',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5342', 'task_id': '2018-04-10 16:28:55.715814 5342'}, 75)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '73404'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Lamb', 1], 'function': 'tasks.mapper', 'args': ['Lamb'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5340', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5340', 'correlation_id': '2018-04-10 16:28:55.715814 5340', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '73404'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '73314'), ('message_id', '2018-04-10 16:29:02.193059 5870'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5342', 'function': 'tasks.mapper', 'args': ('from',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5342', 'task_id': '2018-04-10 16:28:55.715814 5342'}, 75)), ('sender', 'Wei-Legion')])
    
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '73510'), ('function', 'dequeue_task'), ('message_id', '73510'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '73510'), ('message_id', '2018-04-10 16:29:02.288216 5878'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5343', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5343', 'task_id': '2018-04-10 16:28:55.715814 5343'}, 74)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '73510'), ('message_id', '2018-04-10 16:29:02.288216 5878'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5343', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5343', 'task_id': '2018-04-10 16:28:55.715814 5343'}, 74)), ('sender', 'Wei-Legion')])
    
    
    Data received: 543 bytes
    Message:
    OrderedDict([('correlation_id', '73411'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['astray', 1], 'function': 'tasks.mapper', 'args': ['astray'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5341', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5341', 'correlation_id': '2018-04-10 16:28:55.715814 5341', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '73411'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '73520'), ('function', 'dequeue_task'), ('message_id', '73520'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '73520'), ('message_id', '2018-04-10 16:29:02.396504 5887'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5344', 'function': 'tasks.mapper', 'args': ('fold',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5344', 'task_id': '2018-04-10 16:28:55.715814 5344'}, 73)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '73520'), ('message_id', '2018-04-10 16:29:02.396504 5887'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5344', 'function': 'tasks.mapper', 'args': ('fold',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5344', 'task_id': '2018-04-10 16:28:55.715814 5344'}, 73)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '73936'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['from', 1], 'function': 'tasks.mapper', 'args': ['from'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5342', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5342', 'correlation_id': '2018-04-10 16:28:55.715814 5342', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '73936'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '74042'), ('function', 'dequeue_task'), ('message_id', '74042'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '74042'), ('message_id', '2018-04-10 16:29:03.058470 5955'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5345', 'function': 'tasks.mapper', 'args': ('resolved',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5345', 'task_id': '2018-04-10 16:28:55.715814 5345'}, 72)), ('sender', 'Wei-Legion')])
    
    
    Sending 501 bytes
    Message:
    OrderedDict([('correlation_id', '74042'), ('message_id', '2018-04-10 16:29:03.058470 5955'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5345', 'function': 'tasks.mapper', 'args': ('resolved',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5345', 'task_id': '2018-04-10 16:28:55.715814 5345'}, 72)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '74245'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['the'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5343', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5343', 'correlation_id': '2018-04-10 16:28:55.715814 5343', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '74245'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '74350'), ('function', 'dequeue_task'), ('message_id', '74350'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '74350'), ('message_id', '2018-04-10 16:29:03.293504 5977'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5346', 'function': 'tasks.mapper', 'args': ('not',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5346', 'task_id': '2018-04-10 16:28:55.715814 5346'}, 71)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '74350'), ('message_id', '2018-04-10 16:29:03.293504 5977'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5346', 'function': 'tasks.mapper', 'args': ('not',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5346', 'task_id': '2018-04-10 16:28:55.715814 5346'}, 71)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '74298'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['fold', 1], 'function': 'tasks.mapper', 'args': ['fold'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5344', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5344', 'correlation_id': '2018-04-10 16:28:55.715814 5344', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '74298'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '74402'), ('function', 'dequeue_task'), ('message_id', '74402'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '74402'), ('message_id', '2018-04-10 16:29:03.549191 6001'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5347', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5347', 'task_id': '2018-04-10 16:28:55.715814 5347'}, 70)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '74402'), ('message_id', '2018-04-10 16:29:03.549191 6001'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5347', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5347', 'task_id': '2018-04-10 16:28:55.715814 5347'}, 70)), ('sender', 'Wei-Legion')])
    
    
    Data received: 547 bytes
    Message:
    OrderedDict([('correlation_id', '74742'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['resolved', 1], 'function': 'tasks.mapper', 'args': ['resolved'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5345', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5345', 'correlation_id': '2018-04-10 16:28:55.715814 5345', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '74742'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '74850'), ('function', 'dequeue_task'), ('message_id', '74850'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '74850'), ('message_id', '2018-04-10 16:29:03.783937 6023'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5348', 'function': 'tasks.mapper', 'args': ('lay',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5348', 'task_id': '2018-04-10 16:28:55.715814 5348'}, 69)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '74850'), ('message_id', '2018-04-10 16:29:03.783937 6023'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5348', 'function': 'tasks.mapper', 'args': ('lay',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5348', 'task_id': '2018-04-10 16:28:55.715814 5348'}, 69)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '75051'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['not'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5346', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5346', 'correlation_id': '2018-04-10 16:28:55.715814 5346', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '75051'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '75156'), ('function', 'dequeue_task'), ('message_id', '75156'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '75156'), ('message_id', '2018-04-10 16:29:04.014199 6042'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5349', 'function': 'tasks.mapper', 'args': ('violent',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5349', 'task_id': '2018-04-10 16:28:55.715814 5349'}, 68)), ('sender', 'Wei-Legion')])
    
    
    Sending 500 bytes
    Message:
    OrderedDict([('correlation_id', '75156'), ('message_id', '2018-04-10 16:29:04.014199 6042'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5349', 'function': 'tasks.mapper', 'args': ('violent',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5349', 'task_id': '2018-04-10 16:28:55.715814 5349'}, 68)), ('sender', 'Wei-Legion')])
    
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '75372'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['to'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5347', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5347', 'correlation_id': '2018-04-10 16:28:55.715814 5347', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '75372'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '75478'), ('function', 'dequeue_task'), ('message_id', '75478'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '75478'), ('message_id', '2018-04-10 16:29:04.328487 6071'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5350', 'function': 'tasks.mapper', 'args': ('hands',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5350', 'task_id': '2018-04-10 16:28:55.715814 5350'}, 67)), ('sender', 'Wei-Legion')])
    
    
    Sending 498 bytes
    Message:
    OrderedDict([('correlation_id', '75478'), ('message_id', '2018-04-10 16:29:04.328487 6071'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5350', 'function': 'tasks.mapper', 'args': ('hands',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5350', 'task_id': '2018-04-10 16:28:55.715814 5350'}, 67)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '75459'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['lay'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5348', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5348', 'correlation_id': '2018-04-10 16:28:55.715814 5348', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '75459'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '75564'), ('function', 'dequeue_task'), ('message_id', '75564'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '75564'), ('message_id', '2018-04-10 16:29:04.572133 6093'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5351', 'function': 'tasks.mapper', 'args': ('on',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5351', 'task_id': '2018-04-10 16:28:55.715814 5351'}, 66)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '75564'), ('message_id', '2018-04-10 16:29:04.572133 6093'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5351', 'function': 'tasks.mapper', 'args': ('on',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5351', 'task_id': '2018-04-10 16:28:55.715814 5351'}, 66)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '75768'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['violent', 1], 'function': 'tasks.mapper', 'args': ['violent'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5349', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5349', 'correlation_id': '2018-04-10 16:28:55.715814 5349', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '75768'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '75875'), ('function', 'dequeue_task'), ('message_id', '75875'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '75875'), ('message_id', '2018-04-10 16:29:04.766117 6110'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5352', 'function': 'tasks.mapper', 'args': ('him',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5352', 'task_id': '2018-04-10 16:28:55.715814 5352'}, 65)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '75875'), ('message_id', '2018-04-10 16:29:04.766117 6110'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5352', 'function': 'tasks.mapper', 'args': ('him',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5352', 'task_id': '2018-04-10 16:28:55.715814 5352'}, 65)), ('sender', 'Wei-Legion')])
    
    
    Data received: 541 bytes
    Message:
    OrderedDict([('correlation_id', '76043'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['hands', 1], 'function': 'tasks.mapper', 'args': ['hands'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5350', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5350', 'correlation_id': '2018-04-10 16:28:55.715814 5350', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '76043'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '76149'), ('function', 'dequeue_task'), ('message_id', '76149'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '76149'), ('message_id', '2018-04-10 16:29:05.032436 6134'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5353', 'function': 'tasks.mapper', 'args': ('but',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5353', 'task_id': '2018-04-10 16:28:55.715814 5353'}, 64)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '76149'), ('message_id', '2018-04-10 16:29:05.032436 6134'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.715814 5353', 'function': 'tasks.mapper', 'args': ('but',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.715814 5353', 'task_id': '2018-04-10 16:28:55.715814 5353'}, 64)), ('sender', 'Wei-Legion')])
    
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '76292'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['on'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5351', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5351', 'correlation_id': '2018-04-10 16:28:55.715814 5351', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '76292'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '76396'), ('function', 'dequeue_task'), ('message_id', '76396'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '76396'), ('message_id', '2018-04-10 16:29:05.316604 6160'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5354', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5354', 'task_id': '2018-04-10 16:28:55.716314 5354'}, 63)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '76396'), ('message_id', '2018-04-10 16:29:05.316604 6160'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5354', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5354', 'task_id': '2018-04-10 16:28:55.716314 5354'}, 63)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '76530'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['him'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5352', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5352', 'correlation_id': '2018-04-10 16:28:55.715814 5352', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '76530'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '76634'), ('function', 'dequeue_task'), ('message_id', '76634'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '76634'), ('message_id', '2018-04-10 16:29:05.540301 6180'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5355', 'function': 'tasks.mapper', 'args': ('find',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5355', 'task_id': '2018-04-10 16:28:55.716314 5355'}, 62)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '76634'), ('message_id', '2018-04-10 16:29:05.540301 6180'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5355', 'function': 'tasks.mapper', 'args': ('find',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5355', 'task_id': '2018-04-10 16:28:55.716314 5355'}, 62)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '76740'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['but'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.715814 5353', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.715814 5353', 'correlation_id': '2018-04-10 16:28:55.715814 5353', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '76740'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '76845'), ('function', 'dequeue_task'), ('message_id', '76845'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '76845'), ('message_id', '2018-04-10 16:29:05.828388 6205'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5356', 'function': 'tasks.mapper', 'args': ('some',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5356', 'task_id': '2018-04-10 16:28:55.716314 5356'}, 61)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '76845'), ('message_id', '2018-04-10 16:29:05.828388 6205'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5356', 'function': 'tasks.mapper', 'args': ('some',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5356', 'task_id': '2018-04-10 16:28:55.716314 5356'}, 61)), ('sender', 'Wei-Legion')])
    
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '76973'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['to'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5354', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5354', 'correlation_id': '2018-04-10 16:28:55.716314 5354', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '76973'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '77078'), ('function', 'dequeue_task'), ('message_id', '77078'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '77078'), ('message_id', '2018-04-10 16:29:06.045293 6225'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5357', 'function': 'tasks.mapper', 'args': ('plea',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5357', 'task_id': '2018-04-10 16:28:55.716314 5357'}, 60)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '77078'), ('message_id', '2018-04-10 16:29:06.045293 6225'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5357', 'function': 'tasks.mapper', 'args': ('plea',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5357', 'task_id': '2018-04-10 16:28:55.716314 5357'}, 60)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '77487'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['find', 1], 'function': 'tasks.mapper', 'args': ['find'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5355', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5355', 'correlation_id': '2018-04-10 16:28:55.716314 5355', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '77487'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '77595'), ('function', 'dequeue_task'), ('message_id', '77595'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '77595'), ('message_id', '2018-04-10 16:29:06.433515 6262'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5358', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5358', 'task_id': '2018-04-10 16:28:55.716314 5358'}, 59)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '77595'), ('message_id', '2018-04-10 16:29:06.433515 6262'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5358', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5358', 'task_id': '2018-04-10 16:28:55.716314 5358'}, 59)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '77653'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['some', 1], 'function': 'tasks.mapper', 'args': ['some'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5356', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5356', 'correlation_id': '2018-04-10 16:28:55.716314 5356', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '77653'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '77760'), ('function', 'dequeue_task'), ('message_id', '77760'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '77760'), ('message_id', '2018-04-10 16:29:06.666273 6284'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5359', 'function': 'tasks.mapper', 'args': ('justify',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5359', 'task_id': '2018-04-10 16:28:55.716314 5359'}, 58)), ('sender', 'Wei-Legion')])
    
    
    Sending 500 bytes
    Message:
    OrderedDict([('correlation_id', '77760'), ('message_id', '2018-04-10 16:29:06.666273 6284'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5359', 'function': 'tasks.mapper', 'args': ('justify',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5359', 'task_id': '2018-04-10 16:28:55.716314 5359'}, 58)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '77693'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['plea', 1], 'function': 'tasks.mapper', 'args': ['plea'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5357', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5357', 'correlation_id': '2018-04-10 16:28:55.716314 5357', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '77693'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '77800'), ('function', 'dequeue_task'), ('message_id', '77800'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '77800'), ('message_id', '2018-04-10 16:29:06.858484 6301'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5360', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5360', 'task_id': '2018-04-10 16:28:55.716314 5360'}, 57)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '77800'), ('message_id', '2018-04-10 16:29:06.858484 6301'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5360', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5360', 'task_id': '2018-04-10 16:28:55.716314 5360'}, 57)), ('sender', 'Wei-Legion')])
    
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '78208'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['to'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5358', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5358', 'correlation_id': '2018-04-10 16:28:55.716314 5358', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '78208'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '78314'), ('function', 'dequeue_task'), ('message_id', '78314'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '78314'), ('message_id', '2018-04-10 16:29:07.191293 6334'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5361', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5361', 'task_id': '2018-04-10 16:28:55.716314 5361'}, 56)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '78314'), ('message_id', '2018-04-10 16:29:07.191293 6334'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5361', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5361', 'task_id': '2018-04-10 16:28:55.716314 5361'}, 56)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '78430'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['justify', 1], 'function': 'tasks.mapper', 'args': ['justify'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5359', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5359', 'correlation_id': '2018-04-10 16:28:55.716314 5359', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '78430'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '78539'), ('function', 'dequeue_task'), ('message_id', '78539'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '78539'), ('message_id', '2018-04-10 16:29:07.398291 6353'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5362', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5362', 'task_id': '2018-04-10 16:28:55.716314 5362'}, 55)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '78539'), ('message_id', '2018-04-10 16:29:07.398291 6353'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5362', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5362', 'task_id': '2018-04-10 16:28:55.716314 5362'}, 55)), ('sender', 'Wei-Legion')])
    
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '78600'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['to'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5360', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5360', 'correlation_id': '2018-04-10 16:28:55.716314 5360', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '78600'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '78706'), ('function', 'dequeue_task'), ('message_id', '78706'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '78706'), ('message_id', '2018-04-10 16:29:07.622729 6374'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5363', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5363', 'task_id': '2018-04-10 16:28:55.716314 5363'}, 54)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '78706'), ('message_id', '2018-04-10 16:29:07.622729 6374'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5363', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5363', 'task_id': '2018-04-10 16:28:55.716314 5363'}, 54)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '78964'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['the'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5361', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5361', 'correlation_id': '2018-04-10 16:28:55.716314 5361', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '78964'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '79069'), ('function', 'dequeue_task'), ('message_id', '79069'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '79069'), ('message_id', '2018-04-10 16:29:07.927982 6404'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5364', 'function': 'tasks.mapper', 'args': ("Wolf's",), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5364', 'task_id': '2018-04-10 16:28:55.716314 5364'}, 53)), ('sender', 'Wei-Legion')])
    
    
    Sending 499 bytes
    Message:
    OrderedDict([('correlation_id', '79069'), ('message_id', '2018-04-10 16:29:07.927982 6404'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5364', 'function': 'tasks.mapper', 'args': ("Wolf's",), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5364', 'task_id': '2018-04-10 16:28:55.716314 5364'}, 53)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '79063'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Lamb', 1], 'function': 'tasks.mapper', 'args': ['Lamb'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5362', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5362', 'correlation_id': '2018-04-10 16:28:55.716314 5362', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '79063'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '79170'), ('function', 'dequeue_task'), ('message_id', '79170'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '79170'), ('message_id', '2018-04-10 16:29:08.126898 6423'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5365', 'function': 'tasks.mapper', 'args': ('right',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5365', 'task_id': '2018-04-10 16:28:55.716314 5365'}, 52)), ('sender', 'Wei-Legion')])
    
    
    Sending 498 bytes
    Message:
    OrderedDict([('correlation_id', '79170'), ('message_id', '2018-04-10 16:29:08.126898 6423'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5365', 'function': 'tasks.mapper', 'args': ('right',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5365', 'task_id': '2018-04-10 16:28:55.716314 5365'}, 52)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '79256'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['the'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5363', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5363', 'correlation_id': '2018-04-10 16:28:55.716314 5363', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '79256'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '79359'), ('function', 'dequeue_task'), ('message_id', '79359'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '79359'), ('message_id', '2018-04-10 16:29:08.263066 6435'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5366', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5366', 'task_id': '2018-04-10 16:28:55.716314 5366'}, 51)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '79359'), ('message_id', '2018-04-10 16:29:08.263066 6435'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5366', 'function': 'tasks.mapper', 'args': ('to',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5366', 'task_id': '2018-04-10 16:28:55.716314 5366'}, 51)), ('sender', 'Wei-Legion')])
    
    
    Data received: 543 bytes
    Message:
    OrderedDict([('correlation_id', '79685'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ["Wolf's", 1], 'function': 'tasks.mapper', 'args': ["Wolf's"], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5364', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5364', 'correlation_id': '2018-04-10 16:28:55.716314 5364', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '79685'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '79793'), ('function', 'dequeue_task'), ('message_id', '79793'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '79793'), ('message_id', '2018-04-10 16:29:08.587837 6468'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5367', 'function': 'tasks.mapper', 'args': ('eat',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5367', 'task_id': '2018-04-10 16:28:55.716314 5367'}, 50)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '79793'), ('message_id', '2018-04-10 16:29:08.587837 6468'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5367', 'function': 'tasks.mapper', 'args': ('eat',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5367', 'task_id': '2018-04-10 16:28:55.716314 5367'}, 50)), ('sender', 'Wei-Legion')])
    
    
    Data received: 541 bytes
    Message:
    OrderedDict([('correlation_id', '79813'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['right', 1], 'function': 'tasks.mapper', 'args': ['right'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5365', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5365', 'correlation_id': '2018-04-10 16:28:55.716314 5365', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '79813'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '79919'), ('function', 'dequeue_task'), ('message_id', '79919'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '79919'), ('message_id', '2018-04-10 16:29:08.904141 6499'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5368', 'function': 'tasks.mapper', 'args': ('him',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5368', 'task_id': '2018-04-10 16:28:55.716314 5368'}, 49)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '79919'), ('message_id', '2018-04-10 16:29:08.904141 6499'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5368', 'function': 'tasks.mapper', 'args': ('him',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5368', 'task_id': '2018-04-10 16:28:55.716314 5368'}, 49)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '80330'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['eat'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5367', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5367', 'correlation_id': '2018-04-10 16:28:55.716314 5367', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '80330'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '80434'), ('function', 'dequeue_task'), ('message_id', '80434'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '80434'), ('message_id', '2018-04-10 16:29:09.280941 6537'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5369', 'function': 'tasks.mapper', 'args': ('He',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5369', 'task_id': '2018-04-10 16:28:55.716314 5369'}, 48)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '79930'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['to'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5366', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5366', 'correlation_id': '2018-04-10 16:28:55.716314 5366', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '79930'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    Message:
    OrderedDict([('correlation_id', '80434'), ('message_id', '2018-04-10 16:29:09.280941 6537'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5369', 'function': 'tasks.mapper', 'args': ('He',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5369', 'task_id': '2018-04-10 16:28:55.716314 5369'}, 48)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '80036'), ('function', 'dequeue_task'), ('message_id', '80036'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '80036'), ('message_id', '2018-04-10 16:29:09.367808 6544'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5370', 'function': 'tasks.mapper', 'args': ('thus',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5370', 'task_id': '2018-04-10 16:28:55.716314 5370'}, 47)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '80036'), ('message_id', '2018-04-10 16:29:09.367808 6544'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5370', 'function': 'tasks.mapper', 'args': ('thus',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5370', 'task_id': '2018-04-10 16:28:55.716314 5370'}, 47)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '80610'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['him'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5368', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5368', 'correlation_id': '2018-04-10 16:28:55.716314 5368', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '80610'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '80714'), ('function', 'dequeue_task'), ('message_id', '80714'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '80714'), ('message_id', '2018-04-10 16:29:09.580221 6564'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5371', 'function': 'tasks.mapper', 'args': ('addressed',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5371', 'task_id': '2018-04-10 16:28:55.716314 5371'}, 46)), ('sender', 'Wei-Legion')])
    
    
    Sending 502 bytes
    Message:
    OrderedDict([('correlation_id', '80714'), ('message_id', '2018-04-10 16:29:09.580221 6564'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5371', 'function': 'tasks.mapper', 'args': ('addressed',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5371', 'task_id': '2018-04-10 16:28:55.716314 5371'}, 46)), ('sender', 'Wei-Legion')])
    
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '81037'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['He'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5369', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5369', 'correlation_id': '2018-04-10 16:28:55.716314 5369', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '81037'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '81141'), ('function', 'dequeue_task'), ('message_id', '81141'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '81141'), ('message_id', '2018-04-10 16:29:10.050724 6609'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5372', 'function': 'tasks.mapper', 'args': ('him:',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5372', 'task_id': '2018-04-10 16:28:55.716314 5372'}, 45)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '81097'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['thus', 1], 'function': 'tasks.mapper', 'args': ['thus'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5370', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5370', 'correlation_id': '2018-04-10 16:28:55.716314 5370', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '81097'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    Message:
    OrderedDict([('correlation_id', '81141'), ('message_id', '2018-04-10 16:29:10.050724 6609'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5372', 'function': 'tasks.mapper', 'args': ('him:',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5372', 'task_id': '2018-04-10 16:28:55.716314 5372'}, 45)), ('sender', 'Wei-Legion')])
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '81204'), ('function', 'dequeue_task'), ('message_id', '81204'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    
    Processed result:
    OrderedDict([('correlation_id', '81204'), ('message_id', '2018-04-10 16:29:10.111749 6614'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5373', 'function': 'tasks.mapper', 'args': ('"Sirrah',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5373', 'task_id': '2018-04-10 16:28:55.716314 5373'}, 44)), ('sender', 'Wei-Legion')])
    
    
    Sending 501 bytes
    Message:
    OrderedDict([('correlation_id', '81204'), ('message_id', '2018-04-10 16:29:10.111749 6614'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5373', 'function': 'tasks.mapper', 'args': ('"Sirrah',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5373', 'task_id': '2018-04-10 16:28:55.716314 5373'}, 44)), ('sender', 'Wei-Legion')])
    
    
    Data received: 549 bytes
    Message:
    OrderedDict([('correlation_id', '81295'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['addressed', 1], 'function': 'tasks.mapper', 'args': ['addressed'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5371', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5371', 'correlation_id': '2018-04-10 16:28:55.716314 5371', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '81295'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '81404'), ('function', 'dequeue_task'), ('message_id', '81404'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '81404'), ('message_id', '2018-04-10 16:29:10.246118 6625'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5374', 'function': 'tasks.mapper', 'args': ('last',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5374', 'task_id': '2018-04-10 16:28:55.716314 5374'}, 43)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '81404'), ('message_id', '2018-04-10 16:29:10.246118 6625'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5374', 'function': 'tasks.mapper', 'args': ('last',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5374', 'task_id': '2018-04-10 16:28:55.716314 5374'}, 43)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '81806'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['him:', 1], 'function': 'tasks.mapper', 'args': ['him:'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5372', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5372', 'correlation_id': '2018-04-10 16:28:55.716314 5372', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '81806'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '81912'), ('function', 'dequeue_task'), ('message_id', '81912'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '81912'), ('message_id', '2018-04-10 16:29:10.708192 6672'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5375', 'function': 'tasks.mapper', 'args': ('year',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5375', 'task_id': '2018-04-10 16:28:55.716314 5375'}, 42)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '81912'), ('message_id', '2018-04-10 16:29:10.708192 6672'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5375', 'function': 'tasks.mapper', 'args': ('year',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5375', 'task_id': '2018-04-10 16:28:55.716314 5375'}, 42)), ('sender', 'Wei-Legion')])
    
    
    Data received: 547 bytes
    Message:
    OrderedDict([('correlation_id', '81775'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['"Sirrah', 1], 'function': 'tasks.mapper', 'args': ['"Sirrah'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5373', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5373', 'correlation_id': '2018-04-10 16:28:55.716314 5373', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '81775'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '81883'), ('function', 'dequeue_task'), ('message_id', '81883'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '81883'), ('message_id', '2018-04-10 16:29:10.936757 6694'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5376', 'function': 'tasks.mapper', 'args': ('you',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5376', 'task_id': '2018-04-10 16:28:55.716314 5376'}, 41)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '81883'), ('message_id', '2018-04-10 16:29:10.936757 6694'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5376', 'function': 'tasks.mapper', 'args': ('you',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5376', 'task_id': '2018-04-10 16:28:55.716314 5376'}, 41)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '81931'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['last', 1], 'function': 'tasks.mapper', 'args': ['last'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5374', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5374', 'correlation_id': '2018-04-10 16:28:55.716314 5374', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '81931'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '82038'), ('function', 'dequeue_task'), ('message_id', '82038'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '82038'), ('message_id', '2018-04-10 16:29:11.152490 6714'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5377', 'function': 'tasks.mapper', 'args': ('grossly',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5377', 'task_id': '2018-04-10 16:28:55.716314 5377'}, 40)), ('sender', 'Wei-Legion')])
    
    
    Sending 500 bytes
    Message:
    OrderedDict([('correlation_id', '82038'), ('message_id', '2018-04-10 16:29:11.152490 6714'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5377', 'function': 'tasks.mapper', 'args': ('grossly',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5377', 'task_id': '2018-04-10 16:28:55.716314 5377'}, 40)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '82495'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['year', 1], 'function': 'tasks.mapper', 'args': ['year'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5375', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5375', 'correlation_id': '2018-04-10 16:28:55.716314 5375', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '82495'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '82601'), ('function', 'dequeue_task'), ('message_id', '82601'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '82601'), ('message_id', '2018-04-10 16:29:11.485628 6747'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5378', 'function': 'tasks.mapper', 'args': ('grossly',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5378', 'task_id': '2018-04-10 16:28:55.716314 5378'}, 39)), ('sender', 'Wei-Legion')])
    
    
    Sending 500 bytes
    Message:
    OrderedDict([('correlation_id', '82601'), ('message_id', '2018-04-10 16:29:11.485628 6747'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5378', 'function': 'tasks.mapper', 'args': ('grossly',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5378', 'task_id': '2018-04-10 16:28:55.716314 5378'}, 39)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '82730'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['you'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5376', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5376', 'correlation_id': '2018-04-10 16:28:55.716314 5376', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '82730'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '82835'), ('function', 'dequeue_task'), ('message_id', '82835'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '82835'), ('message_id', '2018-04-10 16:29:11.790789 6777'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5379', 'function': 'tasks.mapper', 'args': ('insulted',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5379', 'task_id': '2018-04-10 16:28:55.716314 5379'}, 38)), ('sender', 'Wei-Legion')])
    
    
    Sending 501 bytes
    Message:
    OrderedDict([('correlation_id', '82835'), ('message_id', '2018-04-10 16:29:11.790789 6777'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5379', 'function': 'tasks.mapper', 'args': ('insulted',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5379', 'task_id': '2018-04-10 16:28:55.716314 5379'}, 38)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '82853'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['grossly', 1], 'function': 'tasks.mapper', 'args': ['grossly'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5377', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5377', 'correlation_id': '2018-04-10 16:28:55.716314 5377', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '82853'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '82961'), ('function', 'dequeue_task'), ('message_id', '82961'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '82961'), ('message_id', '2018-04-10 16:29:11.928271 6790'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5380', 'function': 'tasks.mapper', 'args': ('me"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5380', 'task_id': '2018-04-10 16:28:55.716314 5380'}, 37)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '82961'), ('message_id', '2018-04-10 16:29:11.928271 6790'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5380', 'function': 'tasks.mapper', 'args': ('me"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5380', 'task_id': '2018-04-10 16:28:55.716314 5380'}, 37)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '83228'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['grossly', 1], 'function': 'tasks.mapper', 'args': ['grossly'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5378', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5378', 'correlation_id': '2018-04-10 16:28:55.716314 5378', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '83228'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '83338'), ('function', 'dequeue_task'), ('message_id', '83338'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '83338'), ('message_id', '2018-04-10 16:29:12.149112 6811'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5381', 'function': 'tasks.mapper', 'args': ('"Indeed"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5381', 'task_id': '2018-04-10 16:28:55.716314 5381'}, 36)), ('sender', 'Wei-Legion')])
    
    
    Sending 503 bytes
    Message:
    OrderedDict([('correlation_id', '83338'), ('message_id', '2018-04-10 16:29:12.149112 6811'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5381', 'function': 'tasks.mapper', 'args': ('"Indeed"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5381', 'task_id': '2018-04-10 16:28:55.716314 5381'}, 36)), ('sender', 'Wei-Legion')])
    
    
    Data received: 547 bytes
    Message:
    OrderedDict([('correlation_id', '83498'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['insulted', 1], 'function': 'tasks.mapper', 'args': ['insulted'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5379', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5379', 'correlation_id': '2018-04-10 16:28:55.716314 5379', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '83498'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '83605'), ('function', 'dequeue_task'), ('message_id', '83605'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '83605'), ('message_id', '2018-04-10 16:29:12.513643 6848'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5382', 'function': 'tasks.mapper', 'args': ('bleated',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5382', 'task_id': '2018-04-10 16:28:55.716314 5382'}, 35)), ('sender', 'Wei-Legion')])
    
    
    Sending 500 bytes
    Message:
    OrderedDict([('correlation_id', '83605'), ('message_id', '2018-04-10 16:29:12.513643 6848'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5382', 'function': 'tasks.mapper', 'args': ('bleated',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5382', 'task_id': '2018-04-10 16:28:55.716314 5382'}, 35)), ('sender', 'Wei-Legion')])
    
    
    Data received: 532 bytes
    Message:
    OrderedDict([('correlation_id', '83733'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['me"'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5380', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5380', 'correlation_id': '2018-04-10 16:28:55.716314 5380', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '83733'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '83837'), ('function', 'dequeue_task'), ('message_id', '83837'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '83837'), ('message_id', '2018-04-10 16:29:12.715000 6867'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5383', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5383', 'task_id': '2018-04-10 16:28:55.716314 5383'}, 34)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '83837'), ('message_id', '2018-04-10 16:29:12.715000 6867'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5383', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5383', 'task_id': '2018-04-10 16:28:55.716314 5383'}, 34)), ('sender', 'Wei-Legion')])
    
    
    Data received: 551 bytes
    Message:
    OrderedDict([('correlation_id', '83931'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['"Indeed"', 1], 'function': 'tasks.mapper', 'args': ['"Indeed"'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5381', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5381', 'correlation_id': '2018-04-10 16:28:55.716314 5381', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '83931'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '84040'), ('function', 'dequeue_task'), ('message_id', '84040'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '84040'), ('message_id', '2018-04-10 16:29:12.921549 6884'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5384', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5384', 'task_id': '2018-04-10 16:28:55.716314 5384'}, 33)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '84040'), ('message_id', '2018-04-10 16:29:12.921549 6884'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5384', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5384', 'task_id': '2018-04-10 16:28:55.716314 5384'}, 33)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '84163'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['bleated', 1], 'function': 'tasks.mapper', 'args': ['bleated'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5382', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5382', 'correlation_id': '2018-04-10 16:28:55.716314 5382', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '84163'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '84271'), ('function', 'dequeue_task'), ('message_id', '84271'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '84271'), ('message_id', '2018-04-10 16:29:13.114970 6902'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5385', 'function': 'tasks.mapper', 'args': ('in',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5385', 'task_id': '2018-04-10 16:28:55.716314 5385'}, 32)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '84271'), ('message_id', '2018-04-10 16:29:13.114970 6902'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5385', 'function': 'tasks.mapper', 'args': ('in',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5385', 'task_id': '2018-04-10 16:28:55.716314 5385'}, 32)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '84494'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['the'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5383', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5383', 'correlation_id': '2018-04-10 16:28:55.716314 5383', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '84494'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '84599'), ('function', 'dequeue_task'), ('message_id', '84599'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '84599'), ('message_id', '2018-04-10 16:29:13.482080 6940'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5386', 'function': 'tasks.mapper', 'args': ('a',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5386', 'task_id': '2018-04-10 16:28:55.716314 5386'}, 31)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    
    Sending 494 bytes
    Message:
    OrderedDict([('correlation_id', '84599'), ('message_id', '2018-04-10 16:29:13.482080 6940'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5386', 'function': 'tasks.mapper', 'args': ('a',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5386', 'task_id': '2018-04-10 16:28:55.716314 5386'}, 31)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '84685'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Lamb', 1], 'function': 'tasks.mapper', 'args': ['Lamb'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5384', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5384', 'correlation_id': '2018-04-10 16:28:55.716314 5384', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '84685'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '84792'), ('function', 'dequeue_task'), ('message_id', '84792'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '84792'), ('message_id', '2018-04-10 16:29:13.701845 6961'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5387', 'function': 'tasks.mapper', 'args': ('mournful',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5387', 'task_id': '2018-04-10 16:28:55.716314 5387'}, 30)), ('sender', 'Wei-Legion')])
    
    
    Sending 501 bytes
    Message:
    OrderedDict([('correlation_id', '84792'), ('message_id', '2018-04-10 16:29:13.701845 6961'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5387', 'function': 'tasks.mapper', 'args': ('mournful',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5387', 'task_id': '2018-04-10 16:28:55.716314 5387'}, 30)), ('sender', 'Wei-Legion')])
    
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '84766'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['in'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5385', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5385', 'correlation_id': '2018-04-10 16:28:55.716314 5385', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '84766'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '84871'), ('function', 'dequeue_task'), ('message_id', '84871'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '84871'), ('message_id', '2018-04-10 16:29:13.959531 6986'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5388', 'function': 'tasks.mapper', 'args': ('tone',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5388', 'task_id': '2018-04-10 16:28:55.716314 5388'}, 29)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '84871'), ('message_id', '2018-04-10 16:29:13.959531 6986'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5388', 'function': 'tasks.mapper', 'args': ('tone',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5388', 'task_id': '2018-04-10 16:28:55.716314 5388'}, 29)), ('sender', 'Wei-Legion')])
    
    
    Data received: 529 bytes
    Message:
    OrderedDict([('correlation_id', '85371'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['a'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5386', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5386', 'correlation_id': '2018-04-10 16:28:55.716314 5386', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '85371'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '85475'), ('function', 'dequeue_task'), ('message_id', '85475'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '85475'), ('message_id', '2018-04-10 16:29:14.355982 7027'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5389', 'function': 'tasks.mapper', 'args': ('of',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5389', 'task_id': '2018-04-10 16:28:55.716314 5389'}, 28)), ('sender', 'Wei-Legion')])
    
    
    Data received: 547 bytes
    Message:
    OrderedDict([('correlation_id', '85450'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['mournful', 1], 'function': 'tasks.mapper', 'args': ['mournful'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5387', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5387', 'correlation_id': '2018-04-10 16:28:55.716314 5387', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '85450'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '85475'), ('message_id', '2018-04-10 16:29:14.355982 7027'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5389', 'function': 'tasks.mapper', 'args': ('of',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5389', 'task_id': '2018-04-10 16:28:55.716314 5389'}, 28)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '85557'), ('function', 'dequeue_task'), ('message_id', '85557'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '85557'), ('message_id', '2018-04-10 16:29:14.471287 7037'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5390', 'function': 'tasks.mapper', 'args': ('voice',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5390', 'task_id': '2018-04-10 16:28:55.716314 5390'}, 27)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Sending 498 bytes
    
    Message:
    OrderedDict([('correlation_id', '85612'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['tone', 1], 'function': 'tasks.mapper', 'args': ['tone'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5388', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5388', 'correlation_id': '2018-04-10 16:28:55.716314 5388', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '85612'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    Message:
    OrderedDict([('correlation_id', '85557'), ('message_id', '2018-04-10 16:29:14.471287 7037'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5390', 'function': 'tasks.mapper', 'args': ('voice',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5390', 'task_id': '2018-04-10 16:28:55.716314 5390'}, 27)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '85718'), ('function', 'dequeue_task'), ('message_id', '85718'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '85718'), ('message_id', '2018-04-10 16:29:14.603945 7049'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5391', 'function': 'tasks.mapper', 'args': ('"I',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5391', 'task_id': '2018-04-10 16:28:55.716314 5391'}, 26)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '85718'), ('message_id', '2018-04-10 16:29:14.603945 7049'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5391', 'function': 'tasks.mapper', 'args': ('"I',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5391', 'task_id': '2018-04-10 16:28:55.716314 5391'}, 26)), ('sender', 'Wei-Legion')])
    
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '86148'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['of'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5389', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5389', 'correlation_id': '2018-04-10 16:28:55.716314 5389', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '86148'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '86253'), ('function', 'dequeue_task'), ('message_id', '86253'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '86253'), ('message_id', '2018-04-10 16:29:15.151487 7104'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5392', 'function': 'tasks.mapper', 'args': ('was',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5392', 'task_id': '2018-04-10 16:28:55.716314 5392'}, 25)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '86253'), ('message_id', '2018-04-10 16:29:15.151487 7104'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5392', 'function': 'tasks.mapper', 'args': ('was',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5392', 'task_id': '2018-04-10 16:28:55.716314 5392'}, 25)), ('sender', 'Wei-Legion')])
    
    
    Data received: 541 bytes
    Message:
    OrderedDict([('correlation_id', '86327'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['voice', 1], 'function': 'tasks.mapper', 'args': ['voice'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5390', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5390', 'correlation_id': '2018-04-10 16:28:55.716314 5390', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '86327'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '86434'), ('function', 'dequeue_task'), ('message_id', '86434'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '86434'), ('message_id', '2018-04-10 16:29:15.442313 7132'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5393', 'function': 'tasks.mapper', 'args': ('not',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5393', 'task_id': '2018-04-10 16:28:55.716314 5393'}, 24)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '86434'), ('message_id', '2018-04-10 16:29:15.442313 7132'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5393', 'function': 'tasks.mapper', 'args': ('not',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5393', 'task_id': '2018-04-10 16:28:55.716314 5393'}, 24)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '86313'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['"I'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5391', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5391', 'correlation_id': '2018-04-10 16:28:55.716314 5391', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '86313'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '86418'), ('function', 'dequeue_task'), ('message_id', '86418'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '86418'), ('message_id', '2018-04-10 16:29:15.617254 7148'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5394', 'function': 'tasks.mapper', 'args': ('then',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5394', 'task_id': '2018-04-10 16:28:55.716314 5394'}, 23)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '86418'), ('message_id', '2018-04-10 16:29:15.617254 7148'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5394', 'function': 'tasks.mapper', 'args': ('then',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5394', 'task_id': '2018-04-10 16:28:55.716314 5394'}, 23)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '86931'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['was'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5392', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5392', 'correlation_id': '2018-04-10 16:28:55.716314 5392', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '86931'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '87037'), ('function', 'dequeue_task'), ('message_id', '87037'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '87037'), ('message_id', '2018-04-10 16:29:15.906235 7175'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5395', 'function': 'tasks.mapper', 'args': ('born"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5395', 'task_id': '2018-04-10 16:28:55.716314 5395'}, 22)), ('sender', 'Wei-Legion')])
    
    
    Sending 499 bytes
    Message:
    OrderedDict([('correlation_id', '87037'), ('message_id', '2018-04-10 16:29:15.906235 7175'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716314 5395', 'function': 'tasks.mapper', 'args': ('born"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716314 5395', 'task_id': '2018-04-10 16:28:55.716314 5395'}, 22)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '87290'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['not'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5393', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5393', 'correlation_id': '2018-04-10 16:28:55.716314 5393', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '87290'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '87394'), ('function', 'dequeue_task'), ('message_id', '87394'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '87394'), ('message_id', '2018-04-10 16:29:16.227087 7202'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5396', 'function': 'tasks.mapper', 'args': ('Then',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5396', 'task_id': '2018-04-10 16:28:55.716817 5396'}, 21)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '87394'), ('message_id', '2018-04-10 16:29:16.227087 7202'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5396', 'function': 'tasks.mapper', 'args': ('Then',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5396', 'task_id': '2018-04-10 16:28:55.716817 5396'}, 21)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '87273'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['then', 1], 'function': 'tasks.mapper', 'args': ['then'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5394', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5394', 'correlation_id': '2018-04-10 16:28:55.716314 5394', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '87273'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '87378'), ('function', 'dequeue_task'), ('message_id', '87378'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '87378'), ('message_id', '2018-04-10 16:29:16.367733 7214'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5397', 'function': 'tasks.mapper', 'args': ('said',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5397', 'task_id': '2018-04-10 16:28:55.716817 5397'}, 20)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '87378'), ('message_id', '2018-04-10 16:29:16.367733 7214'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5397', 'function': 'tasks.mapper', 'args': ('said',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5397', 'task_id': '2018-04-10 16:28:55.716817 5397'}, 20)), ('sender', 'Wei-Legion')])
    
    
    Data received: 543 bytes
    Message:
    OrderedDict([('correlation_id', '87578'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['born"', 1], 'function': 'tasks.mapper', 'args': ['born"'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716314 5395', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716314 5395', 'correlation_id': '2018-04-10 16:28:55.716314 5395', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '87578'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '87686'), ('function', 'dequeue_task'), ('message_id', '87686'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '87686'), ('message_id', '2018-04-10 16:29:17.002884 7277'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5398', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5398', 'task_id': '2018-04-10 16:28:55.716817 5398'}, 19)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '88089'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Then', 1], 'function': 'tasks.mapper', 'args': ['Then'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5396', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5396', 'correlation_id': '2018-04-10 16:28:55.716817 5396', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '88089'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    Message:
    OrderedDict([('correlation_id', '87686'), ('message_id', '2018-04-10 16:29:17.002884 7277'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5398', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5398', 'task_id': '2018-04-10 16:28:55.716817 5398'}, 19)), ('sender', 'Wei-Legion')])
    
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '88197'), ('function', 'dequeue_task'), ('message_id', '88197'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '88197'), ('message_id', '2018-04-10 16:29:17.198168 7295'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5399', 'function': 'tasks.mapper', 'args': ('Wolf',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5399', 'task_id': '2018-04-10 16:28:55.716817 5399'}, 18)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '88197'), ('message_id', '2018-04-10 16:29:17.198168 7295'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5399', 'function': 'tasks.mapper', 'args': ('Wolf',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5399', 'task_id': '2018-04-10 16:28:55.716817 5399'}, 18)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '88086'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['said', 1], 'function': 'tasks.mapper', 'args': ['said'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5397', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5397', 'correlation_id': '2018-04-10 16:28:55.716817 5397', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '88086'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '88192'), ('function', 'dequeue_task'), ('message_id', '88192'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '88192'), ('message_id', '2018-04-10 16:29:17.611227 7335'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5400', 'function': 'tasks.mapper', 'args': ('"You',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5400', 'task_id': '2018-04-10 16:28:55.716817 5400'}, 17)), ('sender', 'Wei-Legion')])
    
    
    Sending 498 bytes
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '88753'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['the'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5398', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5398', 'correlation_id': '2018-04-10 16:28:55.716817 5398', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '88753'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Message:
    OrderedDict([('correlation_id', '88192'), ('message_id', '2018-04-10 16:29:17.611227 7335'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5400', 'function': 'tasks.mapper', 'args': ('"You',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5400', 'task_id': '2018-04-10 16:28:55.716817 5400'}, 17)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '88857'), ('function', 'dequeue_task'), ('message_id', '88857'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '88857'), ('message_id', '2018-04-10 16:29:17.776226 7349'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5401', 'function': 'tasks.mapper', 'args': ('feed',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5401', 'task_id': '2018-04-10 16:28:55.716817 5401'}, 16)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '88857'), ('message_id', '2018-04-10 16:29:17.776226 7349'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5401', 'function': 'tasks.mapper', 'args': ('feed',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5401', 'task_id': '2018-04-10 16:28:55.716817 5401'}, 16)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '89128'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Wolf', 1], 'function': 'tasks.mapper', 'args': ['Wolf'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5399', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5399', 'correlation_id': '2018-04-10 16:28:55.716817 5399', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '89128'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '89235'), ('function', 'dequeue_task'), ('message_id', '89235'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '89235'), ('message_id', '2018-04-10 16:29:18.151805 7387'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5402', 'function': 'tasks.mapper', 'args': ('in',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5402', 'task_id': '2018-04-10 16:28:55.716817 5402'}, 15)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '89235'), ('message_id', '2018-04-10 16:29:18.151805 7387'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5402', 'function': 'tasks.mapper', 'args': ('in',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5402', 'task_id': '2018-04-10 16:28:55.716817 5402'}, 15)), ('sender', 'Wei-Legion')])
    
    
    Data received: 541 bytes
    Message:
    OrderedDict([('correlation_id', '89319'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['"You', 1], 'function': 'tasks.mapper', 'args': ['"You'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5400', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5400', 'correlation_id': '2018-04-10 16:28:55.716817 5400', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '89319'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '89425'), ('function', 'dequeue_task'), ('message_id', '89425'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '89425'), ('message_id', '2018-04-10 16:29:18.479987 7420'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5403', 'function': 'tasks.mapper', 'args': ('my',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5403', 'task_id': '2018-04-10 16:28:55.716817 5403'}, 14)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '89425'), ('message_id', '2018-04-10 16:29:18.479987 7420'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5403', 'function': 'tasks.mapper', 'args': ('my',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5403', 'task_id': '2018-04-10 16:28:55.716817 5403'}, 14)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '89564'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['feed', 1], 'function': 'tasks.mapper', 'args': ['feed'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5401', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5401', 'correlation_id': '2018-04-10 16:28:55.716817 5401', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '89564'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '89670'), ('function', 'dequeue_task'), ('message_id', '89670'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '89670'), ('message_id', '2018-04-10 16:29:18.789178 7450'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5404', 'function': 'tasks.mapper', 'args': ('pasture"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5404', 'task_id': '2018-04-10 16:28:55.716817 5404'}, 13)), ('sender', 'Wei-Legion')])
    
    
    Sending 502 bytes
    
    Data received: 530 bytes
    Message:
    OrderedDict([('correlation_id', '89896'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['in'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5402', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5402', 'correlation_id': '2018-04-10 16:28:55.716817 5402', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '89896'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    Message:
    OrderedDict([('correlation_id', '89670'), ('message_id', '2018-04-10 16:29:18.789178 7450'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5404', 'function': 'tasks.mapper', 'args': ('pasture"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5404', 'task_id': '2018-04-10 16:28:55.716817 5404'}, 13)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '90001'), ('function', 'dequeue_task'), ('message_id', '90001'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '90001'), ('message_id', '2018-04-10 16:29:19.374720 7511'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5405', 'function': 'tasks.mapper', 'args': ('"No',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5405', 'task_id': '2018-04-10 16:28:55.716817 5405'}, 12)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '90001'), ('message_id', '2018-04-10 16:29:19.374720 7511'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5405', 'function': 'tasks.mapper', 'args': ('"No',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5405', 'task_id': '2018-04-10 16:28:55.716817 5405'}, 12)), ('sender', 'Wei-Legion')])
    
    Data received: 530 bytes
    
    Message:
    OrderedDict([('correlation_id', '90132'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['my'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5403', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5403', 'correlation_id': '2018-04-10 16:28:55.716817 5403', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '90132'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '90236'), ('function', 'dequeue_task'), ('message_id', '90236'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '90236'), ('message_id', '2018-04-10 16:29:19.592436 7532'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5406', 'function': 'tasks.mapper', 'args': ('good',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5406', 'task_id': '2018-04-10 16:28:55.716817 5406'}, 11)), ('sender', 'Wei-Legion')])
    
    
    Sending 497 bytes
    Message:
    OrderedDict([('correlation_id', '90236'), ('message_id', '2018-04-10 16:29:19.592436 7532'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5406', 'function': 'tasks.mapper', 'args': ('good',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5406', 'task_id': '2018-04-10 16:28:55.716817 5406'}, 11)), ('sender', 'Wei-Legion')])
    
    
    Data received: 549 bytes
    Message:
    OrderedDict([('correlation_id', '90458'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['pasture"', 1], 'function': 'tasks.mapper', 'args': ['pasture"'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5404', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5404', 'correlation_id': '2018-04-10 16:28:55.716817 5404', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '90458'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '90566'), ('function', 'dequeue_task'), ('message_id', '90566'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '90566'), ('message_id', '2018-04-10 16:29:19.818293 7553'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5407', 'function': 'tasks.mapper', 'args': ('sir"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5407', 'task_id': '2018-04-10 16:28:55.716817 5407'}, 10)), ('sender', 'Wei-Legion')])
    
    
    Sending 498 bytes
    Message:
    OrderedDict([('correlation_id', '90566'), ('message_id', '2018-04-10 16:29:19.818293 7553'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5407', 'function': 'tasks.mapper', 'args': ('sir"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5407', 'task_id': '2018-04-10 16:28:55.716817 5407'}, 10)), ('sender', 'Wei-Legion')])
    
    
    Data received: 532 bytes
    Message:
    OrderedDict([('correlation_id', '91125'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['"No'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5405', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5405', 'correlation_id': '2018-04-10 16:28:55.716817 5405', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '91125'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '91230'), ('function', 'dequeue_task'), ('message_id', '91230'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '91230'), ('message_id', '2018-04-10 16:29:20.046891 7574'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5408', 'function': 'tasks.mapper', 'args': ('grossly',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5408', 'task_id': '2018-04-10 16:28:55.716817 5408'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Sending 499 bytes
    Message:
    OrderedDict([('correlation_id', '91230'), ('message_id', '2018-04-10 16:29:20.046891 7574'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5408', 'function': 'tasks.mapper', 'args': ('grossly',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5408', 'task_id': '2018-04-10 16:28:55.716817 5408'}, 9)), ('sender', 'Wei-Legion')])
    
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '91376'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['good', 1], 'function': 'tasks.mapper', 'args': ['good'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5406', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5406', 'correlation_id': '2018-04-10 16:28:55.716817 5406', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '91376'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '91482'), ('function', 'dequeue_task'), ('message_id', '91482'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '91482'), ('message_id', '2018-04-10 16:29:20.394078 7607'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5409', 'function': 'tasks.mapper', 'args': ('replied',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5409', 'task_id': '2018-04-10 16:28:55.716817 5409'}, 8)), ('sender', 'Wei-Legion')])
    
    Data received: 541 bytes
    
    Message:
    OrderedDict([('correlation_id', '91514'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['sir"', 1], 'function': 'tasks.mapper', 'args': ['sir"'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5407', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5407', 'correlation_id': '2018-04-10 16:28:55.716817 5407', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '91514'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Sending 499 bytes
    Message:
    OrderedDict([('correlation_id', '91482'), ('message_id', '2018-04-10 16:29:20.394078 7607'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5409', 'function': 'tasks.mapper', 'args': ('replied',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5409', 'task_id': '2018-04-10 16:28:55.716817 5409'}, 8)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '91620'), ('function', 'dequeue_task'), ('message_id', '91620'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '91620'), ('message_id', '2018-04-10 16:29:20.573364 7622'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5410', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5410', 'task_id': '2018-04-10 16:28:55.716817 5410'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    Message:
    OrderedDict([('correlation_id', '91620'), ('message_id', '2018-04-10 16:29:20.573364 7622'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5410', 'function': 'tasks.mapper', 'args': ('the',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5410', 'task_id': '2018-04-10 16:28:55.716817 5410'}, 7)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '91819'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['grossly', 1], 'function': 'tasks.mapper', 'args': ['grossly'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5408', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5408', 'correlation_id': '2018-04-10 16:28:55.716817 5408', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '91819'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '91928'), ('function', 'dequeue_task'), ('message_id', '91928'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '91928'), ('message_id', '2018-04-10 16:29:20.835562 7645'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5411', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5411', 'task_id': '2018-04-10 16:28:55.716817 5411'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '91928'), ('message_id', '2018-04-10 16:29:20.835562 7645'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5411', 'function': 'tasks.mapper', 'args': ('Lamb',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5411', 'task_id': '2018-04-10 16:28:55.716817 5411'}, 6)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '92116'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['replied', 1], 'function': 'tasks.mapper', 'args': ['replied'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5409', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5409', 'correlation_id': '2018-04-10 16:28:55.716817 5409', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '92116'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '92225'), ('function', 'dequeue_task'), ('message_id', '92225'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '92225'), ('message_id', '2018-04-10 16:29:21.402321 7703'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5412', 'function': 'tasks.mapper', 'args': ('"I',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5412', 'task_id': '2018-04-10 16:28:55.716817 5412'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '92306'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['the'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5410', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5410', 'correlation_id': '2018-04-10 16:28:55.716817 5410', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '92306'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    Message:
    OrderedDict([('correlation_id', '92225'), ('message_id', '2018-04-10 16:29:21.402321 7703'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5412', 'function': 'tasks.mapper', 'args': ('"I',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5412', 'task_id': '2018-04-10 16:28:55.716817 5412'}, 5)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '92411'), ('function', 'dequeue_task'), ('message_id', '92411'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '92411'), ('message_id', '2018-04-10 16:29:21.579793 7720'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5413', 'function': 'tasks.mapper', 'args': ('have',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5413', 'task_id': '2018-04-10 16:28:55.716817 5413'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Sending 496 bytes
    Message:
    OrderedDict([('correlation_id', '92411'), ('message_id', '2018-04-10 16:29:21.579793 7720'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5413', 'function': 'tasks.mapper', 'args': ('have',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5413', 'task_id': '2018-04-10 16:28:55.716817 5413'}, 4)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '93051'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['"I'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5412', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5412', 'correlation_id': '2018-04-10 16:28:55.716817 5412', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '93051'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '93156'), ('function', 'dequeue_task'), ('message_id', '93156'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '93156'), ('message_id', '2018-04-10 16:29:22.368429 7801'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5414', 'function': 'tasks.mapper', 'args': ('not',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5414', 'task_id': '2018-04-10 16:28:55.716817 5414'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '93257'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['have', 1], 'function': 'tasks.mapper', 'args': ['have'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5413', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5413', 'correlation_id': '2018-04-10 16:28:55.716817 5413', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '93257'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    Message:
    OrderedDict([('correlation_id', '93156'), ('message_id', '2018-04-10 16:29:22.368429 7801'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5414', 'function': 'tasks.mapper', 'args': ('not',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5414', 'task_id': '2018-04-10 16:28:55.716817 5414'}, 3)), ('sender', 'Wei-Legion')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '93363'), ('function', 'dequeue_task'), ('message_id', '93363'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '93363'), ('message_id', '2018-04-10 16:29:22.454170 7808'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5415', 'function': 'tasks.mapper', 'args': ('yet',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5415', 'task_id': '2018-04-10 16:28:55.716817 5415'}, 2)), ('sender', 'Wei-Legion')])
    
    
    Sending 495 bytes
    
    Data received: 539 bytes
    Message:
    OrderedDict([('correlation_id', '93363'), ('message_id', '2018-04-10 16:29:22.454170 7808'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5415', 'function': 'tasks.mapper', 'args': ('yet',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5415', 'task_id': '2018-04-10 16:28:55.716817 5415'}, 2)), ('sender', 'Wei-Legion')])
    
    Message:
    OrderedDict([('correlation_id', '93120'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['Lamb', 1], 'function': 'tasks.mapper', 'args': ['Lamb'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5411', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5411', 'correlation_id': '2018-04-10 16:28:55.716817 5411', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '93120'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '93226'), ('function', 'dequeue_task'), ('message_id', '93226'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '93226'), ('message_id', '2018-04-10 16:29:22.590882 7820'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5416', 'function': 'tasks.mapper', 'args': ('tasted',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5416', 'task_id': '2018-04-10 16:28:55.716817 5416'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Sending 498 bytes
    Message:
    OrderedDict([('correlation_id', '93226'), ('message_id', '2018-04-10 16:29:22.590882 7820'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5416', 'function': 'tasks.mapper', 'args': ('tasted',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5416', 'task_id': '2018-04-10 16:28:55.716817 5416'}, 1)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '94011'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['not'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5414', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5414', 'correlation_id': '2018-04-10 16:28:55.716817 5414', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '94011'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '94115'), ('function', 'dequeue_task'), ('message_id', '94115'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '94115'), ('message_id', '2018-04-10 16:29:23.099508 7871'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5417', 'function': 'tasks.mapper', 'args': ('grass"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5417', 'task_id': '2018-04-10 16:28:55.716817 5417'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 499 bytes
    Message:
    OrderedDict([('correlation_id', '94115'), ('message_id', '2018-04-10 16:29:23.099508 7871'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d891439'), ('reply_to', 'Wei-Legion'), ('result', ({'sender': 'Wei-Legion', 'message_type': 'function', 'message_id': '2018-04-10 16:28:55.716817 5417', 'function': 'tasks.mapper', 'args': ('grass"',), 'need_result': True, 'reply_to': 'Wei-Legion', 'correlation_id': '2018-04-10 16:28:55.716817 5417', 'task_id': '2018-04-10 16:28:55.716817 5417'}, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 531 bytes
    Message:
    OrderedDict([('correlation_id', '94174'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': None, 'function': 'tasks.mapper', 'args': ['yet'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5415', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5415', 'correlation_id': '2018-04-10 16:28:55.716817 5415', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '94174'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '94278'), ('function', 'dequeue_task'), ('message_id', '94278'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d8904d1'), ('sender', 'ESP32_b4e62d8904d1')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '94278'), ('message_id', '2018-04-10 16:29:23.296062 7886'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '94278'), ('message_id', '2018-04-10 16:29:23.296062 7886'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d8904d1'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 543 bytes
    Message:
    OrderedDict([('correlation_id', '94371'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['tasted', 1], 'function': 'tasks.mapper', 'args': ['tasted'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5416', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5416', 'correlation_id': '2018-04-10 16:28:55.716817 5416', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '94371'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Data received: 219 bytes
    Message:
    OrderedDict([('correlation_id', '94480'), ('function', 'dequeue_task'), ('message_id', '94480'), ('message_type', 'function'), ('need_result', True), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d890c49'), ('sender', 'ESP32_b4e62d890c49')])
    
    
    Processed result:
    OrderedDict([('correlation_id', '94480'), ('message_id', '2018-04-10 16:29:23.623988 7914'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Sending 207 bytes
    Message:
    OrderedDict([('correlation_id', '94480'), ('message_id', '2018-04-10 16:29:23.623988 7914'), ('message_type', 'result'), ('receiver', 'ESP32_b4e62d890c49'), ('reply_to', 'Wei-Legion'), ('result', (None, 0)), ('sender', 'Wei-Legion')])
    
    
    Data received: 545 bytes
    Message:
    OrderedDict([('correlation_id', '94847'), ('function', 'enqueue_result'), ('kwargs', {'message': {'result': ['grass"', 1], 'function': 'tasks.mapper', 'args': ['grass"'], 'reply_to': 'Wei-Legion', 'message_id': '2018-04-10 16:28:55.716817 5417', 'message_type': 'result', 'task_id': '2018-04-10 16:28:55.716817 5417', 'correlation_id': '2018-04-10 16:28:55.716817 5417', 'need_result': True, 'sender': 'Wei-Legion'}}), ('message_id', '94847'), ('message_type', 'function'), ('receiver', 'Wei-Legion'), ('reply_to', 'ESP32_b4e62d891439'), ('sender', 'ESP32_b4e62d891439')])
    
    ********** result:
    words count: 94
    
    [('Lamb', 5), ('grossly', 3), ('Wolf', 2), ('year', 1), ('with', 1), ('voice', 1), ('violent', 1), ('tone', 1), ('thus', 1), ('then', 1)]
    **********
    


```python
# Stopping
the_client.stop()
the_client = None
print('\n[________________ Demo stopped ________________]\n')
```

    [Closed: ('123.240.210.68', 1883)]
    [________________ Demo stopped ________________]
    
    
    
