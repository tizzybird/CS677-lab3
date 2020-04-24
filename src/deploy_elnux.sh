#!/bin/bash
. elnux_credentials.sh

# deploy frontend server
ssh ${Username}@${FrontendServer} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
nohup python3 frontend/frontend.py > frontend_output.txt 2>&1 &
echo $! > frontend.pid
echo "Front End PID: $(cat frontend.pid)"
END_SSH

# deploy catalog server 1
ssh ${Username}@${CatalogServer1} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
nohup python3 catalog/catalog_server.py 0 > catalog0_output.txt 2>&1 &
echo $! > catalog0.pid
echo "Catalog1 PID: $(cat catalog0.pid)"
END_SSH

# deploy catalog server 2
ssh ${Username}@${CatalogServer2} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
nohup python3 catalog/catalog_server.py 1 > catalog1_output.txt 2>&1 &
echo $! > catalog1.pid
echo "Catalog2 PID: $(cat catalog1.pid)"
END_SSH

# deploy lock server
ssh ${Username}@${LockServer} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
nohup python3 order/lock_server.py > lock_output.txt 2>&1 &
echo $! > lock.pid
echo "Lock Server PID: $(cat lock.pid)"
END_SSH

# deploy order server1
ssh ${Username}@${OrderServer1} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
nohup python3 order/order_server.py 0 > order0_output.txt 2>&1 &
echo $! > order0.pid
echo "Order1 Server PID: $(cat order0.pid)"
END_SSH

# deploy order server2
ssh ${Username}@${OrderServer2} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
nohup python3 order/order_server.py 1 > order1_output.txt 2>&1 &
echo $! > order1.pid
echo "Order2 Server PID: $(cat order1.pid)"
END_SSH

# initialize client
ssh ${Username}@${ClientServer} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
nohup python3 client.py > client_output.txt 2>&1 &
echo $! > client.pid
echo "Client PID: $(cat client.pid)"
END_SSH