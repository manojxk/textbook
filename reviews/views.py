from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
import math
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from .forms import UploadFileForm
import urllib.request
import os, io
import json
import requests
from google.cloud import storage
from googleapiclient.discovery import build
from .gcloud import GoogleCloudMediaFileStorage
import re
from bs4 import BeautifulSoup
from google.cloud import vision_v1
from google.cloud.vision_v1 import types
from google.cloud import language_v1
from .models import Upload
from .models import Matching
import argparse
from .forms import MatchingForm
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\Manoj Kumar\Desktop\New folder\ServiceAccountToken.json'
client = vision_v1.ImageAnnotatorClient()


def language_analysis(text):
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content = text, type_=language_v1.Document.Type.PLAIN_TEXT)
    # document = client.document_from_text(text)
    sent_analysis = client.analyze_sentiment(request={'document':document}).document_sentiment
    sentiment = sent_analysis
    return sentiment

def review_view(request):
    # covered topics: mathematics, physics, computer science,
    key_terms = ['algebra', 'topology', 'geometry', 'multivariable', 'calculus', 'analysis', 'trigonometry',
                 'number theory', 'arithmetic', 'probability', 'statistic', 'combinatorics',
                 'discrete mathematics', 'linear algebra', 'algebraic geometry', 'set theory', 'fraction',
                 'differential', 'electromagnetism', 'quantum', 'mechanics',
                 'nuclear', 'physics', 'thermodynamics', 'astrophysics', 'biophysics', 'optics', 'relativity',
                 'particle physics', 'cosmology', 'solid-state', 'atomic', 'molecular',
                 'acoustics', 'astronomy', 'gravity', 'geophysics', 'python', 'java', 'javascript', 'react', 'css',
                 'html', 'scala','coding','biology','organizational','economics','business', 'entrepreneur', 'management',
                 'supply','accounting','law','number theory','optimization','trigonometry', 'MATLAB']

    sites = []
    format_text = []
    videos = []
    comments = []
    keyword = ""
    sent_score = {}
    sent_mag = {}
    # text data from the book image itself
    if request.method == 'POST':
        path = request.FILES['myfile']
        content = path.read()
        image = vision_v1.types.Image(content=content)
        response1 = client.text_detection(image=image)
        texts = response1.text_annotations
        for text in texts:
            # format_text.append('"{}"'.format(text.description))
            format_text.append(text.description)
        for word in format_text:
            word.replace('"',"")
            if str(word).lower() in key_terms:
                keyword = str(word).lower()
                break


        #Youtube search begin
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'
        comment_url = 'https://www.googleapis.com/youtube/v3/commentThreads'

        search_params = {
            'part': 'snippet',
            'q': keyword,# 'multivariable calculus',
            'key': 'AIzaSyDFB8sIfrXJzwotpDyiBko5SvaueuyQat8',
            'maxResults': 10,#2
            'type': 'video' 
        }

        video_ids = []
        r = requests.get(search_url, params=search_params)
        results = r.json()['items']
        for result in results:
            video_ids.append(result['id']['videoId'])
        video_params = {
            'part': 'snippet,contentDetails',
            'key': 'AIzaSyDFB8sIfrXJzwotpDyiBko5SvaueuyQat8',
            'id': ','.join(video_ids),
            'max_results': 4#2
        }

        r = requests.get(video_url, params=video_params)
        results = r.json()['items']
        videos = []
        for result in results:
            video_data = {
                'title': result['snippet']['title'],
                'id': result['id'],
                'url': f'https://www.youtube.com/watch?v={result["id"]}',
                'thumbnails': result['snippet']['thumbnails']['high']['url']
            }
            videos.append(video_data)
        comments = []
        comment_dict = {}
        for id_num in video_ids:
            comment_params = {
                'part': 'snippet',
                'key': 'AIzaSyDFB8sIfrXJzwotpDyiBko5SvaueuyQat8',
                'videoId': id_num,
                'max_results': 5 #3
            }

            r2 = requests.get(comment_url, params=comment_params)

            results2 = r2.json()['items']

            #{video_id: string of comments for that id}

            for result in results2:

                cmt = result['snippet']['topLevelComment']['snippet']['textDisplay']
                com_vid_id = result['snippet']['videoId']
                comment_data = {
                    #'id': id_num,
                    'id': com_vid_id,
                    'comment_text': cmt
                }

                comments.append(comment_data)
                if id_num == com_vid_id:
                    if id_num in comment_dict:
                        comment_dict[id_num] = comment_dict[id_num] + cmt
                    else:
                        comment_dict[id_num] = cmt


        # comment_dict maps the video id to a string that consists of all the comments in that video
        for key, value in comment_dict.items():
            my_text = language_analysis(value)
            sent_score[key] = my_text.score
            sent_mag[key] = my_text.magnitude


        # Youtube search ends
        # start of vision api web detection, uncomment when ready

        response = client.web_detection(image=image)
        web_detection = response.web_detection
        my_formatted_text = web_detection.pages_with_matching_images
        for page in my_formatted_text:
            sites.append(format(page.url))
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        # end of vision api web detection, uncomment when ready

    context = {
        'text': sites,
        'reviews': "",
        'format_text':format_text,
        'yt_vids':videos,
        'comments':comments,
        'keyword':keyword,
        'score':sent_score,
        'magnitude':sent_mag
    }

    return render(request,"reviews/review_detail.html",context)

