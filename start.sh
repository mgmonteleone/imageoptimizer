docker stop imageoptimizer
docker rm imageoptimizer
docker run -d -p 5003:5000 -e mydockerhost=`hostname -f` --restart=on-failure:10 --cpu= 0,1 --name imageoptimizer dkrs.co/imageoptimizer
