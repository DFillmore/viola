from xml.dom.minidom import parse, parseString


def getbibliographic(iFiction):
    dom = parseString(iFiction)
    try:
        story = dom.getElementsByTagName('story')[0] # assumes only one story element
        biblio = story.getElementsByTagName('bibliographic')[0]
    except:
        return None
    return biblio

def gettitle(iFiction):
    try:
        biblio = getbibliographic(iFiction)
        title = biblio.getElementsByTagName('title')[0]
        return title.childNodes[0].wholeText
    except:
        return None

def getheadline(iFiction):
    try:
        biblio = getbibliographic(iFiction)
        headline = biblio.getElementsByTagName('headline')[0]
        return headline.childNodes[0].wholeText
    except:
        return None

def getauthor(iFiction):
    try:
        biblio = getbibliographic(iFiction)
        author = biblio.getElementsByTagName('author')[0]
        return author.childNodes[0].wholeText
    except:
        return None

def getdescription(iFiction):
    try:
        biblio = getbibliographic(iFiction)
        desc = biblio.getElementsByTagName('description')[0]
        fulldesc = []

        return ''.join([ ('\n\n' if a.nodeType == 1 and a.localName == 'br' else ' '.join(a.wholeText.split())) for a in desc.childNodes
                       ]
                      )
        
        for a in desc.childNodes:
            if a.nodeType == 3:
                fulldesc.append(' '.join(a.wholeText.split()))
            elif a.nodeType == 1 and a.localName == 'br':
                fulldesc.append('\n\n')

        return ''.join(fulldesc)
    except:
        return None

def getzcode(iFiction):
    try:
        dom = parseString(iFiction)
        story = dom.getElementsByTagName('story')[0] # assumes only one story element
        zcode = story.getElementsByTagName('zcode')[0]
        return zcode
    except:
        return None

def getcoverpicture(iFiction):
    zcode = getzcode(iFiction)
    try:
        coverpicture = zcode.getElementsByTagName('coverpicture')
        return int(coverpicture[0].childNodes[0].wholeText)
    except:
        return None
        
        
             



