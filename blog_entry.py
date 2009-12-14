import re
import cgi
import cgitb
import datetime
from common_utils import *
from model import *

cgitb.enable()

def make_form(type, original, editid, username):
    default_text = ""
    default_title = ""
    if type == "editentry":
        oldEntry = get_old_entry(editid)
        default_text = oldEntry.words
        default_title = oldEntry.title
    dict = {"type": type,
            "original": original,
            "editid": editid,
            "title": default_title,
            "text": default_text,
            "extras": ""}
    extrasHtml = ""
    # This part is only for when I'm making an entry, not for comments:
    if type == "entry" and username == "Jono":
        extrasHtml += render_template_file( "more_message.html", {} )
        dict["extras"] = extrasHtml
    return render_template_file ( "entry_form.html", dict )

def get_old_entry(id):
    return BlogEntry.selectBy(id = id)[0]

def print_original_entry(id):
    # Slight duplication of code here.
    entry = get_old_entry(id)
    commentsHtml = show_comments_for_entry(id)
    entryHtml = render_template_file( "blog_entry.html", { "id": entry.id,
                                                          "title": entry.title,
                                                          "date": entry.date.strftime("%a, %d %b %Y %H:%M") ,
                                                          "words": entry.words,
                                                          "commentarea": commentsHtml,
                                                          "features": "",
                                                          "tagpics": ""})
    return entryHtml

def add_submission(q, username, type, original):
    if q.has_key("message"):
        words = q["message"].value
    else:
        words = ""
    if q.has_key("more_message"):
        more_words = q["more_message"].value
    else:
        more_words = ""
    if q.has_key("title"):
        title = q["title"].value
    else:
        title = ""

    if username == "Jono" and type == "entry":
        fullText = html_clean(words) + html_clean(more_words)
        kwargs = {"date": datetime.datetime.now(),
                  "title": title,
                  "public": True,
                  "words": fullText}
        newEntry = BlogEntry(**kwargs)
        if q.has_key("tags"):
            tagNames = q["tags"].value.split(",")
            for tagName in tagNames:
                tagName = tagName.strip(" ")
                blogTag = BlogTag.selectBy( name = tagName )
                if blogTag.count() == 0:
                    blogTag = BlogTag( name = tagName )
                else:
                    blogTag = blogTag[0]
                EntryToTagLink(entry = newEntry.id, tag = blogTag.id)

        link = "http://evilbrainjono.net/blog#%d" % newEntry.id
        if len(more_words) > 0:
            message = "\n\n This post was really long, so I snipped it.  Read the rest at http://evilbrainjono.net."
        else:
            message = "\n\n<a href=\"http://www.evilbrainjono.net/blog/new?type=comment&original=%d#form\">Leave a comment</a>" % newEntry.id

        update_rss( title, words + message, link, RSS_FILE )

    elif type == "comment":
        original = int(original)
        words = clean_commenter_html(words)
        words = html_clean(words)
        newEntry = BlogComment(author = username, title = title, words = words,
                               date = datetime.datetime.now(),
                               original_post = original)
        originalPost = BlogEntry.selectBy( id = original )[0]
        longTitle = "%s by %s in response to %s" % (title, username, originalPost.title)
        link = "http://www.evilbrainjono.net/blog?showcomments=true#%dc" % original
        message = "\n\n<a href=\"http://www.evilbrainjono.net/blog/new?type=comment&original=%d#form\">Leave a comment</a>" % original
        update_rss(longTitle, words + message, link, RSS_COMMENTS_FILE)

def commit_edit(q, username, editid):
    if username == "Jono":
        words = html_clean(q["message"].value)
        theEntry = get_old_entry(editid)
        theEntry.words = words

def clean_commenter_html(text):
    text = re.sub(r"<(/?[^bi/].*?)>", r"&lt;\g<1>!&lt;", text)
    regexp = re.sub(r"(http://[\w\./%=&\?\-#]+)\b", 
                    r'<a href="\g<1>">\g<1></a>', 
                    text)
    
    numBoldStarts = len(re.findall("<b>", text)) - len(re.findall("</b>", text))
    numItalicStarts = len(re.findall("<b>", text)) - len(re.findall("</b>", text))

    while numBoldStarts > 0:
        text = text + "</b>"
        numBoldStarts -= 1
    while numItalicStarts > 0:
        text = text + "</i>"
        numItalicStarts -= 1
    return text

def html_clean(text):
    text = re.sub( r"\r?\n\r?\n", r"</p><p>", text)
    # TODO The following hack is supposed to replace " with &quot; except
    # inside html tags, but is known to interact weirdly with my
    # relative/absolute link handling code to sometimes break external links
    # that come after quotes in the input.
    text = re.sub(r'<(.*?)"(.*?)"(.*?)>',
                  r"<\1QUOT_INSIDE_TAG_HAXXOR\2QUOT_INSIDE_TAG_HAXXOR\3>", 
                  text)
    text = re.sub(r'"', r'&quot;', text)
    text = re.sub(r'QUOT_INSIDE_TAG_HAXXOR', r'"', text)
    return text

def get_current_arpadate():
    date = datetime.datetime.now()
    # Must produce time in a string like this:
    #  <pubDate>Sun, 4 Jan 2009 03:00:00 GMT</pubDate>
    # TODO account for daylight savings time (PDT instead of PST).
    return date.strftime("%a, %d %b %Y %H:%M:%S GMT") 


def update_rss(title, description, link, rssFile):
    title = rssclean(title)
    description = rssclean(description)
    arpadate = get_current_arpadate()
    
    xml = """
<item><title>%s</title>
<description><![CDATA[%s]]></description>
<link>%s</link>
<pubDate>%s</pubDate></item>""" % (title, description, link, arpadate)
    infile = open(rssFile, "r")
    outputFeed = ""
    numItems = 0
    for line in infile.readlines():
        if "<lastBuildDate>" in line:
            outputFeed += "      <lastBuildDate>%s</lastBuildDate>\n" % arpadate
        else:
            outputFeed += line
        if "</webMaster>" in line:
            outputFeed += xml
        if "</item>" in line:
            numItems += 1
            if numItems == 12:
                outputFeed += "\n</channel></rss>\n"
                break
    infile.close()
    outfile = open(rssFile, "w")
    outfile.write(outputFeed)
    outfile.close()

def rssclean(input):
    # TODO try keeping links intact in RSS, actually?
    urlprefix = "http://evilbrainjono.net/"
    # replace external links with urls
    regexp = re.compile("""<(a href|img src)="(http:.+?)">""")
    input = regexp.sub("(\g<2>) ", input)
    # replace internal links with absolute urls
    regexp = re.compile("""<(a href|img src)="(.+?)">""")
    input = regexp.sub("(" + urlprefix + "\g<2>) ", input)
    # replce literal quotes with &quot.
    input = re.compile('"').sub("&quot;", input)
    # Strip out all remaining html tags, replace with spaces.
    input = re.compile("<[^>]+?>").sub(" ", input) 
    return input


def printBlogEntryForm():
    # TODO if user isn't already logged in, allow them to enter their username/password
    # right here on this form along with their comment, instead of going through a separate
    # login step.
    q = cgi.FieldStorage()

    cookie = getCookie()
    if cookie.has_key("blogin"):
        username = cookie["blogin"].value
    else:
        username = None

    if q.has_key("type"):
        type = q["type"].value
    else:
        type = None
    if q.has_key("original"):
        original = q["original"].value
    else:
        original = None
    if q.has_key("editid"):
        editid = q["editid"].value
    else:
        editid = None

    if not username:
        print_redirect(LOGIN_PAGE_URL)

    if q.has_key("submission"):
        if type == "editentry":
            commit_edit(q, username, editid)
        else:
            add_submission(q, username, type, original)
        print_redirect("/blog")

    if (type == "entry" or type == "editentry") and username != "Jono":
        print_redirect("/blog")

    contentHtml = ""
    if type == "comment":
        contentHtml += "<h2>" + username + " is adding a comment.  Below is the original blog entry.  Below that is the comment form.</h2>"
        contentHtml += print_original_entry(original)
    elif type == "editentry":
        contentHtml +=  "Jono is editing old entry id " + editid + " : "
    else:
        contentHtml += "Jono is making a new entry: "

    contentHtml += make_form(type, original, editid, username)
    
    print render_template_file("blog.html", {"title": "Jono's Natural Log -- Leave Comments",
                                             "contents": contentHtml,
                                             "navigation": "",
                                             "archivelinks": "",
                                             "actionlinks": "",
                                             "categorylinks": ""
                                             })


if __name__ == "__main__":
    printBlogEntryForm()
