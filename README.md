# CONNET: Accurate Genome Consensus in Assembling Nanopore Sequencing Data via Deep Learning

---

## Introduction

Single-molecule sequencing technologies produce much longer reads compared to next-generation sequencing, greatly improving the contiguity of de novo assembly of genomes. However, the relatively high error rates in long reads make it challenging to obtain high-quality assemblies, and a computationally-intensive consensus step is needed to resolve the discrepancies in the reads. Efficient consensus tools have emerged in the recent past, based on partial-order alignment. In this study, we discovered that the spatial relationship of alignment pileup is crucial to high-quality consensus and developed a deep learning-based consensus tool, CONNET, which outperforms the fastest tools, based on partial-order alignment, in terms of both accuracy and speed. We tested CONNET using a 90x dataset of E. coli and a 37x human dataset. In addition to achieving high-quality consensus results, CONNET is capable of delivering phased diploid genome consensus. Diploid consensus on the above human assembly further reduced 12% of the consensus errors made in the haploid results.

---

## Installation

```bash
# make sure the following tools are installed
samtools 
minimap2
parallel
python

# make sure the following Python packages are installed
tensorflow
keras
numpy

git clone https://github.com/HKU-BAL/CONNET.git
cd CONNET

python setup.py build_ext --inplace
# This will compile a `parse_pileup.so` in current folder.

export CONNET=$PWD/connet.py 
```


---

## Quick demo

* Step 1. Install 
* Step 2. Run

```bash
mkdir ecoli_demo
cd ecoli_demo
python $CONNET ../models/ecoli.model1 ../models/ecoli.model2 ../sample_data/ecoli_raw_reads.fq ../sample_data/ecoli_draft_assembly.fa
```

* Step 3. Result is at `2.fa`

By default, CONNET runs for 2 iterations

Result from iteration 1 is at `1.fa`

---


## Pretrained Models

Included at `models/`

- Trained on _E. coli_: `models/ecoli.*`
- Trained on _H. sapiens_ chromosome 1: `models/human.chr1.*`

N.B. correction phase and recovery phase are trained separately, `*.model1` is trained for correction phase, `*.model2` is trained for recovery phase. They are not compatible and both are necessary.

## General usage

```bash
# haploid consensus
python $CONNET model1 model2 raw_reads.fa draft_assembly.fa

# diploid consensus
# run haploid consensus for at least 1 iteration first
# make sure whatsapp, bgzip, tabix is installed
bash diploid.sh model1 model2 raw_reads.fa haploid_consensus.fa
```

### Notes
CONNET was benchmarked on a 24-core Intel(R) Xeon(R) Silver 4116 CPU @ 2.10GHz workstation
- For machines with limited processors, reduce T (number of thread) in `connet.py`.
- For machines with limited memory, reduce PHASE1_BATCHSIZE, PHASE2_BATCHSIZE (in bp) in `connet.py`.
