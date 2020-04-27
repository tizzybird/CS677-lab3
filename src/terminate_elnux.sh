#!/bin/bash
. elnux_credentials.sh

# terminate client
ssh ${Username}@${ClientServer} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd $TargetPath
cat client.pid > kill
rm client.pid
END_SSH

# terminate frontend server
ssh ${Username}@${FrontendServer} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
cat frontend.pid > kill
rm frontend.pid
END_SSH

# terminate catalog server 1
ssh ${Username}@${CatalogServer1} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
cat catalog0.pid > kill
rm catalog0.pid
END_SSH

# terminate catalog server 2
ssh ${Username}@${CatalogServer2} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
cat catalog1.pid > kill
rm catalog1.pid
END_SSH

# terminate order server 1
ssh ${Username}@${OrderServer1} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
cat order0.pid > kill
rm order0.pid
END_SSH

# terminate order server 2
ssh ${Username}@${OrderServer2} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
cat order1.pid > kill
rm order1.pid
END_SSH

# terminate lock server
ssh ${Username}@${LockServer} TargetPath=$TargetPath 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
cat lock.pid > kill
rm lock.pid
END_SSH
