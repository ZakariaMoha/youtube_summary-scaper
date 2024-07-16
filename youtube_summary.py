import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from nltk.tokenize import sent_tokenize
import nltk
nltk.download('punkt')

# Function to get video transcript
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([t['text'] for t in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

# Function to summarize text
def summarize_text(text, sentence_count=5):
    sentences = sent_tokenize(text)
    summary = ' '.join(sentences[:sentence_count])
    return summary

# Function to get video ID from URL
def get_video_id(url):
    from urllib.parse import urlparse, parse_qs
    query = urlparse(url).query
    video_id = parse_qs(query).get('v')
    if video_id:
        return video_id[0]
    else:
        raise ValueError("Invalid YouTube URL")

# Main function
def main():
    # URL of the YouTube video
    youtube_url = 'https://www.youtube.com/watch?v=SPTfmiYiuok'
    
    # Extract video ID from URL
    video_id = get_video_id(youtube_url)

    # Get the transcript of the video
    transcript = get_transcript(video_id)
    if transcript:
        print("Transcript:\n", transcript)

        # Summarize the transcript
        summary = summarize_text(transcript)
        print("\nSummary:\n", summary)
    else:
        print("Transcript not available.")

if __name__ == "__main__":
    main()
