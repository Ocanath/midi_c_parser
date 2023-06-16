from mido import MidiFile
import numpy as np
import matplotlib.pyplot as plt
from wav import to_wav


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
mid = MidiFile('chicken_squished.mid')
# mid = MidiFile('Bass_sample.mid')
print(mid.ticks_per_beat)

for i, track in enumerate(mid.tracks):
	print("Track "+str(i), str(track.name))
	for  msg in track:
		if(msg.is_meta == 0):
			print(msg)
			pass
			
notelist = []
tracks = [1]
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
			# print(note_lookup[int(np.mod(msg.note,12))]+str(octave), "(" + str(msg.note) + ")", "time = ", time, "velocity: ", msg.velocity)

def retstart(e):
	return e[1]
notelist.sort(key=retstart)

tick_per_beat = int(mid.ticks_per_beat*1.5)

print("creating c file...")
filename = "midi_song"
with open('midi_song.c', 'w') as f:
	f.write("/* This is an autogenerated file, created from a MIDI file*/\n")
	f.write("#include \"Tone.h\"\n\n")
	tmpstr = "midi_evt_t " + filename + "[" + str(len(notelist)) + "] = {\n"
	# print(tmpstr)
	f.write(tmpstr)
	for i in range(0,len(notelist)):
		lineend_char = ",\n"
		if(i == len(notelist)-1):
			lineend_char = '\n'
		tmpstr = "	{.note = "+str(notelist[i][0])+", " + ".ts = "+str(int(1000*(notelist[i][1]/tick_per_beat)))+", " + ".onoff = "+str(notelist[i][2])+"}"+lineend_char
		# print(tmpstr)
		f.write(tmpstr)
	f.write('};\n\n')
	# print('};\n')
f.close()
print("done generating c file")

#following code samples the midi and outputs a pure-sin wave .wav file with the contents. 
#it has some problems, for reasons I don't understand. i think maybe it's pinwheel settings? 
#or maybe a bug in the parser. anyway, it's 'good enough' i think

Fs = 12e3
endtick = notelist[len(notelist)-1][1]
endtime = endtick/tick_per_beat
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
max_simultaneous_note_used = 0
for tidx in range(0,len(t)):

	time = t[tidx]
	
	while(time >= notelist[notelist_idx][1]/tick_per_beat):
		ts = notelist[notelist_idx][1]/tick_per_beat
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
				if(notelist_idx >= len(notelist)):
					break
				if(np.mod(notelist_idx,500) == 0):
					print("evt "+str(notelist_idx)+" out of "+str(len(notelist)))
	
	
	
	
	num_simultaneous_notes = 0
	for i in range(0,len(notestate)):	#try reducing range...
		if(notestate[i] == 1):
			num_simultaneous_notes = num_simultaneous_notes + 1
			# freq = get_note_freq(i)
			output[tidx] += np.sin(2*np.pi*time*notefreq[i])
	if(num_simultaneous_notes > max_simultaneous_note_used):
		max_simultaneous_note_used = num_simultaneous_notes

# output[output>1] = 1
# output[output<-1] = -1
# to_wav(t,output,'48.wav')

print("max number of simultaneous notes played: ", max_simultaneous_note_used)
to_wav(t,output,'chromsezoemoes.wav')

fig,ax = plt.subplots()
ax.plot(t,output)
plt.show()
