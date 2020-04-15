import datetime
import sys
import os

now = datetime.datetime.now()

DIR = os.path.dirname(__file__)
MODEL1 = sys.argv[1]
MODEL2 = sys.argv[2]
RAW_READ = "../input.fa" if len(sys.argv) <= 3 else sys.argv[3]
DRAFT_ASM = "../0.fa" if len(sys.argv) <= 4 else sys.argv[4]

T = 24
N_ITER = 2
PHASE1_BATCHSIZE = 8000000
PHASE2_BATCHSIZE = 3500000

def exe(cmd):
    os.system(cmd)
    return
    "/usr/bin/time -v bash -c ''"

def main():
    os.system("ln -s %s input.fa" % RAW_READ)
    os.system("ln -s %s 0.fa" % DRAFT_ASM)
    for R in range(0, N_ITER):
        print "[%s] Round %d begins" % (now, R)
        exe("minimap2 -a -x map-ont %d.fa input.fa -t %d | samtools sort -@ %d -o %d.bam && samtools index -@ %d %d.bam" % (R, T, T, R, T, R))

        exe("python %s/split_job.py %d %d" % (DIR,R, PHASE1_BATCHSIZE))
        exe("parallel -j%d taskset -c {%%} python %s/%s/phase1.py %s {} :::: %d.parallel " % (T, DIR, "", MODEL1, R))
        exe("python %s/merge.py %d" % (DIR,R))

        exe("minimap2 -a -x map-ont %d.phase1.fa input.fa -t %d | samtools sort -@ %d -o %d.phase1.bam && samtools index -@ %d %d.phase1.bam" % (R, T, T, R, T, R))

        exe("python %s/split_job.py %d.phase1 %d" % (DIR,R, PHASE2_BATCHSIZE))
        exe("parallel -j%d taskset -c {%%} python %s/%s/phase2.py %s {} :::: %d.phase1.parallel " % (T, DIR, "", MODEL2, R))
        exe("parallel python %s/apply_ins.py {.} %d ::: %d.phase1.*.ins.list.aaa" % (DIR,PHASE2_BATCHSIZE, R))
        exe("cat %d.*.fa > %d.fa" % (R+1, R+1))

    print "Result is at %d.fa" % N_ITER

if __name__ == "__main__":
    main()
