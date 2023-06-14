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
	# base = 1.05946309
	# exp = 1.0
	# for i in range(0,step):
		# exp = base*exp
	# return 16.35*exp
	return 16.35*(1.059463094359)**step

note_lookup = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# mid = MidiFile('ChickenFried.mid')
mid = MidiFile('46and2.mid')
# mid = MidiFile('Bass_sample.mid')
print(mid.ticks_per_beat)

for i, track in enumerate(mid.tracks):
	print("Track "+str(i), str(track.name))
	for  msg in track:
		if(msg.is_meta == 0):
			# print(msg)
			pass
			
notelist = []
tracks = [3]
for trackidx in tracks:	
	
	track = mid.tracks[trackidx]
	print('Track {}: {}'.format(trackidx, track.name))

	time = 0
	for i, msg in enumerate(track):
		if("note_on" in str(msg) or "note_off" in str(msg)):
			time = time + msg.time
			note,octave = get_note_from_idx(msg.note)
			
			on_off = 1
			if(msg.velocity == 0) or ("note_off" in str(msg)):
				on_off = 0
			
			notelist.append([msg.note, time, on_off])
			print(note_lookup[int(np.mod(msg.note,12))]+str(octave), "(" + str(msg.note) + ")", "time = ", time, "velocity: ", msg.velocity)

def retstart(e):
	return e[1]
notelist.sort(key=retstart)
		

Fs = 48e3
endtick = notelist[len(notelist)-1][1]
endtime = endtick/mid.ticks_per_beat
t = np.linspace(0, endtime, int(endtime*Fs))
output = t*0

print(endtime)

notestate = np.zeros(88)
notefreq = np.zeros(88)
for i in range(0,len(notefreq)):
	notefreq[i] = get_note_freq(i)
	
notelist_idx = 0
# min_note = 88
# max_note = 0
for tidx in range(0,len(t)):

	time = t[tidx]
	ts = notelist[notelist_idx][1]/mid.ticks_per_beat
	on_off = notelist[notelist_idx][2]
	note = notelist[notelist_idx][0]
	# if(note > max_note):
		# max_note = note
	# if(note < min_note):
		# min_note = note
		
	if(note > 0 and note < 88):
		if(time >= ts):
			if(on_off):
				notestate[note] = 1
			else:
				notestate[note] = 0
			notelist_idx = notelist_idx + 1
			print("evt "+str(notelist_idx)+" out of "+str(len(notelist)))
	
	for i in range(0,len(notestate)):	#try reducing range...
		if(notestate[i] == 1):
			# freq = get_note_freq(i)
			output[tidx] += np.sin(2*np.pi*time*notefreq[i])
	
# output[output>1] = 1
# output[output<-1] = -1
to_wav(t,output,'48.wav')

fig,ax = plt.subplots()
ax.plot(t,output)
plt.show()