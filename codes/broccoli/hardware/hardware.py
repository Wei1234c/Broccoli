# coding: utf-8
import os


# for NodeMCU32
# ON_BOARD_LED_HIGH_IS_ON = (os.uname().sysname == 'esp32')
# ON_BOARD_LED_PIN_NO = 2


# for Lolin32
ON_BOARD_LED_HIGH_IS_ON = False
# ON_BOARD_LED_PIN_NO = 5  # for Lolin32
ON_BOARD_LED_PIN_NO = 22  # for Lolin32 Lite


# gpio_pins
gpio_pins = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
             11, 12, 13, 14, 15, 16, 17, 18, 19,
             21, 22, 23, 25, 26, 27,
             32, 34, 35, 36, 37, 38, 39)
