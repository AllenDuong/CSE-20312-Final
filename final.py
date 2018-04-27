#!/usr/bin/env python3
# Final Project: Wikipedia Web Crawler
# Names: Allen Duong, Nicole Blandin, William Diedrich

# Imports + Libraries

import os
import requests # For Requesting Website Data
import sys 
import time # Add Delay to Prevent DOS on Wiki Servers
from bs4 import BeautifulSoup
import re # For RegEx
import networkx as nx # For Building Complex Networks

# Functions

def usage(status=0):
    print('''Usage: {} [-p PROCESSES -r REQUESTS -v] URL
    -h              Display help message
    -p  PROCESSES   Number of processes to utilize (1)
    -r  REQUESTS    Number of requests per process (1)
    '''.format(os.path.basename(sys.argv[0])))
    sys.exit(status)

# Function to Get a Dictionary of URLs from a Page
def getUrls(url):
    r = requests.get(url)
    while r.status_code != 200:
        print("Connection Failed")
        r = requests.get(url)
    print("Connection Successful")

    regex = r'<a href="(/wiki/[^"]+)".*</a>'
    urls = {}

    for link in re.findall(regex, r.text):
        urls['https://en.wikipedia.org'+link] = ''
    
    return urls

def pickRandom(urls, num):
    indexes = {}
    while len(indexes) < num:
        indexes[random.randint(0,len(urls)-1)] = ''
    
    newurls = []
    for number in indexes:
        newurls.append(urls[number])
    
    return newurls

# This Funtion Scrapes Wikipedia and Build the Graph
def crawlWiki(URL='https://en.wikipedia.org/wiki/University_of_Notre_Dame', nLinks=3, nDepth=3):

    # Create Empty Graph
    G = nx.Graph()

    # Get Root Site
    data = BeautifulSoup(requests.get(URL).content)
    root = str(data.find("title"))[7:-20]

    # Add First Site to Graph
    G.add_node(root)
	
	exploregraph(url, G, root, nLinks, nDepth)
    # Get nLinks Links from Page
        #TODO: Add function that gets nLink links
    
    # TODO: Loop Through nLinks
    # for i in range(0, nDepth):

        # TODO: 


    # Return the Graph
    return G

# Here is how I imagine the recursive function would work
#   def recursepages(graph, depth, url):
#   add node with url to graph
#   search url for new links to search
#   if depth != 0   
#       for each link:
#           recursepages(graph, depth--, newlink)
# we need to find a place to create the edges between graphs in here as well
def exploregraph(URL, graph, parent, nDepth, nLinks):
	if nDepth == 0:
		return
	else:
		nDepth = nDepth-1
	#	create edge to parent
    	urls = pickRandom(getUrls(URL),nLinks)
		for link in urls:
    		data = BeautifulSoup(requests.get(URL).content)
    		root = str(data.find("title"))[7:-20]
    		graph.add_node(root)
			exploregraph(link,graph,root,nLinks,nDepth) 								
		return

# Main Implementation
if __name__ == '__main__':

    # Parse command line arguments
    avg = 0
    args = sys.argv[1:]
    while len(args) and args[0].startswith('-') and len(args[0]) > 1:
        arg = args.pop(0)
        if arg == '-h':
            usage(0)
     
        elif arg == '-p':
            PROCESSES = int(args.pop(0))
        
        elif arg == '-r':
            REQUESTS = int(args.pop(0))
        
        else:
            usage(1)

    # Get Starting URL
    if len(args):
        URL = args.pop(0)
        nLinks = input("Enter a Number of Links per Page: ")
        nDepth = input("Enter a Depth for the Search: ")

    else:
        usage(1)

    # DONE: Build the Graph
    graph = crawlWiki(URL, nLinks, nDepth)

    # Display the Graph

