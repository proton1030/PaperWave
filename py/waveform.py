from __future__ import print_function
import cv2
import numpy as np
import scipy.signal as sig
import math
import sys, os
import csv
import matplotlib.pyplot as plt
import soundfile as sf
import pydub
Fs = 44100
c5 = 587

def main():
	img = cv2.imread('../wav6.jpg')

	gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
	rows, columns = gray.shape
	weightBoard = np.ones(gray.shape) * 255
	black = weightBoard.copy()
	waveSynthed = weightBoard.copy()
	ret, thresh = cv2.threshold(gray, 127, 255, 0)
	im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	for i in range(1, len(contours)):
		cv2.drawContours(weightBoard, contours, i , (0, 0, 0), 1)
	weightBoard = black - weightBoard

	# Apply LPF to smooth the curve
	lpFiltSize = 64
	waveSeq = [0] * columns # 5 is the size for lp filtering
	rowIndex, cnt = 0, 0
	for i in range(0,columns):
		for pixel in weightBoard[:,i]:
			if pixel != 0:
				waveSeq[i] += rowIndex
				cnt += 1
			rowIndex += 1
		if cnt != 0:
			waveSeq[i] = np.floor(waveSeq[i] / cnt)

		cnt, rowIndex = 0, 0
	waveSeq.reverse()
	waveSeq += [waveSeq[-1]] * (lpFiltSize-1)
	lpWave = [0] * columns

	for i in range(0, columns):
		lpWave[i] = np.floor(np.mean(waveSeq[i:i+lpFiltSize]))
		weightBoard[int(lpWave[i]), columns-i-1] = 255

	startPointer, endPointer = 0, columns - 1
	startPointerFlag, endPointerFlag = True, True
	for i in range(0, columns):
		if startPointerFlag and waveSeq[i] != 0:
			startPointer = i
			startPointerFlag = False
		if endPointerFlag and waveSeq[columns-1-i] != 0:
			endPointer = columns-1-i
			endPointerFlag = False
	waveSeqSect = waveSeq[startPointer:endPointer]

	sectLength = len(waveSeqSect)
	lpSect = [0] * sectLength
	waveSeqSect += [waveSeqSect[-1]] * (lpFiltSize-1)
	for i in range(0, sectLength):
		lpSect[i] = np.floor(np.mean(waveSeqSect[i:i + lpFiltSize]))
	lpSect = ((lpSect-min(lpSect))/(max(lpSect)-min(lpSect)))*2-1
	lpSect = lpSect * 0.1

	outputSeq = []
	for i in range(0, c5):
		outputSeq.extend(lpSect)
	outputSeq = sig.resample(outputSeq, Fs)
	print(len(outputSeq))

	sf.write('6.wav', outputSeq, Fs)
	wav_file = pydub.AudioSegment.from_wav('6.wav')
	wav_file.export('6.mp3', format="mp3")
	#
	# # sig = np.zeros((len(outputSeq),2))
	# # sig[:,0] = np.transpose(outputSeq)
	# # sig[:,1] = sig[:,0]
	# # print(sig)
	# # plt.specgram(outputSeq, NFFT=1024, Fs=256)
	# plt.plot(lpSect)
	# plt.show()
	# cv2.imshow('window',weightBoard)
	# cv2.waitKey(0)







if __name__ == '__main__':
	main()
	# cv2.waitKey(0)