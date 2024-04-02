"""
Remember to install packages before starting!
pip install openai==1.13.3
"""

import os
from openai import OpenAI
import requests
from PIL import Image
import matplotlib.pyplot as plt

"""
Set up OpenAI API key
"""
import os

f = open("keys/openai_key.txt", "r")
key = f.readlines()[0]
f.close()

os.environ["OPENAI_API_KEY"] = key



# """
# Use ChatGPT
# """
# client = OpenAI()
# prompt =  "You are an Apple hater who really hates Apple products. Perform the following steps: " \
#           "Step 1 – State the product discussed in the user review delimited by triple quotes with a prefix that says 'Product: '. " \
#           "Step 2 – Identify 3 key design features based on the user review. Show the results as a python list. " \
#           "Step 3 - Write a strongly-worded review. " \
#           "State 'I don’t know.' if an answer cannot be found for the steps. " \
#           " '''The Apple Vision Pro is a truly amazing product that delivers futuristic eye- and hand-tracking interface along with breathtaking 3D video and truly impressive AR apps. It’s also a magical way to extend your Mac. But there’s some early performance bugs that need to be worked out, the battery can get in the way, and Digital Persona is a bit creepy and needs work.''' "
# print(prompt)
# print("\n")

# chat_completion = client.chat.completions.create(
#     model="gpt-4",
#     messages=[{"role": "user", "content": prompt,}],
#     temperature=0.5,                                        # adjust persona and temperature
# )

# result = chat_completion.choices[0].message.content
# print(result)

##### ------------------------------------------------------------------------------------------------------------------------------------------ #####

"""
Use DallE
"""
client = OpenAI()

prompt = "a sports car in the style of The Flash, photorealistic, wide angle, high definition."
print("Prompt:", prompt)

response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,      # The maximum length is 1000 characters
    n=1,                # Number of images
    size="1024x1024",   # Must be one of 256x256, 512x512, or 1024x1024
    quality="hd",       # 'hd' High definition or 'standard'
)
image_url = response.data[0].url
print("Image URL:", image_url)
print("\n")

data = requests.get(image_url).content

f = open('dalle.jpg','wb')
f.write(data)
f.close()

print("Opening image preview...")
img = Image.open('dalle.jpg')
plt.imshow(img)
plt.axis('off')
plt.show()


