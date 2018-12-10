
import time
import cv2
import mss
import numpy
from PIL import Image
import pytesseract
import os
import matplotlib.pyplot as plt
import sys
import requests
from bs4 import BeautifulSoup
import re

'''
	CONSTANTS!!!
	-------------------------
	ratio calc as - 405x720
					divided by 1080x1920
'''
ratio = 0.458
quest_ya = 590 * ratio
quest_xa = 45* ratio
quest_yb = 800* ratio
quest_xb = 1045* ratio
option_startY = 860* ratio
option_hY = 100* ratio
option_startX = 140* ratio
option_hX = 810* ratio
option_separation = 170* ratio

#for 3 lines question --


quest_yb1 = 890* ratio
quest_xb1 = 1045* ratio
option_startY1 = 930* ratio
option_startX1 = 140* ratio

#MULTIPLY BY RATIO
'''

	--------------------------
'''


refPt = [(127,1192)]
output = ""
option1_text=""
option2_text=""
option3_text=""
'''	USE	-	You should click the mouse on the top left corner of the teamviewer screen
			So that the program knows where the screen to capture lies, and its resolution.
'''
def mseclick(event, x, y, flags, param):
	# grab references to the global variables
	global refPt

	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		print refPt

cv2.namedWindow("test")
cv2.setMouseCallback("test", mseclick)


def detectOCR(img):
	text = pytesseract.image_to_string(img,config="-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ().,_:''%-$&*? -psm 6")
	return text

def main():
	with mss.mss() as sct:
		# Part of the screen to capture
		monitor = {'top': 127, 'left': 1192, 'width': 495, 'height': 880}

		while 'Screen capturing':
			last_time = time.time()

			# Get raw pixels from the screen, save it to a Numpy array
			img = numpy.array(sct.grab(monitor))
			#img = cv2.imread("b2.jpg")

			# Press "q" to quit
			cv2.imshow('test',img)
			c = cv2.waitKey(25)
			if c & 0xFF == ord('q'):
				cv2.destroyAllWindows()
				break
			elif c & 0xFF == ord('f'):
				#find the last word of the option in output
				option1_text = option1_text.split()[-1]
				option2_text = option2_text.split()[-1]
				option3_text = option3_text.split()[-1]

				count1 = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(option1_text), output))
				count2 = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(option2_text), output))
				count3 = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(option3_text), output))
				print count1,count2,count3

				print "The answer is: "
				if count1>count2:
					if count1>count3:
						print option1_text
					else:
						print option3_text
				else:
					if count2>count3:
						print option2_text
					else:
						print option3_text

			elif c & 0xFF == ord('c'):
						gray1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
						
						gray = cv2.threshold(gray1, 80, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
						#gray = cv2.adaptiveThreshold(gray1,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
						#            cv2.THRESH_BINARY,11,2)
						#cv2.imshow("gray",gray)
						''' -------------MAIN Code--------
							Parts-
								1. Getting the components from image
									a. Question
									b. Options
								2. OCR Recognition from image
								3. Performing google search of question 
									&&
									Searching for most likely answer from search result
						'''

						#NOTE TO SELF - Make a separate function to handle the OCR Part

						'''
								PART 1
									Specs - 	
										if 2 lines - white at 1045, 1030 (x,y)
										if 3 lines - white at 1045, 1400

										options
											if 2 lines
											1st option - y - 860 - 960
														x - 140 - 950
											2nd option - y - 1030 - 1130
											3rd option - y - 1200 - 1300

											if 3 lines -- 
												1st option - 930 -----

									Question ---
										Start always at 50, 590
										end at -
											2 lines - 1045, 800
											3 lines - 1045, 890
						'''

						#Check for number of lines in question
						#print (gray1[1400*ratio,1045*ratio])
						if(gray1[(1400*ratio,1045*ratio)]<=200):
							#black at this point, meaning 2 lines
							quest = gray[quest_ya:quest_yb,quest_xa:quest_xb]
							quest_text = detectOCR(quest)
							print "Detected Question :: " + quest_text.encode('utf-8')

							option1 = gray[option_startY:option_startY+option_hY,option_startX:option_startX+option_hX]
							option1_text = detectOCR(option1)
							print "Option 1 :: " + option1_text.encode('utf-8')

							option2 = gray[option_startY+option_separation:option_startY+option_separation+option_hY,option_startX:option_startX+option_hX]
							option2_text = detectOCR(option2)
							print "Option 2 :: " + option2_text.encode('utf-8')

							option3 = gray[option_startY+(option_separation*2):option_startY+(option_separation*2)+option_hY,option_startX:option_startX+option_hX]
							option3_text = detectOCR(option3)
							print "Option 3 :: " + option3_text.encode('utf-8')
						else:
							quest = gray[quest_ya:quest_yb1,quest_xa:quest_xb1]
							quest_text = detectOCR(quest)
							print "Detected Question :: " + quest_text.encode('utf-8')

							option1 = gray[option_startY1:option_startY1+option_hY,option_startX1:option_startX1+option_hX]
							option1_text = detectOCR(option1)
							print "Option 1 :: " + option1_text.encode('utf-8')

							option2 = gray[option_startY1+option_separation:option_startY1+option_separation+option_hY,option_startX1:option_startX1+option_hX]
							option2_text = detectOCR(option2)
							print "Option 2 :: " + option2_text.encode('utf-8')

							option3 = gray[option_startY1+(option_separation*2):option_startY1+(option_separation*2)+option_hY,option_startX1:option_startX1+option_hX]
							option3_text = detectOCR(option3)
							print "Option 3 :: " + option3_text.encode('utf-8')

						#Do some formatting before searching

						'''
							PART 3 ----------------------------------------------------------------------------------------------
						'''
						quest_text = quest_text.replace("?","")
						quest_text = quest_text.replace('\r', ' ').replace('\n', ' ')
						whitelist = set('abcdefghijklmnopqrstuvwxy+ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,\(\).:%-_ ')
						quest_text = ''.join(filter(whitelist.__contains__, quest_text))
						
						#Perform the checks here!!
						


						quest_text = quest_text.replace(" ","+")
						
						print quest_text
						query = 'http://www.google.co.in/search?q='+quest_text
						#query = "http://www.google.co.in/search?q="+quest_text+"&oq="+quest_text+"&client=ubuntu&sourceid=chrome&ie=UTF-8"
						output = ""


						'''
						r = requests.get(query)
						html_doc = r.text

						soup = BeautifulSoup(html_doc, 'html.parser')
						print soup
						for s in soup.find_all('span', {'class' : 'st'}):
							output+=s.text
							output+="\n"
						'''
						#cmd = os.popen("lynx -dump %s" % query)
						cmd = os.popen("lynx -dump %s" % query)
						output = cmd.read()
						#print output
						#cmd.close()


						f= open("search_result.txt","w+")
						f.write(output)
						f.close()
						
						count1 = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(option1_text), output))
						count2 = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(option2_text), output))
						count3 = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(option3_text), output))
						print count1,count2,count3

						print "The answer is: "
						if count1>count2:
							if count1>count3:
								print option1_text
							else:
								print option3_text
						else:
							if count2>count3:
								print option2_text
							else:
								print option3_text


						# Display the picture
						
						
						'''
						cv2.imshow('quest', quest)
						cv2.imshow('option1',option1)
						cv2.imshow('option2',option2)
						cv2.imshow('option3',option3)
						
						plt.imshow(img)
						plt.show()
						'''

						# Display the picture in grayscale
						# cv2.imshow('OpenCV/Numpy grayscale',
						#            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

						#print('fps: {0}'.format(1 / (time.time()-last_time)))

			#monitor = {'top': refPt[0][0], 'left': refPt[0][1], 'width': 495, 'height': 880}

main()