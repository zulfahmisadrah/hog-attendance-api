import math
import time
from typing import Union

import cv2
import numpy as np
from PIL.Image import Image
from mtcnn import MTCNN
from os import path
from numpy import ndarray

from app.core.config import settings
from app.utils.commons import get_current_datetime
from app.utils.file_helper import get_dir

detector = MTCNN()


def euclidean_distance(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return math.sqrt(((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)))


def rotate_point(origin, point, angle):
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return int(qx), int(qy)


def radian_to_degree(radian):
    return (radian * 180) / math.pi


def angle_with_direction(angle, direction):
    if direction == -1:
        angle = 90 - angle
    return direction * angle


def align_eyes(left_eye, right_eye):
    # this function aligns given face in img based on left and right eye coordinates
    left_eye_x, left_eye_y = left_eye
    right_eye_x, right_eye_y = right_eye

    # find rotation direction
    if left_eye_y > right_eye_y:
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
        angle = np.arccos(cos_a)
    else:
        angle = 0
    return angle, direction, point_3rd  # angle in radian


def rotate_image(img, angle, center=None):
    (h, w) = img.shape[:2]
    if center:
        (cX, cY) = center
    else:
        (cX, cY) = (w / 2, h / 2)
    matrix = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    rotated_img = cv2.warpAffine(img, matrix, (w, h))
    return rotated_img


def resize_image(image):
    height, width = image.shape[:2]
    if height > settings.IMAGE_RESIZE_1 or width > settings.IMAGE_RESIZE_1:
        if height > width:
            image = cv2.resize(image, (settings.IMAGE_RESIZE_1, settings.IMAGE_RESIZE_2))
        else:
            image = cv2.resize(image, (settings.IMAGE_RESIZE_2, settings.IMAGE_RESIZE_1))
    return image


def put_bounding_box_and_face_landmarks(img, box, keypoints):
    x, y, w, h = box
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.circle(img, keypoints["left_eye"], 4, (0, 255, 0), 2)
    cv2.circle(img, keypoints["right_eye"], 4, (0, 255, 0), 2)
    cv2.circle(img, keypoints["nose"], 4, (0, 255, 0), 2)
    cv2.circle(img, keypoints["mouth_left"], 4, (0, 255, 0), 2)
    cv2.circle(img, keypoints["mouth_right"], 4, (0, 255, 0), 2)
    return img


def cut_forehead_in_box(box, keypoints):
    x, y, w, h = box
    # Cut half forehead above
    left_eye_y = keypoints["left_eye"][1]
    right_eye_y = keypoints["right_eye"][1]
    highest_eye = right_eye_y if right_eye_y < left_eye_y else left_eye_y
    half_forehead = (highest_eye - y) / 2
    new_y = int(y + half_forehead)  # move y down to half forehead point
    new_h = int(h - half_forehead)  # reduce height because half forehead removed
    return x, new_y, w, new_h


def crop_face(img, box, keypoints, cut_forehead=False):
    x, y, w, h = box
    if cut_forehead:
        # Cut half forehead above
        left_eye_y = keypoints["left_eye"][1]
        right_eye_y = keypoints["right_eye"][1]
        highest_eye = right_eye_y if right_eye_y < left_eye_y else left_eye_y
        half_forehead = (highest_eye - y) / 2
        new_y = int(y + half_forehead)  # move y down to half forehead point
        new_h = int(h - half_forehead)  # reduce height because half forehead removed
        # Crop face
        cropped_face = img[int(new_y):int(new_y + new_h), int(x):int(x + w)]
        return cropped_face, new_y, new_h
    else:
        cropped_face = img[int(y):int(y + h), int(x):int(x + w)]
        return cropped_face


def detect_face_from_image_path(image_path: str, save_preprocessing: bool = False):
    image_name = path.basename(path.normpath(image_path))
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    print("DETECTING FACE ON ", image_name)
    detected_faces = detect_face_on_image(img, save_preprocessing)
    return detected_faces


def detect_face_on_image(img: Union[Image, ndarray], save_preprocessing: bool = False, return_box=False):
    if not isinstance(img, ndarray):
        img = np.array(img)
    img = resize_image(img)

    preprocessed_images_dir = get_dir(settings.ML_PREPROCESSED_IMAGES_FOLDER)
    current_datetime = get_current_datetime()

    if save_preprocessing:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        capture_path = path.join(preprocessed_images_dir, f"{current_datetime}.0_input.jpg")
        cv2.imwrite(capture_path, img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Detect Face using MTCNN
    detecting_time_start = time.perf_counter()
    detections = detector.detect_faces(img)
    detecting_time_finish = time.perf_counter()
    detection_time = detecting_time_finish - detecting_time_start

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    print("TOTAL DETECTIONS = ", len(detections))
    print(f"DETECTION TIME = {detection_time} s")

    detected_faces = []
    for (i, detection) in enumerate(detections):
        counter = i + 1
        score = detection["confidence"]
        print("DETECTION = ", detection)
        if score >= 0.97:
            box = detection["box"]
            keypoints = detection["keypoints"]
            left_eye = keypoints["left_eye"]
            right_eye = keypoints["right_eye"]

            # Put bounding box and face landmarks
            img_bounding_box = np.copy(img)
            img_bounding_box = put_bounding_box_and_face_landmarks(img_bounding_box, box, keypoints)
            if save_preprocessing:
                img_box_path = path.join(preprocessed_images_dir, f"{current_datetime}_{counter}.1_detection.jpg")
                cv2.imwrite(img_box_path, img_bounding_box)

            # Cut half forehead above
            bounding_box = cut_forehead_in_box(box, keypoints)
            x, y, w, h = bounding_box

            # Crop face
            cropped_face = crop_face(img, bounding_box, keypoints)
            if save_preprocessing:
                face_path = path.join(preprocessed_images_dir, f"{current_datetime}_{counter}.2_face.jpg")
                cv2.imwrite(face_path, cropped_face)

            # Face alignment
            angle_in_radian, direction, point_3rd = align_eyes(left_eye, right_eye)
            angle = radian_to_degree(angle_in_radian)
            angle = angle_with_direction(angle, direction)
            print(f"ROTATED = {angle} degree")

            bounding_box_center = (int(x + w / 2), int(y + h / 2))
            # Rotate Image with bounding box center as anchor
            aligned_image = rotate_image(img, angle, bounding_box_center)
            # Crop aligned face
            detected_face = crop_face(aligned_image, bounding_box, keypoints)
            if save_preprocessing:
                aligned_path = path.join(preprocessed_images_dir, f"{current_datetime}_{counter}.3_aligned_face.jpg")
                cv2.imwrite(aligned_path, detected_face)

            if return_box:
                detected_faces.append((detected_face, box))
            else:
                detected_faces.append(detected_face)
    return detected_faces

