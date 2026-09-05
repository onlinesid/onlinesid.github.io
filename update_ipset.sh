#!/bin/bash

python3 add_ip_network.py --file ipset/ipset.zone
python3 add_ip_network.py --ipv6 --prefix 32 --file ipset/ipset6.zone