#!/bin/sh

DOCKER="docker"
PWD=`pwd`

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root, it will try 'sudo' when needed."
   DOCKER="sudo docker"
fi

case $1 in
    start)
        echo "Starting containers..."
        cd $PWD/tools/docker
        if [ ! -f prometheus.yml ]; then
            # use the template as default config, to start Prometheus process
            cp prometheus.yml.template prometheus.yml
        fi
        $DOCKER-compose up -d
        cd $PWD
        ;;
    reload)
        echo "Reloading Prometheus..."
        sudo $DOCKER exec prometheus kill -HUP 1
        ;;
    stop)
        echo "Stopping containers..."
        cd $PWD/tools/docker
        $DOCKER-compose down
        cd $PWD
        ;;
    *)
        echo "Setting InfluxDB database name to $1..."
        sed "s/<DBNAME>/$1/g" $PWD/tools/docker/prometheus.yml.template \
            > $PWD/tools/docker/prometheus.yml
        ;;
esac

exit 0;

