#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests_html
from colorconsole import terminal
from collections import defaultdict
import re

import argparse
parser = argparse.ArgumentParser(description='#   hn-tops-topics - Scrap the tops HN news and filters by topics\n'
                                             '#\n'
                                             '#   Author:  @jupachuy - github.com/jpchavat', prog='hn-tops-topic\n')
parser.add_argument('-p', '--max-pages', help='maximum amount of pages to scrap', default=3, type=int)
parser.add_argument('-n', '--max-news', help='maximum amount of news to scrap', default=15, type=int)
parser.add_argument('keywords', help='list of keywords to search while scrapping')
args = parser.parse_args()

#KEYWORDS = 'python,golang,bitcoin,ripple,xrp,stellar,xlm,crypto,uruguay'
KEYWORDS = args.keywords.split(',')
MAX_PAGES = args.max_pages
MAX_NEWS = args.max_news

def itruncate(string, width):
    if len(string) > width:
        string = string[:width-3] + '...'
    return string

# Screen confs
screen = terminal.get_terminal()
screen.clear()
screen.set_title("HN tops topics")
current_line = 0
def get_current_line():
    global current_line
    current_line += 1
    return current_line

# Print title
screen.xterm256_set_bk_color(208)
screen.xterm256_set_fg_color(234)
screen.print_at(0, get_current_line(), "|-----------------|")
screen.print_at(0, get_current_line(), "|  HN tops topics |")
screen.print_at(0, get_current_line(), "|_________________|")
screen.underline()
get_current_line()
screen.print_at(0, get_current_line(), "Topic(s): %s" % " - ".join(KEYWORDS))
get_current_line()
screen.reset()

session = requests_html.Session()

# Build the regex with keywords
topics_regex = r"\b{}".format("|\\b".join(KEYWORDS))

# Scrap the web
topic_news_amount = 0
topic_news = defaultdict(list)
page = 1
while page <= MAX_PAGES and topic_news_amount < MAX_NEWS:
    r = session.get('https://news.ycombinator.com/news?p=%s' % page)
    news = ((x.text, x.absolute_links.pop()) for x in r.html.find('.storylink'))

    for title, link in news:
        if topic_news_amount == MAX_NEWS:
            break
        topic_matches = list(re.finditer(topics_regex, title, re.IGNORECASE))
        #print("Finding '{}' in '{}'".format(topics_regex, title))
        if topic_matches:
            for topic in (x.group(0) for x in topic_matches):
                topic_news[topic.upper()].append((title, link, page))
            topic_news_amount += 1

    page += 1

# Print the results
for topic, news in topic_news.items():
    screen.xterm256_set_bk_color(208)
    screen.xterm256_set_fg_color(234)
    screen.print_at(0, get_current_line(), topic.upper())
    screen.reset()
    for num, (title, link, page) in enumerate(news):
        line_to_write = get_current_line()
        txt = "{:>3d} [P{:>2d}] ".format(num + 1, page)
        screen.print_at(1, line_to_write, txt)
        col = len(txt) + 1
        txt = "{:<50s}   ".format(itruncate(title, 50))
        screen.print_at(col, line_to_write, txt)
        col += len(txt)
        txt = "{}".format(link)
        screen.print_at(col, line_to_write, txt)
    get_current_line()

screen.print_at(0, get_current_line(), "END.\n")
screen.reset()
