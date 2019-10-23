from __future__ import absolute_import
from __future__ import print_function, unicode_literals

import codecs
import os
import sys
import threading
import glob

import esptool

import serial

from serial.tools.list_ports import comports
from serial.tools import hexlify_codec


from pprint import pprint
import urllib.request


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


port_array = {}
# port_array.append('Cancel')
print('Scanning for Serial Ports')
print('Please wait for the scan to complete')
print('Serial Port Options:')
for serial_port in serial_ports():
    sp_key = len(port_array)+1
    port_array.update({str(sp_key): serial_port})

for serial_port in port_array:
    print('[' + serial_port + ']: ' + port_array.get(serial_port))
print('')
target_port_key = input('Please enter the number of the desired Serial Port above: ')

firmware_choices = {
    '1': {
        'name': 'WiFi AWS Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_AWS/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_AWS/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_AWS/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_AWS/partitions.bin'
    },
    '2': {
        'name': 'WiFi Azure Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure/partitions.bin'
    },
    '3': {
        'name': 'WiFi MQTT Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_MQTT/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_MQTT/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_MQTT/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_MQTT/partitions.bin'
    },
    '4': {
        'name': 'WiFi Google IoT Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Google/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Google/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Google/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Google/partitions.bin'
    },
    '5': {
        'name': 'Mega Modem',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/partitions.bin'
    },
    '6': {
        'name': 'Cellular MQTT Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/partitions.bin'
    }
}

print('Firmware Choices:')
for firmware in firmware_choices:
    print('['+firmware+']: ' + firmware_choices.get(firmware).get('name'))
print('')
firmware = input('Please enter the number of the desired firmware: ')

firmware = firmware_choices.get(firmware)
print(firmware.get('firmware'))
firmware_file = urllib.request.urlretrieve(str(firmware.get('firmware')), './firmware.bin')
print(firmware_file)

print(firmware.get('spiffs'))
spiffs_file = urllib.request.urlretrieve(str(firmware.get('spiffs')), './spiffs.bin')
print(spiffs_file)

print(port_array.get(target_port_key))

print('')
print('fingers crossed:')

try:
    espmodule = esptool.main(['--chip', 'esp32', '--port', port_array.get(target_port_key), '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_size', 'detect', '2691072', 'spiffs.bin', '0x10000', 'firmware.bin'])
    # espmodule = esptool.main(['--chip', 'esp32', '--port', '/dev/cu.SLAB_USBtoUART', '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_size', 'detect', '2691072', 'spiffs.bin', '0x10000', 'firmware.bin'])
except:
    print('fail cu')
