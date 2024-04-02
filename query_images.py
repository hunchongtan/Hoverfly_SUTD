"""
Remember to install packages before starting!
pip install openai==1.13.3
"""

import os
import base64
from PIL import Image
import matplotlib.pyplot as plt
from openai import OpenAI

"""
Set up OpenAI API key
"""
f = open("keys/openai_key.txt", "r")
key = f.readlines()[0]
f.close()

os.environ["OPENAI_API_KEY"] = key

"""
Use GPT with Vision
"""
##### Define the number of images you have #####
num_images = 2

# Create a list to store the image paths
image_paths = []

# Loop through the range of image numbers and generate paths
for i in range(1, num_images + 1):
    image_path = f"others/image_{i}.png"
    image_paths.append(image_path)

# Define a function to encode images into base64 format
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Create a dictionary to store base64 encoded images
base64_images = {}

# Encode all images in the image_paths list
for image_path in image_paths:
    base64_images[image_path] = encode_image(image_path)

"""
Display Image
"""
for image_path in image_paths:
    img = Image.open(image_path)
    plt.imshow(img)
    plt.axis('off')
    plt.show()

"""
Query
"""
client = OpenAI()

prompt = "\
        1. Identify the products. \
        2. Identify the top 5 elements of each product. Each element should be fewer than 3 words. Express the results as a python list. \
        3. Identify the differences in these elements. Each difference should be fewer than 5 words. Express the results as a python list. \
        Do not output anything else. Keep the answer as concise as possible."

client = OpenAI()

prompt = "You are given different images of the same product.\n \
        1. Identify the product.\n \
        2. Identify the top 5 elements of the product. Each element should be fewer than 3 words. Express the results as a python list. \n \
        3. Identify the 3 differences in these elements. Each difference should be fewer than 3 words. Express the results as a python list. \n \
        Do not output anything else. Keep the answer as concise as possible."

# Construct the messages list
messages = [{
    "role": "user",
    "content": [{"type": "text", "text": prompt}]
}]

# Add base64-encoded images to the messages list
for image_path in image_paths:
    messages.append({
        "role": "user",
        "content": [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64_images[image_path]}}]
    })

# Make the completion request
response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=messages,
    max_tokens=300  # max length of response
)

print("Prompt:", prompt)
print("Output:")
print(response.choices[0].message.content)
