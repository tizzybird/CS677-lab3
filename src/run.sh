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
nohup python3 frontend.py > frontend_output.txt 2>&1 &
echo $! > frontend.pid
echo "Front End PID: $(cat frontend.pid)"
END_SSH

# deploy catalog server
ssh ${username}@${catalogServer} << 'END_SSH'
set -x
targetPath=./cs677/lab2/src
cd ${targetPath}
nohup python3 catalog_server.py catalog.csv > catalog_output.txt 2>&1 &
echo $! > catalog.pid
echo "Catalog PID: $(cat catalog.pid)"
END_SSH

# deploy order server
ssh ${username}@${orderServer} << 'END_SSH'
set -x
targetPath=./cs677/lab2/src
cd ${targetPath}
nohup python3 order_server.py > order_output.txt 2>&1 &
echo $! > order.pid
echo "Order Server PID: $(cat order.pid)"
END_SSH

# initialize client
ssh ${username}@${clientServer} << 'END_SSH'
set -x
targetPath=./cs677/lab2/src
cd ${targetPath}
nohup python3 client.py > client_output.txt 2>&1 &
echo $! > client.pid
echo "Client PID: $(cat client.pid)"
END_SSH