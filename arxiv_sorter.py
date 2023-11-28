from __future__ import print_function

import os.path
import sendgrid
import os
from sendgrid.helpers.mail import *

#my own imports for string parsing
import re
import toml
import feedparser
import requests

class arxiv_article:
    def __init__(self, id, t,a,c,d):
        self.id=id
        self.title = t
        self.authors=a
        self.contents=c
        self.date=d

    # says if an email is relevant
    def is_relevant(self, dic):
        title_match = any([not (re.search(w,self.title,re.IGNORECASE)==None) for w in dic['selection']['titles']])
        authors_match = any([not (re.search(w,self.authors,re.IGNORECASE)==None) for w in dic['selection']['authors']])
        return title_match or authors_match

    def format(self):
        return f'{self.id}\n\nDate : {self.date}\n\nTitle : {self.title}\n\nSummary : {self.contents}\n\nAuthors : {self.authors}'

def retrieve_latest_articles(latest_id):
    categories=["cond-mat.stat-mech","cs.LG"]
    # search across all categories
    cat = "+".join(categories)

    
    #by default we will query 50 articles 
    api_url = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results=50"
    response = requests.get(api_url)
    parsed_response=feedparser.parse(response.text)

    latest_articles = []
    for entry in parsed_response.entries:
        if entry.id==latest_id:
            break
        authors_name=[]
        for author in entry.authors:
            authors_name.append(author.name)
        authors = ", ".join(authors_name)
        latest_articles.append(arxiv_article(entry.id, entry.title,authors, entry.summary,' '.join(entry.updated.split('T'))))
    return latest_articles


#sending an email with sendgrid
def send_email(contents,sender_adress,receive_adress):

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(sender_adress)
    to_email = To(receive_adress)
    subject = "Daily ArXiv"
    content = Content("text/plain", contents)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    #print(response.status_code)
    #print(response.body)
    #print(response.headers)

def main():

    #retrieve useful email adresses
    with open('email_adress.txt') as f:
        lines=f.readlines()
    send_adress = lines[0]
    receive_adress = lines[1]
    
    #retrieve article selection
    selection = toml.load('sorter.toml')

    # find old id
    with open('old_id.txt') as f:
        latest_id = f.readlines()[0]

    # query until old id and parse into article format
    latest_articles = retrieve_latest_articles(latest_id)


    # sort articles
    relevant_articles = []
    for article in latest_articles:
        if article.is_relevant(selection):
            relevant_articles.append(article)
    if len(relevant_articles)==0:
        contents="No news today !"
    else:
        # update old_id
        with open('old_id.txt','w') as f:
            f.write(relevant_articles[0].id)

        del_article = "\n\n----------------------------------------------------------------------------------\n\n"
        contents = del_article.join([a.format() for a in relevant_articles])

    send_email(contents, send_adress, receive_adress)



if __name__ == '__main__':
    main()
