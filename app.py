# app.py
from flask import Flask, render_template, request
import re
import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer
import heapq

app = Flask(__name__)

# Initialize NLTK resources
import nltk
nltk.download('punkt')
nltk.download('stopwords')

# Function to extract video details from YouTube URL
def extract_video_details(video_url):
    video_id = None
    video_title = None
    video_description = None
    
    # Extract video ID from URL using regex
    regex = r"(?:https:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, video_url)
    
    if match:
        video_id = match.group(1)
        
        # Fetch video page HTML to get title and description
        video_page = requests.get(f"https://www.youtube.com/watch?v={video_id}")
        if video_page.status_code == 200:
            soup = BeautifulSoup(video_page.content, 'html.parser')
            video_title = soup.find("meta", property="og:title")['content']
            video_description = soup.find("meta", property="og:description")['content']
        
    return video_id, video_title, video_description

# Function to generate summary from text
def generate_summary(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text)
    
    word_freq = {}
    for word in words:
        word = word.lower()
        if word not in stop_words:
            if word not in word_freq:
                word_freq[word] = 1
            else:
                word_freq[word] += 1
    
    max_freq = max(word_freq.values())
    for word in word_freq.keys():
        word_freq[word] = (word_freq[word] / max_freq)
    
    sent_tokens = sent_tokenize(text)
    sent_scores = {}
    for sent in sent_tokens:
        for word in word_tokenize(sent.lower()):
            if word in word_freq.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sent_scores.keys():
                        sent_scores[sent] = word_freq[word]
                    else:
                        sent_scores[sent] += word_freq[word]
    
    summary_sentences = heapq.nlargest(7, sent_scores, key=sent_scores.get)
    summary = ' '.join(summary_sentences)
    
    return summary

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summary', methods=['POST'])
def get_summary():
    video_url = request.form['video_url']
    
    # Extract video details from URL
    video_id, video_title, video_description = extract_video_details(video_url)
    
    if video_id:
        # Generate summary (assuming video_description is available)
        summary = generate_summary(video_description)
        
        # Prepare data for rendering
        video_details = {
            'title': video_title,
            'description': video_description,
            'video_url': f"https://www.youtube.com/watch?v={video_id}"
        }
        
        return render_template('summary.html', video_details=video_details, summary=summary)
    else:
        return "Invalid YouTube video URL."

if __name__ == '__main__':
    app.run(debug=True)
