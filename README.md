# DomoticzPsutil

Motherboard Sensors using Python Psutil module.
This Domoticz Plugin is still in Beta ...

Using Ubuntu, I couşdn't get any reliable information from Domoticz Native 'Motherboard Sensors' plugin. Especially the empty space for HDD was always giving wrong counts. So I wrote this plugin for my own needs and dedide to give up on native 'Motherboard Sensors'.

## Installation:
Please install the 'psutil' Python module first:
###sudo pip3 install psutil

When you first enable this Plugin It provides:
- CPU Usage Percentage
- Memory (Virtual) Memory Usage
- All mounted HDD Usage Percentages
And, if supported by your platform:
- Sensor Temperatures (Celcius)
- Fan Speeds (RPM)
- Battery Left Percentage


