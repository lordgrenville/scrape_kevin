# provide an RSS feed for Kevin Lewis

from time import sleep

import requests
from bs4 import BeautifulSoup

root = "https://www.nationalaffairs.com"
r_root = requests.get(root + "/authors/detail/kevin-lewis")
soup_root = BeautifulSoup(r_root.text, "html.parser")
titles_di = {
    link.text.strip(): root + link["href"]
    for link in soup_root.find_all("a", attrs={"class": "article-title-link"})
}


def htmlencode(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rssify(title, link, title_di):
    feed = []
    feed += (
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>\n  <title>'
        + htmlencode(title)
        + "</title>\n  <link>"
        + htmlencode(link)
        + "</link>\n  <description>Scraping Kevin Lewis to RSS for fun and profit"
        + "</description>"
        + '<atom:link href="localhost:8888/rss.xml" rel="self" type="application/rss+xml" />'
    )
    for item_title, item_link in title_di.items():
        soup = BeautifulSoup(requests.get(item_link).text, "html.parser")
        soup.find("div", {"class": "article-social-bar"}).clear()
        feed += "  <item>"
        feed += f"  <title>{item_title} </title>"
        feed += f"  <link>{root + item_link} </link>"
        feed += "  <description>"
        feed += htmlencode(str(soup.find("div", attrs={"class": "article-content"})))
        feed += "</description>  </item>"
    feed += "</channel></rss>"
    sleep(5)
    return "".join(feed)


aa = rssify("Kevin Lewis", root + "/authors/detail/kevin-lewis", titles_di)
with open("/Users/josh/Downloads/foo.rss", "w+") as f:
    f.write(aa)
