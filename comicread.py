#!/usr/bin/python

import os
import cgi
import cgitb; cgitb.enable()
import sqlobject
from model import *
from constants import *
from common_utils import *

def printHeader( page ):
    print "Content-type: text/html\n\n"

    title = page.title + ": Yuki Hoshigawa and the Scariest Thing in the World"
    print MIGHTY_HEAD_CHUNK % ( title, CSS_FILE )

    # Print the body tag, applying color:
    if page.bgColor != None:
	print COLOR_BODY_CHUNK % page.bgColor
    else:
	print BODY_CHUNK


def getPage( form ):
    """
    Returns an sql ComicPage object.
    If there is a cgi argument called page, it will tell us the page
    sequence number; attempt to select that page from the DB.
    If there's no argument, or if a nonexistent page is requested,
    default to the most recent page.
    Attatches attributes "nextPageNum" and "prevPageNum" to the returned
    object, which are integers if there is such a page, or None if there
    is not.
    """
    pages =  ComicPage.select( orderBy = "-sequence" )
    lastPage = pages[0]
    lastPageNum = lastPage.sequence

    if form.has_key('page'):
	pageNum = int( form['page'].value )
	pages = ComicPage.selectBy( sequence = pageNum )
        if pages.count() != 0:
            page = pages[0]
	    # We found the page; figure out numbers of
	    # next page and previous page.
	    pageNum = page.sequence
	    if pageNum == 0:
		page.prevPageNum = None
	    else:
		page.prevPageNum = pageNum - 1
	    if pageNum == lastPageNum:
		page.nextPageNum = None
	    else:
		page.nextPageNum = pageNum + 1
	    page.lastPageNum = lastPageNum
	    return page

    # if we got to here, there was either no page number, or a
    # bogus one, so return the last page.
    page = lastPage
    if lastPageNum == 0:
	page.prevPageNum = None
    else:
	page.prevPageNum = lastPageNum - 1
    # since this is the last page, there's no next:
    page.nextPageNum = None
    page.lastPageNum = lastPageNum
    
    return page


def getCustomPanelHtml( customPanels, thisPanelNum ):
    for customPanel in customPanels:
	if customPanel.panelNum == thisPanelNum:
	    return customPanel.customHtml
    return None

def printComic( page ):
    """
    page is the sql ComicPage object
    """

    # TODO need a div around all the panels??

    # If the page has custom HTML, print that and done:
    if page.customHtml != None:
	print page.customHtml
	return

    # Otherwise, loop through panels:
    customPanels = CustomPanel.selectBy( pageRef = page.id )
    customPanels = list( customPanels )
    for panelNum in range( 1, page.numPanels + 1 ):
	print '<div class="frame">'

	# Check if there's a custom panel entry for this number:
	customHtml = getCustomPanelHtml( customPanels, panelNum )
	if customHtml != None:
	    print customHtml
	# Otherwise, here's the default:
	else:
	    panelFile = "%s_00%d%s" % ( page.baseImageFile,
					panelNum,
					page.suffix )
	    panelPath = os.path.join( BASE_PATH, panelFile )
	    print IMAGE_CHUNK % panelPath

	print '</div>'


def printNavButtons( page ):
    """
    page is the sql ComicPage object; it must have already had
    prevPageNum and nextPageNum attributes attatched; this should
    have been done by getPage.
    """

    print '<br clear="all"/>'
    print '<div class="menu">'


    if page.prevPageNum != None: 
	print PREV_BUTTON_CHUNK % page.prevPageNum

    print CONTENTS_BUTTON_CHUNK

    if page.nextPageNum != None:
	print NEXT_BUTTON_CHUNK % page.nextPageNum

    print MORE_BUTTONS_CHUNK

    print CREATIVE_COMMONS_IMG_CHUNK

    print "<br>"
    print INFO_CHUNK % ( page.sequence,
			 page.lastPageNum,
			 str(page.publishDate ) )
    print '<br clear="all"/>'
    print "</div>"

def printComments( page ):
    comments = ComicComment.selectBy( pageRef = page.id )

    print TOP_OF_COMMENTS_CHUNK
    for comment in comments:
	authorText = comment.commenter
	authorImg = ""

	authors = User.selectBy( username = comment.commenter )
	if authors.count() != 0:
	    author = authors[0]
	    if author.link:
		authorText = COMMENTER_LINK_CHUNK % { "name": author.username,
						      "link" : author.link }
	    if author.icon:
		authorImg = COMMENTER_ICON_CHUNK % author.icon
	    print COMMENT_CHUNK % { "authorText": authorText,
				    "subject": comment.subject,
				    "date": str(comment.postDate),
				    "words": comment.words,
				    "link": author.link,
				    "authorImg": authorImg  }
    print '</div>'


def printCommentForm( page, form ):
    """
    If there is a cookie identifying the user already, read username from
    that cookie, print only subject/words.
    
    If there is not a cookie identifying the user, print also input boxes
    for username/password.
    """
    if form.has_key("errorMsg"):
	errorMsg = form["errorMsg"].value
    else:
	errorMsg = ""

    cookie = getCookie()
    if cookie.has_key("blogin"):
	print LOGGED_IN_COMMENT_FORM_CHUNK % {
	    "pageId" : page.id,
	    "pageSequence" : page.sequence,
	    "defaultTitle": "",
	    "defaultText": "",
	    "defaultUsername" : cookie["blogin"].value,
	    "errorMsg" : errorMsg
	    }   
    else:
	print COMMENT_FORM_CHUNK % {
	    "pageId" : page.id,
	    "pageSequence" : page.sequence,
	    "defaultTitle": "",
	    "defaultText": "",
	    "defaultUsername" : "",
	    "errorMsg" : errorMsg
	    }
	
def printFooter():
    print CREATIVE_COMMONS_TEXT_CHUNK
    print "</body></html>"

def incrementViewCounter( page ):
    page.views = page.views + 1


if __name__ == "__main__":
    form = cgi.FieldStorage()
    page = getPage( form )
    printHeader( page )

    if not form.has_key( "nonav" ):
	printNavButtons( page )
    printComic( page )
    if not form.has_key( "nonav" ):
	printNavButtons( page )
	printComments( page )
	printCommentForm( page, form )
    printFooter()
    incrementViewCounter( page )
	


# TODO:



# Calliagraphy of title
# Integrate index.cgi into contents.html.
# implement the "public-private" distinction

# Have settings on whether
# index.cgi should show at the chapter level, scene level, or individual
# comic level?

# put the fullText somewhere invisibly in the page source
# clean up the relevant directories, remove cruft, security settings

# Script to upload a comic (makes the correct sequence entry in db etc.)
# Script to publicize a comic (runs automatically sunday midnight, adds to
# rss feed, etc)

# Write characters, about pages

# Make an evilbrainjono site front page.  Establish links in all
# directions between front page, blog, and comic.  Front page could
# perhaps include the rss summary of the latest blog post, the latest blog
# comment (not neccessarily same post), the most recent comic -- in full?
# in an iframe?  and permanent links to Humanized, UCJAS, Aikikai...
# basically my front page would be an aggregator.


