# NCD Gateway Firmware Flashing Utility

Update the firmware in your [NCD](https://ncd.io) Micro Gateway, Mega Modem or WiFi Sensor.

https://ncd.io/how-to-ncd-grepy

## Setup

Install the pre-requisite software.

1. Install [Python 3](https://www.python.org)
2. Install [PySerial](https://pythonhosted.org/pyserial/pyserial.html#installation)
3. Install the [Silicon Labs USB to UART Bridge VCP driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers)
4. [Download this Python script](https://github.com/telliottosceola/Flash_Script/archive/refs/heads/master.zip). Unzip the download.

Connect your gateway to your computer using a USB cable.

## Run the Script

**Windows**: Double click *run.bat*.

**Linux / MacOS**: Using the terminal, run `python3 ncd_flasher.py`.

Select the COM port for your gateway.

Select the firmware you wish to flash to the gateway.

Cross your fingers 🤞.

### Options

You can run *ncd_flasher.py* with *one* of the following command line options.

- `dev`: Use developer firmware URLs
- `ns`: Do not flash the spiffs
- `sota`: Use the sota firmware

**Windows**: You may run *run_ns.bat* or *run_sota.bat*.

## Contributing

TODO

## Testing

TODO

---

&copy; 2019 - 2021 National Control Devices, LLC. All rights reserved.
