"""mmsparser - Parses MMS HTML documents using the beautiful soup library into 
   meaningful data structures.

sf37 - 31/12/2011
Part of the MMSpider project.
"""
from BeautifulSoup import BeautifulSoup
import string

BASE_URL = "https://www.st-andrews.ac.uk"

def parse_modules_list(html):
    """Parses the main modules display page (accordion style only atm, todo: add support for other layouts)
       Returns a dictionary containing name-coursework url pairs."""
    ret = {}
    parser = BeautifulSoup(html)
    
    modules_entries = parser.findAll("h3", { "class" : "module_heading" })
    for entry in modules_entries: # enumerates all modules
        name = entry.a.contents[0]
        section = entry.nextSibling.nextSibling # 2x nextSibling. why? beats me.
        cwk_section = section.find("a", { "class" : "resource coursework" } )
        if cwk_section != None:
            link = BASE_URL + cwk_section["href"]
            ret[name] = link
    return ret
    
def parse_cwk_list(html): 
    """Parses a coursework display page. Returns a list of dictionaries - each dictionary is formatted as 
       {name : assignment name, grade : assignment grade, comments_url : comments url}"""
    ret = []
    parser = BeautifulSoup(html)
    
    table = parser.find("tbody")
    entries = table.findAll("tr") # finds a list of all coursework elements
    
    for entry in entries:
        children = entry.findAll("td") # enumerates all attributes
        name = children[0].contents[0]
        grade = string.replace(children[6].contents[0], "&#160;", "") # whimsical little character we need to rid ourselves of
        comments_url = children[5].find("li", {"style" : True}).a["href"] # TODO: handle appending base comments url here, also my GOD what a line of code
        ret.append({"name" : name, "grade" : grade, "comments_url" : comments_url})
        
    return ret
    
def parse_login(html):
    """Parses the login page. Returns a dictionary of the form { id : form id, dest : destination url, lt : lt hidden value, eventid : eventId hidden value}."""
    parser = BeautifulSoup(html)
     
    # extract the information
    form = parser.find("form")
    id = form["id"]
    action_url = form["action"]
    lt_hidden = form.find("input", { "type" : "hidden", "name" : "lt" })["value"]
    eid_hidden = form.find("input", { "type" : "hidden", "name" : "_eventId" })["value"]
    
    return { "id" : id, "dest" : action_url, "lt" : lt_hidden, "eventid" : eid_hidden }
