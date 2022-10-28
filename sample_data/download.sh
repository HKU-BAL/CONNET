#!/bin/bash
wget https://s3-eu-west-1.amazonaws.com/ont-research/medaka_walkthrough_no_reads.tar.gz -O medaka_walkthrough_no_reads.tar.gz
tar xzf medaka_walkthrough_no_reads.tar.gz
ln -s data/basecalls.fa ecoli_raw_reads.fq
