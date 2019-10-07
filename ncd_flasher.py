from __future__ import absolute_import
from __future__ import print_function, unicode_literals

import codecs
import os
import sys
import threading
import glob

import serial

from serial.tools.list_ports import comports
from serial.tools import hexlify_codec


from pprint import pprint
from PyInquirer import style_from_dict, Token, prompt, Separator
from examples import custom_style_2

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/cu[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def flashFirmware(answers):
    print("Port: "+answers['port'])
    print("Firmware: "+answers['firmware'])
    #this is the command that would run
    #esptool.py --chip esp32 --port "/dev/cu.SLAB_USBtoUART" --baud 921600 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_size detect 2691072 spiffs.bin 0x10000 firmware.bin


questions = [
    {
        'type': 'list',
        'name': 'port',
        'message': 'Select Serial Port for Device',
        'choices': serial_ports()
    },
    {
        'type': 'list',
        'name': 'firmware',
        'message': 'Select Firmware to flash',
        'choices': ['WiFi_AWS', 'WiFi_Azure', 'WiFi_MQTT', 'WiFi_Losant', 'WiFi_GoogleIoT', 'Mega_Modem', 'Cellular_MQTT'],
    }
]

answers = prompt(questions, style=custom_style_2)
flashFirmware(answers)
