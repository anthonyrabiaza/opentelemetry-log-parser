#!/bin/bash
nohup /usr/bin/python3 -u ${PWD}/main.py -background >>${PWD}/otel-log-parser.log 2>${PWD}/otel-log-parser.log &