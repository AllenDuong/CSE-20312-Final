#!/usr/bin/env python
# scraper.py
#
# Wikipedia Scraper

# Modules
# ------------------------------------------------------------------------------

import request
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import networkx as nx
from clint.textui import colored, progress, puts
import getopt
import sys
import os
import multiprocessing
from multiprocessing import Queue

# Global Variables
# ------------------------------------------------------------------------------

G = nx.DiGraph()
shorten = lambda url: url[len('https://en.wikipedia.org/wiki/'):]
lengthen = lambda url: 'https://en.wikipedia.org'+url
bad_keys = ['Special', 'Wikipedia', 'Portal', 'Talk', 'Q68', 'index.php', 'Category', 'File', 'Main_Page', 'Help', 'Template', 'Template_talk', ]
mpQ = Queue()

# Utility Functions
# ------------------------------------------------------------------------------

def is_valid(url):
    if url[:len('/wiki/')] != '/wiki/':
        return False
    shortened = url[len('/wiki/'):]
    for key in bad_keys:
        if len(shortened) < len(key): continue
        if shortened[:len(key)] == key: return False
    if "disambiguation" in url: return False
    return True

def get_url_list(page='https://en.wikipedia.org/wiki/Computer'):
    urls = []
    req = urllib2.Request(page, headers={'User-Agent': "Magic Browser"})
    con = urllib2.urlopen(req)
    soup = BeautifulSoup(con.read(), 'html.parser')
    con.close()
    for i in soup.find_all('a', href=True):
        urls.append(i['href'])
    return filter(is_valid, urls)


def mp_helper_dfs(search_url, max_count):
    found_urls = list(map(lengthen, get_url_list(search_url)))[:max_count]
    found_urls.append(search_url)
    mpQ.put(found_urls)


def dfs_map_pl(start_url='https://en.wikipedia.org/wiki/Computer', max_count=2, max_depth=2, threads=16):
    # we call this a depth first traversal, but it is not a true depth traversal like our recursive implementation, due to the parallel nature
    # we take advantage of the cyclical, infinite nature of wikipedia in our implementation
    G.add_node(start_url)
    stack, visited, buffer = list(map(lengthen, get_url_list(start_url)))[:max_count], set(), set()
    visited.add(start_url)
    for child in stack:
        G.add_edge(start_url, child)
    count = 0
    while stack:
        to_process = min(len(stack), threads)
        subset = [(stack.pop(-1), max_count) for _ in range(to_process)]
        for search_url in subset:
            visited.add(search_url)

        p = multiprocessing.Pool(to_process)
        p.map(mp_helper_dfs, subset)

        for i in range(to_process):
            links = mpQ.get()
            children, parent = links[:-1], links[-1]
            for child in children: G.add_edge(parent, child)
            for link in children: buffer.add(link)

        if not stack:
            stack = list(buffer)
            buffer = set()
            count += 1
            if count >= max_depth-1:
                return


def rec_dfs_draw_graph(parent_url, child_urls, depth_count, max_count=2, max_depth=2):
    for count, url in enumerate(child_urls):
        if count >= max_count: break
        G.add_node(shorten(url))
        G.add_edge(shorten(parent_url), shorten(url))
        if depth_count < max_depth-1:
            rec_dfs_draw_graph(url, map(lengthen, get_url_list(url)), depth_count+1, max_count=max_count, max_depth=max_depth)


def mp_helper_bfs(search_url, search_page):
    found_urls = list(map(lengthen, get_url_list(search_url)))
    found_urls.append(search_url)
    mpQ.put(found_urls)


def bfs_search_url_pl(start_page='https://en.wikipedia.org/wiki/Computer', search_page='https://en.wikipedia.org/wiki/United_States', threads=16):
    G.add_node(start_page)
    search_urls = map(lengthen, get_url_list(start_page))
    for url in search_urls:
        G.add_edge(start_page, url)
    visited, queue = set(), search_urls
    count = 0
    while queue:
        subset = [(queue.pop(0), search_page) for _ in range(threads)]
        for search_url in subset:
            G.add_node(search_url[0])
            visited.add(search_url[0])
            count += 1

        p = multiprocessing.Pool(threads)
        p.map(mp_helper_bfs, subset)

        for i in range(threads):
            found = mpQ.get()
            parent = found[-1]
            children = found[:-1]
            for child in children:
                G.add_edge(parent, child)
            queue.extend(filter(lambda x: x not in visited, children))

        if search_page in queue:
            return

def bfs_search_url(start_page='https://en.wikipedia.org/wiki/Computer', search_page='https://en.wikipedia.org/wiki/United_States'):
    G.add_node(start_page)
    search_urls = map(lengthen, get_url_list(start_page))
    for url in search_urls:
        G.add_edge(start_page, url)
    visited, queue = set(), search_urls
    count = 0
    while queue:
        search_url = queue.pop(0)
        count += 1
        G.add_node(search_url)
        if search_url not in visited:
            visited.add(search_url)
            found_urls = map(lengthen, get_url_list(search_url))
            for url in found_urls:
                G.add_edge(search_url, url)
            if search_page in found_urls:
                return
            queue.extend(found_urls)

def get_url_dict(starting_url='https://en.wikipedia.org/wiki/Computer', max_depth=2, max_count=2):
    G.add_node(shorten(starting_url))
    urls = map(lengthen, get_url_list(starting_url))
    #time.sleep(random.randint(2, 10))
    rec_dfs_draw_graph(starting_url, urls, 0, max_depth=max_depth, max_count=max_count)

def usage(exit_code=0):
    print >> sys.stderr, '''Usage: scraper.py [OPTION]...

Options:
        -f  scraper.py SOURCE TARGET
            Finds the path to the target from the source Wikipedia page.
        -s  SOURCE
        -t  TARGET
        -T  threads

        -m  scraper.py DEPTH_COUNT NUM_PAGES_FROM_SOURCE
            Maps Wikipedia links based on the depth count and limits the number of pages from the page.
        -d  DEPTH_COUNT
        -n  NUM_PAGES_FROM_SOURCE
        -T  Threads
'''.format(os.path.basename(sys.argv[0]))
    sys.exit(exit_code)

# Main Execution
# ------------------------------------------------------------------------------

if __name__ == "__main__":

    # Initialize Variables
    SOURCE = "https://en.wikipedia.org/wiki/Computer"
    TARGET = "https://en.wikipedia.org/wiki/United_States"
    DEPTH_COUNT = 3
    NUM_PAGE = 3
    MODE = "map"
    fig, ax = plt.subplots()
    threads=16

    # Parse Command-Line Arguments:
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "fms:t:d:n:T:")
    except getopt.GetoptError as e:
        usage(1)

    for option, value in options:
        if option == "-f":
            MODE = "find"
        elif option == "-s":
            SOURCE = value
        elif option == "-t":
            TARGET = value
        elif option == "-m":
            MODE = "map"
        elif option == "-d":
            DEPTH_COUNT = int(value)
        elif option == "-n":
            NUM_PAGE = int(value)
        elif option == "-T":
            threads = int(value)
        elif option == "-h":
            usage(0)

    if MODE == "find":
        puts(colored.blue('Finding Path...'))
        if threads > 1:
            bfs_search_url_pl(SOURCE, TARGET, threads)
        else:
            bfs_search_url(SOURCE, TARGET)
        count = 1
        for i in nx.shortest_path(G, source=SOURCE, target=TARGET):
            print ("\t" + str(count) + ". " + i)
            count += 1
    elif MODE == "map":
        if threads > 1:
            dfs_map_pl(SOURCE, max_count=NUM_PAGE, max_depth=DEPTH_COUNT, threads=threads)
        else:
            get_url_dict(SOURCE, max_depth=DEPTH_COUNT, max_count=NUM_PAGE)

        puts(colored.blue('Drawing Map...'))
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        nx.draw(G, pos=pos)
        nx.draw_networkx_labels(G, pos=pos)
        plt.draw()
        plt.show(block=False)

    sys.exit(0)
