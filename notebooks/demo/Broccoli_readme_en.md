
# Broccoli - distributed task queues for ESP32 cluster
[GitHub repo.](https://github.com/Wei1234c/Broccoli)

Wei Lin
2018-04-06

![Broccoli](https://raw.githubusercontent.com/Wei1234c/Broccoli/master/jpgs/Broccoli_cluster_cover.gif)

## [Motivations and Goal]
- Building cluster with Raspberry Pi  
  - For those who like DIY, it is very interesting to create a cluster. With the appearance of [Raspberry Pi](https://www.raspberrypi.org/), the cost of building a cluster is drastically reduced and many [examples](https://www.google.com.tw/search?q=raspberry+pi+cluster&tbm=isch&tbo=u&source=univ&sa=X&ved=0ahUKEwiTuYuw4qDaAhWMgLwKHXaMCNkQsAQIUA&biw=1543&bih=732) of using the Raspberry Pi to create clusters can be found on the Internet.  
- Relationship between cost and quantity  
  - However, at present, a Raspberry Pi 3 still costs USD 35 or more, if you can build a cluster with a smaller machine, such as [ESP32](https://en.wikipedia.org/wiki/ESP32), so the cost of each node only costs USD 7 or so. Under the same budget, the lower the cost of a single node is, the more nodes can be, and it will be more ideal for some purposes.  
- The importance of software  
  - There are many existing communication and software platforms, such as Kafka, Dask, Ipython Parallel, Celery, MQTT, etc., which can be used as a mechanism for communication and integration between cluster and distributed systems. There are many common design patterns, for example: controller/master/broker corresponds to nodes/workers/clients, the message queue and message-passing mechanism, and the structure of producer/queue/consumer or publisher/topic/subscriber. With these all combined, it is possible to build an elastic and robust computing platform for distributed/parallel operations. [Celery](http://www.celeryproject.org/) is one of the famous examples.  
- Principles and Processes of Celery  
  - Celery operates in a producer/queue/consumer paradigm. It follows the [AMQP](https://www.amqp.org/) protocol and can be used with some suites (eg RabbitMQ, Redis...) The function of providing task queues is described in detail in the [Celery documents](http://docs.celeryproject.org/en/latest/getting-started/index.html). Also refer to [this]( Https://www.vinta.com.br/blog/2017/celery-overview-archtecture-and-how-it-works/) easy-to-understand articles.  
- Canvas is one of the cores of Celery  
  - Celery provides a sub-modules called [Canvas](http://docs.celeryproject.org/en/latest/userguide/canvas.html). Through Canvas it's easy to organize tasks into workflow and dispatch it to workers for processing all at once. The client only needs to wait for the final results.  
- project goal:  
  - Therefore, the goal of this project is set as: Create a package, with which we can use pattern similar to Celery Canvas on the client side and dispatch tasks to the ESP32 cluster for processing.  

## [Design and Features]
- Lower costs  
  - With ESP32 as a hardware platform, the cost of construction is lower.  
- Symmetrical architecture  
  - ESP32 cluster is symmetrical in its architecture  
    - Each node actually has its own task queue and also plays as both broker and worker.  
    - Each node can dispatch tasks to other ESP32 workers in the cluster.  
- Multi-brokers  
  - The reason is the same as above. Each ESP32 node is actually a combination of broker + task queue + worker.  
- Dynamic deployment of functions  
  - We can package functions that need to be executed in a module.py file and dynamically deploy the module to each node in the cluster via the network. Workers can then perform new functions.  
- Support functions and instructions similar to Canvas  
  - Support mechanisms similar to Celery Canvas to organize tasks.  


### Some Canvas functionalities:

- **[Chains](http://docs.celeryproject.org/en/latest/userguide/canvas.html#chains)** The main purpose is to **cascade** multiple operations, The result of previous operation is the parameter of the next operation. For example, the following example uses `chain` to perform ((4+4) * 8) * 10 = 640  


```
>>> # (4 + 4) * 8 * 10
>>> res = chain(add.s(4, 4), mul.s(8), mul.s(10))
Proj.tasks.add(4, 4) | proj.tasks.mul(8) | proj.tasks.mul(10)

>>> res = chain(add.s(4, 4), mul.s(8), mul.s(10))()
>>> res.get()
640
```

- **[Groups](http://docs.celeryproject.org/en/latest/userguide/canvas.html#groups)** main purpose is to **parallel** multiple operations, sending multiple homogeneity tasks to many remote workers for processing, and then collect results returned by the workers, combine them into a set of results. For example, the following example uses `group` to calculate (2+2) and (4+4) simultaneously. The result is [4, 8]  

```
>>> group(add.s(2, 2), add.s(4, 4))
(proj.tasks.add(2, 2), proj.tasks.add(4, 4))

>>> g = group(add.s(2, 2), add.s(4, 4))
>>> res = g()
>>> res.get()
[4, 8]
```

- **[Chords](http://docs.celeryproject.org/en/latest/userguide/canvas.html#chords)** joins two operations, the first one being a `Groups`. The result of`group`operation will be passed to the operation in the second parentheses, as a parameter.

Its role can be illustrated by the following example. The result of the `header` operation is passed to `callback` for further processing:
```
>>> callback = tsum.s()
>>> header = [add.s(i, i) for i in range(10)]
>>> result = chord(header)(callback)
>>> result.get()
90
```
The above operation can be written directly as:
```
Chord(add.s(i, i) for i in xrange(10))(tsum.s()).get()
```

- **[Map & Starmap](http://docs.celeryproject.org/en/latest/userguide/canvas.html#map-starmap)** is the same as Python's `map` command. Each element in a list is applied with the specified operation. For example, `map` in the example below will do `sum` operations on `range(10)` and `range(100)` respectively:
```
>>> ~xsum.map([range(10), range(100)])
[45, 4950]
```
The effect of `starmap` is the same as that of the `map` command. It will perform the specified operation on each element in a list. It will just do a star expansion and expand a `list` into positional arguments:
```
>>> ~add.starmap(zip(range(10), range(10)))
[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

- **[Chunks](http://docs.celeryproject.org/en/latest/userguide/canvas.html#chunks)** is to split a long list of data into specified bins and distribute them to The workers. In the following example, a long list is divided into 10 equal-length segments and dispatched to the workers for processing:
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
 [160,162,164,166,168,170,172,174,176,178],
 [180, 182, 184, 186, 188, 190, 192, 194, 196, 198]]
```


## [Test Results]
- Test equipment and components  
  - Use the PC to execute the client program to dispatch tasks to a cluster consisting of three ESP32s. Please refer to the following video for description.  
 - Please refer to [the Jupyter notebook for testing](https://github.com/Wei1234c/Broccoli/blob/master/notebooks/demo/mini%20cluster%20test.ipynb)  
 
 
[![Broccoli](https://raw.githubusercontent.com/Wei1234c/Broccoli/master/jpgs/youtube.jpeg)](https://youtu.be/LbiSnh8w1kM)



## [Disadvantages and Advantages]
- Disadvantages  
  - If you faced CPU-bound problems, performance of ESP32 cluster is not as good as multi-processes on multi-core CPUs.  
  - If you faced IO-bound problems, performance of ESP32 cluster is not as good as multi-threads on multicore CPUs.  
- Advantages  
  - However, if you need to deal with problems of geographically dispersed nature, such as large-area / scattered data points, with the low cost and flexibility of deploying, ESP32 is preferable than an ordinary PC or Raspberry Pi.  


#### Reference:
  1. [Celery On Docker Swarm](https://github.com/Wei1234c/CeleryOnDockerSwarm/blob/master/celery_projects/CeleryOnDockerSwarm.md)   
  1. [IOT as Brain](https://github.com/Wei1234c/IOTasBrain)   
  1. [Elastic Network of Things with MQTT and MicroPython](https://github.com/Wei1234c/Elastic_Network_of_Things_with_MQTT_and_MicroPython)
