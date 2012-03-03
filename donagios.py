#!/usr/bin/python
# version=1.1
# last change: replace all empty args with ""
# use: <thisscript.py> service_description hostname
# it should parse services.cfg and checkcommands.cfg and build a checkcommand
import sys, subprocess, re
from socket import gethostbyname 
service = sys.argv[1]
host = sys.argv[2]

def nslooky(name):
    try: 
       output = gethostbyname(name)
       return output
    except: 
       output = "not found" 
       return output

#service_filename = "./services.cfg"
service_filename = "/usr/local/nagios/etc/services.cfg"
#command_filename = "./checkcommands.cfg"
command_filename = "/usr/local/nagios/etc/checkcommands.cfg"
user1 = "/usr/local/nagios/libexec"
user2 = "Ap0iLai5oxieshee"
hostip = nslooky(host)

def split1strip(delim,somestring): #split once on given delimiter
    somestringsplit=somestring.split(delim,1)
    for x in range(len(somestringsplit)): #strip whitespace incl \n
        somestringsplit[x]=somestringsplit[x].strip()
    return somestringsplit

def service_cmd(service):
    f = open(service_filename, 'r')
    block = ""
    foundservice = ""
    for serviceline in f:
        if serviceline == "define service{\n":
            block = "spam"    #set block to something, were in a serviceblock!
        if serviceline[0] == "}":
            block = ""        #set block to nothing, were NOT in a serviceblock!
            foundservice = ""
        if block == "spam":   #in a serviceblock, not found end of block yet
            servicewords = split1strip(None,serviceline)
            servicecmd = ""
            if servicewords[0] == 'service_description' and servicewords[1] == service:
                foundservice = "brian" #set foundservice to something, we found the service!
            if servicewords[0] == 'check_command' and foundservice == "brian":
                servicecmd=split1strip('!',servicewords[1])
                return servicecmd
    f.close
    return

def cmd_cmd(servicecmd):
    f2 = open(command_filename, 'r')
    cmd = servicecmd[0]
    if len(servicecmd)>1:
        cmdargs = servicecmd[1]
    else:
        cmdargs = ""
    listargs = cmdargs.split('!')
    cmdblock = ""
    foundcommand = ""
    for cmdline in f2:            #open checkcommand.cfg file
        if cmdline == "define command{\n":
            cmdblock = "ham"          #set cmdblock to something
            foundcommand=""
        if cmdline[0] == "}":
            cmdblock = ""
            foundcommand=""
        if cmdblock == "ham":
            cmdwords=split1strip(None,cmdline)
            if cmdwords[1] == cmd:
                foundcommand = "parrot" #set foundcommand to something, we found command!
            if foundcommand == "parrot" and cmdwords[0] == "command_line":
                for x in range(len(listargs)):
                    arg="$ARG"+str(x+1)+"$"          #build $ARGn$ list
                    cmdwords[1]=cmdwords[1].replace(arg,listargs[x])
                cmdwords[1]=cmdwords[1].replace("$USER1$",user1)
                cmdwords[1]=cmdwords[1].replace("$HOSTADDRESS$",hostip)
                cmdwords[1]=cmdwords[1].replace("$HOSTNAME$",host)
                cmdwords[1]=re.sub("\$ARG[1-9]\$","",cmdwords[1])
                return cmdwords
    f2.close
    return

sercmd = service_cmd(service)
print "sercmd: ",sercmd
words = cmd_cmd(sercmd)
print words[1]
