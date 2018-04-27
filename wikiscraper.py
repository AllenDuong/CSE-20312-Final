#!/usr/bin/env python3

import requests
import re
import random

def getUrls(url):
	r = requests.get(url)
	while r.status_code != 200:
		r = requests.get(url)

	regex = r'[^>]<a href="(/wiki/[^"]+)".*</a>[^<]'
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

def exploregraph(URL, nDepth, nLinks):
	if nDepth == 0:
		return
	else:
		nDepth = nDepth-1
		urls = pickRandom(getUrls(first),nLinks)
		for link in urls:
			print(link)
			exploregraph(link,nLinks,nDepth)
		return

first = "https://en.wikipedia.org/wiki/University_of_Notre_Dame"

exploregraph(first, 3, 2)

