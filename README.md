# PingTracker
Track LAN device online/offline status with ping commands, and update SmartThings Edge presence device (present / not present)

## Pre-requisites
- SmartThings Edge-enabled Hub
- SmartThings Edge LAN Presence Device Driver:  https://bestow-regional.api.smartthings.com/invite/Q1jP7BqnNNlL
- Edge Forwarding Bridge Server:  https://github.com/toddaustin07/edgebridge
- Python 3.7 or later (Linux, Windows, Mac)

## Caveats
Tested on Debian Linux and Windows.  Other OS's may require a minor modification to the code.  Post requests here:  https://github.com/toddaustin07/PingTracker/issues

## Setup Steps
1. Configure & install Edge Forwarding Bridge Server on a LAN computer (Linux/Windows/Mac)
2. Install Edge driver to SmartThings hub via channel invite (above); in mobile app, Add device / Scan nearby devices to create new LAN Presence device
3. Create additional LAN Presence devices as needed using button within device Controls screen
4. Configure pingtrack.cfg (see details below)
5. Configure each of the new SmartThings LAN Presence devices:
   - LAN Device Name:  unique device name (must match one of the 'ping_names' in config file below; [a-zA-Z0-9_] only; no spaces or other special characters)
   - LAN Device Address: IP:port **of pingtrack.py application** (*e.g. 192.168.1.nnn:50001*)
   - Bridge Address: IP:port of bridge server (*e.g. 192.168.1.nnn:8088*)
7. Start pingtrack.py

### Configuration File (pingtrack.cfg)

```
[config]
ping_ips = 192.168.1.nnn, 192.168.1.mmm       << list of IP addresses to be monitored (comma separated)
ping_names = dev1, dev2                       << associated list of unique names representing each device (comma separated)
ping_count = 2, 3                             << how many ping iterations to send in each scan; unique for each IP address above (comma separated)
ping_offline_retries = 2, 2                   << how many scan failures before offline status is sent to SmartThings; unique for each IP address above (comma separated)
#
ping_interval = 10                            << number of seconds interval between each scan
#
port = 50002                                  << port number to use for this application (default is 50002)
bridge_address = 192.168.1.nnn:8088           << address of Edge bridge
console_output = yes                          << log messages to console
logfile_output = yes                          << log messages to a log file
logfile = pingtrack.log                       << name of log file to use if logfile_output = 'yes'
```
