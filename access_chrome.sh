#!/bin/bash

for i in `seq 0 12`
do
  echo "[$i]" ` date '+%y/%m/%d %H:%M:%S'` "connected."
  open 'https://colab.research.google.com/drive/1zFUaQFGeYpvinUihCAssr_jnKdGWim67?hl=ja#scrollTo=xG9uLRMXovj4'
  sleep 3600
done
