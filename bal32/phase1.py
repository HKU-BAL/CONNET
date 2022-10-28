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
    return X

def main():
    #sys.argv: model, "round, ctg, output name, begin, end"
    model = keras.models.load_model(sys.argv[1])
    sys.stderr.write("Phase 1 with param %s\n" % sys.argv[2:])
    args = sys.argv[2].split(' ')
    session_conf = tf.ConfigProto( intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
    sess = tf.Session(config=session_conf)

    OUT = open("%s.%s.phase1.fa.%s" % (args[0], args[1], args[2]), "w")
    X = load_one([args[1], int(args[3]), int(args[4]), args[0] + ".bam"])
    Xs = np.vsplit(X,range(1000,X.shape[0],1000))
    for X in Xs:
        y0 = model.predict_on_batch(X)
        X = np.reshape(X, (-1,feat_size))
        y0 = np.reshape(y0,(-1,n_class))
        y0_class = y0.argmax(axis=-1)
        keep_idx_x = np.where(np.sum(X, axis = 1) >= 4)[0]
        keep_idx_y = np.where(y0_class < 4)[0]
        keep_idx = np.intersect1d(keep_idx_x, keep_idx_y, assume_unique = True)
        y0_class = y0_class[keep_idx]
        ret = "".join(map(lambda x:"ACGT"[x], y0_class))
        OUT.write("%s" % ret[1:-1])
    OUT.write("\n")
    OUT.close()

if __name__ == "__main__":
    main()
