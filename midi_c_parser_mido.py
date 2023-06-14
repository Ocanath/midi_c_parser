from mido import MidiFile
import numpy as np
import matplotlib.pyplot as plt
from wav import to_wav

bps = 120

def get_note_from_idx(idx):
	note = int(np.mod(idx,12))
	octave = int(np.floor(idx/12))
	return note,octave

"""
	note is in half steps from C0, where each step is a half step through an entire octave.
	so c, c#, d, d#
	taken from tone.c. modified to remove octave as an argument
"""
def get_note_freq(step):
	base = 1.05946309
	exp = 1.0
	for i in range(0,step):
		exp = base*exp
	return 16.35*exp

note_lookup = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


mid = MidiFile('ChickenFried.mid')
# mid = MidiFile('Bass_sample.mid')
print(mid.ticks_per_beat)

notelist = []
for i, track in enumerate(mid.tracks):
	print("Track "+str(i), str(track.name))
	for  msg in track:
		if(msg.is_meta == 0):
			# print(msg)
			pass
	
trackidx = 1
track = mid.tracks[trackidx]
print('Track {}: {}'.format(trackidx, track.name))


time = 0
notelist = []
for i, msg in enumerate(track):
	if("note_on" in str(msg)):
		time = time + msg.time
		if(msg.velocity > 0):
			note,octave = get_note_from_idx(msg.note)
			for j in range(i,len(track)):
				if(track[j].is_meta == 0 and (("note_on" in str(track[j])) or ("note_off" in str(track[j]))) ):
					if(track[j].note == msg.note and ( (("note_on" in str(track[j])) and track[j].velocity == 0) or ("note_off" in str(track[j])) )  ):
						notelist.append([msg.note, time, time+track[j].time])
						print(note_lookup[note]+str(octave), "(" + str(note+12*octave) + ")", "start time = ", time, "end time = ", time+track[j].time, "duration = ", track[j].time, msg.velocity)
						break
		
				
Fs = 48e3
endtick = notelist[len(notelist)-1][2]
endtime = endtick/mid.ticks_per_beat
t = np.linspace(0, endtime, int(endtime*Fs))
output = 0*t

print(endtime)


for tidx in range(0,len(t)):
	time = t[tidx]
	for i in range(0,len(notelist)):
		st = notelist[i][1]/mid.ticks_per_beat
		et = notelist[i][2]/mid.ticks_per_beat
		if(time > st and  time < et):
			output[tidx]+=np.sin(2*np.pi*time*get_note_freq(notelist[i][0]))

to_wav(t,output,'nylon_chicken.wav')

fig,ax = plt.subplots()
ax.plot(t,output)
plt.show()