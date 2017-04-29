#启动代理
python /root/down_load/stratum-mining-proxy/mining_proxy.py -pa scrypt -o coinotron.com -p 3334
./minerd -a scrypt -x http:://127.0.0.1:3334 -u buring -p xiao11lang 

#不启用代理
#./minerd -a scrypt -o stratum+tcp://coinotron.com:3334 --userpass=buring:xiao11lang 

