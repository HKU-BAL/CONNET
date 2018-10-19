import tensorflow as tf
import datetime
import numpy as np
import pandas as pd
import os
import sys

os.environ["CUDA_VISIBLE_DEVICES"]="0"

from tensorflow.python.client import device_lib
import keras
from keras.callbacks import ModelCheckpoint
import keras.backend as K
#from keras.layers import *

NPY_SIZE = int(1e6)

time_steps = 100
feat_size = 5


DIR = '/nas3/yfzhang2/CY3/mm2_tensors/'
I = None
O = None

def test_data_generator(what):
	for FIN, FOUT in zip(I,O):
		rawX = pd.read_csv(DIR+FIN, header = None, usecols = range(2500)).values
		rawY = pd.read_csv(DIR+FOUT, header = None, usecols = range(2500)).values
		x = np.reshape(rawX, (-1, time_steps, feat_size))
		y = np.reshape(rawY, (-1, time_steps, feat_size))

		if what=='x': yield x
		elif what=='y': yield y
		else: yield (x,y)


def NOW(msg):
	print "[",msg,"]", datetime.datetime.time(datetime.datetime.now())

def load(fn):
	raw = pd.read_csv(fn, header = None, usecols = range(1001)).values


	X, Y, POS = np.hsplit(raw, [500,1000])

	Y2 = np.ones(Y.shape) * 2.0
	Y = Y / Y2


	X = np.reshape(X, (-1, time_steps, feat_size))
	Y = np.reshape(Y, (-1, time_steps, feat_size))
	return X, Y, POS



def main():
	print get_available_gpus()
	print "Hi I am training, data =", sys.argv[2]
	X,Y,POS = load(sys.argv[2])
	print "data size", X.shape[0]

	model = keras.models.load_model(sys.argv[1])

	print "Model Loaded: ", sys.argv[1]

	MAGIC = open("incorrect_predictions","w")

	np.set_printoptions(precision=3)
	np.set_printoptions(suppress=True)
	if True:
		NOW("before eval")
		print model.evaluate((X,Y))
		NOW("after eval")

	if True:
		NOW("before predict")
		y_prob = model.predict((X,Y))
		y_classes = y_prob.argmax(axis=-1).astype(int).flatten()
		y_classes = np.reshape(y_classes, (-1, NPY_SIZE))
		y_prob = np.reshape(y_prob, (-1, NPY_SIZE, 5))

		#labels = (next(test_data('y')) for _ in range(len(I) * NSPLIT))
		#labels = np.vstack(labels).argmax(axis=-1).astype(int).flatten()


		#labels = np.reshape(labels, (-1, NPY_SIZE))
		NOW("after predict")
		#for i,y,l in zip(I,y_classes, labels):
		for i,y,p in zip(I,y_classes, y_prob):
			l = next(YGEN).argmax(axis=-1).astype(int).flatten()
			xx = next(XGEN2)
			xx = np.reshape(xx, (NPY_SIZE, 5))

			tricon = xx.argmax(axis=-1).astype(int).flatten()
			tricon_wrong = np.nonzero(tricon-l)[0]
			print "tricon have", len(tricon_wrong), "incorrects in this batch", i[:-3]

			wrong = np.nonzero(y - l)[0]
			print "CY3 have", len(wrong), "incorrects in this batch", i[:-3]
			ch, pos, _ = i.split('.')
			pos = int(pos) * int(1e6)
			for ww in wrong: 
				ww = np.asscalar(ww)
				MAGIC.write("%s:%d pred: %c, truth: %c, x: %s, y: %s\n" % (ch, pos+ww, "ACGT$"[y[ww]], "ACGT$"[l[ww]], xx[ww], p[ww]))
			for ww in tricon_wrong: 
				ww = np.asscalar(ww)
				MAGIC.write("TRICON %s:%d pred: %c, truth: %c, x: %s, y: %s\n" % (ch, pos+ww, "ACGT$"[y[ww]], "ACGT$"[l[ww]], xx[ww], p[ww]))
			ret = "".join(["ACGT"[yy] for yy in y if yy!=4])
			OUT = open("predict_%s_%sfa" % (sys.argv[1],i[:-2]),"w")
			OUT.write(">%s:\n%s\n" % (i[:-3],ret))






if __name__ == "__main__":
    main()
