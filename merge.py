import sys
import os
import glob

"""
Merge all result from job R (phase1) to a single fasta.

param:
R: job name
OUT: output filename
"""

R = int(sys.argv[1])

OUT = open("%d.phase1.fa" % R, "w")

for f in glob.glob("%d.*.phase1.fa.aaa" % R):
    f = f[:-4]
    print f
    OUT.write(">%s\n" % (f.split('.')[1]))
    for g in sorted(glob.glob("%s.???" % f)):
        fasta = open(g).read()[:-1]
        OUT.write("%s" % fasta)
    OUT.write("\n")

OUT.close()

os.system("samtools faidx %d.phase1.fa" % R)
