#!/usr/bin/env bash
docker stop imageoptimizer
docker rm imageoptimizer
docker run -d -p 5003:5000 -e mydockerhost=`hostname -f` --restart=on-failure:10  --dns dkr4.aut-aut.rocks --name imageoptimizer dkrs.co/imageoptimizer
