#!/bin/bash

#test /dank coffee

curl -X POST -d @testmessage.txt http://localhost:8080 --header "Content-Type:application/json"
echo

imgur_id="676ec4b5cd4739e"
imgur_secret="b0cfd7e695ab47ae34974408fde67d4fb5e0ebdb"
goog_key="AIzaSyAWaPsdfQTj8zNH9nkJOe_eQV9mhccoAcA"
python hipchat.py
