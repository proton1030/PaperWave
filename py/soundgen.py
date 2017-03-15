from __future__ import print_function
import numpy as np
import sys, os
import csv
import soundfile as sf
import pydub
#
# csvPath = '../public/results/grid.csv'
# writePath = '../public/results/mix.wav'

Fs = 44100
bpm = 120
beat_per_sec = bpm / 60
samples_per_beat = np.round(Fs/beat_per_sec)

chiptune_kick_path = 'assets/soundsets/chiptune/kick.wav'
chiptune_snare_path = 'assets/soundsets/chiptune/snare.wav'
chiptune_hh_path = 'assets/soundsets/chiptune/hh.wav'
chiptune_blip_path = 'assets/soundsets/chiptune/blip.wav'
chiptune_fx1_path = 'assets/soundsets/chiptune/fx1.wav'
chiptune_fx2_path = 'assets/soundsets/chiptune/fx2.wav'
chiptune_set_path = [chiptune_kick_path,chiptune_snare_path,chiptune_hh_path,chiptune_blip_path,chiptune_fx1_path,chiptune_fx2_path]

def main(grid_csv_path, write_audio_path, mp3_audio_path ,sound_set_path, samples_per_b, Fs, divider):
	samples_per_beat = samples_per_b / divider
	grid = readGridValues(grid_csv_path)
	track_mix = np.zeros([samples_per_beat*32,2])
	track_num = 0


	for i in range (0 , 6):
		if np.sum(grid[i]) != 0:
			track_num += 1
			track = np.zeros([samples_per_beat * 32, 2])
			sound_clip, _ = sf.read(sound_set_path[i])
			sound_clip_length = len(sound_clip)
			trigger_count = 0
			for trigger in grid[i]:
				if trigger == 0:
					trigger_count += 1
				else:
					if trigger_count*samples_per_beat+sound_clip_length > len(track):
						track[trigger_count * samples_per_beat:(trigger_count+1) * samples_per_beat-1,:] = sound_clip[samples_per_beat-1,:]
					else:
						track[trigger_count*samples_per_beat:trigger_count*samples_per_beat+sound_clip_length,:] = sound_clip
					trigger_count += 1
			track_mix += track
			track_num += 1

	track_mix = (track_mix/np.amax([np.amax(track_mix),abs(np.amin(track_mix))]))

	sf.write(write_audio_path, track_mix, Fs)
	wav_file = pydub.AudioSegment.from_wav(write_audio_path)
	wav_file.export(mp3_audio_path, format="mp3")
	os._exit(0)


def readGridValues(path):
	grid = []
	row = []
	with open(path, 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=',')
		for rows in reader:
			for items in rows:
				row.append(int(float(items)))
			grid.append(row)
			row = []
	return grid



if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2], sys.argv[3], chiptune_set_path, samples_per_beat, Fs, 2)