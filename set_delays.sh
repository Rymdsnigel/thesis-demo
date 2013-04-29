
tc qdisc add dev lo handle 1: root htb

tc class add dev lo parent 1: classid 1:1 htb rate 1000Mbps

tc class add dev lo parent 1:1 classid 1:11 htb rate 100Mbps
tc class add dev lo parent 1:1 classid 1:12 htb rate 100Mbps
tc class add dev lo parent 1:1 classid 1:13 htb rate 100Mbps

tc qdisc add dev lo parent 1:11 handle 10: netem delay 50ms
tc qdisc add dev lo parent 1:12 handle 20: netem delay 20ms
tc qdisc add dev lo parent 1:13 handle 30: netem delay 0ms

tc filter add dev lo protocol ip prio 1 u32 match ip dport 10001 0xffff flowid 1:11
tc filter add dev lo protocol ip prio 1 u32 match ip dport 10002 0xffff flowid 1:12
tc filter add dev lo protocol ip prio 1 u32 match ip dport 10003 0xffff flowid 1:13

tc filter add dev lo protocol ip prio 1 u32 match ip sport 10001 0xffff flowid 1:11
tc filter add dev lo protocol ip prio 1 u32 match ip sport 10002 0xffff flowid 1:12
tc filter add dev lo protocol ip prio 1 u32 match ip sport 10003 0xffff flowid 1:13