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
import multiprocessing # TODO
from clint.textui import colored, progress, puts

# Plotting
import networkx as nx # For Building Complex Networks
import pylab as plt
plt.switch_backend('agg')

# Global Variables + Macros
shorten = lambda url: url[len('https://en.wikipedia.org/wiki/'):]
lengthen = lambda url: 'https://en.wikipedia.org'+url
bad_keys = ['Special', 'ISO', 'Wikipedia', 'Portal', 'Talk', 'Q68', 'index.php', 'Category', 'File', 'Main_Page', 'Help', 'Template', 'Template_talk', ]
labels = {}
numNodes = 1
# UTILITY FUNCTIONS
def usage(status=0):
    print('''Usage: {} [OPTIONS]...
    -h                  Display help message
    -f  SOURCE TARGET   Finds the path to the target from the source Wikipedia Page
    -m                  Map Mode: Build Graph with DEPTH and LINKS and save as PDF
    -d  DEPTH_COUNT     Depth of levels for graph
    -l  LINKS           Links to visit per page
    -p  PROCESSES       Number of processes to utilize (1)

    '''.format(os.path.basename(sys.argv[0])))
    sys.exit(status)

def is_valid(url):
    if url[:len('/wiki/')] != '/wiki/':
        return False

    if len(url[:len('/wiki/')]) > 8:
        return False

    for key in bad_keys:
        if len(url) < len(key):
            continue
        if key in url:
            return False
    
    if "disambiguation" in url:
        return False

    return True

def getUrls(url):
    r = requests.get(url)
    while r.status_code != 200:
        r = requests.get(url)

    regex = r'<a href="(/wiki/[^"]+)".*</a>'
    urls = []

    for link in re.findall(regex, r.text):
        if is_valid(link):
            urls.append(lengthen(link))
    
    return list(urls)

def pickRandom(urls, num):
    indexes = {}
    while len(indexes) < num:
        indexes[random.randint(0,len(urls)-1)] = ''
    
    newurls = []
    for number in indexes:
        newurls.append(urls[number])
    
    return newurls

# BUILD MAP FUNCTIONS
def crawlWiki(URL='https://en.wikipedia.org/wiki/University_of_Notre_Dame', nLinks=3, nDepth=3):
    global numNodes
    # Create Empty Graph
    G = nx.DiGraph()
    # Get Root Site
    data = BeautifulSoup(requests.get(URL).content, "lxml")
    root = str(data.find("title"))[7:-20]
    # Add First Site to Graph
    labels[root] = numNodes
    numNodes = numNodes + 1
    G.add_node(labels[root])

    exploregraph(URL, G, root, nDepth, nLinks)
	# Return the Graph
    return G

def exploregraph(URL, graph, parent, nDepth, nLinks):
	global numNodes
	if nDepth == 0:
		return
	else:
		nDepth = nDepth-1
	#	create edge to parent
		urls = pickRandom(getUrls(URL),nLinks)
		for link in urls:
			data = BeautifulSoup(requests.get(link).content, "lxml")
			root = str(data.find("title"))[7:-20]
			if root not in labels:
				labels[root] = numNodes
				numNodes = numNodes + 1
				graph.add_node(labels[root])
			graph.add_edge(labels[parent],labels[root])
			exploregraph(link,graph,root,nDepth,nLinks) 								
		return

# FINE PATH FUNCTIONS

# Main Implementation
if __name__ == '__main__':

    # Initialize Variables
    SOURCE = "https://en.wikipedia.org/wiki/University_of_Notre_Dame"
    TARGET = "https://en.wikipedia.org/wiki/United_States"
    DEPTH = 3
    LINKS = 2
    MODE = "map"
    FILENAME = 'graph'
    PROCESSES = 1

    # Parse command line arguments
    avg = 0
    args = sys.argv[1:]
    while len(args) and args[0].startswith('-') and len(args[0]) > 1:
        arg = args.pop(0)

        if arg == "-f":
            MODE = "map"
            SOURCE = args.pop(0)

        elif arg == "-m":
            MODE = "map"

        elif arg == "-d":
            DEPTH = int(args.pop(0))

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
    
    # TODO: Implement Shortest Path Finder ()
    if MODE == "find":
        puts(colored.blue('Finding Path...'))
        graph = crawlWiki(SOURCE, LINKS, DEPTH)
        count = 1

        # TODO: Modify Links to Get Titles (Copy from Crawlwiki())
        for i in nx.shortest_path(graph, source=SOURCE, target=TARGET):
            print ("\t" + str(count) + ". " + i)
            count += 1

    elif MODE == "map":

        puts(colored.blue('Drawing Map...'))
        # DONE: Build the Graph
        puts(colored.green("Progress: Entered crawlWiki() Function"))
        graph = crawlWiki(SOURCE, LINKS, DEPTH)
        puts(colored.green("Progress: Exited crawlWiki() Function"))



        pos = nx.drawing.nx_agraph.graphviz_layout(graph, prog='dot')
        nx.draw(graph, pos=pos, with_labels=True, arrows=True, font_size=6, node_size=4570/pow(LINKS,DEPTH)) # , node_color=colors
        plt.savefig('{}.pdf'.format(FILENAME), bbox_inches='tight')
        for a in sorted(labels.keys(),key=labels.get):
            print(str(labels[a]) + ": " + a)
        # Print Done Message
        puts(colored.blue("Web Crawling Completed! File was saved as: {}.pdf".format(FILENAME)))


