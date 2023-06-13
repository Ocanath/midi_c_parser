from MIDI import *
import numpy as np
import matplotlib.pyplot as plt
from wav import to_wav

c = MIDIFile("Bass_sample.mid")
# c = MIDIFile("ChickenFried.mid")
c.parse()
print(str(c))
print("time quantum is:", c.division)

note_lookup = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

"""
	note is 0-11, where each step is a half step through an entire octave.
	so c, c#, d, d#
	taken from tone.c
"""
def get_note_freq(note, octave):
	NOTES_PER_OCTAVE = 12
	step = ((NOTES_PER_OCTAVE*octave+note))
	base = 1.05946309
	exp = 1.0
	# for(int i = 0; i < step; i++)
	for i in range(0,step):
		exp = base*exp
	return 16.35*exp

def get_note_idx(note, octave):
	return int(note + octave*12)
	
def get_note_from_idx(idx):
	note = int(np.mod(idx,12))
	octave = int(np.floor(idx/12))
	return note,octave
	
noteslist = []
for trackidx, track in enumerate(c):
	track.parse()
	for eventidx, event in enumerate(track):
		if("ON" in str(event.message) or "OFF" in str(event.message)):
			str_evtmsg = str(event.message)
			evt_parts = str_evtmsg.split(' ')
			tmp = evt_parts[0]
			octave = -1
			notestr = ""
			if(tmp[1] == "#"):
				octave = int(tmp[2])
				notestr = tmp[0:2]
			else:
				octave = int(tmp[1])
				notestr = tmp[0:1]
			note_int = note_lookup.index(notestr)
			on_off_str = evt_parts[1]
			on_off = 0
			if(on_off_str == "ON"):
				on_off = 1

			# print("track", trackidx, "time:", event.time, "msg: ", event.message, "parsed note:", note_int, note_lookup[note_int], octave, "onoff:", on_off)
			noteslist.append([note_int, octave, on_off, event.time, trackidx])

def getevttime(e):
	return e[3]
noteslist.sort(key=getevttime)

onofflkp = ["OFF", "ON"]
for i in range(0,len(noteslist)):
	print("track", noteslist[i][4], "time", noteslist[i][3], "note", note_lookup[noteslist[i][0]]+str(noteslist[i][1]), onofflkp[noteslist[i][2]])
	

fsamp = 48e3 #samps/sec
ticks_per_sec = 1000
endtime = (noteslist[len(noteslist)-1][3]) / ticks_per_sec
numsamps = fsamp*endtime
t = np.linspace(0, endtime, int(numsamps))
output = 0*t

note_active = np.zeros(88)
for i in range(0,len(t)):
	for nidx in range(0,len(noteslist)):
		ts = noteslist[nidx][3]/ticks_per_sec
		if(t[i] > ts):
			tmp = get_note_idx(noteslist[nidx][0],noteslist[nidx][1])
			if(noteslist[nidx][2] != 0):
				note_active[tmp] = 1
			else:
				note_active[tmp] = 0
	for n in range(0,len(note_active)):
		if(note_active[n]):
			note,octave = get_note_from_idx(n)
			freq = get_note_freq(note,octave)
			output[i] += np.sin(freq*2*np.pi*t[i])


to_wav(t,output,'bass.wav')
fig,ax = plt.subplots()
# ax.plot(t,np.sin(t*2*np.pi*get_note_freq(4,4)))
ax.plot(t,output)
plt.show()