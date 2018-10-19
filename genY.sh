#!/bin/bash

samtools mpileup $3 -r $1:${2}000000-${2}999999 -Q0 -B -aa | /nas3/yfzhang2/CY3/gen > /nas3/yfzhang2/CY3/tensors/$1.$2.out
