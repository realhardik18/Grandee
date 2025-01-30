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

#def generate_system_prompt():
    #client = Together(api_key=os.getenv('API_KEY'))    