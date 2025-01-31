from dotenv import load_dotenv
from utils import generateimage

load_dotenv()

def read_prompt(file):
    with open(file, 'r') as f:
        data=f.readlines()
    data=''.join(data)
    return data

with open("prompts/generated_prompt.txt", "r", encoding="utf-8") as file:
    output=file.read()

output=eval(output)
for index,obj in enumerate(output):
    '''
    image_prompt=obj['imageprompt']
    generateimage(image_prompt,f"frames/{index}.png")
    print("generated image",index)
    '''
    print(obj['voice_over_text'])
    