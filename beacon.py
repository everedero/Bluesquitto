#!/usr/bin/python3

"""
Usage: sudo python3 beacon.py

Hcitool has a limitation, it only accepts 31 bytes packets.
Zero pad the smaller ones and fail if there are too much data.
"""

import os
import subprocess
import sys
import re
import getopt
import uuid
import time
import numpy as np

def process_command(c):
    """
    Process a command string
    """
    print(c)
    os.system(c)

def check_for_sudo():
  """
  Check to see if we are the superuser, return with error if not
  """
  if 'SUDO_UID' in os.environ.keys():
    return(1)
  else:
    raise IOError("This script requires superuser privileges." +\
            "Please re-run with `sudo.'")

def is_valid_device(device):
    """
    Check to see if the hci device is valid
    kind of a cheaty way of doing this, we just grep the output of
    `hcitool list' to make sure the passed-in device string is present
    """
    valid = os.system("hciconfig list 2>/dev/null | grep -q {}".format(device))
    if valid:
        raise IOError("Invalid device {}".format(device))

def add_spaces_to_string(input):
    """
    Transforms "11223344" to "11 22 33 44"
    """
    hex_string = ""
    for idx, i in enumerate(input):
        hex_string += i
        if idx%2:
            hex_string += " "
    return(hex_string)

def test_packet():
    """
    A working, fixed packet for manufacturer data
    """
    hex_string_packed = "1E 02 01 1A    1A FF    FF FF 02 15 E2 0A 39 F4 73 F5 4B C4 A1 2F 17 D1 AD 07 A9 61 00 00 00 00 C8".replace(" ", "")
    hex_string = add_spaces_to_string(hex_string_packed)
    return(hex_string)

def set_manuf_data():
    """
    Create package with manufacturer data
    """
    manuf_data = "2B3A02005A0100E96200FD7FFF7F37891543000000"
    len_manuf = int(len(manuf_data) / 2)
    manuf_name = "8D02"
    field_type = "FF"
    total_manuf = "{:02X}{}{}{}".format(len_manuf, field_type,
             manuf_name, manuf_data)
    print(total_manuf)
    total_payload = "{}{}".format("02011A", total_manuf)
    len_payload = int(len(total_payload) / 2)
    if len_payload > 31:
        raise IOError("Hcitool max message length is 31 bytes")
    print("Payload (not padded) data {}".format(len_payload))
    hex_string_packed = total_payload.ljust(31*2, '0')
    len_payload = int(len(total_payload) / 2)
    fixed_header = "{:2X}".format(len_payload)
    total_payload = "{}{}".format(fixed_header, hex_string_packed)
    total_payload = add_spaces_to_string(total_payload)
    return(total_payload)

def set_response_data(ble_name = "43:15:89"):
    response_data = "".join(["{:02X}".format(ord(i)) for i in ble_name])
    #response_data = "6c 69 6e 6b 6d 6f 74 69 6f 6e".replace(" ", "")
    len_resp = int(len(response_data) / 2)
    resp_type = "09"
    payload = "{:02X}{:02X}{}{}".format(len_resp + 2, len_resp + 1,
            resp_type, response_data)
    len_payload = int(len(payload) / 2)
    if len_payload > 31:
        raise IOError("Hcitool max message length is 31 bytes")
    hex_string_packed = payload.ljust(31*2, '0')
    total_payload = add_spaces_to_string(hex_string_packed)
    return(total_payload)


def get_random_uuid():
    """
    Generate UUID for custom IBeacon
    """
    return uuid.uuid4().hex.upper()

def set_ibeacon_payload():
    """
    An example of IBeacon payload format, with random UUID generated.
    """
    power_hex = "33"
    split_major_hex = "00 01"
    split_minor_hex = "00 00"
    uuid = get_random_uuid()
    split_uuid = add_spaces_to_string(uuid)
    payload = "1E 02 01 1A 1A FF 4C 00 02 15 {} {} {} {} 00".format(
            split_uuid, split_major_hex, split_minor_hex, power_hex)
    return(payload)


def main(argv=None):
    device = "hci0"
    is_valid_device(device)
    check_for_sudo()
    # Shut down bluetooth
    process_command("hciconfig %s down" % device)
    # first bring up bluetooth
    process_command("hciconfig %s up" % device)

    hex_string = set_manuf_data()
   # hex_string = set_ibeacon_payload()

    # Configure BLE advertising
    # set up the beacon
    process_command("hcitool -i hci0 cmd 0x08 0x0008 {}".format(hex_string))
    # Configure BLE advertising response (beacon name)
    hex_resp = set_response_data("My Own Beacon")
    process_command("hcitool -i hci0 cmd 0x08 0x0009 {}".format(hex_resp))
    # now turn on LE advertising
    process_command("hciconfig %s leadv" % device)
    # now turn off scanning
    process_command("hciconfig %s noscan" % device)

if __name__ == "__main__":
  sys.exit(main())
