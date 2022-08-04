import joblib
from fastapi.logger import logger
from os import path

import cv2
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_site_setting
from app.services.image_processing import get_hog_features, enhance_image, convert_to_grayscale, get_embedding
from app.utils.commons import get_current_datetime
from app.utils.file_helper import get_course_models_directory, get_dir


def recognize(db: Session, face_image, semester_code: str, course_code: str, save_preprocessing: bool = False,
              return_probability: bool = False):
    use_facenet = crud_site_setting.site_setting.use_facenet(db)
    current_datetime = get_current_datetime()
    preprocessed_images_dir = get_dir(path.join(settings.ML_PREPROCESSED_IMAGES_FOLDER))
    file_name_prefix = f"{current_datetime}_{str(uuid.uuid4())}"

    image = face_image
    # if save_preprocessing:
    #     capture_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.1_face.jpg")
    #     cv2.imwrite(capture_path, image)

    if use_facenet:
        image = cv2.resize(image, settings.FACENET_INPUT_SIZE)
        feature = get_embedding(image)
    else:
        # Image Enhancement
        enhanced_image = enhance_image(image)
        # enhanced_image = image
        if save_preprocessing:
            enhanced_image_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.4_enhanced.jpg")
            cv2.imwrite(enhanced_image_path, enhanced_image)

        # Grayscaling
        gray_image = convert_to_grayscale(enhanced_image)
        if save_preprocessing:
            gray_image_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.5_gray.jpg")
            cv2.imwrite(gray_image_path, gray_image)

        # Resize
        resized_image = cv2.resize(gray_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
        if save_preprocessing:
            resized_image_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.6_resized.jpg")
            cv2.imwrite(resized_image_path, resized_image)

        # HOG Features
        (feature, hog_image) = get_hog_features(resized_image)
        if save_preprocessing:
            hog_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.7_hog.jpg")
            cv2.imwrite(hog_path, hog_image * 255.)

    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    svm_model = joblib.load(model_path)
    pred = svm_model.predict([feature])
    results = svm_model.predict_proba([feature])[0]
    prob_per_class_dictionary = dict(zip(svm_model.classes_, results))
    results_ordered_by_probability = sorted(zip(svm_model.classes_, results), key=lambda x: x[1], reverse=True)
    probability = prob_per_class_dictionary[pred[0]]
    if pred:
        logger.info(f"PREDICTION -- label: {pred[0]}, prob: {str(prob_per_class_dictionary[pred[0]])}, "
                    f"others: {str(results_ordered_by_probability[1:4])}")
    return pred[0]

