#!/bin/bash
curl -X POST -d @testmessage.txt http://localhost:8080 --header "Content-Type:application/json"
