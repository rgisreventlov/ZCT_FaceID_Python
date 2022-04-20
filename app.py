import base64
import io
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from azure.cognitiveservices.vision.face import FaceClient
from flask import Flask, render_template, Response, url_for, send_from_directory
import cv2
from msrest.authentication import CognitiveServicesCredentials

app = Flask(__name__)

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # use 0 for web camera
with open('api_key.json', 'r') as f:
  settings = json.load(f)
API_KEY = settings['key']
ENDPOINT = settings['endpoint']
face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(API_KEY))

global img_id
img_id = 0

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


def get_frame():
    return camera.read()[1]


def recognize_faces(rgb_image_stream):
    response_detected_faces = face_client.face.detect_with_stream(
        rgb_image_stream,
        detection_model='detection_01',
        recognition_model='recognition_04',
        return_face_attributes=['age', 'gender', 'emotion']
    )
    # print(response_detected_faces)
    if not response_detected_faces:
        print('No face detected')
        return "NoFace"

    print('Number of people detected: {0}'.format(len(response_detected_faces)))

    return response_detected_faces


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

        # Rectange for face
        rect = face.face_rectangle
        left = rect.left
        top = rect.top
        right = rect.width + left
        bottom = rect.height + top
        draw.rectangle(((left, top), (right, bottom)), outline='green', width=5)

        # Face parameters
        draw.text((right + 4, top), 'Age: ' + str(int(age)), fill=(255, 255, 255), font=font)
        draw.text((right + 4, top + font_size), 'Gender: ' + gender, fill=(255, 255, 255), font=font)
        draw.text((right + 4, top + font_size * 2), 'Neutral: ' + neutral, fill=(255, 255, 255), font=font)
        draw.text((right + 4, top + font_size * 3), 'Happy: ' + happiness, fill=(255, 255, 255), font=font)
        draw.text((right + 4, top + font_size * 4), 'Sad: ' + sandness, fill=(255, 255, 255), font=font)
        draw.text((right + 4, top + font_size * 5), 'Angry: ' + anger, fill=(255, 255, 255), font=font)
        return img


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/take_a_photo')
def take_a_photo():
    print("took a photo")
    global img_id
    img_id = img_id + 1
    frame = get_frame()
    img = frame.copy()
    im = Image.fromarray(np.uint8(img * 255))
    _, buffer = cv2.imencode('.jpg', frame)
    stream = io.BytesIO(buffer)

    recognized_face = recognize_faces(stream)
    im = draw_one_image(stream, recognized_face)

    im.save(stream, "JPEG")
    encoded_img_data = base64.b64encode(stream.getvalue())
    im.save(f'static/image_{img_id}.jpg')

    return encoded_img_data


@app.route('/sample')
def sample():
    print(img_id)
    return send_from_directory("static", f"image_{img_id}.jpg")


if __name__ == '__main__':
    app.run(debug=False)
