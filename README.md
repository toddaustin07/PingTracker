# PingTracker
Track LAN device online/offline status with ping commands, and update SmartThings Edge presence device (present / not present)

## Pre-requisites
- SmartThings Edge-enabled Hub
- SmartThings Edge LAN Presence Device Driver:  https://bestow-regional.api.smartthings.com/invite/Q1jP7BqnNNlL
- Edge Forwarding Bridge Server:  https://github.com/toddaustin07/edgebridge
- Python 3.7 or later (Linux, Windows, Mac)

## Configuration File (pingtrack.cfg)

```
[config]
ping_ips = 192.168.1.nnn, 192.168.1.mmm       << list of IP addresses to be monitored
ping_names = dev1, dev2                       << associated list of unique names representing each device
ping_count = 2, 3                             << how many ping iterations to send in each scan; unique for each IP address above
ping_offline_retries = 2, 2                   << how many ping failures before offline status is sent to SmartThings; unique for each IP address above
#
ping_interval = 10                            << number of seconds interval between each scan
#
port = 50002                                  << port number to use for this application (default is 50002)
bridge_address = 192.168.1.nnn:8088           << address of Edge bridge
console_output = yes                          << log messages to console
logfile_output = yes                          << log messages to a log file
logfile = pingtrack.log                       << name of log file to use if logfile_output = yes`
```
