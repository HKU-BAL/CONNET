import os
import sys
import glob

"""
Apply predicted insertions to assembly
"""

def toint(x):
    x = x.lower()
    if x=='a': return 0
    elif x=='c': return 1
    elif x=='g': return 2
    elif x=='t': return 3
    return 4

PREFIX = sys.argv[1][:-9]
R, _,CTG = PREFIX.split('.')
OFFSET = int(sys.argv[2])
offset = 0
REF = os.popen("samtools faidx %s.phase1.fa %s" % (R, CTG)).read().splitlines()[1:]
REF = list("".join(REF))

nr = 0

PILEUP = os.popen("samtools mpileup -r %s -B -q0 -Q0 -aa %s.phase1.bam" % (CTG, R))

RESULT = []

for f in sorted(glob.glob("%s.???" % sys.argv[1])):
    for row in open(f):
        pred_pos, pred_len = map(int, row.split(','))
        pred_pos += 1 + offset
   
        while nr <= pred_pos:
            pileup = next(PILEUP)
            nr += 1

        ins_patterns = []
        ins_lengths = []
        p = pileup.split()[4].split('+')[1:] # pileup cannot start with '+', can safely discard the first chunk
        for pp in p:
            ins_len = ""
            idx = 0
            while pp[idx].isdigit():
                ins_len += pp[idx]
                idx += 1
        
            ins_len = int(ins_len) if ins_len != "" else 0
            ins_lengths.append(ins_len)
            ins_pattern = pp[idx:idx+ins_len]
            ins_patterns.append(ins_pattern)
    
        median_ins_len = sorted(ins_lengths)[len(ins_lengths)/2] if len(ins_lengths) else 0
        if pred_len == 5 and median_ins_len > 5: 
            pred_len = median_ins_len
    
        vote = [[0,0,0,0,0] for _ in range(pred_len)]
        for pattern in ins_patterns:
            for i,ch in enumerate(pattern):
                if i==pred_len: break
                vote[i][toint(ch)] += 1
    
        predicted = "".join([ "ACGTN"[vote[i].index(max(vote[i]))] for i in range(len(vote))])
    
        RESULT.append((pred_pos,predicted))
                
    offset += OFFSET

for i,p in RESULT[::-1]: REF[i] += p

OUT = open("%d.%s.fa" % (int(R)+1, CTG),"w")
OUT.write(">%s\n%s\n" % (CTG, "".join(REF))) 
