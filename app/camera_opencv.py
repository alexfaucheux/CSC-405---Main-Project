import os
import cv2
from app.base_camera import BaseCamera
from app.models import Image


# Class used to capture frames from camera
class Camera(BaseCamera):
    # 0 == native
    # >0 == peripheral
    video_source = 0

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
