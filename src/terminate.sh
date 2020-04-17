#!/bin/bash
username=yensungchen
frontendServer=elnux1.cs.umass.edu
catalogServer=elnux2.cs.umass.edu
orderServer=elnux7.cs.umass.edu
clientServer=elnux3.cs.umass.edu
# deploy frontend server
ssh ${username}@${frontendServer} << 'END_SSH'
set -x
targetPath=./cs677/lab2/src
cd ${targetPath}
cat frontend.pid > kill
rm frontend.pid
END_SSH

# deploy catalog server
ssh ${username}@${catalogServer} << 'END_SSH'
set -x
targetPath=./cs677/lab2/src
cd ${targetPath}
cat catalog.pid > kill
rm catalog.pid
END_SSH

# deploy order server
ssh ${username}@${orderServer} << 'END_SSH'
set -x
targetPath=./cs677/lab2/src
cd ${targetPath}
cat order.pid > kill
rm order.pid
END_SSH

# initialize client
ssh ${username}@${clientServer} << 'END_SSH'
set -x
targetPath=./cs677/lab2/src
cd ${targetPath}
cat client.pid > kill
rm client.pid
END_SSH