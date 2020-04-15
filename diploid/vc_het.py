import os, sys
import logging
logging.getLogger('tensorflow').disabled = True
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OMP_THREAD_LIMIT'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import parse_pileup
import tensorflow as tf
import numpy as np
import keras

time_steps = 100
feat_size = 250
n_class = 6

def load_one(args):
    raw = parse_pileup.gen_phase1(*args)
    X = np.reshape(raw, (-1, time_steps, feat_size))
    print X.shape
    return X

def main():
    THRESHOLD = 0.04
    FN = [] #[63244, 70980]
    #sys.argv: model, round, ctg, output name, begin, end
    sys.stderr.write("Predicting , data = %s\n" % sys.argv[2:])
    args = sys.argv[2].split(' ')
    ST = int(args[3])
    CHR = args[1]
    REF = "".join(os.popen("samtools faidx 0.fa %s:%s-%s" % (args[1],args[3],args[4])).read().splitlines()[1:])
    REF = np.array(map(lambda x: "ACGTN!".find(x), REF))

    model = keras.models.load_model(sys.argv[1])
    session_conf = tf.ConfigProto( intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
    sess = tf.Session(config=session_conf)

    OUT = open("HET.%s.%s.phase1.vcf.%s" % (args[0], args[1], args[2]), "w")
    X = load_one([args[1], int(args[3]), int(args[4]), args[0] + ".bam"])
    #OUT.write(">%s\nN" % fn.split('.')[-2])
    Xs = np.vsplit(X,range(1000,X.shape[0],1000))
    for X in Xs:
        y0 = model.predict_on_batch(X)
        X = np.reshape(X, (-1,feat_size))
        y0 = np.reshape(y0,(-1,n_class))
        y0_class = y0.argmax(axis=-1)
        second_maxi = y0.argsort(axis = -1)[:, -2]
        second = np.sort(y0, axis = -1)[:, -2]

        Y = REF[:100000]
        REF = REF[100000:]

        Y = Y[:y0_class.shape[0]]
        var = Y - y0_class
        var_idx = np.where(var != 0) [0]
        # argmax is different from REF
        het_idx = np.intersect1d(np.where(second > THRESHOLD)[0], np.where(second_maxi != 4)[0], assume_unique = True)
        # second max > Threshold and is not DEL
        var_idx = np.union1d(var_idx, het_idx)

        ref_not_N = np.where(Y < 4)[0]
        alt_not_N = np.where(y0_class < 4)[0]
        keep_idx = np.intersect1d(ref_not_N, alt_not_N, assume_unique = True)

        snp_idx = np.intersect1d(keep_idx, var_idx, assume_unique = True)
        for ii in snp_idx:
            #print ii+ST, "REF", Y[ii], "ALT", y0_class[ii], y0[ii][y0_class[ii]], "second best", second_maxi[ii], second[ii]
            vcf_pos = ii + ST
            vcf_alt = "ACGTN"[np.asscalar(y0_class[ii] if y0_class[ii] != Y[ii] else second_maxi[ii])]
            vcf_ref = "ACGTN"[np.asscalar(Y[ii])]
            #vcf_gt = 1 if np.asscalar(max(y0[ii][:-1])) > .96 else 0
            vcf_gt = 1 if y0[ii][y0_class[ii]]> 1 - THRESHOLD else 0

            "20      278515  rs2223665       T       C       50      PASS    .       GT:DP:ADALL:AD:GQ:IGT:IPS:PS    1|1:444:0,196:41,237:99:1/1:.:PATMAT"
            OUT.write("%s\t%d\t.\t%s\t%s\t.\tPASS\t.\tGT\t%d/1\n" % (CHR, vcf_pos, vcf_ref, vcf_alt, vcf_gt))
            #print CHR, vcf_pos, vcf_alt, vcf_ref, "confidence", max(y0[ii][:-1]), y0[ii][:-1]
        #print snp_idx 
        #print snp_idx.shape

        for fn in FN:
            ii = fn - ST
            if ii > 0:
                vcf_pos = ii + ST
                vcf_alt = "ACGTN"[np.asscalar(y0_class[ii])]
                vcf_ref = "ACGTN"[np.asscalar(Y[ii])]
                vcf_gt = 1 if np.asscalar(max(y0[ii][:-1])) > .96 else 0
                print "FN!!", vcf_pos, vcf_alt, vcf_ref, "confidence", max(y0[ii][:-1]), y0[ii][:-1]

        ST += 100000
    
    #OUT.write("\n")
    OUT.close()


if __name__ == "__main__":
    main()
