import numpy as np
from scipy.io.wavfile import write


def to_wav(time, data, filename):
	print('creating file', filename)
	Fs = int(np.round(len(time)/(np.max(time) - np.min(time))))	#ie 1000 samples in 30e-3 seconds
	print('Fs =',int(Fs))
	amp_scale = (2**15-1) / max(np.abs(data))	#set it to max range, so maxv scaling in tina works
	dataout = (data*amp_scale)
	write(filename, Fs, dataout.astype(np.int16))
	