from together import Together
import os
import base64

def generateimage(prompt,path):
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

data_generator("prompts/script.txt")