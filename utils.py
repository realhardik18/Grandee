from together import Together
import os
import base64
from elevenlabs.client import ElevenLabs
from moviepy.editor import AudioFileClip, ImageClip,VideoFileClip, concatenate_videoclips
import assemblyai as aai

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

def generate_srt(video):
    aai.settings.api_key = os.getenv('ASSEMBLY_API_KEY')
    transcriber = aai.Transcriber()       
    transcript = transcriber.transcribe(video)    
    srt_content = transcript.export_srt(
        chars_per_caption=15,  
        max_words_per_caption=3
    )    
    with open("subtitles.srt", "w", encoding="utf-8") as f:
        f.write(srt_content)    

generate_srt("output.mp4")