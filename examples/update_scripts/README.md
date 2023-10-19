# o2x5xx_multi_fw_updater.py

## Description

A Python Firmware Updater Script for the ifm sensors O2D5xx and O2I5xx.
The application is able to back up the device settings and restore them after the update process.

## Contact

In case of any issues or if you want to report a bug please [contact our](mailto:support.efector.object-ident@ifm.com)
support team or create an issue in the Github repository.

## Prerequisites

### Dependent Packages

Usage of examples requires package requests. Install the package with

    $ pip install requests>=2.27.1

## Script Arguments Explained

    usage: o2x5xx_multi_fw_updater.py [-h] -i INPUT [INPUT ...] -H HOST [HOST ...]
                                      [-b BACKUP] [-l LOG] [-r]
    
    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                            specify input SWU file(s)
      -H HOST [HOST ...], --host HOST [HOST ...]
                            specify host IPs
      -b BACKUP, --backup BACKUP
                            path for config backup folder
      -l LOG, --log LOG     path for log file folder
      -r, --remove          remove config backup folder after application finished

### Usage with config backup

Go to the `examples/update_scripts` folder and run the script with following arguments

    $ python o2x5xx_multi_fw_updater.py -r -b ./backup -l ./logs -i O2x5xx_Firmware_1.30.10629.swu -H 192.168.0.69

### Usage without config backup and without logs

Go to the `examples/update_scripts` folder and run the script with following arguments

    $ python o2x5xx_multi_fw_updater.py -i O2x5xx_Firmware_1.30.10629.swu -H 192.168.0.69
