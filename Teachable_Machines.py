from keras.models import load_model
import PIL
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt

"""
Initalise and load model -- (1) Create folder 'CV' and save model.h5 and labels.txt (2) Create sub-folder 'img
"""
model = load_model('CV/keras_model.h5')   # Load the model from TM (water bottle w or w/o crest)

capture = 10                              # Capture 10 images if none found

img_dir = 'CV/img'                        # define the image directory



# """
# Capture images if CV/img is empty (### Comment out if not using Colab Version)
# """
# images = os.listdir(img_dir)              # get all images from img_dir, if any
# print(images)

# if len(images) == 0:                      # if no images
#   i = 0                                   # counter
#   while True:                             # keep running (until break)

#     """start of code snippet from Colab"""
#     from IPython.display import display, Javascript
#     from google.colab.output import eval_js
#     from base64 import b64decode

#     def take_photo(filename='CV/img/image_%s.jpg' % (i + 1), quality=1):      # store in folder CV/img and label by image
#       js = Javascript('''
#         async function takePhoto(quality) {
#           const div = document.createElement('div');
#           const capture = document.createElement('button');
#           capture.textContent = 'Capture';
#           div.appendChild(capture);

#           const video = document.createElement('video');
#           video.style.display = 'block';
#           const stream = await navigator.mediaDevices.getUserMedia({video: true});

#           document.body.appendChild(div);
#           div.appendChild(video);
#           video.srcObject = stream;
#           await video.play();

#           // Resize the output to fit the video element.
#           google.colab.output.setIframeHeight(document.documentElement.scrollHeight, true);

#           // Wait for Capture to be clicked.
#           // await new Promise((resolve) => capture.onclick = resolve);       # comment off to take images immediately

#           const canvas = document.createElement('canvas');
#           canvas.width = video.videoWidth;
#           canvas.height = video.videoHeight;
#           canvas.getContext('2d').drawImage(video, 0, 0);
#           stream.getVideoTracks()[0].stop();
#           div.remove();
#           return canvas.toDataURL('image/jpeg', quality);
#         }
#         ''')
#       display(js)
#       data = eval_js('takePhoto({})'.format(quality))
#       binary = b64decode(data.split(',')[1])
#       with open(filename, 'wb') as f:
#         f.write(binary)
#       return filename

#     ## second part from code snippet
#     from IPython.display import Image
#     try:
#       filename = take_photo()
#       print('Saved to {}'.format(filename))

#       # Show the image which was just taken.
#       display(Image(filename))
#     except Exception as err:
#       # Errors will be thrown if the user does not have a webcam or if they do not
#       # grant the page permission to access it.
#       print(str(err))

#     """end of code snippet from Colab"""

#     i += 1                                # 1 image taken
#     if i == capture:                      # If required number of images met,
#       break                               # get out of While loop


"""
Capture images if CV/img is empty (Non-Colab Version)
"""
images = os.listdir(img_dir)              # get all images from img_dir, if any
print(images)

if len(images) == 0:                      # if no images
    i = 0                                   # counter
    capture = 10                            # Capture 10 images if none found

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    while i < capture:                     # Capture required number of images
        ret, frame = cap.read()            # Read a frame from the webcam
        filename = os.path.join(img_dir, f'image_{i + 1}.jpg')  # Define filename for saving the image
        cv2.imwrite(filename, frame)       # Save the image
        print(f"Image {i + 1} saved as {filename}")

        i += 1                             # Increment counter

    # Release the webcam
    cap.release()



"""
Get images into correct format
"""
images = os.listdir(img_dir)                                            # get all images from img_dir
size = 224                                                              # size defined by TM
data = np.ndarray(shape=(len(images), 224, 224, 3), dtype=np.float32)   # set array shape for TM model

for i in range(len(images)):
  image = PIL.Image.open(img_dir + "/" + 'image_%s.jpg' % (i + 1))      # open image saved
  width, height = image.size                                            # image dimensions

  if width > height:                                                    # if landscape
    new_height = size
    new_width = int(width * (new_height/height))

  else:                                                                 # if portrait
    new_width = size
    new_height = int(height * (new_width/width))

  new_image = image.resize((new_width, new_height))                     # Create a new resized image

  xcenter = new_width / 2                                               # Coordinates of image centre
  ycenter = new_height / 2

  if new_height == size:                                                # Crop to size, if landscape
    crop_width = (new_width - size) / 2
    x1 = int(0 + crop_width)
    y1 = int(0)
    x2 = int(new_width - crop_width)
    y2 = int(new_height)

  else:                                                                 # Crop to size, if portrait
    crop_height = (new_height - size) / 2
    x1 = int(0)
    y1 = int(0 + new_height)
    x2 = int(new_width)
    y2 = int(new_height - crop_height)

  cropped_image = new_image.crop((x1, y1, x2, y2))

  image_array = np.asarray(cropped_image)                                 # turn the image into a numpy array
  normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1   # normalize the image
  data[i] = normalized_image_array                                        # load the image into the data array



"""
Analyse images with model
"""
print("Analysing", len(data), "images.")
print("\n")
prediction = model.predict(data)            # predict based on model with data
print(prediction)                           # show prediction

print("\n---------Labels---------")
labels_file = open("CV/labels.txt", "r")    # open labels.txt file
print(labels_file.read())                   # show labels
labels_file.close()

print("\n---------Results--------")
predict = prediction.tolist()  # convert prediction to list
labels_file = open("CV/labels.txt", "r")  # open labels.txt file
labels = labels_file.readlines()  # read lines from the file
labels_file.close()  # close the file

for j in range(len(predict)):  # for the number of images analysed,...
    max_value = max(predict[j])  # identify the max value in the entire list
    max_index = predict[j].index(max_value)  # identify the list index with max value
    
    image_path = os.path.join(img_dir, 'image_%s.jpg' % (j + 1))  # Path to the current image
    cropped_image = PIL.Image.open(image_path)  # Open the current image
    plt.imshow(cropped_image)
    plt.axis('off')  # Hide axes
    label = labels[max_index][2:]
    plt.text(0, 10, f"image {j + 1}\n{label}", fontsize=12, color='red')
    plt.show()
    
    print("image", j + 1)  # identifier for image
    print(label)  # show results, [2:] to remove label number in results