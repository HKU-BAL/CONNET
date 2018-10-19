#!/bin/bash

#if [ -s "/nas3/yfzhang2/CY3/vcfs/$1.$2.recode.vcf" ]
#then
#echo "vcf $1.$2 already exists"
#else
#vcftools --chr $1 --from-bp ${2}000000 --to-bp ${2}999999 --gzvcf /nas3/yfzhang2/CY3/true.vcf.gz --recode --out /nas3/yfzhang2/CY3/vcfs/$1.$2 
#fi
a="/bal1-1/rbluo/Clairvoyante/data/ont-hg19-ngmlr-v3/na12878_ont_rel5_rel3and4_ngmlr-0.2.6_mapped.bam"
samtools mpileup $3 -r $1:${2}000000-${2}999999 -Q0 -B -aa | /nas3/yfzhang2/CY3/gen > /nas3/yfzhang2/CY3/tensors/$1.$2.in
