#!/usr/local/bin/python

import cgi
import cgitb; cgitb.enable()
import sqlobject
from model import *
from constants import *

"""
This comic has three meaningful levels of hierarchy:
the chapter
the scene
the page/strip.
So far there's just one chapter, and each splash page defines a
scene.
I guess the only meaningful thing about scenes is, what sequence
number do they start at?  And what are they called?  And do they have
a summary?  A summary which is more likely to be used for nihongo puns
and prog rock references than actual summary?


Since I include the full text of each comic as metadata, I can totally
have a search-by-text function on this page.
"""

def printHeader():
    print 'Content-type: text/html\n\n'
    title = "Yuki Hoshigawa and the Scariest Index in the World"
    print MIGHTY_HEAD_CHUNK % ( title, CSS_FILE )
    print INDEX_BODY_CHUNK

def printPageTable( pages ):
    print INDEX_TABLE_HEADER
    for page in pages:
	print INDEX_TABLE_ROW % ( page.sequence,
				  page.title,
				  str( page.publishDate ) )
    print INDEX_TABLE_FOOTER

def printFooter():
    print "</body></html>"

if __name__ == "__main__":
    pages = Page.select( orderBy = "sequence" )
    printHeader()
    printPageTable( pages )
    printFooter()
