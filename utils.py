from together import Together
import os
import base64
from elevenlabs.client import ElevenLabs
from moviepy.editor import AudioFileClip, ImageClip,VideoFileClip, concatenate_videoclips,TextClip,CompositeVideoClip
import assemblyai as aai
import pysrt
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

#function to create an image from a prompt
def generate_image(prompt,path):
    client = Together(api_key=os.getenv('API_KEY'))
    response = client.images.generate(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-dev",
        width=1008,
        height=1792,
        steps=28,
        n=1,
        response_format="b64_json"
    )
    image_data=response.data[0].b64_json
    with open(path, "wb") as img_file:
        img_file.write(base64.b64decode(image_data))

    print(f"Image saved in {path}")    

#function which can make a script for the video production
def generate_script(prompt,path):
    client = Together(api_key=os.getenv('API_KEY'))    
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
        messages=[
            {"role": "system", "content": "You are an AI that generates short scripts for voiceovers. Respond strictly with only the script, with no introductions, explanations, or extra text. The script should be engaging, natural-sounding, and within 35-45 seconds of speaking time.Make sure the script is just text and nothing else"},
            {"role": "user", "content": prompt}
        ],
    )

    script=response.choices[0].message.content
    with open(path, "w") as file:
        file.write(script) 

#function which can generate data file for video production
def data_generator(path_to_script):    
    with open("prompts/system_prompt.txt", "r", encoding="utf-8") as file:
        system_prompt=file.read()

    with open(path_to_script, "r", encoding="utf-8") as file:
        user_prompt=file.read()        

    client = Together(api_key=os.getenv('API_KEY'))    
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    script=response.choices[0].message.content
    with open("prompts/data.txt", "w") as file:
        file.write(script) 

#function to generate a singular frame
def generate_frames():
    with open("prompts/data.txt", "r", encoding="utf-8") as file:
        output=file.read()
    output=eval(output)
    for index,obj in enumerate(output):
        print(f"Generating image {index}")
        generate_image(obj['image_prompt'],f"frames/{index}.png")        

#function to generate audio from the data.txt
def generate_audio():
    with open("prompts/data.txt", "r", encoding="utf-8") as file:
        output=file.read()
    output=eval(output)
    for index,obj in enumerate(output[:1]):
        client = ElevenLabs(api_key=os.getenv('ELEVEN_LABS_API_KEY'))
        audio = client.generate(
            text=obj['voice_over_text'],
            voice="Brian"
        )        
        save(audio, f"audio/{index}.mp3")
        print(f"Generated audio {index}")

def compile_videos(clips_folder: str, output_file: str, transition_duration: float = 1.0):
    clip_files = sorted([f for f in os.listdir(clips_folder) if f.endswith(('.mp4', '.mov', '.avi', '.mkv'))])
    
    if not clip_files:
        print("No video files found in the folder.")
        return
    
    clips = []
    
    for file in clip_files:
        clip_path = os.path.join(clips_folder, file)
        clip = VideoFileClip(clip_path)
        if transition_duration > 0:
            clip = clip.crossfadein(transition_duration)
        
        clips.append(clip)
    
    # Apply crossfade transition between clips
    final_video = concatenate_videoclips(clips, method="compose")
    
    # Write the final video to a file
    final_video.write_videofile(output_file, codec='libx264', fps=24)
    final_video.close()
    
    print(f"Final video saved to {output_file}")

import os
import assemblyai as aai

def seconds_to_srt_timestamp(milliseconds):
    """Convert milliseconds to SRT timestamp format (HH:MM:SS,mmm)."""
    seconds = milliseconds / 1000  # Convert ms to seconds
    millis = milliseconds % 1000
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

def generate_srt(video):
    """Transcribe video using AssemblyAI and generate an SRT file with correct timestamps."""
    # Set API Key
    aai.settings.api_key = os.getenv("ASSEMBLY_API_KEY")

    # Initialize transcriber
    transcriber = aai.Transcriber()

    # Transcribe video with word-level timestamps
    transcript = transcriber.transcribe(video)

    # Extract words with timestamps
    words = transcript.words  
    if not words:
        print("No words detected in the transcript.")
        return

    srt_content = []
    index = 1
    words_per_segment = 1  # Ensure 2-3 words per second

    for i in range(0, len(words), words_per_segment):
        segment_words = words[i:i + words_per_segment]
        start_time = seconds_to_srt_timestamp(segment_words[0].start)
        end_time = seconds_to_srt_timestamp(segment_words[-1].end)

        text = " ".join([word.text for word in segment_words])

        srt_content.append(f"{index}\n{start_time} --> {end_time}\n{text}\n")
        index += 1

    # Save to SRT file
    with open("subtitles.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    print("SRT file generated successfully: subtitles.srt")


# Function to read SRT file and return the subtitles as a list of tuples
def parse_srt(file_path):
    subs = pysrt.open(file_path)
    subtitles = []
    for sub in subs:
        start_time = sub.start.to_time()
        end_time = sub.end.to_time()
        text = sub.text
        # Convert time to seconds (float)
        start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second + start_time.microsecond / 1e6
        end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second + end_time.microsecond / 1e6
        subtitles.append((start_seconds, end_seconds, text))
    return subtitles

# Function to create a video with subtitles using OpenCV for text rendering
def add_subtitles_to_video(video_path, srt_file, output_path):
    # Load the video
    video = VideoFileClip(video_path)
    
    # Parse subtitles from the srt file
    subtitles = parse_srt(srt_file)
    
    # Function to overlay text on the video frame using OpenCV
    def add_text_to_frame(frame, text, position, font_scale=4, color=(255, 255, 255), thickness=10):
        # Convert the frame to RGB (OpenCV uses BGR by default)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)        
        # Get the size of the text to position it correctly
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_width, text_height = text_size
        
        # Position the text in the middle
        x = int((frame.shape[1] - text_width) / 2)
        y = int(frame.shape[0]/2)  # Slightly above the bottom
        cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        
        # Convert the frame back to BGR for moviepy
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Function to apply subtitles to each frame of the video
    def add_subtitles_to_clip(get_frame, t):
        frame = get_frame(t)  # Get the current frame at time `t`
        
        # Add subtitles for the current time if there are any
        for start_seconds, end_seconds, text in subtitles:
            if start_seconds <= t <= end_seconds:
                frame = add_text_to_frame(frame, text, position="center")
                break  # Only one subtitle per frame
        
        return frame

    # Apply the subtitle function to the video
    video_with_subtitles = video.fl(lambda gf, t: add_subtitles_to_clip(gf, t))

    # Write the output video
    video_with_subtitles.write_videofile(output_path, codec="libx264", fps=video.fps)



video_path = "output.mp4"
srt_file = "subtitles.srt"
output_path = "output_video.mp4"


add_subtitles_to_video(video_path, srt_file, output_path)