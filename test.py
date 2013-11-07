# SmartTemp tester
# https://github.com/piscis/sd-smarttemp

# This is a small test suite to test the smarttemp plugin manually

from SmartTemp import SmartTemp
from ConfigParser import ConfigParser

config = ConfigParser()
config.read('/etc/sd-agent/config.cfg')

# Returns checks as dictanary
check = SmartTemp('','',config._sections).run()
print check

# Print out data as table
SmartTemp('','',config._sections).run(True)