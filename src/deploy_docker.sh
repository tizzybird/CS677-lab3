#!/bin/bash
# build docker images of each component
IMG_NAME="lab3_img:v1"
CMD=docker.exe
# type "./deploy_docker.sh build" if you haven't build below docker images
if [ $# == 1 ];
then
    if [ $1 == "build" ];
    then
        echo "=================================================================="
        echo "=================== Building Image ======================"
        echo "=================================================================="
        $CMD build -t $IMG_NAME . --no-cache
    fi
fi
# initialize containers
echo "=================================================================="
echo "=================== Initializing Containers ======================"
echo "=================================================================="
$CMD run --net=host -w /app -itd $IMG_NAME python frontend/frontend.py
$CMD run --net=host -w /app -itd $IMG_NAME python catalog/catalog_server.py 0
$CMD run --net=host -w /app -itd $IMG_NAME python catalog/catalog_server.py 1
$CMD run --net=host -w /app -itd $IMG_NAME python order/lock_server.py 
$CMD run --net=host -w /app -itd $IMG_NAME python order/order_server.py 0
$CMD run --net=host -w /app -itd $IMG_NAME python order/order_server.py 1
# initialize client
$CMD run --net=host -w /app -itd $IMG_NAME python client.py