import io
import os
try:
	import Image
except ImportError:
	from PIL import Image,ImageEnhance,ImageGrab
import pytesseract
import webbrowser
from googleapiclient.discovery import build
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import re
import sys
from PIL import ImageFile
#import pyscreenshot
import mss
from google.cloud import vision
from google.cloud.vision import types
import numpy
import cv2

ratio = 0.458
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

refPt = [(127,1192)]
check = False
number = 0

def retrieve_q_and_a(text):
	question_answers = text.split('?')
	if len(question_answers) > 2:
		corrString = ''
		for x in range(len(question_answers) - 1):
			corrString += question_answers[x]
		question_answers = [corrString, question_answers[len(question_answers) - 1]]
	question = question_answers[0].replace('\n', ' ')
	answers = question_answers[1].split('\n')
	answers = [ans.strip() for ans in answers]
	answers = [x for x in answers if x != '']
	#print(answers)
	return question, answers

g_cse_api_key = 'AIzaSyDGe6mTBYsQwU7fp0TW3vq8bhadPL8kx4w'
g_cse_id = '004161184837490897252:-sosddvo1ew'
#

def notify(title, text):
	os.system("""
			  osascript -e 'display notification "{}" with title "{}"'
			  """.format(text, title))

def approach1(question):
	url = "https://www.google.com.tr/search?q={}".format(question)
	webbrowser.open(url)

def google_search(query, start):
	service = build("customsearch", "v1", developerKey=g_cse_api_key)
	res = service.cse().list(q=query, cx=g_cse_id, start=start).execute()
	return res
#
#
output = ""
def abhi(quest_text,option1_text,option2_text,option3_text,check):
	global output
	if( not check):
		quest_text = quest_text.replace("?","")
		quest_text = quest_text.replace('\r', ' ').replace('\n', ' ')
		whitelist = set('abcdefghijklmnopqrstuvwxy+ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,\(\). ')
		quest_text = ''.join(filter(whitelist.__contains__, quest_text))
		
		#Perform the checks here!!
		


		quest_text = quest_text.replace(" ","+")
		if quest_text[0] == "+" :
			quest_text = quest_text[1:]
		print quest_text
		query = 'http://www.google.co.in/search?q='+quest_text
		#query = "http://www.google.co.in/search?q="+quest_text+"&oq="+quest_text+"&client=ubuntu&sourceid=chrome&ie=UTF-8"

		#cmd = os.popen("lynx -dump %s" % query)
		cmd = os.popen("lynx -dump %s" % query)
		output = cmd.read()
		count1 = sum(1 for _ in re.finditer(r'\b' + option1_text + r'\b', output))
		count2 = sum(1 for _ in re.finditer(r'\b' + option2_text + r'\b', output))
		count3 = sum(1 for _ in re.finditer(r'\b' + option3_text + r'\b', output))
		print count1,count2,count3

		print "The answer is: (abhi)"
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
	else:
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


def approach2(question, answers):
	met1 = [0, 0, 0]
	res = google_search(question,None)
	#print res
	items = str(res['items']).lower()
	# print items
	met1[0] = items.count(answers[0].lower())
	met1[1] = items.count(answers[1].lower())
	met1[2] = items.count(answers[2].lower())
	return met1

def approach3(question, answers):
	met2 = [0, 0, 0]
	res0 = google_search(question + ' "' + answers[0] + '"', None)
	res1 = google_search(question + ' "' + answers[1] + '"', None)
	res2 = google_search(question + ' "' + answers[2] + '"', None)
	return [int(res0['searchInformation']['totalResults']), int(res1['searchInformation']['totalResults']), int(res2['searchInformation']['totalResults'])]

def predict(metric1, metric2, answers):
	max1 = metric1[0]
	max2 = metric2[0]
	for x in range(1, 3):
		if metric1[x] > max1:
			max1 = metric1[x]
		if metric2[x] > max2:
			max2 = metric2[x]
	if metric1.count(0) == 3:
		return answers[metric2.index(max2)]
	elif metric1.count(max1) == 1:
		if metric1.index(max1) == metric2.index(max2):
			return answers[metric1.index(max1)]
		else:
			percent1 = max1 / sum(metric1)
			percent2 = max2 / sum(metric2)
			if percent1 >= percent2:
				return answers[metric1.index(max1)]
			else:
				return answers[metric2.index(max2)]
	elif metric1.count(max1) == 3:
		return answers[metric2.index(max2)]
	else:
		return answers[metric2.index(max2)]

def main():
	with mss.mss() as sct:
		# Part of the screen to capture
		monitor = {'top': 127, 'left': 1192, 'width': 495, 'height': 880}

		while 'Screen capturing':
			last_time = time.time()

			# Get raw pixels from the screen, save it to a Numpy array
			img = numpy.array(sct.grab(monitor))
			#img = cv2.imread("l1.jpg")


			
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
				abhi(quest_text,option1_text,option2_text,option3_text,True)
			elif c & 0xFF == ord('c'):
				startTime = datetime.now()
				vision_client = vision.ImageAnnotatorClient()
				#file_name = ImageGrab.grab(bbox=(1235, 407, 1849, 959))
				
				
				#gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
				#image = cv2.imread('l2.jpg')
				image = img
				image = image[500*ratio:1700*ratio,:]
				gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
				cv2.imwrite('screenshot.png',gray)
				file_name1='screenshot.png'
				
				with io.open(file_name1,'rb') as image_file:
					content = image_file.read()
					image = types.Image(content=content)
				
				print "before labels"
				response = vision_client.document_text_detection(image=image)
				labels = response.full_text_annotation
				print "after labels"
			# print type(labels.text)
				ocr_output=str(labels.text)
				print ocr_output
				# print ocr_output
				ocr_output=ocr_output.replace('-','?')
				ocr_output=ocr_output.replace('Q?','')
				ocr_output=ocr_output.replace('S 32.5K','')
				ocr_output=ocr_output.replace('TIME UP','')
				ocr_output=ocr_output.replace('NOT','')
				# print ocr_output
				question, answers = retrieve_q_and_a(ocr_output)
				question=question.replace('ELIMINATED', '')
				ans = []
				for i in range(len(answers)):
					ans.append(str(answers[i]))
				quest_text = question
				option1_text = answers[0]
				option2_text = answers[1]
				option3_text = answers[2]
				abhi(quest_text,option1_text,option2_text,option3_text,False)
				#res1 = approach2(question, ans)
				#res2 = approach3(question, ans)
				#print(res1)
				#print(res2)
				#print predict(res1, res2, ans)
				#notify(question, predict(res1, res2, answers))
				print(datetime.now() - startTime)    

				
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
				

				#NOTE TO SELF - Make a separate function to handle the OCR Part

				
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
				

				#Check for number of lines in question
				#NOTE THAT FOR LOCO LINES CAN BE 2,3,4

				x = 225
				y = 870
				while(gray[(y,x)]==0):
					y-=1
					continue
				quest = gray[quest_ya:quest_yb,quest_xa:quest_xb]

				option1 = gray[option_startY:option_startY+option_hY,option_startX:option_startX+option_hX]

				option2 = gray[option_startY+option_separation:option_startY+option_separation+option_hY,option_startX:option_startX+option_hX]

				option3 = gray[option_startY+(option_separation*2):option_startY+(option_separation*2)+option_hY,option_startX:option_startX+option_hX]
				if(y>1540*ratio and y<1570*ratio): 
					#white at this point, meaning 2 lines
					quest = gray[quest_ya:quest_yb,quest_xa:quest_xb]

					option1 = gray[option_startY:option_startY+option_hY,option_startX:option_startX+option_hX]

					option2 = gray[option_startY+option_separation:option_startY+option_separation+option_hY,option_startX:option_startX+option_hX]

					option3 = gray[option_startY+(option_separation*2):option_startY+(option_separation*2)+option_hY,option_startX:option_startX+option_hX]

				
				elif(y>1570*ratio and y<1600*ratio):
					#3 lines
					quest = gray[quest_ya1:quest_yb1,quest_xa1:quest_xb1]


					option1 = gray[option_startY1:option_startY1+option_hY,option_startX:option_startX+option_hX]


					option2 = gray[option_startY1+option_separation:option_startY1+option_separation+option_hY,option_startX:option_startX+option_hX]


					option3 = gray[option_startY1+(option_separation*2):option_startY1+(option_separation*2)+option_hY,option_startX:option_startX+option_hX]


				elif(y>1600*ratio and y<1640*ratio):
					#4 lines
					quest = gray[quest_ya2:quest_yb2,quest_xa2:quest_xb2]


					option1 = gray[option_startY2:option_startY2+option_hY,option_startX:option_startX+option_hX]


					option2 = gray[option_startY2+option_separation:option_startY2+option_separation+option_hY,option_startX:option_startX+option_hX]


					option3 = gray[option_startY2+(option_separation*2):option_startY2+(option_separation*2)+option_hY,option_startX:option_startX+option_hX]


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

				
					PART 3 ----------------------------------------------------------------------------------------------
				
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


				
				r = requests.get(query)
				html_doc = r.text

				soup = BeautifulSoup(html_doc, 'html.parser')
				print soup
				for s in soup.find_all('span', {'class' : 'st'}):
					output+=s.text
					output+="\n"
					
				
				cmd = os.popen("lynx -dump -pauth=abh.anand:1996.anand %s" % query)
				output = cmd.read()
				#print output
				f= open("search_result.txt","w+")
				f.write(output)
				f.close()
				#cmd.close()
				
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
				
				
				plt.imshow(img)
				plt.show()
				cv2.imshow('quest', quest)
				cv2.imshow('option1',option1)
				cv2.imshow('option2',option2)
				cv2.imshow('option3',option3)
				
				cv2.imwrite(""+number+".jpg",img)
				number+=1
				# Display the picture in grayscale
				# cv2.imshow('OpenCV/Numpy grayscale',
				#            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

				#print('fps: {0}'.format(1 / (time.time()-last_time)))
				'''	
			#monitor = {'top': refPt[0][0], 'left': refPt[0][1], 'width': 495, 'height': 880}

main()