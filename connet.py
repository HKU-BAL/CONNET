import datetime
import os
import sys

now = datetime.datetime.now()

#DIR = os.environ['CONNETROOT']
DIR ="/mnt/bal20/yfzhang2/CONNET/"
H = os.popen("hostname").read().strip()
#H = "."
T = 48
N_ITER = 2
MODEL1 = sys.argv[1]
MODEL2 = sys.argv[2]
RAW_READ = "../input.fa"
DRAFT_ASM = "../0.fa"

def exe(cmd):
    os.system(cmd)
    return
    "/usr/bin/time -v bash -c ''"

def main():
    os.system("ln -s %s ." % RAW_READ)
    os.system("ln -s %s ." % DRAFT_ASM)
    for R in range(0, N_ITER):
        print "[%s] Round %d begins" % (now, R)
        exe("minimap2 -a -x map-ont %d.fa input.fa -t %d | samtools sort -@ %d -o %d.bam && samtools index -@ %d %d.bam" % (R, T, T, R, T, R))

        exe("python %s/split_job.py %d 8000000" % (DIR,R))
        exe("parallel -j%d taskset -c {%%} python %s/%s/phase1.py %s {} :::: %d.parallel " % (T, DIR, H, MODEL1, R))
        exe("python %s/merge.py %d" % (DIR,R))

        exe("minimap2 -a -x map-ont %d.phase1.fa input.fa -t %d | samtools sort -@ %d -o %d.phase1.bam && samtools index -@ %d %d.phase1.bam" % (R, T, T, R, T, R))

        exe("python %s/split_job.py %d.phase1 3500000" % (DIR,R))
        exe("parallel -j%d taskset -c {%%} python %s/%s/phase2.py %s {} :::: %d.phase1.parallel " % (T, DIR, H, MODEL2, R))
        exe("parallel python %s/apply_ins.py {.} 3500000 ::: %d.phase1.*.ins.list.aaa" % (DIR,R))
        exe("cat %d.*.fa > %d.fa" % (R+1, R+1))

    print "Result is at %d.fa" % N_ITER

if __name__ == "__main__":
    main()
