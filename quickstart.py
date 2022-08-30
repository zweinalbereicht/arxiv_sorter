from __future__ import print_function
from base64 import b64decode

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


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
    message_text = results['payload']['parts'][0]['body']['data']
    message_text = b64decode(message_text).decode("utf-8")
    return message_text
    

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
        messages = retrieve_unread_arxiv_email(service)
        for m in messages:
            print(get_email_contents(service, m))

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
