from PIL import Image
import argparse
import cv2
import os
import io
try:
	import Image
except ImportError:
	from PIL import Image,ImageEnhance,ImageGrab
import pytesseract
import webbrowser
from googleapiclient.discovery import build
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import re
import sys
from PIL import ImageFile
from google.cloud import vision
from google.cloud.vision import types
import numpy
import mss
ratio = 0.458

def retrieve_q_and_a(text):
	question_answers = text.split('?')
	if len(question_answers) > 2:
		corrString = ''
		for x in range(len(question_answers) - 1):
			corrString += question_answers[x]
		question_answers = [corrString, question_answers[len(question_answers) - 1]]
	question = question_answers[0].replace('\n', '')
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
def approach2(question, answers):
	met1 = [0, 0, 0]
	res = google_search(question,None)
	items = str(res['items']).lower()
	# print items
	met1[0] = items.count(answers[0].lower())
	met1[1] = items.count(answers[1].lower())
	met1[2] = items.count(answers[2].lower())
	return met1

def approach3(question, answers):
	met2 = [0, 0, 0]
	res0 = google_search(question + ' ' + answers[0], None)
	res1 = google_search(question + ' ' + answers[1], None)
	res2 = google_search(question + ' ' + answers[2], None)
	return [int(res0['searchInformation']['totalResults']), int(res1['searchInformation']['totalResults']), int(res2['searchInformation']['totalResults'])]


def approach4(question,ans):
	question = question.replace(" ","+")
	query = 'http://www.google.co.in/search?q='+question
	cmd = os.popen("lynx -dump -pauth=gyan.2015:1234 %s" % query)
	output = cmd.read()
	f= open("search_result.txt","w+")
	f.write(output)
	f.close()
	count1 = sum(1 for _ in re.finditer(r'\b' + ans[0] + r'\b', output))
	count2 = sum(1 for _ in re.finditer(r'\b' + ans[1] + r'\b', output))
	count3 = sum(1 for _ in re.finditer(r'\b' + ans[2] + r'\b', output))
	res3=[count1,count2,count3]
	return res3;


def predict(metric1, metric2, metric3, answers):
	max1 = metric1[0]
	max2 = metric2[0]
	max3 = metric3[0]
	for x in range(1, 3):
		if metric1[x] > max1:
			max1 = metric1[x]
		if metric2[x] > max2:
			max2 = metric2[x]
		if metric3[x] > max3:
			max3 = metric3[x]
	# if metric1.count(0) == 3:
	#     return answers[metric2.index(max2)]
	# elif metric1.count(max1) == 1:
	#     if metric1.index(max1) == metric2.index(max2):
	#         return answers[metric1.index(max1)]
	if metric3.count(0)==3 and metric1.count(0)!=3:
		return answers[metric1.index(max1)]
	elif metric1.count(0)== 3 and metric3.count(0)!=3:
		return answers[metric3.index(max3)]
	elif metric3.count(max3)> 1 :
		if metric1.count(max1)== 1:
			return answers[metric1.index(max1)]
		elif metric2.count(max2)== 1:
			return answers[metric2.index(max2)]
	elif max3>max1:
		return answers[metric3.index(max3)]
	elif max3<=max1:
		return answers[metric1.index(max1)]
	elif metric1.count(0) == 3 and metric3.count(0)==3:
		return answers[metric2.index(max2)]
	elif metric3.count(max3) == 1:
		if metric1.index(max1) == metric3.index(max3) and metric1.index(max1) == metric2.index(max2):
			return answers[metric1.index(max1)]
		else:
			percent1 = max1 / sum(metric1)
			percent2 = max2 / sum(metric2)
			percent3 = max3 /sum(metric3)
			if percent1 >= percent2 and percent1>= percent3:
				return answers[metric1.index(max1)]
			elif percent2 >= percent1 and percent2>= percent3:
				return answers[metric2.index(max2)]
			else:
				return answers[metric3.index(max3)]
	elif metric1.count(max1) == 3:
		return answers[metric2.index(max2)]
	else:
		return answers[metric2.index(max2)]

monitor = {'top': 127, 'left': 1192, 'width': 495, 'height': 880}
def startnow():
	with mss.mss() as sct:
		startTime = datetime.now()
		#file_name = ImageGrab.grab(bbox=(2020, 470, 2550, 1220))#1270
		# file_name.show()
		image = numpy.array(sct.grab(monitor))
		image = image[500*ratio:1800*ratio,:]
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		cv2.imwrite('screenshot.png',gray)

		vision_client = vision.ImageAnnotatorClient()
		file_name1='screenshot.png'
		with io.open(file_name1,'rb') as image_file:
			content = image_file.read()
			image = types.Image(content=content)

		response = vision_client.document_text_detection(image=image)
		labels = response.full_text_annotation

	# print type(labels.text)
		ocr_output=str(labels.text)
		ocr_output = ocr_output.encode("ascii", errors="ignore").decode()

		# print ocr_output
		ocr_output=ocr_output.replace('_','?')
		ocr_output=ocr_output.replace('Q?','')
		ocr_output=ocr_output.replace('S 32.5K','')
		ocr_output=ocr_output.replace('TIME UP','')
		ocr_output=ocr_output.replace('NOT','')
		ocr_output=ocr_output.replace('ELIMINATED', '')
		ocr_output=ocr_output.replace('...', '?')
		ocr_output=ocr_output.replace('-', '')
		print ocr_output
		question, answers = retrieve_q_and_a(ocr_output)
		ans = []
		for i in range(len(answers)):
			ans.append(str(answers[i]))
		res3= approach4(question,ans)
		print(res3)
		res1 = approach2(question, ans)
		res2 = approach3(question, ans)
		print(res1)
		print(res2)
		print predict(res1, res2, res3, ans)
		# notify(question, predict(res1, res2, answers))
		print(datetime.now() - startTime)

fd = sys.stdin.fileno()
#old = termios.tcgetattr(fd)
cv2.namedWindow("test")
while True:
	print("Waiting....")
	c = cv2.waitKey(0)
	if c & 0xFF == ord('c'):
		print("Running Question Analysis")
		startnow()
	elif c & 0xFF == ord('q'):
		sys.exit(0)
