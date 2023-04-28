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

dev = False
spiffs = True
sota = False


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
if(len(sys.argv)>1):
    print('sys args present')
    print(sys.argv[1])
    if(sys.argv[1] == "dev" or sys.argv[1] == "-dev"):
        print('running dev')
        dev = True
    if(sys.argv[1] == "ns" or sys.argv[1] == "-ns"):
        print('not flashing spiffs')
        spiffs = False
    if(sys.argv[1] == "-sota" or sys.argv[1] == "sota"):
        print('Sota Firmware');
        sota = True

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
    },
    '7': {
        'name': 'Losant Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Losant/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Losant/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Losant/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Losant/partitions.bin'
    },
    '8': {
        'name': '4 Relay MirPro',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/4_Relay_MirPro/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/4_Relay_MirPro/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/4_Relay_MirPro/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/4_Relay_MirPro/partitions.bin'
    },
    '9': {
        'name': 'AWS WiFi Sensor',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/AWS_Sensor/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/AWS_Sensor/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/AWS_Sensor/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/AWS_Sensor/partitions.bin'
    },
    '10': {
        'name': 'MQTT WiFi Sensor',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/MQTT_Sensor/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/MQTT_Sensor/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/MQTT_Sensor/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/MQTT_Sensor/partitions.bin'
    },
    '11': {
        'name': 'Mirror PR53-4',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Mirror_PR53-4/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Mirror_PR53-4/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Mirror_PR53-4/bootloader-dev.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Mirror_PR53-4/partitions.bin'
    },
    '12': {
        'name': 'Azure WiFi Sensor',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Azure_Sensor/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Azure_Sensor/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Azure_Sensor/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Azure_Sensor/partitions.bin'
    },
    '13': {
        'name': 'Contact Closure Email Generator',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Email_Generator/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Email_Generator/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Email_Generator/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Email_Generator/partitions.bin'
    },
    '14': {
        'name': 'ESP XBee',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/ESP_XBee/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/ESP_XBee/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/ESP_XBee/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/ESP_XBee/partitions.bin'
    },
    '15':{
        'name': 'WiFi Azure Gateway Custom',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure_Custom/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure_Custom/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure_Custom/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure_Custom/partitions.bin'
    },
    '16':{
        'name': '4-20mA Input Transmitter 4 channel',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/4-20_Input_Mirror_Transmitter_4_Channel/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/4-20_Input_Mirror_Transmitter_4_Channel/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/4-20_Input_Mirror_Transmitter_4_Channel/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/4-20_Input_Mirror_Transmitter_4_Channel/partitions.bin'
    },
    '17':{
        'name': 'Radon MN',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/radonmn_mqtt/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/radonmn_mqtt/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/radonmn_mqtt/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/radonmn_mqtt/partitions.bin'
    },
    '18':{
        'name': '0-10VDC Input Transmitter 4 channel',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/0-10V_Input_Mirror_Transmitter_4_Channel/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/0-10V_Input_Mirror_Transmitter_4_Channel/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/0-10V_Input_Mirror_Transmitter_4_Channel/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/0-10V_Input_Mirror_Transmitter_4_Channel/partitions.bin'
    },
    '19':{
        'name': 'Goodtech 4 channel',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Goodtech_4_Relay/firmware.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Goodtech_4_Relay/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Goodtech_4_Relay/partitions.bin'
    },
    '20':{
        'name': 'SOTA Relay',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/SOTA_Relay/firmware.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/SOTA_Relay/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/SOTA_Relay/partitions.bin'
    },
    '21':{
        'name': 'Goodtech 2 relay 2 dac',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Goodtech_2_Relay_2_Dac/firmware.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Goodtech_2_Relay_2_Dac/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Goodtech_2_Relay_2_Dac/partitions.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Goodtech_2_Relay_2_Dac/spiffs.bin'
    },
    '22':{
        'name': 'RFID'
    },
    '23': {
        'name': 'MQTT V2 Temperature/Humidity Sensor',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/ESP32_V2_Sensor_Temperature_Humidity/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/ESP32_V2_Sensor_Temperature_Humidity/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/ESP32_V2_Sensor_Temperature_Humidity/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/ESP32_V2_Sensor_Temperature_Humidity/partitions.bin'
    },
    '24':{
        'name': 'SOTA PWM',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/SOTA_PWM/firmware.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/SOTA_PWM/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/SOTA_PWM/partitions.bin'
    },
    '25':{
<<<<<<< HEAD
        'name': 'Smart Repeater',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Smart_Repeater/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Smart_Repeater/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Smart_Repeater/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Smart_Repeater/partitions.bin'
=======
        'name': '8 Input Mirror Transmitter',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/eight_input_seme_mirror/firmware.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/eight_input_seme_mirror/spiffs.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/eight_input_seme_mirror/bootloader.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/eight_input_seme_mirror/partitions.bin'
>>>>>>> 453f74b7456608396189b425a66f1a2d3c733a17
    }
}

firmware_choices_dev = {
    '1': {
        'name': 'WiFi AWS Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_AWS/firmware-dev.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_AWS/spiffs-dev.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_AWS/bootloader-dev.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_AWS/partitions-dev.bin'
    },
    '2': {
        'name': 'WiFi Azure Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure/firmware-dev.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure/spiffs-dev.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure/bootloader-dev.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Azure/partitions-dev.bin'
    },
    '3': {
        'name': 'WiFi MQTT Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_MQTT/firmware-dev.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_MQTT/spiffs-dev.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_MQTT/bootloader-dev.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_MQTT/partitions-dev.bin'
    },
    '4': {
        'name': 'WiFi Google IoT Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Google/firmware-dev.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Google/spiffs-dev.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Google/bootloader-dev.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/WiFi_Google/partitions-dev.bin'
    },
    '5': {
        'name': 'Mega Modem',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/firmware-dev.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/spiffs-dev.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/bootloader-dev.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Mega_Modem/partitions-dev.bin'
    },
    '6': {
        'name': 'Cellular MQTT Gateway',
        'firmware': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/firmware-dev.bin',
        'spiffs': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/spiffs-dev.bin',
        'bootloader': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/bootloader-dev.bin',
        'partitions': 'https://ncd-esp32.s3.amazonaws.com/Cellular_MQTT/partitions-dev.bin'
    }
}

if sota:
    firmware_file = urllib.request.urlretrieve('https://ncd-esp32.s3.amazonaws.com/SOTA_Relay/firmware.bin', './firmware.bin')
    partitions_file = urllib.request.urlretrieve('https://ncd-esp32.s3.amazonaws.com/SOTA_Relay/partitions.bin', './partitions.bin')
    bootloader_file = urllib.request.urlretrieve('https://ncd-esp32.s3.amazonaws.com/SOTA_Relay/bootloader.bin', './bootloader.bin')
    espmodule = esptool.main(['--chip', 'esp32', '--port', port_array.get(target_port_key), '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_freq', '40m', '--flash_size', 'detect', '0x1000', 'bootloader.bin', '0x8000', 'partitions.bin', '0x10000', 'firmware.bin'])
    sys.exit()

print('Firmware Choices:')
for firmware in firmware_choices:
    print('['+firmware+']: ' + firmware_choices.get(firmware).get('name'))
print('')
firmware_choice = input('Please enter the number of the desired firmware: ')

if firmware_choice == '19' or firmware_choice == '20' or firmware_choice == '24':
    spiffs = False;

# if firmware_choice == '22':
    # __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    # firmware_file = open(os.path.join(__location__, 'firmware.bin'))
    # spiffs_file = open(os.path.join(__location__, 'spiffs.bin'))
    # bootloader_file = open(os.path.join(__location__, 'bootloader.bin'))
    # partitions_file = open(os.path.join(__location__, 'partitions.bin'))
    # espmodule = esptool.main(['--chip', 'esp32', '--port', port_array.get(target_port_key), '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_freq', '40m', '--flash_size', 'detect', '0x1000', 'bootloader.bin', '0x8000', 'partitions.bin', '0x00290000', 'spiffs.bin', '0x10000', 'firmware.bin'])

if(dev):
    firmware = firmware_choices_dev.get(firmware_choice)
else:
    firmware = firmware_choices.get(firmware_choice)

if firmware_choice != '22':
    print(firmware.get('firmware'))
    firmware_file = urllib.request.urlretrieve(str(firmware.get('firmware')), './firmware.bin')
    print(firmware_file)

    if spiffs:
        print(firmware.get('spiffs'))
        spiffs_file = urllib.request.urlretrieve(str(firmware.get('spiffs')), './spiffs.bin')
        print(spiffs_file)

        print(firmware.get('bootloader'))
        bootloader_file = urllib.request.urlretrieve(str(firmware.get('bootloader')), './bootloader.bin')
        print(bootloader_file)

        print(firmware.get('partitions'))
        partitions_file = urllib.request.urlretrieve(str(firmware.get('partitions')), './partitions.bin')
        print(partitions_file)

        print(port_array.get(target_port_key))

        print('')
        print('fingers crossed:')

# try:
if spiffs:
    if firmware_choice == '5' or firmware_choice == '14':
        espmodule = esptool.main(['--chip', 'esp32', '--port', port_array.get(target_port_key), '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_freq', '40m', '--flash_size', 'detect', '0x1000', 'bootloader.bin', '0x8000', 'partitions.bin', '0x00383000', 'spiffs.bin', '0x10000', 'firmware.bin'])
    else:
        espmodule = esptool.main(['--chip', 'esp32', '--port', port_array.get(target_port_key), '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_freq', '40m', '--flash_size', 'detect', '0x1000', 'bootloader.bin', '0x8000', 'partitions.bin', '0x00290000', 'spiffs.bin', '0x10000', 'firmware.bin'])
else:
    print('no spiffs')
    espmodule = esptool.main(['--chip', 'esp32', '--port', port_array.get(target_port_key), '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_freq', '40m', '--flash_size', 'detect', '0x1000', 'bootloader.bin', '0x10000', 'firmware.bin'])
    # espmodule = esptool.main(['--chip', 'esp32', '--port', '/dev/cu.SLAB_USBtoUART', '--baud', '921600', '--before', 'default_reset', '--after', 'hard_reset', 'write_flash', '-z', '--flash_mode', 'dio', '--flash_size', 'detect', '2691072', 'spiffs.bin', '0x10000', 'firmware.bin'])
# except:
    # print('fail cu')
