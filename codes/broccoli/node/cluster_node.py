# coding: utf-8
import sys
import config_mqtt
from cluster_broker import Broker
import node


class Node(node.Node):

    broker = None
    
    if broker is None:
        broker = Broker(config_mqtt.BROKER_HOST, config_mqtt.HUB_PORT)

    def __init__(self):
        self.worker = Node.broker
        self.worker.set_parent(self)
        self.broadcast = self.worker.broadcast


def main():
    try:
        the_node = Node()
        the_node.run()

    except KeyboardInterrupt:
        print("Ctrl C - Stopping.")
        the_node.stop()
        the_node = None
        sys.exit(1)


if __name__ == '__main__':
    main()
