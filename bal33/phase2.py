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
feat_size = 550
n_class = 6

def load_one(args):
    raw = parse_pileup.gen_phase2(*args)
    X = np.reshape(raw, (-1, time_steps, feat_size))
    return X

def main():
    #sys.argv: model, "round, ctg, output name, begin, end"
    model = keras.models.load_model(sys.argv[1])
    sys.stderr.write("Phase 2 with param %s\n" % sys.argv[2:])
    args = sys.argv[2].split(' ')
    session_conf = tf.ConfigProto( intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
    sess = tf.Session(config=session_conf)
    
    X = load_one([args[1], int(args[3]), int(args[4]), args[0] + ".bam"])
    Xs = np.vsplit(X,range(1000,X.shape[0],1000))
    offset = 0
    OUT = open("%s.%s.ins.list.%s" % (args[0], args[1], args[2]), "w")
    for X in Xs:
        y1 = model.predict_on_batch(X)
        y1 = np.reshape(y1,(-1,n_class))
        y1_class = y1.argmax(axis=-1)
        keep_idx = np.where(y1_class != 0)[0]
        for idx in keep_idx: OUT.write("%d,%d\n" % (offset+idx,y1_class[idx]))
        offset += 100000
    OUT.close()

if __name__ == "__main__":
    main()
