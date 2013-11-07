import re
import sys
import os
import subprocess
import signal
import platform

class SmartTemp:

    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig
        self.smarterror = False
        self.pcidevices = ""
        self.diskbypathdata = ""
        self.cfgField = '^SmartTemp'
        self.baseCMD = 'sudo /usr/sbin/smartctl -a -d ata'
        self.cmdStack = []

    def num (self, s):

        try:
            return int(s)
        except ValueError:
            try:
                return float(s)
            except ValueError:
                return s

    def get_block_devices(self):
        devicepath = "/sys/block"
        diskdevices = os.listdir(devicepath)
        return diskdevices

    def get_disk_paths(self):
        self.diskbypathdata = subprocess.Popen(['ls', '-alh', '/dev/disk/by-path'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        return self.diskbypathdata

    def is_real_device(self, device):
        for item in self.diskbypathdata.splitlines():
            if device in item:
                return True
        return False

    def get_parameter_from_smart(self, data,parameter,distance):
        regex = re.compile(parameter + '(.*)')   
        match = regex.search(data)
        if match:
            try:
                model = match.group(1).split("   ")[distance].split(" ")[1]
                # model = match.group(1)
                return str(model)
            except OSError:
                print "An error happened"
                return ""
        return ''


    def get_power_on_hours(self, smartdata):
        parameter = 'Power_On_Hours'
        distance = 12
        match = self.get_parameter_from_smart(smartdata,parameter,distance)
        return match

    def get_disk_temperature(self, smartdata):
        parameter = 'Temperature_Celsius'
        distance = 10
        match = self.get_parameter_from_smart(smartdata,parameter,distance)
        return match

    def get_reallocatedsector(self, smartdata):
        parameter = 'Reallocated_Sector_Ct'
        distance = 9
        match = self.get_parameter_from_smart(smartdata,parameter,distance)
        return match

    def get_reallocatedsectorevent(self, smartdata):
        parameter = 'Reallocated_Event_Count'
        distance = 9
        match = self.get_parameter_from_smart(smartdata,parameter,distance)
        return match

    def get_udma_crc_error(self, smartdata):
        parameter = 'UDMA_CRC_Error_Count'
        distance = 10
        match = self.get_parameter_from_smart(smartdata,parameter,distance)
        return match

    def get_pending_sector(self, smartdata):
        parameter1 = 'Total_Pending_Sectors'
        parameter2 = 'Current_Pending_Sector'
        distance1 = 10
        distance2 = 9
        match = self.get_parameter_from_smart(smartdata,parameter1,distance1)
        if not match:
            match = self.get_parameter_from_smart(smartdata,parameter2,distance2)
        return match

    def process_device(self, diskdevice):

        fullpath = "/dev/" + diskdevice

        cmd = self.baseCMD.split()
        cmd.append(fullpath)
        cmd = " ".join(cmd)

        return self.process_cmd(cmd, diskdevice)

    def process_cmd(self, cmd, name):

        try:
            rawdata = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
            diskdata = rawdata[0]
            errordata = rawdata[1]
            if errordata:
                return None

        except OSError:
            self.smarterror = True
            return ""

        #print "Diskdata: " + str(diskdata)
        
        if not diskdata:
            return None
        
        disktemp = self.get_disk_temperature(diskdata)
        diskpoweronhours = self.get_power_on_hours(diskdata)
        #print "- Disktemp: " + disktemp
        diskreallocatedsector = self.get_reallocatedsector(diskdata)
        #print "- REALLOC : " + diskreallocatedsector
        diskreallocatedevent = self.get_reallocatedsectorevent(diskdata)
        diskcurrentpending = self.get_pending_sector(diskdata)
        #print "- Pending: " + diskcurrentpending
        diskudmacrcerror = self.get_udma_crc_error(diskdata)
        
        device = [ name, disktemp, diskpoweronhours, diskreallocatedsector, diskcurrentpending, diskudmacrcerror ]
        
        return device

    #
    # Get collumn size for proper table formatting
    # Find the biggest string in a collumn
    #
    def get_collumn_size(self, table):

        col_count = len(table[0])
        col_widths = []
        for i in xrange(col_count):
            collumn = []
            for row in table:
                collumn.append(len(row[i]))
            length = max(collumn)
            col_widths.append(length)
        return col_widths            

    def display_table(self, table):

        col_widths = self.get_collumn_size(table)

        # Dirty hack to get a closing pipe character at the end of the row
        col_widths.append( 1 )

        # Some values to calculate the actual table with, including spacing 
        spacing = 1
        delimiter = 3
        table_width=(sum(col_widths) + len(col_widths)*spacing*delimiter)-delimiter

        format = ""
        for col in col_widths:
            form = "| %" + str(col) + "s "
            format += form

        #
        # Print header
        # 
        header = table[0]
        header.append("")
        print '%s' % '-'*table_width
        print format % tuple(header)
        print '%s' % '-'*table_width

        #
        # Drop header from table data  
        # 
        table.pop(0)

        #
        # Print actual table contents
        #
        for row in table:
            row.append("")
            print format % tuple(row)
        print '%s' % '-'*table_width

        if self.smarterror:
            print "ERROR: smart not installed or not working!"

        return ''


    def display_json(self, table):

        records = {}
        keys = table[0]
        table.pop(0)

        for row in table:
            data = {}

            for idx,val in enumerate(row):
                val = self.num(val)
                data[keys[idx]]=val

            if 'device' in data: 
                deviceKey = data['device']

                for idx, val in enumerate(data):

                    if val != "device":
                        records[deviceKey+" "+val] = data[val]


        if self.smarterror:
            print "ERROR: smart not installed or not working!"
            return None

        return records

    def get_table_output(self):
        #
        # Define table and add header as first row
        # The header also defines the table / collumn width
        #
        table = []
        header = [ "DEVICE", "TEMP", "POWERON", "REALLOC.", "PENDING", "CRC ERR."  ]
        table.append(header)

        if self.cmdStack:

            for executor in self.cmdStack:
                table.append(self.process_cmd(executor['smartcmd'],executor['name']))

        else:
            #
            # Main: get all interfaces and their data and display it in a table
            #
            self.get_disk_paths()

            for device in self.get_block_devices():
                if self.is_real_device(device):
                    devicedata = self.process_device(device)
                    if devicedata:
                        table.append(devicedata)


        return self.display_table(table)

    def get_json_output(self):

        #
        # Define table and add header as first row
        # The header also defines the table / collumn width
        #
        table = []
        header = [ "device", "temp", "poweron", "realloc", "pending", "crcerr"  ]
        table.append(header)

        
        if self.cmdStack:

            for executor in self.cmdStack:
                table.append(self.process_cmd(executor['smartcmd'],executor['name']))

        else:
            #
            # Main: get all interfaces and their data and display it as json
            #
            self.get_disk_paths()

            for device in self.get_block_devices():
                if self.is_real_device(device):
                    devicedata = self.process_device(device)
                    if devicedata:
                        table.append(devicedata)

        return self.display_json(table)

    def run(self,table=False):

        cfgre = re.compile(self.cfgField)

        for field in self.rawConfig:
            if cfgre.match(field):

                if 'smartcmd' in self.rawConfig[field]:
                    self.cmdStack.append(self.rawConfig[field])

        if table is True:
            return self.get_table_output()
        else:
            return self.get_json_output()
