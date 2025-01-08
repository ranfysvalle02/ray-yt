import ray  
from youtubesearchpython import VideosSearch  
from youtube_transcript_api import YouTubeTranscriptApi  
from youtube_transcript_api._errors import (  
    TranscriptsDisabled,  
    VideoUnavailable,  
    NoTranscriptFound,  
    CouldNotRetrieveTranscript,  
)  

# Initialize Ray  
ray.init()  

# Function to check if English transcripts are available  
@ray.remote  
def has_en_transcript(video_id):  
    try:  
        # Request the English transcript  
        YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])  
        return True  
    except (TranscriptsDisabled, VideoUnavailable, NoTranscriptFound, CouldNotRetrieveTranscript):  
        return False  
    except Exception as e:  
        print(f"Unexpected error for video {video_id}: {e}")  
        return False  

# Main function to fetch videos with available English transcripts  
def fetch_videos_with_en_transcripts(search_query):  
    # Perform YouTube search using youtubesearchpython  
    videosSearch = VideosSearch(search_query, limit=50)  # Increase limit for demonstration  
    video_results = videosSearch.result()['result']  

    print(f"Found {len(video_results)} YouTube video(s)")  

    # Prepare data structures  
    video_ids = []  
    video_info = {}  
    for video in video_results:  
        video_id = video['id']  
        video_ids.append(video_id)  
        video_info[video_id] = {  
            "video_id": video_id,  
            "url": video['link'],  
            "title": video['title']  
        }  

    # Use Ray to check transcripts concurrently  
    futures = [has_en_transcript.remote(vid) for vid in video_ids]  
    results = ray.get(futures)  

    # Collect videos with English transcripts  
    videos_with_en_transcripts = [  
        video_info[vid] for vid, has_transcript in zip(video_ids, results) if has_transcript  
    ]  

    # Print video URLs with English transcripts  
    print("Videos with English transcripts:")  
    for video in videos_with_en_transcripts:  
        print(f"- {video['title']}: {video['url']}")  

# Example usage  
search_query = "Python web scraping"  
fetch_videos_with_en_transcripts(search_query)  

# Shutdown Ray when done  
ray.shutdown()  
