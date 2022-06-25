import time
from shutil import rmtree
from fastapi.logger import logger
from typing import Union

import cv2
from os import path
from mtcnn import MTCNN
from PIL.Image import Image

from app.db.session import SessionLocal
from app.services.image_processing import *
from app.utils.file_helper import get_dir, generate_file_name
from app.utils.commons import get_current_datetime
from app.ml.face_recognition import recognize

detector = MTCNN()


def detect_face_on_image(image_src: Union[Image, ndarray, str], save_path: str = "", save_preprocessing: bool = False,
                         resize_image: bool = True, multiple_faces: bool = True, return_box: bool = False,
                         recognize_face=False, semester_code: str = "", course_code: str = "",
                         custom_threshold: float = None):
    if isinstance(image_src, str):
        image_name = path.basename(path.normpath(image_src))
        image_input = cv2.imread(image_src)
        image_input = cv2.cvtColor(image_input, cv2.COLOR_RGB2BGR)
        logger.info("-----------------------------------")
        logger.info("DETECTING FACE ON " + image_name)
    else:
        image_input = image_src

    if not isinstance(image_input, ndarray):
        image = np.array(image_input)
    else:
        image = image_input
    img = resize_image_if_too_big(image) if resize_image else image

    current_datetime = get_current_datetime()
    if save_path:
        # total_datasets = get_total_files(preprocessed_images_dir)
        # if total_datasets > 0:
        #     rmtree(preprocessed_images_dir)
        #     preprocessed_images_dir = get_dir(path.join(get_dir(settings.ML_PREPROCESSED_IMAGES_FOLDER), save_path))
        username = path.basename(path.normpath(save_path))
        prefix_name = generate_file_name(save_path, username, extension="")
    else:
        prefix_name = current_datetime

    preprocessed_images_dir = save_path if save_path else get_dir(settings.ML_PREPROCESSED_IMAGES_FOLDER)
    # if save_preprocessing:
    #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     capture_path = path.join(preprocessed_images_dir, f"{prefix_name}.0_input.jpg")
    #     cv2.imwrite(capture_path, img)
    #     img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Detect Face using MTCNN
    detecting_time_start = time.perf_counter()
    detections = detector.detect_faces(img)
    detecting_time_finish = time.perf_counter()
    detection_time = detecting_time_finish - detecting_time_start

    if len(detections) == 0:
        logger.info("TOTAL DETECTIONS = " + str(len(detections)))
        logger.info("RETRYING WITH ORIGINAL IMAGE SIZE")
        logger.info(f"PREV SIZE : {img.shape}")
        img = image
        logger.info(f"CURRENT SIZE : {img.shape}")
        detecting_time_start = time.perf_counter()
        detections = detector.detect_faces(image)
        detecting_time_finish = time.perf_counter()
        detection_time = detecting_time_finish - detecting_time_start

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    logger.info("TOTAL DETECTIONS = " + str(len(detections)))

    if len(detections) == 0:
        with open('confidences.csv', 'a') as fd:
            fd.write(f"{current_datetime},{prefix_name}.0,{str(0)},FAILED\n")
            img_failed_path = path.join(preprocessed_images_dir, f"FAILED_{prefix_name}.jpg")
            cv2.imwrite(img_failed_path, img)

    detected_faces = []
    highest_conf = 0
    total_rejected = 0
    for (i, detection) in enumerate(detections):
        counter = i + 1
        file_name_prefix = f"{prefix_name}.{counter}"

        if return_box:
            capture_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.0_input.jpg")
            cv2.imwrite(capture_path, img)

        score = detection["confidence"]

        db = SessionLocal()
        with_masked_datasets = crud_site_setting.site_setting.datasets_with_mask(db)

        if custom_threshold:
            threshold = custom_threshold
        elif with_masked_datasets:
            threshold = settings.ML_THRESHOLD_FACE_DETECTION_MASKED
        else:
            threshold = settings.ML_THRESHOLD_FACE_DETECTION

        if multiple_faces:
            is_detection_accepted = score >= threshold
        else:
            is_detection_accepted = score >= threshold and score >= highest_conf

        with open('confidences.csv', 'a') as fd:
            fd.write(f"{current_datetime},{file_name_prefix},{str(score)},{'ACCEPTED' if is_detection_accepted else 'REJECTED'}\n")

        box = detection["box"]
        keypoints = detection["keypoints"]
        if is_detection_accepted:
            highest_conf = score
            left_eye = keypoints["left_eye"]
            right_eye = keypoints["right_eye"]

            # Put bounding box and face landmarks
            img_bounding_box = np.copy(img)
            img_bounding_box = put_bounding_box_and_face_landmarks(img_bounding_box, box, keypoints)
            if save_preprocessing:
                img_box_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.1_detection.jpg")
                cv2.imwrite(img_box_path, img_bounding_box)

            # Cut half forehead above
            bounding_box = cut_forehead_in_box(box, keypoints)
            x, y, w, h = bounding_box

            # Save image for validation
            # margin = 50
            # img_h, img_w = img.shape[:2]
            # val_box = [max(0, x-margin), max(0, y-margin), min(img_w, w+2*margin), min(img_h, h+2*margin)]
            # val_image = crop_face(img, val_box, keypoints)
            # if save_preprocessing:
            #     face_path = path.join(preprocessed_images_dir, f"val_{file_name_prefix}.jpg")
            #     cv2.imwrite(face_path, val_image)

            # Crop face
            cropped_face = crop_face(img, bounding_box, keypoints)
            if save_preprocessing:
                face_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.2_face.jpg")
                cv2.imwrite(face_path, cropped_face)

            # Face alignment
            angle_in_radian, direction, point_3rd = align_eyes(left_eye, right_eye)
            angle = radian_to_degree(angle_in_radian)
            angle = angle_with_direction(angle, direction)
            logger.info(f"box: {str(detection['box'])}, conf: {str(detection['confidence'])}, rotated: {angle}, "
                        f"time: {detection_time} s")

            bounding_box_center = (int(x + w / 2), int(y + h / 2))
            # Rotate Image with bounding box center as anchor
            aligned_image = rotate_image(img, angle, bounding_box_center)
            # Crop aligned face
            detected_face = crop_face(aligned_image, bounding_box, keypoints)
            if save_preprocessing:
                aligned_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.3_aligned_face.jpg")
                cv2.imwrite(aligned_path, detected_face)

            if recognize_face:
                label = recognize(db, detected_face, semester_code, course_code, save_preprocessing=save_preprocessing)

            if return_box and recognize_face:
                output = (detected_face, box, label)
            elif recognize_face:
                output = (detected_face, label)
            elif return_box:
                output = (detected_face, box)
            else:
                output = detected_face

            if multiple_faces:
                detected_faces.append(output)
            else:
                detected_faces = [output]
        else:
            total_rejected = total_rejected + 1
            logger.info("REJECTED -- " + str(detection))
            # Put bounding box and face landmarks and save
            img_bounding_box = np.copy(img)
            img_bounding_box = put_bounding_box_and_face_landmarks(img_bounding_box, box, keypoints)
            img_box_path = path.join(preprocessed_images_dir, f"REJECTED_{file_name_prefix}.jpg")
            cv2.imwrite(img_box_path, img_bounding_box)

    total_detected = len(detections)
    total_saved = len(detected_faces)
    is_different = total_saved != total_detected
    logger.info(f"SAVED -- {str(total_saved)}/{str(total_detected)}" + (" (DIFFERENT)" if is_different else ""))
    result = {
        "detected_faces": detected_faces,
        "total_rejected": total_rejected,
        "total_saved": total_saved
    }
    return result
