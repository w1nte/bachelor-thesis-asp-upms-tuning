#!/usr/bin/env bash

EXPERIMENT=$1

scp -r tucluster:~/cluster-experiments/$EXPERIMENT/output ./experiments/$EXPERIMENT
