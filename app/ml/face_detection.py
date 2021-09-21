import math

import cv2
import numpy as np
from PIL import Image
from mtcnn.mtcnn import MTCNN

detector = MTCNN()


def euclidean_distance(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return math.sqrt(((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)))


def alignment_procedure(img, left_eye, right_eye):
    # this function aligns given face in img based on left and right eye coordinates
    left_eye_x, left_eye_y = left_eye
    right_eye_x, right_eye_y = right_eye

    # find rotation direction
    if left_eye_y >= right_eye_y:
        point_3rd = (right_eye_x, left_eye_y)
        direction = -1  # rotate same direction to clock
    else:
        point_3rd = (left_eye_x, right_eye_y)
        direction = 1  # rotate inverse direction of clock

    # find length of triangle edges
    a = euclidean_distance(np.array(left_eye), np.array(point_3rd))
    b = euclidean_distance(np.array(right_eye), np.array(point_3rd))
    c = euclidean_distance(np.array(right_eye), np.array(left_eye))

    # apply cosine rule
    if b != 0 and c != 0:  # this multiplication causes division by zero in cos_a calculation
        cos_a = (b * b + c * c - a * a) / (2 * b * c)
        angle = np.arccos(cos_a)  # angle in radian
        angle = (angle * 180) / math.pi  # radian to degree

        # rotate base image
        if direction == -1:
            angle = 90 - angle
        img = Image.fromarray(img)
        img = np.array(img.rotate(direction * angle))
    return img


def rotate_image(img, angle):
    img = Image.fromarray(img)
    img = np.array(img.rotate(angle))
    return img


def detect_face(image_path: str):
    img = cv2.imread(image_path)
    detections = detector.detect_faces(img)
    for detection in detections:
        score = detection["confidence"]
        print("DETECTION = ", detection)
        print("CONFIDENCE = ", score)
        if score >= 0.80:
            x, y, w, h = detection["box"]
            keypoints = detection["keypoints"]
            left_eye = keypoints["left_eye"]
            right_eye = keypoints["right_eye"]
            face = alignment_procedure(img, left_eye, right_eye)
            detected_face = face[int(y):int(y + h), int(x):int(x + w)]
            return detected_face
#to draw faces on image
# for result in faces:
#     x, y, w, h = result['box']
#     x1, y1 = x + w, y + h
#     cv2.rectangle(img, (x, y), (x1, y1), (0, 0, 255), 2)
