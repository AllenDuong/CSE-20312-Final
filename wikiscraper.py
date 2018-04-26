#!/usr/bin/env python3

import requests
import re

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
	
	return urls

first = "https://en.wikipedia.org/wiki/English_language"

getUrls(first)

