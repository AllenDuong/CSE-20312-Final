#!/usr/bin/env python3
# Final Project: Wikipedia Web Crawler
# Names: Allen Duong, Nicole Blandin, William Diedrich

# Imports + Libraries

import multiprocessing
import os
import requests # For Requesting Website Data
import sys 
import time # Add Delay to Prevent DOS on Wiki Servers
from bs4 import BeautifulSoup
import re # For RegEx
import networkx as nx # For Building Complex Networks

<title>University of Notre Dame - Wikipedia</title>

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

# This Funtion Scrapes Wikipedia and Build the Graph
def crawlWiki(URL='https://en.wikipedia.org/wiki/University_of_Notre_Dame', nLinks=3, nDepth=3):

    # Create Empty Graph
    G = nx.Graph()

    # Get Root Site
    data = BeautifulSoup(requests.get(URL).content)
    root = str(data.find("title"))[7:-20]

    # Add First Site to Graph
    G.add_node(root)

    # Get nLinks Links from Page
    urls = getUrls(URL)
        #TODO: Add function that gets nLink links

    # TODO: Loop Through nLinks
    for i in range(0, nDepth):
        
        # TODO: 


    # Return the Graph
    return G

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

    # TODO: Multiprocessing
    # Create pool of workers and perform requests
    # pool = multiprocessing.Pool(PROCESSES)
    # pavg = pool.map(do_request, range(PROCESSES))
    # pass

