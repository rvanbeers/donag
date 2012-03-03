#!/usr/bin/env python
# use: thisscript.py <nagiosserver> <service_to_check> <hostname>
import sys, subprocess

server = sys.argv[1]
service = sys.argv[2]
host = sys.argv[3]
lscommand = "ls donagios.py | grep donagios.py > /dev/null"
iam = subprocess.check_output(["whoami"]).strip()
iamatserver = str(iam)+"@"+server+":~"
commandfileexist = subprocess.call(['ssh', server, lscommand])

if commandfileexist == 0:
  print "yay"
else:
  print "nay"
  subprocess.call(['scp', 'donagios.py', iamatserver])

donag = './donagios.py "' + service + '" ' + host + ' && /bin/bash --login -i'
print donag
subprocess.call(['ssh', '-t', server, donag]) 
