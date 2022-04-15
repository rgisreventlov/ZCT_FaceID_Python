import cv2
import numpy as np
import os
import glob
import io
import json
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from PIL import Image, ImageDraw, ImageFont

images_rgb = []
response_detected_faces = []

with open('api_key.json', 'r') as f:
  settings = json.load(f)
API_KEY = settings['key']
ENDPOINT = settings['endpoint']
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(API_KEY))

def remove_all_photos_from_folder():
  files = glob.glob('images/*.jpg')
  for f in files:
      os.remove(f)

def recognize_faces(rgb_image_stream):
  response_detected_faces = face_client.face.detect_with_stream(
  rgb_image_stream,
  detection_model='detection_01',
  recognition_model='recognition_04',
  return_face_attributes=['age','gender','emotion']
  )
  # print(response_detected_faces)
  if not response_detected_faces:
    print('No face detected')
    return "NoFace"
  
  print('Number of people detected: {0}'.format(len(response_detected_faces)))
  
  return response_detected_faces




def recognize_from_img_path(path):
  img = open(path, 'rb')
  images_rgb.append(img)
  response_detected_faces.append(recognize_faces(img))




def start_webcam(real_time = None):
  capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
  img_number = 0
  while True:
      _, frame = capture.read()
      # width = int(capture.get(3))
      # height = int(capture.get(4))
      if cv2.waitKey(1) == ord('s'):
          img_number += 1
          img = frame.copy()
          img[:,:,1] = 0
          print("Photo ", img_number)
          cv2.imshow('frame', img)
          _, buffer = cv2.imencode('.jpg', frame)
          stream = io.BytesIO(buffer)
          response_detected_faces.append(recognize_faces(stream))
          images_rgb.append(stream)
          if real_time:
            img = draw_one_image(stream, response_detected_faces[-1])
            # img.show()
            img.save(f'images/photo{img_number}.jpg')
            cv2.imshow('frame', np.array(img))
            pause = cv2.waitKey(15000)
            continue
          pause = cv2.waitKey(2000)
      cv2.imshow('frame', frame)
      if cv2.waitKey(1) == ord('q') or cv2.waitKey(10) == ord(' '):
        break
  capture.release()
  cv2.destroyAllWindows()
  
def draw_one_image(image, faces_of_image):
    # print("Draw:", image, faces_of_image)
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    font_size = 30
    try:
      font = ImageFont.truetype("arial.ttf", size=font_size)
    except:
      print("Can`t find font in OS")
      font = None
    # response_detected_faces = recognize_faces(img)
    # for face in response_detected_faces:
    
    if faces_of_image == "NoFace":
      draw.text((200, 10), "No face detected", fill=(255, 255, 255), font=font)
      return img
    
    for face in faces_of_image:
      # face_id = face.face_id
      age = face.face_attributes.age
      emotion = face.face_attributes.emotion
      gender = face.face_attributes.gender
      neutral = '{0:.0f}%'.format(emotion.neutral * 100)
      happiness = '{0:.0f}%'.format(emotion.happiness * 100)
      anger = '{0:.0f}%'.format(emotion.anger * 100)
      sandness = '{0:.0f}%'.format(emotion.sadness * 100)
          
      #Rectange for face    
      rect = face.face_rectangle
      left = rect.left
      top = rect.top
      right = rect.width + left
      bottom = rect.height + top
      draw.rectangle(((left, top), (right, bottom)), outline='green', width=5)
      
      #Face parameters
      draw.text((right + 4, top), 'Age: ' + str(int(age)), fill=(255, 255, 255), font=font)
      draw.text((right + 4, top+font_size), 'Gender: ' + gender, fill=(255, 255, 255), font=font)
      draw.text((right + 4, top+font_size*2), 'Neutral: ' + neutral, fill=(255, 255, 255), font=font)
      draw.text((right + 4, top+font_size*3), 'Happy: ' + happiness, fill=(255, 255, 255), font=font)
      draw.text((right + 4, top+font_size*4), 'Sad: ' + sandness, fill=(255, 255, 255), font=font)
      draw.text((right + 4, top+font_size*5), 'Angry: ' + anger, fill=(255, 255, 255), font=font)
      return img
  
  
def draw_and_save_all():

      
  for idx, (image, faces) in enumerate(zip(images_rgb, response_detected_faces)):
    img = draw_one_image(image, faces, idx)
    img.show()
    img.save(f'images/photo{idx+1}.jpg')
  print("The End")


if __name__ == "__main__":
  remove_all_photos_from_folder()
  start_webcam(real_time=True) 
  # recognize_from_img_path(path)
  
  # draw_and_save_all() # alebo start_webcam(real_time = True) 
  




