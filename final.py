#!/usr/bin/env python3
# Final Project: Wikipedia Web Crawler
# Names: Allen Duong, Nicole Blandin, William Diedrich

# Imports + Libraries

import os
import sys
import getopt
import requests # For Requesting Website Data
from bs4 import BeautifulSoup
import re # For RegEx
import random
import multiprocessing

# Plotting
import networkx as nx # For Building Complex Networks
import pylab as plt
plt.switch_backend('agg')

# Global Variables + Macros
shorten = lambda url: url[len('https://en.wikipedia.org/wiki/'):]
lengthen = lambda url: 'https://en.wikipedia.org'+url
bad_keys = ['Special', 'Wikipedia', 'Portal', 'Talk', 'Q68', 'index.php', 'Category', 'File', 'Main_Page', 'Help', 'Template', 'Template_talk', ]

# Functions
def usage(status=0):
    print('''Usage: {} [OPTIONS]...
    -h                  Display help message
    -f  SOURCE TARGET   Finds the path to the target from the source Wikipedia Page
    -m                  Map Mode: Build Graph with DEPTH and LINKS and save as PDF
    -d  DEPTH_COUNT     Depth of levels for graph
    -l  LINKS           Links to visit per page
    -n  FILENAME        Name to save the graph PDF as. Default: graph.pdf
    -p  PROCESSES       Number of processes to utilize (1)

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
        urls[lengthen(link)] = ''
    
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

    # Initialize Variables
    SOURCE = "https://en.wikipedia.org/wiki/University_of_Notre_Dame"
    TARGET = "https://en.wikipedia.org/wiki/United_States"
    DEPTH = 3
    LINKS = 3
    MODE = "map"
    FILENAME = 'graph'
    PROCESSES = 1

    # Parse command line arguments
    avg = 0
    args = sys.argv[1:]
    while len(args) and args[0].startswith('-') and len(args[0]) > 1:
        arg = args.pop(0)

        if arg == "-f":
            MODE = "find"
            SOURCE = args.pop(0)
            TARGET = args.pop(0)

        elif arg == "-m":
            MODE = "map"

        elif arg == "-d":
            TARGET = value

        elif arg == "-l":
            LINKS = int(args.pop(0))

        elif arg == "-n":
            FILENAME =  args.pop(0)

        elif arg == "-p":
            PROCESSES = int(args.pop(0))

        elif arg == "-h":
            usage(0)

        else:
            usage(1)

    # TODO: Add case for multiprocessing
    pool = multiprocessing.Pool(PROCESSES)
    
    # DONE: Build the Graph
    print("Progress: Entered crawlWiki() Function")
    graph = crawlWiki(SOURCE, LINKS, DEPTH)
    print("Progress: Exited crawlWiki() Function")

   
    # Display the Graph
    # pos = nx.circular_layout(graph, scale=3)
    # root = str((BeautifulSoup(requests.get(url).content, "lxml")).find("title"))[7:-20]
    pos = nx.drawing.nx_agraph.graphviz_layout(graph, prog='dot')
    nx.draw(graph, pos=pos, with_labels=True, arrows=True, font_size=2, node_size=1000) # , node_color=colors
    plt.savefig('{}.pdf'.format(FILENAME), bbox_inches='tight')

    # Print Done Message
    print("Web Crawling Completed! File was saved as: {}.pdf".format(FILENAME))


