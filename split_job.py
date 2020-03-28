import os
import sys
import itertools

"""
Split job into smaller batches,
each batch contains one contig only.

Only supports < 26 ** 3 batches now.

param:

R: job name
BATCH: size in bp, default 8Mbp for phase1, 3.5Mbp for phase2
"""

alphabet = "abcdefghijklmnopqrstuvwxyz"
names = ["".join(x) for x in itertools.product(alphabet, alphabet, alphabet)]

R = sys.argv[1]
BATCH = int(sys.argv[2])

os.system("samtools faidx %s.fa" % R)
faidx = open("%s.fa.fai" % R).read().splitlines()
jobs = []
for row in faidx:
    row = row.split()
    ctg = row[0]
    length = int(row[1])
    begin = 0

    while begin + 100 < length:
        end = min(length, begin + BATCH)
        jobs.append([ctg, begin+1, end, names[begin / BATCH]])
        begin += BATCH

OUT = open("%s.parallel" % R, "w")
for j in jobs:
    OUT.write("%s %s %s %d %d\n" % (R, j[0],j[3],j[1],j[2]))
OUT.close()


