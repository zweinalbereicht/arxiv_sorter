from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
import email
from email.message import EmailMessage
# largest possible scope, necessary to delete emails.
SCOPES = ['https://mail.google.com/']


#my own imports for string parsing
import re
import base64
import toml


def retrieve_unread_arxiv_email(service):
        # Call the Gmail API
    # this is the querying string, works like the gmail query box
    myquery = 'in:inbox is:unread subject:physics daily'

    messages=[]
    results = service.users().messages().list(userId='me',q=myquery).execute()
    if 'messages' in results:
        messages.extend(results['messages'])
    while 'nextPageToken' in results:
        results = service.users().messages().list(userId='me',q=myquery, pageToken=results['nextPageToken']).execute()
        if 'messages' in results:
            messages.extend(results['messages'])
    return messages

def get_email_contents(service, message):
    results=service.users().messages().get(userId='me',id=message['id'],format='full').execute()
    message_text = results['payload']['body']['data']
    message_text = base64.b64decode(message_text).decode("utf-8")
    return message_text

def extract_title(string):
    match = re.search('Title: (.*)(Authors)',string,re.DOTALL) 
    if match:
        return match.group(1)
    else:
        print(string)
        return None

def extract_authors(string):
    match = re.search('Authors: (.*)(Cat)',string,re.DOTALL) 
    if match:
        return match.group(1)
    else:
        return None

class arxiv_article:
    def __init__(self, id, t,a,c):
        self.id=id
        self.title = t
        self.authors=a
        self.contents=c

    # says if an email is relevant
    def is_relevant(self, dic):
        title_match = any([not (re.search(w,self.title,re.IGNORECASE)==None) for w in dic['selection']['titles']])
        authors_match = any([not (re.search(w,self.authors,re.IGNORECASE)==None) for w in dic['selection']['authors']])
        return title_match or authors_match

    def format(self):
        return f'{self.id}\n{self.contents}'


def parse_email_content(contents):
    arxiv_id = re.findall(r'^\\\\\r\narXiv:[0-9]{4}.*$',contents, flags=re.M)
    contents = re.split(r'^\\\\\r\narXiv:[0-9]{4}.*$',contents, flags=re.M)[1:]
    titles = [extract_title(c) for c in contents]
    authors = [extract_authors(c) for c in contents]
    arxiv_articles=[arxiv_article(id.split('\n')[1],t,a,c) for id,t,a,c in zip(arxiv_id,titles,authors,contents)]
    return arxiv_articles

#sending an email
def send_email(contents,send_adress,service):

    message = EmailMessage()
    message.set_content(str(contents))

    message['Subject'] = 'Daily ArXiv'
    message['To'] = send_adress

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {
        'raw': encoded_message
    }
    # pylint: disable=E1101
    send_message = (service.users().messages().send(userId="me", body=create_message).execute())
    print(F'Message Id: {send_message["id"]}')
   
def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    try:
        # load toml setup file
        parsed_toml = toml.load('sorter.toml')

        # adress to send to, specified in 'email_adress.txt' file
        with open('email_adress.txt') as f:
            send_adress=f.readline()


        # treat emails
        messages = retrieve_unread_arxiv_email(service)

        #if no new emails, return
        if len(messages)==0:
            print('no new messages')
            return

        #store relevant articles to send
        relevant_articles=[]
        email_contents="Salut Jerem, voici ton daily load of scientific news :)\n\n\n"

        for m in messages:
            contents = get_email_contents(service, m)

            arxiv_articles = parse_email_content(contents)
            # sort the relevant ones
            for article in arxiv_articles:
                if article.is_relevant(parsed_toml):
                    relevant_articles.append(article)

        if len(relevant_articles)>0:
            for article in relevant_articles:
                email_contents+=article.format()

            send_email(email_contents,send_adress,service)

        #trash all emails
        for m in messages:
            _ = service.users().messages().trash(userId='me',id=m['id']).execute()


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
