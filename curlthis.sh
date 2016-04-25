#!/bin/bash

#for i in ./test/* ; do
for i in $@ ; do
  curl -X POST -d @$i http://localhost:8080 --header "Content-Type:application/json"
  echo
done
