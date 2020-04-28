#!/bin/bash
. elnux_credentials.sh

# terminate client
ssh ${Username}@${ClientServer} TargetPath=$TargetPath Username=${Username} 'bash -s' << 'END_SSH'
set -x
cd $TargetPath
rm client.pid
pkill -u $Username
END_SSH

# terminate frontend server
ssh ${Username}@${FrontendServer} TargetPath=$TargetPath Username=${Username} 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
rm frontend.pid
pkill -u $Username
END_SSH

# terminate catalog server 1
ssh ${Username}@${CatalogServer1} TargetPath=$TargetPath Username=${Username} 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
rm catalog0.pid
pkill -u $Username
END_SSH

# terminate catalog server 2
ssh ${Username}@${CatalogServer2} TargetPath=$TargetPath Username=${Username} 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
rm catalog1.pid
pkill -u $Username
END_SSH

# terminate order server 1
ssh ${Username}@${OrderServer1} TargetPath=$TargetPath Username=${Username} 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
rm order0.pid
pkill -u $Username
END_SSH

# terminate order server 2
ssh ${Username}@${OrderServer2} TargetPath=$TargetPath Username=${Username} 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
rm order1.pid
pkill -u $Username
END_SSH

# terminate lock server
ssh ${Username}@${LockServer} TargetPath=$TargetPath Username=${Username} 'bash -s' << 'END_SSH'
set -x
cd ${TargetPath}
rm lock.pid
pkill -u $Username
END_SSH
