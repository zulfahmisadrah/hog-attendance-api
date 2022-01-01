import time
from typing import Union

from os import path
from mtcnn import MTCNN
from PIL.Image import Image

from app.services.image_processing import *
from app.utils.file_helper import get_dir
from app.utils.commons import get_current_datetime

detector = MTCNN()


def detect_face_from_image_path(image_path: str, save_preprocessing: bool = False):
    image_name = path.basename(path.normpath(image_path))
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    print("-----------------------------------")
    print("DETECTING FACE ON ", image_name)
    detected_faces = detect_face_on_image(img, save_preprocessing)
    return detected_faces


def detect_face_on_image(img: Union[Image, ndarray], save_preprocessing: bool = False, return_box=False):
    if not isinstance(img, ndarray):
        img = np.array(img)
    img = resize_image(img)

    preprocessed_images_dir = get_dir(settings.ML_PREPROCESSED_IMAGES_FOLDER)
    current_datetime = get_current_datetime()

    # if save_preprocessing:
    #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     capture_path = path.join(preprocessed_images_dir, f"{current_datetime}.0_input.jpg")
    #     cv2.imwrite(capture_path, img)
    #     img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

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
