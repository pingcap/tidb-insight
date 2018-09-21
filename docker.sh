#!/bin/sh

SUDO=""
PWD=`pwd`

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root, it will try 'sudo' when needed."
   SUDO="sudo"
fi

case $1 in
    start)
        echo "Starting containers..."
        cd $PWD/tools/docker
        if [ ! -f prometheus.yml ]; then
            # use the template as default config, to start Prometheus process
            cp configs/prometheus.yml.template prometheus.yml
        fi
        $SUDO docker-compose up -d

        # if datasource "test-cluster" doesn't exist, this is a new Grafana instahce,
        # and we'll going to initial its configs
        if [[ `curl -s -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Basic YWRtaW46YWRtaW4=" "http://localhost:3000/api/datasources/id/test-cluster"` = *"Data source not found"* ]]; then
            # add datasource
            curl -s -H "Accept: application/json" -H "Content-Type: application/json" \
                -H "Authorization: Basic YWRtaW46YWRtaW4=" -XPOST \
                -d '{
                        "name": "test-cluster",
                        "type": "prometheus",
                        "access": "proxy",
                        "url": "http://prometheus:9090",
                        "basicAuth": false,
                        "withCredentials": false,
                        "isDefault": true,
                        "jsonData": {
                            "httpMethod": "GET",
                            "keepCookies": [

                            ]
                        },
                        "readOnly": true
                    }' \
                "http://localhost:3000/api/datasources"
            # import dashboards
            cd configs
            ./grafana-config-copy.py
        fi

        cd $PWD
        ;;
    reload)
        echo "Reloading Prometheus..."
        $SUDO docker exec prometheus kill -HUP 1
        ;;
    stop)
        echo "Stopping containers..."
        cd $PWD/tools/docker
        $SUDO docker-compose down
        cd $PWD
        ;;
    clean)
        echo "Stopping containers..."
        cd $PWD/tools/docker
        $SUDO docker-compose down
        echo "Deleting all containers and data..."
        $SUDO rm -rf data
        ;;
    *)
        echo "Setting InfluxDB database name to $1..."
        sed "s/<DBNAME>/$1/g" $PWD/tools/docker/configs/prometheus.yml.template \
            > $PWD/tools/docker/prometheus.yml
        $SUDO docker exec prometheus kill -HUP 1
        ;;
esac

exit 0;

