sd-smarttemp
============

A server density plugin to check some S.M.A.R.T. information's for your hard drives with ``smartmontools``.

### Sample information
```
  -----------------------------------------------------------
  | DEVICE | TEMP | POWERON | REALLOC. | PENDING | CRC ERR. |
  -----------------------------------------------------------
  |    sda |   56 |   14641 |        0 |       0 |        0 |
  -----------------------------------------------------------
```
* **DEVICE**   = Device identifier or name key
* **TEMP**     = Actual temperature
* **POWERON**  = Amount of minutes running since first power on
* **REALLOC.** = Reallocated Sector Count
* **PENDING**  = Current Pending Sector
* **CRC ERR.** = UDMA CRC ERROR

### Configure the plugin

1. First install ``smartmontools`` for your operating system on UBUNTU execute: ``apt-get install smartmontools``
2. Copy the plugin ***(SmartTemp.py)*** to your SD agent plugin directory
3. See additional config steps to learn how to configure the plugin for certain hard drives only
4. Restart the Server density plugin

### Additional configuration steps (optional)
The standard behavior of SmartTemp is to find all of you hard drives and extract S.M.A.R.T. information's. As an alternative to the standard behavior
you can provide custom configurations, SmartTemp will then only monitor the devices you configured in the server density agent configuration file.

#### Use a custom smartctl command
1. Open your server density client config file ``(default: /etc/sd-agent/config.cfg)``
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

The following section describes how to monitor a mega raid array with ``smartctl`` and SmartTemp.

1. Extract you're mega raid drive id's with ``megacli`` (you have to install this)
```
  # megacli -pdlist -a0| grep "Device Id"
  Device Id: 4
  Device Id: 5
```
2. Open your server density agent config file ``(default: /etc/sd-agent/config.cfg)``
3. Add the configuration section to the agent config file. Example config:
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

4. You can test this by copying test.py to your agent's plugin directory and execute it with:
```
  python test.py
```

### Acknowledgements
This plugin makes heavy use of [http://louwrentius.com/](Louwrentius) excellent ** showsmart ** shell script.
**Source:** http://louwrentius.com/static/files/showsmart

Also and because I'm a python noob (hours<20h) I think this script could be improved and I would appreciate any contributions to it. Fork away!
Tested under Ubuntu 12.10

### [LICENSE](LICENSE MIT)
