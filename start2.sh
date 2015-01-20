docker stop imageoptimizer-1
docker rm imageoptimizer-1
docker run -d -p 5003:5000 -e mydockerhost=`hostname -f` --restart=always --name imageoptimizer-1 dkrs.co/imageoptimizer

docker stop imageoptimizer-2
docker rm imageoptimizer-2
docker run -d -p 5004:5000 -e mydockerhost=`hostname -f` --restart=always --name imageoptimizer-2 dkrs.co/imageoptimizer
