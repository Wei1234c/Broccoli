# coding: utf-8

import sys

# 'esp8266' or 'win32'
# SYS_PLATFORM = sys.platform

# 'micropython' or 'cpython'
# SYS_IMPLEMENTATION = sys.implementation.name
IS_MICROPYTHON = sys.implementation.name == 'micropython'
 

# DEBUG_MODE = True


# Shared ************************
HUB_PORT = 1883
SERVER_NAME = 'Hub'
BUFFER_SIZE = 4096
PACKAGE_START = b'---PACKAGE_START---'
PACKAGE_END = b'---PACKAGE_END---'



# Hub ***************************
BIND_IP = '0.0.0.0'   # the ip which broker listens to.
MAX_CONCURRENT_CONNECTIONS = 200
SERVER_POLLING_REQUEST_TIMEOUT_SECONDS = 60 
HEART_BEAT_PROBING_PER_SECONDS = 60  



# Client ************************
# Must config ******************
BROKER_HOST = 'address_of_mqtt_broker'
# Must config ******************
GROUP_NAME = 'u_python'
USERNAME = 'USERNAME_for_mqtt_client'
PASSWORD = 'PASSWORD_for_mqtt_client'
MAX_INFLIGHT_MESSAGES = 1
KEEPALIVE = 60
QOS_LEVEL = 0  # change to QoS 0
CLIENT_RETRY_TO_CONNECT_AFTER_SECONDS = 3
CLIENT_RECEIVE_TIME_OUT_SECONDS = 5
PING_BROKER_TO_KEEP_ALIVE_EVERY_CLIENT_RECEIVE_CYCLES = int((KEEPALIVE / CLIENT_RECEIVE_TIME_OUT_SECONDS) / 2)
REQUESTS_NEED_RESULT_TIME_TO_LIVE = 12
ASYNCH_RESULT_TIMEOUT = 3
MICROPYTHON_SOCKET_CONNECTION_RESET_ERROR_MESSAGE = '[Errno 104] ECONNRESET'
MICROPYTHON_MQTT_CONNECTION_RESET_ERROR_MESSAGE = '-1'
MICROPYTHON_SOCKET_RECEIVE_TIME_OUT_ERROR_MESSAGE = 'timed out'
