#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from lxml import html
from requests import get
from re import compile
from colorama import Fore, Style

#=============[ read wordlist ]=================================================

folder = 'ipenama'
input = open(os.path.join(folder, sys.argv[1] + '.hyph'))
words = input.read().splitlines()
input.close()

#=============[ clean wordlist ]================================================

# suppress math
words = map(lambda x: compile('\$.*?\$').sub('', x), words)
# suppress non-word, digits and whitespace characters
words = map(lambda x: compile('\W|\d|\s').sub('', x), words)
# make everything lowercase
words = map(lambda x: x.lower(), words)
# filter empty words
words = filter(lambda x: x is not '', words)
# remove duplicates and sort alphabetically
words = sorted(list(set(words)))

#=============[ open and initialize output files ]==============================

# unsuccesful matches
log_err = open('ipenama/ipenama.err','w')
# inexact or duplicate matches
log_dup = open('ipenama/ipenama.dup','w')
# successful matches
log_tex = open('ipenama/ipenama.tex','w')
print("\\hyphenation{", file=log_tex)

#=============[ define search routine ]=========================================

# using Merriam Webster dictionary
def search(word):
    url = 'http://www.merriam-webster.com/dictionary/' + word
    response = get(url)
    tree = html.fromstring(response.content)
    syllables = tree.xpath('normalize-space((//*[@class="word-syllables"])[1]/text())')
    control = syllables.replace(u'·','')
    return syllables, control

#=============[ process wordlist ]==============================================

found = []
N = len(words)
for i, word in enumerate(words):
    syllables, control = search(word)
    if control == word and word not in found:
        print("{:>4} of {:>4}: {}✓ {}{}"
            .format(i+1,N,Fore.GREEN,syllables,Style.RESET_ALL))
        print(syllables.replace(u'·','-'), file=log_tex)
        found.append(word)
    elif syllables:
        print("{:>4} of {:>4}: {}? {} ({}){}"
            .format(i+1,N,Fore.YELLOW,word,syllables,Style.RESET_ALL))
        print(word, file=log_dup)
    else:
        print("{:>4} of {:>4}: {}✗ {}{}"
            .format(i+1,N,Fore.RED,word,Style.RESET_ALL))
        print(word, file=log_err)

#=============[ finalize and close output files ]===============================

print("}", file=log_tex)
log_tex.close()
log_dup.close()
log_err.close()

