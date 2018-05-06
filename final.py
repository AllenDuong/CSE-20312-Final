#!/usr/bin/env python3
# Final Project: Wikipedia Web Crawler
# Names: Allen Duong, Nicole Blandin, William Diedrich

# Imports + Libraries

import os
import requests # For Requesting Website Data
import sys 
from bs4 import BeautifulSoup
import re # For RegEx
import networkx as nx # For Building Complex Networks
import random

# Plot Libraries
import pylab as plt
plt.switch_backend('agg')

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
        r = requests.get(url)

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

# This Funtion Scrapes Wikipedia and Build the Graph
def crawlWiki(URL='https://en.wikipedia.org/wiki/University_of_Notre_Dame', nLinks=3, nDepth=3):
    # Create Empty Graph
    G = nx.DiGraph()
    # Get Root Site
    data = BeautifulSoup(requests.get(URL).content, "lxml")
    root = str(data.find("title"))[7:-20]

    # Add First Site to Graph
    G.add_node(root)

    exploregraph(URL, G, root, nLinks, nDepth)
	# Return the Graph
    return G

def exploregraph(URL, graph, parent, nDepth, nLinks):
	if nDepth == 0:
		return
	else:
		nDepth = nDepth-1
	#	create edge to parent
		urls = pickRandom(getUrls(URL),nLinks)
		for link in urls:
			data = BeautifulSoup(requests.get(URL).content, "lxml")
			root = str(data.find("title"))[7:-20]
			graph.add_node(root)
			graph.add_edge(parent,root)

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

    # Get User Input
    url = input("Enter a Starting Link:")
    if not url:
        url = 'https://en.wikipedia.org/wiki/University_of_Notre_Dame'

    try:
        nLinks = int(input("Enter a Number of Links per Page: "))
    except ValueError:
        nLinks = 3

    try:
        nDepth = int(input("Enter a Depth for the Search: "))
    except ValueError:
        nDepth = 3

    filename = input("Enter a Name to Save the Graph as: ")
    if not filename:
        filename = 'graph'
    
    # TODO: Add case for multiprocessing

    # DONE: Build the Graph
    print("Progress: Entered crawlWiki() Function")
    graph = crawlWiki(url, nLinks, nDepth)
    print("Progress: Exited crawlWiki() Function")

   
    # Display the Graph
    # pos = nx.circular_layout(graph, scale=3)
    # root = str((BeautifulSoup(requests.get(url).content, "lxml")).find("title"))[7:-20]
    pos=nx.spring_layout(graph,k = 0.004, iterations = 500, scale = 0.6)
    nx.draw(graph, pos=pos, with_labels=True, arrows=True, font_size=4, node_size=600) # , node_color=colors
    plt.savefig('{}.pdf'.format(filename), bbox_inches='tight')

    # Print Done Message
    print("Web Crawling Completed! File was saved as: {}.pdf".format(filename))


