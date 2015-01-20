docker stop imageoptimizer
docker rm imageoptimizer
docker run -d -p 5003:5000 -e mydockerhost=`hostname -f` --restart=always --name imageoptimizer dkrs.co/imageoptimizer
