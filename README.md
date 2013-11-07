sd-smarttemp
============

A server density plugin to check some S.M.A.R.T. informations for your harddrives with smartmontools.

### Sample information
```
  -----------------------------------------------------------
  | DEVICE | TEMP | POWERON | REALLOC. | PENDING | CRC ERR. |
  -----------------------------------------------------------
  |    sda |   56 |   14641 |        0 |       0 |        0 |
  -----------------------------------------------------------
```
* DEVICE = Device identifier or name key 
* TEMP = Actual temperature
* POWERON = Amount of minutes running since first power on
* REALLOC. = Reallocated Sector Count
* PENDING = Current Pending Sector
* CRC ERR. = UDMA CRC ERROR

### Configure the plugin

1. Install smartmontools for your operating system on UBUNTU execute: `` apt-get install smartmontools ``
2. Copy the plugin ***(SmartTemp.py)*** to your SD agent plugin directory
3. See additional config steps to learn how to configure the plugin for sertain harddrives only
4. Restart the Server density plugin

### Additional configuration steps (optional)
If you don't specify a custom command SmartTemp will try to find all of you harddrives and extract S.M.A.R.T. informations. If you provide a configuration SmartTemp will only monitor the devices you configured in the server density agent file.

#### Use a custom smartctl command
1. Open your server density client config file (default: /etc/sd-agent/config.cfg)
2. Add the configuration section to the client the looks like this:
```
  # Check 1
  [SmartTemp sda]
  smartcmd = smartctl -a -d ata /dev/sda
  name = sda

  # Check 2
  [SmartTemp custom]
  smartcmd = smartctl -a -d ata /dev/sdb
  name = {your custom identifier}
```

**Note:** Every SmartTemp configuration must consist of a smartcmd and name key. The smartcmd is the actual overwrite of the default command and the name key is the attribute that the check that will appear in the server density graph.

#### Example monitor a MegaRaid-Array

The following section descripts how to monitor a mega raid array with smartctl and SmartTemp. 

1. Extract you're mega raid drive ids with megacli (have to install this)
```
  # megacli -pdlist -a0| grep "Device Id"
  Device Id: 4
  Device Id: 5
```

2. Add the configuration section to the client the looks like this:
```
  # Check 1
  [SmartTemp raid_0]
  smartcmd = smartctl -d sat+megaraid,4 -a /dev/sda
  name = raid_0

  # Check 2
  [SmartTemp raid_1]
  smartcmd = smartctl -d sat+megaraid,[DEVICE ID] -a /dev/sda
  name = [your custom identifier]
```

3. You can test this by copying test.py to your agents plugin dir and execute
```
  python test.py
```

### Acknowledgements
This plugin makes heavy use of [http://louwrentius.com/](Louwrentius) excellent ** showsmart ** shell script.  
**Source:** http://louwrentius.com/static/files/showsmart

Also and because I'm a python noob (hours<20h) I think this script could be inproved and I would apprijiate any contributions to it. Fork away!

### [LICENSE](LICENSE MIT)
