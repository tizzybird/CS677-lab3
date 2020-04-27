CMD=docker.exe
$CMD stop $($CMD ps -a -q)
$CMD rm $($CMD ps -a -q)