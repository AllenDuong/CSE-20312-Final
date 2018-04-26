#!/usr/bin/env python3

import requests
import re
import random

def getUrls(url):
	r = requests.get(url)
	while r.status_code != 200:
		print("Connection failed")
		r = requests.get(url)
	print("Connection successful")

	regex = r'<a href="(/wiki/[^"]+)".*</a>'
	urls = {}

	for link in re.findall(regex, r.text):
		urls['https://en.wikipedia.org'+link] = ''
	
	return list(urls)

def pickRandom(urls, num):
	indexes = {}
	while len(indexes) < num:
		indexes[random.randint(0,len(urls)-1)] = ''
	
	newurls = []
	for number in indexes:
		newurls.append(urls[number])
	
	return newurls
	
first = "https://en.wikipedia.org/wiki/English_language"

print(pickRandom(getUrls(first), 4))


