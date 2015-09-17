#!/bin/bash

dirname=$(dirname $0)
exec > $dirname/lastcron.log 2>&1

date

# test if root cron jobs are being run, exit
if [ "$(pgrep run-parts)" != "" ]; then
    echo "Cron jobs being run, exiting!"
    exit 1
fi

export PATH=/home/vzabalza/anaconda/bin:$PATH
cd /home/vzabalza/src/naima-benchmarks

asv run NEW
git add results/draco
git commit -am 'new results'
git push
asv gh-pages

