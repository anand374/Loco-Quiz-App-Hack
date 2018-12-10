
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
from google import google
from skimage.transform import radon

'''
	CONSTANTS!!!
	-------------------------
	ratio calc as - 405x720
					divided by 1080x1920
'''


#MULTIPLY BY RATIO
'''

	--------------------------
'''
ratio = 0.458
#ratio = 1
quest_ya = 770 * ratio
quest_xa = 90* ratio
quest_yb = 960* ratio
quest_xb = 990* ratio
option_startY = 1020* ratio
option_hY = 100* ratio
option_startX = 180* ratio
option_hX = 720* ratio
option_separation = 200* ratio

#for 3 lines question --

quest_ya1 = 730 * ratio
quest_xa1 = 90* ratio
quest_yb1 = 1000* ratio
quest_xb1 = 990* ratio
option_startY1 = 1050* ratio

#for 4 lines question
quest_ya2 = 700 * ratio
quest_xa2 = 90* ratio
quest_yb2 = 1030* ratio
quest_xb2 = 990* ratio
option_startY2 = 1090* ratio

#For 1 line
quest_ya0 = 820 * ratio
quest_xa0 = 90* ratio
quest_yb0 = 930* ratio
quest_xb0 = 990* ratio
option_startY0 = 980* ratio
option_hY0 = 80* ratio
option_separation0 = 180* ratio

refPt = [(127,1192)]
check = False
number = 0
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
	text = pytesseract.image_to_string(img,config="-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ().,""''_:-%? -psm 6")
	return text

def calc_no_of_questions(gray,y):
	projections = radon(gray, theta=[270])
	print projections.shape
	count=0
	start = 0
	end = 0
	contour =[]
	print projections[1]
	'''
	for x in projections:
		count+=1
		print x
		
		if(int(x)>0):
			start = count
			while(x>0):
				count+=1
				print count
			end = count
			contour.append([start,end])
	'''
	return contour


def main():
	with mss.mss() as sct:
		# Part of the screen to capture
		monitor = {'top': 127, 'left': 1192, 'width': 495, 'height': 880}

		while 'Screen capturing':
			last_time = time.time()

			# Get raw pixels from the screen, save it to a Numpy array
			img = numpy.array(sct.grab(monitor))
			#img = cv2.imread("Test/3.png")


			
			# Press "q" to quit
			cv2.imshow('test',img)
			
			c = cv2.waitKey(1)
			if c & 0xFF == ord('q'):
				cv2.destroyAllWindows()
				break
			elif c & 0xFF == ord('o'):
				check = not(check)
				if(check):
					print "Check is ON!"
				else:
					print "Check is OFF!"
			elif c & 0xFF == ord('f'):
				#find the last word of the option in output
				option1_textf = option1_text.split(' ',1)[0]
				option2_textf = option2_text.split(' ',1)[0]
				option3_textf = option3_text.split(' ',1)[0]

				count1 = sum(1 for _ in re.finditer(r'\b' + option1_textf + r'\b', output))
				count2 = sum(1 for _ in re.finditer(r'\b' + option2_textf + r'\b', output))
				count3 = sum(1 for _ in re.finditer(r'\b' + option3_textf + r'\b', output))
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
			elif c & 0xFF == ord('r'):
				#find the last word of the option in output
				option1_textr = option1_text.split(' ')[-1]
				option2_textr = option2_text.split(' ')[-1]
				option3_textr = option3_text.split(' ')[-1]

				count1 = sum(1 for _ in re.finditer(r'\b' + option1_textr + r'\b', output))
				count2 = sum(1 for _ in re.finditer(r'\b' + option2_textr + r'\b', output))
				count3 = sum(1 for _ in re.finditer(r'\b' + option3_textr + r'\b', output))
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
				gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
				gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
				grayadapt = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY,11,2)
				#plt.imshow(gray,cmap="gray")
				#plt.show()

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
								if 2 lines - white b/w 1540 - 1570
								if 3 lines - white 1570 - 1600
								if 4 lines - white 1600 - 1640

								options
									if 2 lines
									1st option - y - 1020 - 1120
												x - 180 - 900
									2nd option - y - 1220 - 1320
									3rd option - y - 1420 - 1520

									if 3 lines -- 
										1st option - 1050 -----

									if 4 lines --
										1st option - 1090

							Question ---
								x - 90 - 990
								end at -
									2 lines - y - 770 : 960
									3 lines - y - 730 : 1000
									4 lines - y - 700 : 1030
				'''

				#Check for number of lines in question
				#NOTE THAT FOR LOCO LINES CAN BE 2,3,4

				x = 225
				y = 870
				#x = 540
				#y = 1900
				while(gray[(y,x)]==0):
					y-=1
					continue
				#print y
				quest = gray[quest_ya:quest_yb,quest_xa:quest_xb]

				option1 = gray[option_startY:option_startY+option_hY,option_startX:option_startX+option_hX]

				option2 = gray[option_startY+option_separation:option_startY+option_separation+option_hY,option_startX:option_startX+option_hX]

				option3 = gray[option_startY+(option_separation*2):option_startY+(option_separation*2)+option_hY,option_startX:option_startX+option_hX]

				#quest_type = calc_no_of_questions(gray,y)
				#print quest_type
				#plt.plot(quest_type)
				#plt.show()

				if(y>1470*ratio and y<1500*ratio): 
					#white at this point, meaning 2 lines
					quest = gray[quest_ya:quest_yb,quest_xa:quest_xb]

					option1 = gray[option_startY:option_startY+option_hY,option_startX:option_startX+option_hX]

					option2 = gray[option_startY+option_separation:option_startY+option_separation+option_hY,option_startX:option_startX+option_hX]

					option3 = gray[option_startY+(option_separation*2):option_startY+(option_separation*2)+option_hY,option_startX:option_startX+option_hX]

				
				elif(y>1500*ratio and y<1530*ratio):
					#3 lines
					quest = gray[quest_ya1:quest_yb1,quest_xa1:quest_xb1]


					option1 = gray[option_startY1:option_startY1+option_hY,option_startX:option_startX+option_hX]


					option2 = gray[option_startY1+option_separation:option_startY1+option_separation+option_hY,option_startX:option_startX+option_hX]


					option3 = gray[option_startY1+(option_separation*2):option_startY1+(option_separation*2)+option_hY,option_startX:option_startX+option_hX]


				elif(y>1530*ratio and y<1570*ratio):
					#4 lines
					quest = gray[quest_ya2:quest_yb2,quest_xa2:quest_xb2]


					option1 = gray[option_startY2:option_startY2+option_hY,option_startX:option_startX+option_hX]


					option2 = gray[option_startY2+option_separation:option_startY2+option_separation+option_hY,option_startX:option_startX+option_hX]


					option3 = gray[option_startY2+(option_separation*2):option_startY2+(option_separation*2)+option_hY,option_startX:option_startX+option_hX]
				elif(y>1350*ratio and y<1390*ratio):
					quest = gray[quest_ya0:quest_yb0,quest_xa0:quest_xb0]

					option1 = gray[option_startY0:option_startY0+option_hY0,option_startX:option_startX+option_hX]

					option2 = gray[option_startY0+option_separation0:option_startY0+option_separation0+option_hY0,option_startX:option_startX+option_hX]

					option3 = gray[option_startY0+(option_separation0*2):option_startY0+(option_separation0*2)+option_hY0,option_startX:option_startX+option_hX]

				#Do some formatting before searching
				print "in loop"
				quest_text = detectOCR(quest)
				print "Detected Question :: " + quest_text.encode('utf-8')
				option1_text = detectOCR(option1)
				print "Option 1 :: " + option1_text.encode('utf-8')
				option2_text = detectOCR(option2)
				print "Option 2 :: " + option2_text.encode('utf-8')
				option3_text = detectOCR(option3)
				print "Option 3 :: " + option3_text.encode('utf-8')

				'''
					PART 3 ----------------------------------------------------------------------------------------------
				'''
				#quest_text = quest_text.replace(" ","+")
				quest_text = quest_text.replace("?","")
				quest_text = quest_text.replace('\r', ' ').replace('\n', ' ')
				whitelist = set('abcdefghijklmnopqrstuvwxy+ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,\(\). ')
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
				cmd = os.popen("lynx -dump %s" % query)
				#cmd = os.popen("lynx -dump %s" % query)
				output = cmd.read()
				#print output
				f= open("search_result.txt","w+")
				f.write(output)
				f.close()
				#cmd.close()
				'''
				f= open("search_result.txt","w+")
				f.write(output)
				f.close()
				N=100
				f=open("search_result.txt")
				for i in range(N):
				    line=f.next().strip()
				    print line
				f.close()
				
				num_page = 5
				search_results = google.search(quest_text, num_page)
				for result in search_results:
				    output+=result.description
				print output.encode('utf-8')
				f= open("search_result.txt","w+")
				f.write(output.encode('utf-8'))
				f.close()	
				'''

				count1 = sum(1 for _ in re.finditer(r'\b' + option1_text + r'\b', output))
				count2 = sum(1 for _ in re.finditer(r'\b' + option2_text + r'\b', output))
				count3 = sum(1 for _ in re.finditer(r'\b' + option3_text + r'\b', output))
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
				plt.imshow(img)
				plt.show()
				
				cv2.imshow('quest', quest)
				cv2.imshow('option1',option1)
				cv2.imshow('option2',option2)
				cv2.imshow('option3',option3)
				'''
				
				# Display the picture in grayscale
				# cv2.imshow('OpenCV/Numpy grayscale',
				#            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

				#print('fps: {0}'.format(1 / (time.time()-last_time)))

			#monitor = {'top': refPt[0][0], 'left': refPt[0][1], 'width': 495, 'height': 880}

main()