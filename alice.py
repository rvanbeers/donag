#!/usr/bin/python
#version 0.1
# should parse a host and service regex and list them to confirm an action like disable notifs or downtime
# TODO, build checkcommand from matching host,service, go to host, display matchinf nrpe.cfg line if applicable
# TODO, build actual downtime and disable notifs commands to write to the named pipe
import sys, subprocess, re, glob, time
from socket import gethostbyname 
#service = sys.argv[1]
#host = sys.argv[2]

def nslooky(name):
    try: 
       output = gethostbyname(name)
       return output
    except: 
       output = "not found" 
       return output

#service_filename = "./services.cfg"
#service_filename = "/usr/local/nagios/etc/services.cfg"
#command_filename = "./checkcommands.cfg"
#command_filename = "/usr/local/nagios/etc/checkcommands.cfg"
#nagios_config = "/usr/local/nagios/etc/nagios.cfg"
nagios_config = "/etc/nagios3/nagios.cfg"

filelist = []
servicelist = []
#hostregexp = re.compile('mp-casmq00\w*')
#hostregexp = re.compile('\local\w*')
hostregexp = re.compile('mp-fe0\w*')
#serviceregexp = re.compile('ActiveMQ\w*')
serviceregexp = re.compile('nl.marktplaats.suma.directory\w*')
servicelines = []

user1 = "/usr/local/nagios/libexec"
user2 = "Ap0iLai5oxieshee"
user3 = "nagios"
user4 = "blergh666"

#hostip = nslooky(host)
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

def get_dirlist(cfg_dir):
    cfg_dir = cfg_dir+"/*.cfg"
#    print "going to glob :", cfg_dir
    list = glob.glob(cfg_dir)
#    print "listzz =",list
    return list

def list_configfiles(nagios_config):
    f = open(nagios_config, 'r')
    flist = []
    for line in f:
        cfg_options=split1strip('=',line)
        if cfg_options[0] == "cfg_file":
#            print "file =",cfg_options[1]
            flist.append(cfg_options[1])
        if cfg_options[0] == "cfg_dir":
            dirlist = get_dirlist(cfg_options[1])
            for x in range(len(dirlist)):
                flist.append(dirlist[x])


    return flist

def list_services(cfg_list):
    all_services_list = []
    all_host_list = []
    match_host_list = []
    match_service_list = []
    host_services_dict = {}
    match_host_services_dict = {}
    service_start_regexp = re.compile('define service\s*{')
    for fs in cfg_list:
        f = open (fs, 'r')
        block = ""
        foundservice = ""
        last_service_found = ""
        last_match_service_found = ""
        last_host_found = ""
        last_match_host_found = ""
        servicelines = []
        servicematch = serviceregexp.match('bla') #initialize regexp before use
        hostmatch = hostregexp.match('bla')
        for configline in f:
            configline=configline.strip()
            servicestartmatch = service_start_regexp.match(configline)
            if servicestartmatch:
                block = "spam" #begin serviceblock
            if configline == "}"and block == "spam": #were in block, the end
                block = "" #end service block
                servicelines.append(configline)
#                for x in range (len(servicelines)):
#                    print servicelines[x]
                #servicematch = serviceregexp.match(last_match_service_found)
                servicematch = serviceregexp.match(last_service_found)
                hostmatch = hostregexp.match(last_host_found)
                #hostmatch = hostregexp.match(last_match_host_found)
                if servicematch and hostmatch:
#                    print FAIL,'woopdie',last_host_found,last_service_found,ENDC
#                    print FAIL,'diewoop',last_match_host_found,last_match_service_found,ENDC
                    old_service_list = []
                    new_service_list = []
                    if last_host_found in match_host_services_dict:
                        old_service_list = match_host_services_dict[last_match_host_found]
                        old_service_list.append(last_match_service_found)
                        new_service_list = old_service_list
                        match_host_services_dict[last_match_host_found] = new_service_list
                    else:
                        new_service_list.append(last_match_service_found)
                        match_host_services_dict[last_match_host_found] = new_service_list
                servicelines = []
            if block == "spam": # in a block
                servicewords = split1strip(None,configline)
                servicelines.append(configline)
                if servicewords[0] == 'service_description': # we found a random service
                    last_service_found = servicewords[1]
                    if not servicewords[1] in all_services_list:
                        all_services_list.append(servicewords[1])
                    servicematch = serviceregexp.match(servicewords[1])
                    if servicematch:
                        last_match_service_found = servicewords[1]
                if servicewords[0] == 'host_name':
                    last_host_found = servicewords[1]
                    if not  servicewords[1] in all_host_list:
                        all_host_list.append(servicewords[1])
                    hostmatch = hostregexp.match(servicewords[1])
                    if hostmatch:
                        last_match_host_found = servicewords[1]
              #          if not servicewords[1] in match_host_list:
              #              match_host_list.append(servicewords[1])
    return match_host_list, match_host_services_dict

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
filelist = list_configfiles(nagios_config)
matchhostlist,matchhostservicesdict = list_services(filelist)
#`print "filessssss: ",filelist
#print "hostlistssss: ",hostlist
#print "matchhostlistssss: ",matchhostlist
#print 'matchservicelist: ',matchservicelist
print FAIL,'matching host + services (in dict), key,value: ',ENDC
for key,value in matchhostservicesdict.iteritems():
#    print 'this key should:', key,'have these values', value
    services = value
    date_now = time.mktime(time.gmtime())
    period = 3600
    date_later = date_now + period
    print "date now:, %s, date later:, %s"  % (date_now,date_later)
#    iam      = subprocess.check_output(["whoami"]).strip()
    for item in  services:
        print 'I can haz downtimez',key, 'on this service', item
        print "SCHEDULE_HOST_DOWNTIME;%s;%s;%s;0;0;7200;Some One;Some Downtime Comment\n",date_now % (key,date_now,date_later)
        print "%s, bla die blad" % (date_now)
        #subprocess.call(['/usr/bin/printf',  "[%lu] SCHEDULE_HOST_DOWNTIME;key;1110741500;1110748700;0;0;7200;Some One;Some Downtime Comment\n" date_now])
    #    date_now = subprocess.call(['/usr/bin/printf', date_now])
print FAIL,'*************************',ENDC
print FAIL,'/usr/bin/printf "[%lu] SCHEDULE_HOST_DOWNTIME;host1;1110741500;1110748700;0;0;7200;Some One;Some Downtime Comment\n" $now > $command', ENDC
#print servicelist
# sercmd = service_cmd(service)
#print "sercmd: ",sercmd
#words = cmd_cmd(sercmd)
#print words[1]
