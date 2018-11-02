import requests
import lxml
from lxml import html


def get_prof_page(name):
    university = "University of Southern California"

    prof = name.split(" ")
    # print prof

    query = "http://www.ratemyprofessors.com/search.jsp?query="
    query = query + prof[0] + "%20" + prof[1]

    for word in university.split(" "):
        query = query + "%20" + word

    # print query

    r = requests.get(query)
    prof_listing = lxml.html.fromstring(r.content)

    professors = prof_listing.xpath("//li[@class='listing PROFESSOR']/a")

    # print professors[0].attrib['href']# etree.tostring(professors[0])

    return "http://www.ratemyprofessors.com" + professors[0].attrib['href']


def get_rating(name):
    query = get_prof_page(name)
    r = requests.get(query)

    tree = lxml.html.fromstring(r.content)
    elements = tree.xpath("//div[@class='grade']")
    for e in elements:
        print e.text_content()

    # print name + elements[0].text_content()
    return float(elements[0].text_content().strip())


def get_difficulty(name):
    query = get_prof_page(name)
    r = requests.get(query)

    tree = lxml.html.fromstring(r.content)
    elements = tree.xpath("//div[@class='grade']")

    # print name + elements[0].text_content()
    return float(elements[2].text_content().strip())


#profname = "Nimfa Bemis"
#print profname
#print get_rating(profname)
