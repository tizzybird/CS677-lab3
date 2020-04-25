#!/bin/bash
Username="yensungchen"
TargetPath=./cs677/lab3/src

# NOTE that if you would like to deploy all servers on a single machine,
# Please change below variables to the address of a same single server,
# Otherwise it fetchs elnux server IPs from config.json
# You should change those values in config.json
MultipleServer=0

if [ $MultipleServer == 1 ];
then
    FrontendServer=`python3 -c "import sys, json; f=open(sys.argv[1]); j=json.load(f); print(j['ip']['frontend']['addr'])" config.json`
    CatalogServer1=`python3 -c "import sys, json; f=open(sys.argv[1]); j=json.load(f); print(j['ip']['catalog'][0]['addr'])" config.json`
    CatalogServer2=`python3 -c "import sys, json; f=open(sys.argv[1]); j=json.load(f); print(j['ip']['catalog'][1]['addr'])" config.json`
    LockServer=`python3 -c "import sys, json; f=open(sys.argv[1]); j=json.load(f); print(j['ip']['lock'])" config.json`
    OrderServer1=`python3 -c "import sys, json; f=open(sys.argv[1]); j=json.load(f); print(j['ip']['order'][0]['addr'])" config.json`
    OrderServer2=`python3 -c "import sys, json; f=open(sys.argv[1]); j=json.load(f); print(j['ip']['order'][1]['addr'])" config.json`
    ClientServer=elnux3.cs.umass.edu
else
    TargetServer=elnux7.cs.umass.edu
    FrontendServer=$TargetServer
    CatalogServer1=$TargetServer
    CatalogServer2=$TargetServer
    LockServer=$TargetServer
    OrderServer1=$TargetServer
    OrderServer2=$TargetServer
    ClientServer=$TargetServer
fi
