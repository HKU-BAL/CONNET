#!/bin/bash

T=24
BATCH_SIZE=8000000
model1=$1
model2=$2
input=$3
asm=$4
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
mkdir -p diploid_result
cd diploid_result
<<<<<<< HEAD
ln -s $asm 0.fa
minimap2 -a -x map-ont 0.fa $input -t$T | samtools sort -@$T -o 0.bam
samtools index 0.bam -@$T 
samtools faidx 0.fa
python $DIR/split_job.py 0 $BATCH_SIZE

parallel -j1 python $DIR/diploid/vc_het.py $model1 :::: 0.parallel
=======
ln -s ../$asm 0.fa
minimap2 -a -x map-ont 0.fa ../$input -t$T | samtools sort -@$T -o 0.bam
samtools index 0.bam -@$T 
samtools faidx 0.fa
python2 $DIR/split_job.py 0 $BATCH_SIZE

parallel -j1 python2 $DIR/vc_het.py ../$model1 :::: 0.parallel
>>>>>>> 9eeb8bd4bdf398bc0b808b88a0a3abdf9e654216
cat $DIR/diploid/header HET.*.vcf.??? | vcf-sort > unphased.vcf
bgzip unphased.vcf
tabix -p vcf unphased.vcf.gz

whatshap phase --reference 0.fa -o phased.vcf unphased.vcf.gz 0.bam --ignore-read-groups
bgzip phased.vcf
tabix -p vcf phased.vcf.gz
whatshap haplotag -o phased.bam --reference 0.fa phased.vcf.gz 0.bam --ignore-read-groups
samtools index -@$T phased.bam
samtools view -@$T -h phased.bam  | grep -v "HP:i:1" | samtools view -@$T -b -o HP2.bam
samtools view -@$T -h phased.bam  | grep -v "HP:i:2" | samtools view -@$T -b -o HP1.bam
samtools index -@$T HP1.bam
samtools index -@$T HP2.bam


mkdir -p HP1
cd HP1
ln -s ../0.bam .
ln -s ../0.bam.bai .
ln -s ../0.parallel .
samtools fastq 0.bam -0 input.fa
<<<<<<< HEAD
python $DIR/connet.py $model1 $model2
=======
python2 $DIR/connet.py ../$model1 ../$model2
>>>>>>> 9eeb8bd4bdf398bc0b808b88a0a3abdf9e654216

cd ..
mkdir -p HP2
cd HP2
ln -s ../0.bam .
ln -s ../0.bam.bai .
ln -s ../0.parallel .
samtools fastq 0.bam -0 input.fa
<<<<<<< HEAD
python $DIR/connet.py $model1 $model2
=======
python2 $DIR/connet.py $model1 $model2
>>>>>>> 9eeb8bd4bdf398bc0b808b88a0a3abdf9e654216

cp HP1/2.fa diploid_consensus_1.fa
cp HP2/2.fa diploid_consensus_2.fa
echo "Result at diploid_consensus_?.fa"
