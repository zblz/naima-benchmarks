#!/bin/bash

export PATH=/home/vzabalza/anaconda/bin:$PATH
cd /home/vzabalza/src/naima-benchmarks

asv run NEW
git add results/draco
git commit -am 'new results'
git push
asv gh-pages

