import os

# Path constants:
BASE_PATH = "/images/yuki"
CSS_FILE = os.path.join( BASE_PATH, "comic_styles.css" )

# Constant HTML chunks:

# TODO move all this to the template system

MIGHTY_HEAD_CHUNK = """
<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
<head>
<title>%s</title>
<link rel="stylesheet" type="text/css" href="%s" />
</head>
"""
COLOR_BODY_CHUNK = """
<body class="comic" bgcolor="%s">
"""
BODY_CHUNK = """
<body class="comic">
"""
IMAGE_CHUNK = """
<img src="%s" alt="This is a panel." />
"""
PREV_BUTTON_CHUNK = """
<a href="/yuki/%d">
<img src="/images/yuki/modoru.png" alt="Prev page" class="menu" /></a>
"""
NEXT_BUTTON_CHUNK = """
<a href="/yuki/%d">
<img src="/images/yuki/susumu.png" alt="Next page" class="menu" /></a>
"""
CONTENTS_BUTTON_CHUNK = """
<a href="/images/yuki/contents.html">
<img src="/images/yuki/mokuhyoh.png" alt="Contents" class="menu" /></a>
"""
MORE_BUTTONS_CHUNK = """
<a href="/yuki">Latest</a> |
<a href="/blog">Weblog</a> |
<a href="/yuki.rss">Subscribe (RSS)</a>
"""
INFO_CHUNK = """
<small>Page %s / %s, %s</small>.
"""
INDEX_TABLE_ROW = """
<tr><td><a href="/yuki/%d">%s</a></td><td>%s</td></tr>
"""
INDEX_TABLE_HEADER = """
<table>
<tr><th>Comic</th><th>Publiation date</th></tr>
"""
INDEX_TABLE_FOOTER = """
</table>
"""
INDEX_BODY_CHUNK = """
<body class="index">
"""

NONEXISTENT_LINKS = """
<a href="/yuki/about.html">About</a> | 
<a href="/yuki/characters.html">Characters</a> | 
"""

COMMENT_CHUNK = """
<table><tr><td rowspan=2 valign=top>
%(authorText)s<br>
%(date)s<br>
%(authorImg)s</td>
<th>%(subject)s</th></tr>
<td>%(words)s</td>
</tr></table><hr>
"""

COMMENTER_ICON_CHUNK = """
<img src="/images/commenters/%s" class="commenter" width="100" height="100">
"""

COMMENTER_LINK_CHUNK = """
<a href="%(link)s">%(name)s</a>
"""

TOP_OF_COMMENTS_CHUNK = """
<div class="comments"/>
<h3>Comments</h3>(Cliches Commentary Controversy Chatter chit chat chit chat chit chat Conversation Contradiction Criticism...)
"""

COMMENT_FORM_CHUNK = """
<div class="comment_form">
<a name="comment_form" />
<form action="/leave-comic-comment.py" method="POST">
<h2>Leave A Comment:</h2>
<h2 class="error">%(errorMsg)s</h2>
<input type="hidden" name="pageId" value="%(pageId)d" />
<input type="hidden" name="pageSequence" value="%(pageSequence)d" />
Title:<input type="text" name="title" value="%(defaultTitle)s" size=32 />
<br />
<br />
<textarea name="message" rows=10 cols=64>%(defaultText)s</textarea><br />
Username: <input type="text" name="username" value="%(defaultUsername)s" />
<br />
Password: <input type="password" name="password" />
<br />
<input type="submit" value="Execute!!"/>
</form>
</div>
"""

LOGGED_IN_COMMENT_FORM_CHUNK = """
<div class="comment_form">
<a name="comment_form" />
<form action="/leave-comic-comment.py" method="POST">
<h2>Hello, %(defaultUsername)s</h2>
<h2>Leave A Comment:</h2>
<h2 class="error">%(errorMsg)s</h2>
<input type="hidden" name="pageId" value="%(pageId)d" />
<input type="hidden" name="pageSequence" value="%(pageSequence)d" />
Title:<input type="text" name="title" value="%(defaultTitle)s" size=32 />
<br />
<br />
<textarea name="message" rows=10 cols=64>%(defaultText)s</textarea><br />
<input type="submit" value="Execute!!"/>
</form>
</div>
"""
CREATIVE_COMMONS_IMG_CHUNK = """
<div style="float:right">
<a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/">
<img alt="Creative Commons License" style="border-width:0" src="http://creativecommons.org/images/public/somerights20.png" />
</a></div>
"""

CREATIVE_COMMONS_TEXT_CHUNK = """
<div style="font-size:10pt;text-align:center;">
<span xmlns:dc="http://purl.org/dc/elements/1.1/" href="http://purl.org/dc/dcmitype/StillImage" property="dc:title" rel="dc:type">Yuki Hoshigawa and the Scariest Thing in the World</span> by 
<a xmlns:cc="http://creativecommons.org/ns#" href="http://www.evilbrainjono.net" property="cc:attributionName" rel="cc:attributionURL">Jono S. Xia</a> is licensed under a 
<a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/">Creative Commons Attribution-Share Alike 3.0 Unported License</a>.</div>
"""
