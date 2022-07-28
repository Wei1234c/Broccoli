
# Broccoli - distributed task queues for ESP32 cluster
[GitHub repo.](https://github.com/Wei1234c/Broccoli)

Wei Lin  
2018-04-06  

![Broccoli](https://raw.githubusercontent.com/Wei1234c/Broccoli/master/jpgs/Broccoli_cluster_cover.gif)  

## [緣由與目標]
- Cluster 與 Raspberry Pi
  - 對於喜歡 DIY 的人來說，建立一個 cluster 是件很有趣的事情，隨著 [Raspberry Pi](https://www.raspberrypi.org/) 的出現，讓購置多台機器來建置 cluster 的成本大幅降低，網路上可以搜尋到很多用 Raspberry Pi 建立 cluster 的 [例子](https://www.google.com.tw/search?q=raspberry+pi+cluster&tbm=isch&tbo=u&source=univ&sa=X&ved=0ahUKEwiTuYuw4qDaAhWMgLwKHXaMCNkQsAQIUA&biw=1543&bih=732)。
- 成本與數量的關係
  - 但是，目前一台 Raspberry Pi 3 畢竟還是需要 NTD 1000元以上，如果可以用更小的機器，例如 [ESP32](https://en.wikipedia.org/wiki/ESP32)，來組成一個 cluster，這樣每個 node 的成本只需要 NTD 200元左右。在相同的預算下，單一節點的成本越低，nodes 的數量就可以更多，在某些用途上會更理想。
- 常見的 frameworks 和 design patterns  
  - 現有很多通訊息定和軟體平台，例如 Kafka, Dask, Ipython Parallel, Celery, MQTT ... 都可以作為 cluster 與分散式系統中 溝通與整合的機制。有很多常見的 design patterns，例如: controller/master/broker 對應 nodes/workers/clients、透過 message queue 的機制來傳遞與管理訊息的流通、producer/queue/consumer 或 publisher/topic/subscriber 的結構。組合搭配之後可以建造出彈性且強健的分散/併行運算的運算平台， [Celery](http://www.celeryproject.org/) 是很著名的例子之一。
- Celery 的原理與流程
  - Celery 是以 producer/queue/consumer 的模式來運作的，它遵循 [AMQP](https://www.amqp.org/) 的協議，可以搭配一些的套件 (例如: RabbitMQ, Redis...) 提供 task queues 的功能，在 Celery 的 [文件](http://docs.celeryproject.org/en/latest/getting-started/index.html) 中有詳細的說明，另外也可以參考 [這篇](https://www.vinta.com.br/blog/2017/celery-overview-archtecture-and-how-it-works/) 淺顯易懂的文章。
- Canvas 是 Celery 的精華之一
  - Celery 提供了一套 [Canvas](http://docs.celeryproject.org/en/latest/userguide/canvas.html) 的 sub module，透過其所提供的功能，可以很容易地把一些工作 (tasks) 事先規劃好先後順序相依關係，再一次性地提交給 broker 排入 task queues 並分派給 workers 來協助處理，client 端只需要坐等最後的處理結果就可以了。很好奇它的 source code 是怎麼寫的。
- Project 目標
  - 因此，基於上面的原因，就將這個 project 的目標就設定為: 建立一個 package，可以在 client 端透過類似 Celery Canvas 的指令模式，將工作分派給 ESP32 cluster 來協助處理。

## [作法與特色]
- 成本較低
  - 以 ESP32 作為硬體平台，建置成本較低。
- 多 brokers
  - 每個 node 其實也是一組 broker + task queue + worker，有幾個 nodes 就有幾個 brokers。
- 對稱的架構
  - ESP32 cluster 的架構上是對稱的
    - 每個 node 其實都是一組 broker + task queue + worker，並無結構上的差別。
    - 每個 node 都可以將 tasks 排入其 task queue 並發出要求，將工作分派給 cluster 中其他的 ESP32 workers。
- 透過 MQTT 溝通
  - ESP32 本來就有 WiFi 連線的功能，各個 nodes 之間透過 MQTT 做溝通，可以很容易地與現有 MQTT 系統環境接軌。
- 功能的動態佈署
  - 功能 (functions) 的遠端佈署: 我們可以將需要執行的 functions 包在一個 module.py 檔案中，透過網路動態佈署到 cluster 中的每個 node 上面，workers 就能夠執行新的功能。
- 支援類似 Canvas 的功能與指令
  - 支援類似 Celery Canvas 的機制，可以組成需要的處理流程。


### 模擬的 Canvas 功能，現在可以在 ESP32 cluster 上執行:

- **[Chains](http://docs.celeryproject.org/en/latest/userguide/canvas.html#chains):** 的主要作用是把多個運算**串聯**起來，前一個運算的結果是下一個運算的參數，這樣就可以組成一個完整的運算過程，例如下例中用`chain`組成一個 ((4+4) * 8) * 10  = 640 的計算過程  
   
```
>>> # (4 + 4) * 8 * 10
>>> res = chain(add.s(4, 4), mul.s(8), mul.s(10))
proj.tasks.add(4, 4) | proj.tasks.mul(8) | proj.tasks.mul(10)

>>> res = chain(add.s(4, 4), mul.s(8), mul.s(10))()
>>> res.get()
640
```

- **[Groups](http://docs.celeryproject.org/en/latest/userguide/canvas.html#groups):** 的主要作用是把多個運算**併聯**起來，把很多同質性的運算同時發送給許多遠端的 workers 協助處理，再收集 workers 傳回來的結果彙整成為一個結果集，例如下例中用`group`同時計算 (2+2) 和 (4+4)，結果是 [4, 8]  

```
>>> group(add.s(2, 2), add.s(4, 4))
(proj.tasks.add(2, 2), proj.tasks.add(4, 4))

>>> g = group(add.s(2, 2), add.s(4, 4))
>>> res = g()
>>> res.get()
[4, 8]
```

- **[Chords](http://docs.celeryproject.org/en/latest/userguide/canvas.html#chords):** 的主要作用是由兩段運算所組成的，第一段是一個`Groups`運算，其運算的結果會傳給第二段中的運算，作為其運算所需的參數。  

其作用可以用以下的例子來說明，`header`運算的結果會傳給`callback`做進一步的處理：
```
>>> callback = tsum.s()
>>> header = [add.s(i, i) for i in range(10)]
>>> result = chord(header)(callback)
>>> result.get()
90
```
上述的運算可以直接寫成：
```
chord(add.s(i, i) for i in xrange(10))(tsum.s()).get()
```


- **[Map & Starmap](http://docs.celeryproject.org/en/latest/userguide/canvas.html#map-starmap):** 的主要作用和 Python 中的`map`指令一樣，會對一個 list 中的每個 element 做指定的運算，例如下例中的`map`會分別對`range(10)`,`range(100)`做`sum`運算：
```
>>> ~xsum.map([range(10), range(100)])
[45, 4950]
```
`starmap`的作用和`map`指令一樣，會對一個 list 中的每個 element 做指定的運算，只是會先做 star展開，將一個`list`展開成為 positional arguments：
```
>>> ~add.starmap(zip(range(10), range(10)))
[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

- **[Chunks](http://docs.celeryproject.org/en/latest/userguide/canvas.html#chunks):** 的主要作用是把一大串的資料切成指定的份數，分派給遠端的 workers 協處處理，下例中將一個 list 切分成 10等分並發派給 workers 協助處理：
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

 
## [測試結果]
- 測試設備與組成
  - 以 PC 執行 client 端程式將 tasks 分派給一個由三個 ESP32 所組成的 cluster 來處理，請參考下列 video 的說明。
  - 詳細的程式碼，請參考 [測試用的 Jupyter notebook](https://github.com/Wei1234c/Broccoli/blob/master/notebooks/demo/mini%20cluster%20test.ipynb)   
 
 
[![ROS chatters on Windows](https://raw.githubusercontent.com/Wei1234c/Broccoli/master/jpgs/youtube.jpeg)](https://youtu.be/LbiSnh8w1kM)  



## [優缺點與應用]
- 缺點
  - 如果面對的是 CPU bound 的問題，效能上比不上 多核 CPU 上跑  multi-processes
  - 如果面對的是 IO bound，效能上比不上 多核 CPU 上跑  multi-threads
- 優點
  - 如果需要的是 實際在地理上的分散，例如大面積 分散地點的資料或設備監控，佈署 ESP32 的低成本與彈性，就不是一般 PC 或 Raspberry Pi 可比的。

#### Notes
- 雖然所提供的功能與指令與 Celery Canvas 類似，但限於 ESP32 硬體上的限制，其實在軟體上的做法差異很大。

#### Reference:  
  1. [Celery On Docker Swarm](https://github.com/Wei1234c/CeleryOnDockerSwarm/blob/master/celery_projects/CeleryOnDockerSwarm.md)   
  1. [IoT as Brain](https://github.com/Wei1234c/IOTasBrain)   
  1. [Elastic Network of Things with MQTT and MicroPython](https://github.com/Wei1234c/Elastic_Network_of_Things_with_MQTT_and_MicroPython)
