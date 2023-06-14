from mido import MidiFile
import numpy as np


def get_note_from_idx(idx):
	note = int(np.mod(idx,12))
	octave = int(np.floor(idx/12))
	return note,octave

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

note_lookup = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# mid = MidiFile('ChickenFried.mid')
mid = MidiFile('Bass_sample.mid')
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
		
				
				
