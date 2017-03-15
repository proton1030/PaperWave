from __future__ import print_function
import cv2
import numpy as np
import math
import sys, os
import csv



def main(image, identifier, resizeParameter):

	kernel_sharpen = np.array([[-1, -1, -1, -1, -1],
	                           [-1, 2, 2, 2, -1],
	                           [-1, 2, 8, 2, -1],
	                           [-1, 2, 2, 2, -1],
	                           [-1, -1, -1, -1, -1]]) / 8.0
	tryTimes = 0
	while True:
		(markers, mu, mc, contours, img, image) = preProcessing(image, resizeParameter)
		if len(markers) == 6:
			break
		elif len(markers) != 6 and tryTimes ==1:
			image = cv2.blur(image, (3, 3))
			tryTimes += 1
		elif len(markers) != 6 and tryTimes ==2:
			image = cv2.filter2D(image, -1, kernel_sharpen)
			tryTimes += 1
		elif len(markers) != 6 and tryTimes ==3:
			image = cv2.filter2D(image, -1, kernel_sharpen)
			tryTimes += 1
		else:
			os._exit(5)
			

	# print(markers)
	# if len(markers)
	# for mark in markers:
	# 	cv2.drawContours(image, contours, mark, (255, 0, 0), 2)
	# cv2.imshow("rect", image)
	varianceArray = list()
	dists = np.zeros((len(markers), len(markers)))
	for i in range(0, len(markers)):
		for j in range(0, len(markers)):
			dists[i, j] = distance(mc[markers[i]], mc[markers[j]])
		varianceArray.append(np.var(dists[i, :]))
	farthest = varianceArray.index(np.amax(varianceArray))
	setBig = list()
	setSmall = list()

	for i in range (0, len(markers)):
		if dists[farthest, i] > np.mean(dists[farthest, :]):
			setBig.append(markers[i])
		else:
			setSmall.append(markers[i])
	setBigDist = 0.0
	setSmallDist = 0.0
	for i in setBig:
		for j in setBig:
			setBigDist += distance(mc[i],mc[j])
	for i in setSmall:
		for j in setSmall:
			setSmallDist += distance(mc[i],mc[j])
	if setBigDist < setSmallDist:
		temp = setBig
		setSmall = setBig
		setBig = temp

	(srcSmall, topSmall, rightSmall, bottomSmall, _) = calculateCorrespondingPoints(setSmall[0],setSmall[1],setSmall[2], mc, contours)
	(srcBig, topBig, rightBig, bottomBig, innerSrcBig) = calculateCorrespondingPoints(setBig[0], setBig[1], setBig[2], mc, contours)
	srcBig[0] = innerSrcBig[0]
	srcBig[1] = innerSrcBig[1]
	srcBig[2] = srcSmall[0]
	srcBig[3] = innerSrcBig[2]


	qrcode = cv2.resize(cv2.cvtColor(four_point_transform(img, srcSmall), cv2.COLOR_BGR2GRAY), (200, 200))
	grid = cv2.cvtColor(four_point_transform(img, srcBig), cv2.COLOR_BGR2GRAY)
	(gridW, gridH) = grid.shape
	qrcode =  cv2.filter2D(qrcode, -1, kernel_sharpen)
	#cv2.imshow("QRcode", qrcode)

	grid = cv2.resize(grid, (34*30, 26*35))
	grid = cv2.filter2D(grid, -1, kernel_sharpen)
	# grid = cv2.resize(grid, (gridH / resizeParameter, gridW / resizeParameter))
	#cv2.imshow("Grid",grid)

	cv2.circle(image, (srcBig[0][0], srcBig[0][1]), 3, (0, 0, 255), 4)
	cv2.circle(image, (srcBig[1][0], srcBig[1][1]), 3, (0, 0, 255), 4)
	cv2.circle(image, (srcBig[2][0], srcBig[2][1]), 3, (0, 0, 255), 4)
	cv2.circle(image, (srcBig[3][0], srcBig[3][1]), 3, (0, 0, 255), 4)
	cv2.circle(image, (srcSmall[0][0], srcSmall[0][1]), 3, (0, 0, 255), 4)
	cv2.circle(image, (srcSmall[1][0], srcSmall[1][1]), 3, (0, 0, 255), 4)
	cv2.circle(image, (srcSmall[2][0], srcSmall[2][1]), 3, (0, 0, 255), 4)
	cv2.circle(image, (srcSmall[3][0], srcSmall[3][1]), 3, (0, 0, 255), 4)
	cv2.drawContours(image, contours, topBig, (255, 0, 0), 2)
	cv2.drawContours(image, contours, rightBig, (0, 255, 0), 2)
	cv2.drawContours(image, contours, bottomBig, (0, 0, 255), 2)
	cv2.drawContours(image, contours, topSmall, (255, 0, 0), 2)
	cv2.drawContours(image, contours, rightSmall, (0, 255, 0), 2)
	cv2.drawContours(image, contours, bottomSmall, (0, 0, 255), 2)
	# image = cv2.resize(image, (imHeight / resizeParameter, imWidth / resizeParameter))
	#cv2.imshow("image", image)

	cv2.imwrite("public/results/" + identifier + "/DetectionResult.png",image)
	cv2.imwrite("public/results/" + identifier + "/grid.png",grid)
	cv2.imwrite("public/results/" + identifier + "/qrcode.png",qrcode)
	gridDisected = getGridValues(grid)
	if np.amax(gridDisected) == 0:
		os._exit(6)
	with open('public/results/' + identifier + '/grid.csv', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		for rows in gridDisected:
			writer.writerow(rows)
	os._exit(0)

def getGridValues(grid):
	thres = 120
	Height, Width = grid.shape
	columnBlockNum = 34
	columnPixel = Width/columnBlockNum
	rowBlockNum = 26
	rowPixel = Height/rowBlockNum
	gridDisected = np.zeros((rowBlockNum, columnBlockNum))
	for i in range (0, rowBlockNum):
		for j in range (0, columnBlockNum):
			gridDisected[i,j] = 0 if (np.mean(grid[i*rowPixel:(i+1)*rowPixel-1 , j*columnPixel:(j+1)*columnPixel-1]) > thres) else 1
	gridDisected = np.delete(gridDisected, ([0,33]), axis=1)
	gridDisected = np.delete(gridDisected, ([6, 19]), axis=0)
	return gridDisected




def preProcessing(image, resizeP):
	imWidth, imHeight, imChannel = image.shape
	image = cv2.resize(image, (imHeight / resizeP, imWidth / resizeP))
	# image = cv2.blur(image, (3, 3))
	imWidth, imHeight, imChannel = image.shape
	img = image.copy()

	#cv2.imshow("image", image)

	gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
	edges = cv2.Canny(gray, 100, 200)
	_, contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	mark = 0

	mu = list()
	mc = list()
	markers = list()
	for i in range(0, len(contours)):
		mu.append(cv2.moments(contours[i], False))
	for m in mu:
		if m['m00'] != 0:
			mc.append((m['m10'] / m['m00'], m['m01'] / m['m00']))
		else:
			mc.append((0, 0))
	for x in range(0, len(contours)):
		k = x
		c = 0
		while (hierarchy[0][k][2] != -1):
			k = hierarchy[0][k][2]
			c = c + 1
		if hierarchy[0][k][2] != -1:
			c = c + 1
		if c >= 5:
			markers.append(x)
	return (markers, mu, mc, contours, img, image)


def calculateCorrespondingPoints(A, B, C, mc, contours):
	AB = distance(mc[A], mc[B])
	BC = distance(mc[B], mc[C])
	AC = distance(mc[A], mc[C])
	if (AB > BC and AB > AC):
		outlier = C
		median1 = A
		median2 = B
	elif (AC > AB and AC > BC):
		outlier = B
		median1 = A
		median2 = C
	else:
		outlier = A
		median1 = B
		median2 = C

	top = outlier
	dist = lineEquation(mc[median1], mc[median2], mc[outlier])
	slope, align = lineSlope(mc[median1], mc[median2])

	if align == 0:
		bottom = median1
		right = median2
	elif (slope < 0 and dist < 0):
		bottom = median1
		right = median2
		orientation = 0
	elif (slope > 0 and dist < 0):
		right = median1
		bottom = median2
		orientation = 1
	elif (slope < 0 and dist > 0):
		right = median1
		bottom = median2
		orientation = 2
	elif (slope > 0 and dist > 0):
		bottom = median1
		right = median2
		orientation = 3
	if (top < len(contours) and right < len(contours) and bottom < len(contours) and cv2.contourArea(
			contours[top]) > 10 and cv2.contourArea(contours[right]) > 10 and cv2.contourArea(
		contours[bottom]) > 10):
		tempL = []
		tempM = []
		tempO = []
		src = []
		innersrc = []
		N = (0, 0)
		tempL = getVertices(contours, top, slope, tempL)
		tempM = getVertices(contours, right, slope, tempM)
		tempO = getVertices(contours, bottom, slope, tempO)
		L = updateCornerOr(orientation, tempL)
		M = updateCornerOr(orientation, tempM)
		O = updateCornerOr(orientation, tempO)
		N = getIntersectionPoint(L[0], M[1], O[3])
		src.append(L[0])
		src.append(M[1])
		src.append(N)
		src.append(O[3])
		innersrc.append(L[2])
		innersrc.append(M[3])
		innersrc.append(O[1])
		src =  np.asarray(src, np.float32)
		return (src, top, right, bottom, innersrc)

def distance(p,q):
	return math.sqrt(math.pow(math.fabs(p[0]-q[0]),2)+math.pow(math.fabs(p[1]-q[1]),2))

def lineEquation(l,m,j):
	a = -((m[1] - l[1])/(m[0] - l[0]))
	b = 1.0
	c = (((m[1] - l[1])/(m[0] - l[0]))*l[0]) - l[1]
	try:
		pdist = (a*j[0]+(b*j[1])+c)/math.sqrt((a*a)+(b*b))
	except:
		return 0
	else:
		return pdist

def lineSlope(l,m):
	dx = m[0] - l[0]
	dy = m[1] - l[1]
	if dy != 0:
		align = 1
		dxy = dy/dx
		return dxy,align
	else:
		align = 0
		dxy = 0.0
		return dxy,align

def getSquares(contours,cid):
	x,y,w,h= cv2.boundingRect(contours[cid])
	return x,y,w,h

def updateCorner(p,ref,baseline,corner):
	temp_dist = distance(p,ref)
	if temp_dist > baseline:
		baseline = temp_dist
		corner = p
	return baseline,corner

def getVertices(contours,cid,slope,quad):
	M0 = (0.0,0.0)
	M1 = (0.0,0.0)
	M2 = (0.0,0.0)
	M3 = (0.0,0.0)
	x,y,w,h = cv2.boundingRect(contours[cid])
	A = (x,y)
	B = (x+w,y)
	C = (x+w,h+y)
	D = (x,y+h)
	W = ((A[0]+B[0])/2,A[1])
	X = (B[0],(B[1]+C[1])/2)
	Y = ((C[0]+D[0])/2,C[1])
	Z = (D[0],(D[1]+A[1])/2)
	dmax = []
	for i in range(4):
		dmax.append(0.0)
	if(slope > 5 or slope < -5 ):
		for i in range(len(contours[cid])):
			pd1 = lineEquation(C,A,contours[cid][i])
			pd2 = lineEquation(B,D,contours[cid][i])
			if(pd1 >= 0.0 and pd2 > 0.0):
				dmax[1],M1 = updateCorner(contours[cid][i],W,dmax[1],M1)
			elif(pd1 > 0.0 and pd2 <= 0):
				dmax[2],M2 = updateCorner(contours[cid][i],X,dmax[2],M2)
			elif(pd1 <= 0.0 and pd2 < 0.0):
				dmax[3],M3 = updateCorner(contours[cid][i],Y,dmax[3],M3)
			elif(pd1 < 0 and pd2 >= 0.0):
				dmax[0],M0 = updateCorner(contours[cid][i],Z,dmax[0],M0)
			else:
				continue
	else:
		halfx = (A[0]+B[0])/2
		halfy = (A[1]+D[1])/2
		for i in range(len(contours[cid])):
			if(contours[cid][i][0][0]<halfx and contours[cid][i][0][1]<=halfy):
				dmax[2],M0 = updateCorner(contours[cid][i][0],C,dmax[2],M0)
			elif(contours[cid][i][0][0]>=halfx and contours[cid][i][0][1]<halfy):
				dmax[3],M1 = updateCorner(contours[cid][i][0],D,dmax[3],M1)
			elif(contours[cid][i][0][0]>halfx and contours[cid][i][0][1]>=halfy):
				dmax[0],M2 = updateCorner(contours[cid][i][0],A,dmax[0],M2)
			elif(contours[cid][i][0][0]<=halfx and contours[cid][i][0][1]>halfy):
				dmax[1],M3 = updateCorner(contours[cid][i][0],B,dmax[1],M3)
	quad.append(M0)
	quad.append(M1)
	quad.append(M2)
	quad.append(M3)
	return quad

def updateCornerOr(orientation,IN):
	if orientation == 0:
		M0 = IN[0]
		M1 = IN[1]
		M2 = IN[2]
		M3 = IN[3]
	elif orientation == 1:
		M0 = IN[1]
		M1 = IN[2]
		M2 = IN[3]
		M3 = IN[0]
	elif orientation == 2:
		M0 = IN[2]
		M1 = IN[3]
		M2 = IN[0]
		M3 = IN[1]
	elif orientation == 3:
		M0 = IN[3]
		M1 = IN[0]
		M2 = IN[1]
		M3 = IN[2]

	OUT = []
	OUT.append(M0)
	OUT.append(M1)
	OUT.append(M2)
	OUT.append(M3)

	return OUT

def cross(v1,v2):
	cr = v1[0]*v2[1] - v1[1]*v2[0]
	return cr

def getIntersectionPoint(tl,tr,bl):
	return bl+tr-tl


def getGridPoints(tl,tr,bl):
	gridLocation = [[],[],[],[]]
	gridLocation[2] = (bl-tl)*(0.285/1.028)+tl+(tl-tr)*(0.169/1.028)
	gridLocation[1] = gridLocation[2] + (tl-bl)*(6.783/1.028)
	gridLocation[0] = gridLocation[1] + (tl-tr)*(8.351/1.028)
	gridLocation[3] = gridLocation[2] + (tl-tr)*(8.351/1.028)
	return gridLocation


def order_points(pts):
	rect = np.zeros((4, 2), dtype="float32")
	s = pts.sum(axis=1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	diff = np.diff(pts, axis=1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	return rect

def four_point_transform(image, pts):
	rect = order_points(pts)
	(tl, tr, br, bl) = rect

	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))

	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype="float32")
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	return warped


if __name__ == '__main__':
	#file_path = '/Users/hanyu/Desktop/testcase/mod1.jpg'
	file_path = ''.join(sys.argv[1])
	identifier = ''.join(sys.argv[2])
	if not os.path.exists("public/results/" + identifier + "/"):
		os.makedirs("public/results/" + identifier + "/")
	image = cv2.imread(file_path)
	main(image, identifier, 4)
	# cv2.waitKey(0)

