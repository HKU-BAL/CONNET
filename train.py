import glob
import random
import tensorflow as tf
import numpy as np
import pandas as pd
import os
import sys

import keras
from keras.callbacks import ModelCheckpoint
import keras.backend as K
from keras.models import Model
from keras.layers import Input, merge
from keras.layers.core import Lambda


batch_size = 2500
time_steps = 100
feat_size = 5

lstm_size = 200

from tensorflow.python.client import device_lib

def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos if x.device_type == 'GPU']

def load(fn):
	raw = pd.read_csv(fn, header = None, usecols = range(1001)).values
	np.random.shuffle(raw)


	T,V = np.vsplit(raw,[int(raw.shape[0] * 0.9)])
	Vx, Vy, _ = np.hsplit(V, [500,1000])
	Tx, Ty, _ = np.hsplit(T, [500,1000])

	V2 = np.ones(Vy.shape) * 2.0
	T2 = np.ones(Ty.shape) * 2.0
	Vy = Vy / V2
	Ty = Ty / T2

	Vx = np.reshape(Vx, (-1, time_steps, feat_size))
	Vy = np.reshape(Vy, (-1, time_steps, feat_size))
	Tx = np.reshape(Tx, (-1, time_steps, feat_size))
	Ty = np.reshape(Ty, (-1, time_steps, feat_size))

	return Tx, Ty, Vx, Vy

def main():
	print get_available_gpus()
	print "Hi I am training, data =", sys.argv[1]
	Tx, Ty, Vx, Vy = load(sys.argv[1])
	print "train size", Tx.shape[0]
	print "valid size", Vx.shape[0]

	model = keras.Sequential()
	model.add(keras.layers.Bidirectional(keras.layers.LSTM(lstm_size, return_sequences=True), input_shape=(time_steps, feat_size)))
	#model.add(keras.layers.Bidirectional(keras.layers.LSTM(lstm_size, return_sequences=True)))
	#model.add(keras.layers.LSTM(lstm_size, return_sequences=True))
	#model.add(keras.layers.Dense(640,activation='relu'))
	model.add(keras.layers.Dense(feat_size,activation='softmax'))

	#model = keras.utils.multi_gpu_model(model, gpus=2, cpu_merge=True, cpu_relocation=False) # slower !
	#model.compile(optimizer = keras.optimizers.Adam(lr=1e-3), loss='categorical_crossentropy', metrics=['accuracy'])
	model.compile(optimizer = keras.optimizers.Adam(lr=1e-3), loss='kullback_leibler_divergence', metrics=['accuracy'])

	print "model compiled."
	
	filepath="model-{epoch:04d}-{val_acc:.6f}.hdf5"
	checkpointer = ModelCheckpoint(filepath, verbose=1, save_best_only=True, monitor = "val_acc")

        model.fit(x=Tx, y=Ty, 
                batch_size = batch_size, 
                epochs = 100, 
                callbacks = [checkpointer],
                validation_data = (Vx,Vy),
                shuffle = True
        )

	print "Model fit success"

if __name__ == "__main__":
    main()
