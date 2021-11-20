import math
from typing import Union

import cv2
import numpy as np
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile
from mtcnn import MTCNN
from os import path
from numpy import ndarray

from app.core.config import settings
from app.utils.commons import get_current_datetime

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
        print("ROTATED = ", direction, angle)
    return img


def rotate_image(img, angle):
    img = Image.fromarray(img)
    img = np.array(img.rotate(angle))
    return img


def detect_face(image_path: str, save_preprocessing: bool = False):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (1200, 1600))

    current_datetime = get_current_datetime()
    # if save_preprocessing:
    #     capture_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.capture.jpg")
    #     cv2.imwrite(capture_path, img)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    detections = detector.detect_faces(img)
    detected_faces = []
    print("TOTAL DETECTIONS = ", len(detections))
    for detection in detections:
        score = detection["confidence"]
        print("DETECTION = ", detection)
        # print("CONFIDENCE = ", score)
        if score >= 0.97:
            x, y, w, h = detection["box"]
            keypoints = detection["keypoints"]
            left_eye = keypoints["left_eye"]
            right_eye = keypoints["right_eye"]
            # aligned_image = alignment_procedure(img, left_eye, right_eye)
            # detected_face = aligned_image[int(y)-extra:int(y + h)+extra, int(x)-extra:int(x + w)+extra]
            detected_face = img[int(y):int(y + h), int(x):int(x + w)]
            detected_face = cv2.cvtColor(detected_face, cv2.COLOR_RGB2BGR)

            if save_preprocessing:
                face_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.1_face.jpg")
                cv2.imwrite(face_path, detected_face)

            detected_face = alignment_procedure(detected_face, left_eye, right_eye)

            if save_preprocessing:
                aligned_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.2_aligned.jpg")
                cv2.imwrite(aligned_path, detected_face)

            detected_face = cv2.cvtColor(detected_face, cv2.COLOR_BGR2RGB)
            detection2 = detector.detect_faces(detected_face)

            if detection2:
                detection2 = detection2[0]
                print("DETECTION2 = ", detection2)
                # eye = detected_face[int(ly):int(ly + padding_y), int(lx):int(lx + padding_y)]
                x2, y2, w2, h2 = detection2["box"]
                detected_face2 = detected_face[int(y2):int(y2 + h2), int(x2):int(x2 + w2)]
                detected_face2 = cv2.cvtColor(detected_face2, cv2.COLOR_RGB2BGR)
                keypoints = detection2["keypoints"]
                left_eye = keypoints["left_eye"]
                right_eye = keypoints["right_eye"]
                left_mouth = keypoints["mouth_left"]
                right_mouth = keypoints["mouth_right"]
                padding_y = int(0.1 * h2)
                padding_x = int(0.2 * w2)
                lx = max(0, left_eye[0] - padding_x)
                ly = max(0, left_eye[1] - int(0.15 * h2))
                lx2 = right_eye[0] + padding_x
                ly2 = left_eye[1] + int(0.1 * h2)
                mlx = left_mouth[0] - int(0.05 * w2)
                mlx2 = right_mouth[0] + int(0.05 * w2)
                mly = left_mouth[1] - padding_y
                mly2 = left_mouth[1] + int(0.15 * h2)
                mask = np.zeros(detected_face2.shape[:2], dtype="uint8")
                cv2.rectangle(mask, (lx, ly), (lx2, ly2), 255, -1)
                cv2.rectangle(mask, (mlx, ly2), (mlx2, mly2), 255, -1)

                if save_preprocessing:
                    mask_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.4_mask_path.jpg")
                    cv2.imwrite(mask_path, mask)

                masked = cv2.bitwise_and(detected_face2, detected_face2, mask=mask)

                if save_preprocessing:
                    masked_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.5_masked.jpg")
                    cv2.imwrite(masked_path, masked)

                cropped = masked[ly:mly2, lx:lx2]

                if save_preprocessing:
                    cropped_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.6_cropped.jpg")
                    cv2.imwrite(cropped_path, cropped)

                detected_faces.append(cropped)
            else:
                detected_faces.append(detected_face)
    if not detected_faces:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        detected_faces.append(img)
    return detected_faces


def detect_face_on_image(image: Union[JpegImageFile, ndarray]):
    if isinstance(image, JpegImageFile):
        img = np.array(image)
    # img = cv2.resize(img, (1200, 1600))
    else:
        img = image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    current_datetime = get_current_datetime()
    capture_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.capture.jpg")
    cv2.imwrite(capture_path, img)
    detections = detector.detect_faces(img)
    detected_faces = []
    print("TOTAL DETECTIONS = ", len(detections))
    for detection in detections:
        score = detection["confidence"]
        print("DETECTION = ", detection)
        # print("CONFIDENCE = ", score)
        if score >= 0.97:
            x, y, w, h = detection["box"]
            keypoints = detection["keypoints"]
            left_eye = keypoints["left_eye"]
            right_eye = keypoints["right_eye"]
            detected_face = img[int(y):int(y + h), int(x):int(x + w)]
            face_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.1_face.jpg")
            cv2.imwrite(face_path, detected_face)
            detected_face = alignment_procedure(detected_face, left_eye, right_eye)
            aligned_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.2_aligned.jpg")
            cv2.imwrite(aligned_path, detected_face)
            detection2 = detector.detect_faces(detected_face)
            if detection2:
                detection2 = detection2[0]
                print("DETECTION2 = ", detection2)
                # eye = detected_face[int(ly):int(ly + padding_y), int(lx):int(lx + padding_y)]
                # eye_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.eye.jpg")
                x2, y2, w2, h2 = detection2["box"]
                detected_face2 = detected_face[int(y2):int(y2 + h2), int(x2):int(x2 + w2)]
                if not isinstance(image, JpegImageFile):
                    detected_face2 = cv2.cvtColor(detected_face2, cv2.COLOR_RGB2BGR)
                aligned_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.3_face2.jpg")
                cv2.imwrite(aligned_path, detected_face2)
                keypoints = detection2["keypoints"]
                left_eye = keypoints["left_eye"]
                right_eye = keypoints["right_eye"]
                left_mouth = keypoints["mouth_left"]
                right_mouth = keypoints["mouth_right"]
                padding_y = int(0.1 * h2)
                padding_x = int(0.2 * w2)
                lx = max(0, left_eye[0] - padding_x)
                ly = max(0, left_eye[1] - int(0.15 * h2))
                lx2 = right_eye[0] + padding_x
                ly2 = left_eye[1] + int(0.1 * h2)
                mlx = left_mouth[0] - int(0.05 * w2)
                mlx2 = right_mouth[0] + int(0.05 * w2)
                # mly = left_mouth[1] - padding_y
                mly2 = left_mouth[1] + int(0.15 * h2)
                print(lx, ly, lx2, ly2, mlx, mlx2, mly2)
                # eye = detected_face2[ly:ly2, lx:lx2]
                # nose_mouth = detected_face2[ly2:mly2, mlx:mlx2]
                # nose_mouth_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.nose_mouth.jpg")
                # cv2.imwrite(eye_path, eye)
                # cv2.imwrite(nose_mouth_path, nose_mouth)
                mask = np.zeros(detected_face2.shape[:2], dtype="uint8")
                cv2.rectangle(mask, (lx, ly), (lx2, ly2), 255, -1)
                cv2.rectangle(mask, (mlx, ly2), (mlx2, mly2), 255, -1)
                mask_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.4_mask_path.jpg")
                cv2.imwrite(mask_path, mask)
                masked = cv2.bitwise_and(detected_face2, detected_face2, mask=mask)
                masked_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.5_masked.jpg")
                cv2.imwrite(masked_path, masked)
                cropped = masked[ly:mly2, lx:lx2]
                cropped_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_0.6_cropped.jpg")
                cv2.imwrite(cropped_path, cropped)
                # if isinstance(image, JpegImageFile):
                detected_faces.append((cropped, detection["box"]))
            else:
                # detected_face = cv2.cvtColor(detected_face, cv2.COLOR_RGB2BGR)
                if isinstance(image, JpegImageFile):
                    detected_face = cv2.cvtColor(detected_face, cv2.COLOR_RGB2BGR)
                detected_faces.append((detected_face, detection["box"]))
    return detected_faces
#to draw faces on image
# for result in faces:
#     x, y, w, h = result['box']
#     x1, y1 = x + w, y + h
#     cv2.rectangle(img, (x, y), (x1, y1), (0, 0, 255), 2)
