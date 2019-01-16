"""
<plugin key="Psutil" name="PSUtil Motherboard Sensors" author="febalci" version="0.3">
    <description>
        <h2>Psutil Plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>This Plugin gets MotherBoard Sensors Information With the usage of psutil Python module.</li>
            <li>Don't forget to install psutil Python module before using this Plugin by:</li>
            <li>pip3 install psutil</li>
        </ul>
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>CPU Percentage, Virtual Memory Percentage</li>
            <li>HDD Percentages</li>
            <li>Battery Percentage</li>
            <li>CPU Temperature, Fan Speed : Not Compatible with Windows</li>
        </ul>
    </description>
    <params>
        <param field="Mode2" label="Poll Period (min)" width="75px" required="true" default="1"/>
        <param field="Mode3" label="Mounted Network Drives" width="75px">
            <options>
                <option label="True" value="True" default="true" />
                <option label="False" value="False"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
#0.3 Bugfix: Dish Usage order again...
#    New: Include network mounted disks
#0.2 Bugfix: Disk Usage shows wrong device when df -h list order changes.
#0.1 First Commit

import Domoticz
import sys
import site

path=''
path=site.getsitepackages()
for i in path:
    sys.path.append(i)

import psutil
import json

class BasePlugin:

    def __init__(self):
        self.pollPeriod = 0
        self.pollCount = 0
        self.partitions = None
        self.number_of_disks = 0
        self.tempexist = False
        self.fanexist = False
        self.batteryexist = False
        self.number_of_added_disks = 0
        self.jsonDisks = {}
        return

    def onStart(self):

        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        self.partitions = psutil.disk_partitions(all=True)
        Domoticz.Debug(str(self.partitions))
        self.number_of_disks = len(self.partitions)
        Domoticz.Debug("Number of Devices = " + str(self.partitions))

        if (len(Devices) == 0):

            Domoticz.Device(Name="CPU", Unit=1, TypeName="Percentage", Used=1).Create()
            Domoticz.Device(Name="Memory", Unit=2, TypeName="Percentage", Used=1).Create()

            icounter = 0
            self.jsonDisks = {}

            for newdevice in list(range(self.number_of_disks)):
# Include here the missing FileSystem type you would like to see:
                if self.partitions[newdevice].fstype == 'apfs' or self.partitions[newdevice].fstype == 'NTFS' \
                 or self.partitions[newdevice].fstype == 'ntfs' or self.partitions[newdevice].fstype == 'ext4':
                    icounter += 1
                    self.jsonDisks[str(icounter)] = {}
                    self.jsonDisks[str(icounter)]['Mount'] = self.partitions[newdevice].mountpoint
                    Domoticz.Device(Name=self.partitions[newdevice].mountpoint, Unit=9+icounter, TypeName="Percentage", Used=0).Create()
# Include here the missing FileSystem for the mounted network drive you would like to see:          
                elif self.partitions[newdevice].fstype == 'nfs' or self.partitions[newdevice].fstype == 'nfs4' \
                 or self.partitions[newdevice].fstype == 'cifs' or self.partitions[newdevice].fstype == 'smbfs':
                    if Parameters["Mode3"] == "True":
                        icounter += 1
                        self.jsonDisks[str(icounter)] = {}
                        self.jsonDisks[str(icounter)]['Mount'] = self.partitions[newdevice].mountpoint
                        Domoticz.Device(Name=self.partitions[newdevice].mountpoint, Unit=9+icounter, TypeName="Percentage", Used=0).Create()
            
            with open(Parameters["HomeFolder"]+"diskorder.txt","w") as f:
                json.dump(self.jsonDisks,f, indent=4)
            self.number_of_added_disks = icounter

            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                tempcounter = 0
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            Domoticz.Debug(str(tempcounter)+' = '+str(name)+'/'+str(entry.label))
                            Domoticz.Device(Name='Temp '+str(entry.label or name), Unit=50+tempcounter, TypeName="Temperature", Used=0).Create()
                            tempcounter += 1
                else:
                    Domoticz.Log('No Temperature Sensors Found...')
            else:
                Domoticz.Log('Platform Not Supported For Sensor Temperatures...')

            if hasattr(psutil, "sensors_fans"):
                fans = psutil.sensors_fans()
                fancounter = 0
                if fans:
                    for name, entries in fans.items():
                        for entry in entries:
                            Domoticz.Device(Name='Fan '+entry.label or name, Unit=70+fancounter, TypeName="Custom", Used=0).Create()
                            fancounter += 1
                else:
                    Domoticz.Log('No Fans Found...')
            else:
                Domoticz.Log('Platform Not Supported For Sensor Fans...')

            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery:
                    Domoticz.Device(Name='Battery', Unit=70, TypeName="Percentage", Used=0).Create()
                else:
                    Domoticz.Log('No Battery Found...')
            else:
                Domoticz.Log('Platform Not Supported For Battery...')

        else:
            with open(Parameters["HomeFolder"]+"diskorder.txt") as f:
                self.jsonDisks = json.load(f)
                self.number_of_added_disks = len(self.jsonDisks)

        Domoticz.Debug("Devices created.")
        DumpConfigToLog()
           
        self.pollPeriod = 6 * int(Parameters["Mode2"]) 
        self.pollCount = self.pollPeriod - 1
        Domoticz.Heartbeat(10)

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data, Status, Extra):
        Domoticz.Debug("onMessage called with Data: '"+str(Data)+"'")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartBeat called:"+str(self.pollCount)+"/"+str(self.pollPeriod))
        if self.pollCount >= self.pollPeriod:
            cpu_percent = psutil.cpu_percent(interval=1)
            UpdateDevice(1,0,cpu_percent)
            mem = psutil.virtual_memory()
            mem_percent = mem.percent
            UpdateDevice(2,0,mem_percent)

            self.partitions = psutil.disk_partitions(all=True)
            self.number_of_disks = len(self.partitions)

            for newdevice in list(range(self.number_of_disks)):
                if self.partitions[newdevice].fstype != '':
                    disk_percent = psutil.disk_usage(self.partitions[newdevice].mountpoint)
                    Domoticz.Debug(self.partitions[newdevice].mountpoint+str(disk_percent))

                    for processeddevice in list(range(self.number_of_added_disks)):
                        Domoticz.Debug(self.partitions[newdevice].mountpoint+' - '+self.jsonDisks[str(processeddevice+1)]["Mount"])
                        if (self.partitions[newdevice].mountpoint == self.jsonDisks[str(processeddevice+1)]["Mount"]):
                            UpdateDevice(10+processeddevice,0,disk_percent.percent)

            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                tempcounter = 0
                if temps:
                    Domoticz.Debug(str(temps))
                    for name, entries in temps.items():
                        for entry in entries:
                            UpdateDevice(50+tempcounter,0,entry.current)
                            tempcounter += 1
                            Domoticz.Debug("    %-20s %s °C (high = %s °C, critical = %s °C)" % (
                                entry.label or name, entry.current, entry.high,
                                entry.critical))
                else:
                    Domoticz.Debug('No Temperature Sensors Found...')
            else:
                Domoticz.Debug('Platform Not Supported For Sensor Temperatures...')


            if hasattr(psutil, "sensors_fans"):
                fans = psutil.sensors_fans()
                fancounter = 0
                if fans:
                    Domoticz.Debug(str(fans))
                    for name, entries in fans.items():
                        for entry in entries:
                            UpdateDevice(70+fancounter,0,entry.current)
                            fancounter += 1
                            Domoticz.Debug("    %-20s %s RPM" % (entry.label or name, entry.current))
                else:
                    Domoticz.Debug('No Fans Found...')
            else:
                Domoticz.Debug('Platform Not Supported For Fans...')

            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery:
                    Domoticz.Debug(str(battery))
                    UpdateDevice(70,0,battery.percent)
                else:
                    Domoticz.Debug('No Battery Found...')
            else:
                Domoticz.Debug('Platform Not Supported For Battery...')

            self.pollCount = 0 #Reset Pollcount
        else:
            self.pollCount += 1


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue, str(sValue))
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
