import openai
import requests
import json
from moviepy.editor import VideoFileClip
from utils import *

# Extract audio from video
def extract_audio(video_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio_path = 'audio.wav'
    audio.write_audiofile(audio_path)
    return audio_path

# Transcribe audio using Whisper ASR API
def transcribe_audio(audio_path):
    with open(audio_path, 'rb') as f:
        response = openai.Answer.create(
            search_model="davinci",
            model="whisper",
            question="Transcribe the audio",
            documents=[],
            file=f,
            examples_context="Transcribe the audio",
            max_rerank=10,
            stop=None,
            log_level="info"
        )
    return response.choices[0].text.strip()

# Generate SRT file from transcribed text
def generate_srt(transcribed_text, output_path):
    sentences = transcribed_text.split('. ')
    srt_content = ''
    for i, sentence in enumerate(sentences):
        start_time = i * 3  # Assuming each sentence is 3 seconds long
        end_time = (i + 1) * 3
        srt_content += f"{i+1}\n{start_time} --> {end_time}\n{sentence}\n\n"
    with open(output_path, 'w') as f:
        f.write(srt_content)

# Step 6: Execute the process
video_path = '/Users/chivier/tmp/a.mp4'
audio_path = extract_audio(video_path)
transcribed_text = transcribe_audio(audio_path)
output_path = 'output.srt'
generate_srt(transcribed_text, output_path)
