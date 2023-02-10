# Bluesquitto

Bluetooth BLE to MQTT server gateway with an Android application.

# Beacon MQTT Android application

I forked Turbolab’s [Beacon MQTT](https://github.com/everedero/android-beacon-mqtt/tree/eve/test_broodminder) application.
It uses:

* org.altbeacon.beacon for Bluetooth BLE beacon

* org.eclipse.paho.client.mqttv3 for MQTT transmission

Originally this app is designed to work with iBeacons and detect beacon distance, but it can be modified to be an IoT BLE advertising to MQTT gateway.

## Example manufacturer payload

As a proof of concept, I added a parser for a custom manufacturer payload looking like this:

```
0   1   2   3   4   5   6   15  16
|---|---|---|---|---|---|...|---|
| MANUF |MOD|MIN|MAJ|   DATA    |
|8D  02  2B |                   |

* MANUF: Manufacturer number 0x8D02
* MOD: Model number
* MIN: Version minor number
* MAJ: Version major number
* DATA: Data payload, containing all sensor measurements.
```

Here, we are showing only the manufacturer payload, starting after the "0xFF" field type indication.

See [this document](https://www.dropbox.com/s/hwmde6h97sbmzl4/BroodMinder-User-Guide.pdf) appendix B, page 119 for more information.

In this particular example, there are no UUID in the payload, so we use the device Bluetooth address to know which device from this manufacturer is talking. This does not comply with BLE specifications, but it does happen in the real world sometimes.

In this example, this manufacturer is using the BLE device’s name to identify different devices, which is probably difficult to handle with the org.altbeacon library.

There are also no power byte at the end of the payload, so we have to "sacrifice" the latest data byte to indicate a power byte, which mandatory in org.altbeacon.beacon format.

## Use Beacon MQTT

Launch Beacon MQTT, program test.mosquitto.org, port 1883 as server.

Choose a topic name, such as "eve/bluesquitto", as topics for you MQTT messages (Beacon state topic, Master topic, Track topic). Topics work like folders on the MQTT server.

Track topic will send a message each time a new beacon is seen.

Use the "%msg%" to refer to the payload and send it through MQTT.

# Set up MQTT server and client

For test purposes, it is possible to use the free "test.mosquitto.org" MQTT server.

We will also need a desktop client to be able to retrieve messages from the remote MQTT service.

## MQTT Linux host configuration

On a Linux host:

    sudo apt install mosquitto-clients

### Reading messages from the server

    mosquitto_sub -h test.mosquitto.org -t "eve/bluesquitto" -p 1883

### Sending a message to the server

    mosquitto_pub -t 'eve/bluesquitto' -h test.mosquitto.org -m 'hello from computer' -p 1883

# Beacon simulation

A simple beacon emulation Python script is provided.

This script starts beacon advertising via hcitool, with custom manufacturer data and device name.

    sudo python3 beacon.py

# Troubleshooting

## App crashing while trying to send MQTT messages

Verify the MQTT server is alive and connected. A toast message "MQTT connected" should have appeared, and the "server" logo at the bottom of the screen should not be crossed out. The app does not check if the remote network is actually up, so remember to switch on WiFi or cellular data.
