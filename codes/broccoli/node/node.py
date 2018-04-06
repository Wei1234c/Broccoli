# coding: utf-8

import sys
import config_mqtt
from cluster_broker import Broker


class Node:

    broker = None
    if broker is None:
        broker = Broker(config_mqtt.BROKER_HOST, config_mqtt.HUB_PORT)

    def __init__(self):
        Node.broker.set_parent(self)
        
    def run(self):
        Node.broker.run()
        
    def stop(self):
        Node.broker.stop()
        Node.broker.set_parent(None)

    def request(self, **message):
        return Node.broker.request(message)


def main():
    try:
        node = Node()
        node.run()

    except KeyboardInterrupt:
        print("Ctrl C - Stopping.")
        node.stop()
        node = None
        sys.exit(1)


if __name__ == '__main__':
    main()
