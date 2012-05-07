from sqlobject import *
from blog_config import DB_URL
import datetime

connection = connectionForURI( DB_URL )
sqlhub.processConnection = connection

# Blog
class BlogEntry( SQLObject ):
    class sqlmeta:
        table = "entries"
        defaultOrder = "-date"
    date = DateTimeCol()
    words = StringCol()
    more_words = StringCol()
    title = StringCol()
    public = BoolCol(default = True)
    comments_disabled = BoolCol(default = False)

class BlogTag( SQLObject ):
    class sqlmeta:
        table = "tag_names"
    name = StringCol()

class EntryToTagLink( SQLObject ):
    class sqlmeta:
        table = "entry_to_tag_link"
    entry = ForeignKey("BlogEntry")
    tag = ForeignKey("BlogTag")


# Blog
class BlogComment( SQLObject ):
    class sqlmeta:
        table = "comments"
    author = StringCol()
    title = StringCol()
    words = StringCol()
    date = DateTimeCol()
    original_post = ForeignKey( "BlogEntry" )

# Blog AND comic
class User( SQLObject ):
    class sqlmeta:
        table = "users"
    username = StringCol()
    password = StringCol()
    icon = StringCol()
    email = StringCol()
    link = StringCol()

# Comic
class ComicPage( SQLObject ):

    # The title that will be displayed in <title></title> and possibly
    # on archive links to the page
    title = StringCol()

    # background color to use (#RRGGBB)
    bgColor = StringCol( default = "#cccccc" )

    # The position of the page among all pages.
    sequence = IntCol()

    # The number of panels on the page
    numPanels = IntCol( default = 6 )

    # The prefix for image files to put in the panels.
    # A path relative to web server root/images/yuki/.
    baseImageFile = StringCol()

    # The suffix to append after each number
    suffix = StringCol( default = ".png" )

    # So, for instance, baseImageFile="office1", then the page will try to
    # load images called office1_001.png, office1_002.png... through
    # office1_006.png from www-root/images/yuki.

    # If I want a splash page with just one panel, set numPanels to 1 and
    # use customHtml.

    # The date this page was made public
    publishDate = DateCol( default = datetime.datetime.now() )

    # The date in the story's internal chronology when this strip happens.
    internalDate = DateCol()

    # String representation of all the text in the comic.  Will be
    # put secretly on the page to make it searchable.
    fullText = StringCol()

    # If this is not NULL, then the part of the standard HTML template 
    # which contains the six panels is replaced with this.
    customHtml = StringCol( default=None ) 

    # If this is true, page is displayed to the public; otherwise it is
    # displayed only for me.
    isPublic = BoolCol( default = False )

    # Any panels that require any special html:
    customPanels = MultipleJoin( "CustomPanel" )

    # Comments that visitors have left on this page:
    comments = MultipleJoin( "Comment" )

    # Number of page views:
    views = IntCol( default = 0 )

# Comic
class CustomPanel( SQLObject ):
    # If a particular panel on an otherwise normal page needs some custom
    # HTML, a row in this table can provide it.

    # The page to which this panel belongs
    pageRef = ForeignKey( "ComicPage" )

    # The number of the panel
    panelNum = IntCol()

    # The custom HTML
    customHtml = StringCol()

# Comic
class ComicComment( SQLObject ):
    pageRef = ForeignKey( "ComicPage" )

    # This should match up with one of the names in the blog database
    # table users:
    commenter = StringCol()

    subject = StringCol()

    postDate = DateCol( default = datetime.datetime.now() )

    words = StringCol()

# Comic
class Scene( SQLObject ):
    
    firstPage = ForeignKey( "ComicPage" )
    title = StringCol()
    summary = StringCol()
    
if __name__ == "__main__":
    BlogEntry.createTable()
    BlogComment.createTable()
    User.createTable()
    ComicPage.createTable()
    CustomPanel.createTable()
    ComicComment.createTable()
    Scene.createTable()
