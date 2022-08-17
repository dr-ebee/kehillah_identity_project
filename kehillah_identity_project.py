#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# TODO: make images out of text repsonses
# TODO: filter out old responses from the same student
# TODO: make a readme with instructions for getting auth credentials
# TODO: accept images that are pdf or jpg (not just png)
##

from cgitb import text
import io
import os.path

import pandas as pd
import re
from PIL import Image, ImageTk
import tkinter as tk
import random

# For authenticating
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# For downloading files
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# For downloading files
from googleapiclient.discovery import build
import io
from apiclient import http
from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']
CRED_FILE = "client_secret_264567668652-0duhg8u5q8o00bnj1r66pq5mfmeog9us.apps.googleusercontent.com.json"

class gui:
    def __init__(self, mainwin, images):
        self.mainwin = mainwin
        self.images = images
        self.mainwin.title("Tkinter Picture Frame")
        self.mainwin.state("zoomed")

        self.mainwin.configure(bg = "yellow")
        self.frame = tk.Frame(mainwin)

        self.frame.place(relheight = 0.85, relwidth=0.9, relx = 0.05, rely = 0.05)

        self.image = tk.Label(self.frame)
        self.image.pack()

        self.show_slide()

    def show_slide(self):
        self.colors = ["gray", "black", "red", "green", "blue", "yellow", "pink", "purple", "cyan", "magenta"]
        color = random.choice(self.colors)
        self.load = random.choice(self.images)
        self.pic_width = self.load.size[0]
        self.pic_height = self.load.size[1]
        self.real_aspect = self.pic_width / self.pic_height
        self.cal_width = int(self.real_aspect * 800)
        self.load2 = self.load.resize((self.cal_width, 800))
        self.render = ImageTk.PhotoImage(self.load2)
        self.image.config(image = self.render)
        self.image.image = self.render

        self.mainwin.configure(bg = color)
        self.mainwin.after(1000, self.show_slide)


def read_csv(creds, file_id, output_filename):
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=file_id,
                                range="A1:ZZ10000").execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return

    df = pd.DataFrame(values[1:], columns = values[0])

    return df

def download_pdf(service, file_id, output_filename):
    local_fd = open(f'{output_filename}.pdf','wb')

    request = service.files().export_media(fileId=file_id,
                                            mimeType='application/pdf')
    downloader = MediaIoBaseDownload(local_fd, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(F'Download {int(status.progress() * 100)}.')

def download_image(service, file_id, output_filename):
  local_fd = open(output_filename,'wb')

  request = service.files().get_media(fileId=file_id)
  media_request = http.MediaIoBaseDownload(local_fd, request)

  while True:    
    _, done = media_request.next_chunk()

    if done:
      print ('Download Complete')
      return

def authenticate():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
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
                CRED_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def filter_old_responses_out(df):
    return df

def read_image(image_id, service):
    output_filename = f"{image_id}.png"
    download_image(service, image_id, output_filename)
    image = Image.open(output_filename)
    return image

def get_image_id_from_url(image_url):
    image_id = re.sub(".*?id=", "", image_url)
    return image_id

def load_images(image_url_series, service):
    image_ids = [get_image_id_from_url(image_url) for image_url in image_url_series]
    images = [read_image(image_id, service) for image_id in image_ids if image_id != ""]
    return images

def make_text_slides(text_responses):
    return []

def make_image_slides(images):
    return images

def make_slides(text_responses, images):
    return make_text_slides(text_responses) + make_image_slides(images)

def make_presentation(raw_df, service):
    df = filter_old_responses_out(raw_df)
    text_responses = df["Or you can submit some text"]
    text_responses = [response for response in text_responses if (not response is None) and response != ""]
    images = load_images(df["You can upload an image here if you want"], service)
    slides = make_slides(text_responses, images)
    return slides

def play_slides(slides):
    root = tk.Tk()
    myprog = gui(root, slides)
    root.mainloop()

def main():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    responses_sheets_file = "1FD721rrfKDhcwEKt5nO_JoCbf01S1WhZnRItrzEDLgY"
    df = read_csv(creds=creds, file_id=responses_sheets_file, output_filename="tmp")
    slides = make_presentation(df, service)
    # example_image = Image.open("1sUBFSEriRCl0tMAvZO1e_BzgOzjT_5b4.png")
    # slides = make_slides(["example response"], [example_image])
    play_slides(slides)

if __name__ == '__main__':
    main()