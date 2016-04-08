#!/usr/bin/env bash

# The run script for running the average_degree calculation and running unittests

# I'll execute my programs, with the input directory tweet_input and output the files in the directory tweet_output

python3 src/average_degree.py tweet_input/tweets.txt tweet_output/output.txt

# Not running unittests because each one cannot be executed as an independent unit.

# python3 -m unittest -v src/unittests_average_degree.py