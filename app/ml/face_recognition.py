import joblib
from os import path

import cv2
import uuid

from app.core.config import settings
from app.services.image_processing import get_hog_features, enhance_image, convert_to_grayscale, get_embedding
from app.utils.commons import get_current_datetime
from app.utils.file_helper import get_course_models_directory, get_dir


def recognize(face_image, semester_code: str, course_code: str, save_preprocessing: bool = False,
              use_facenet: bool = settings.USE_FACENET):
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

    # pred = svm_model.predict(hog_desc.reshape(1, -1))
    # print("hog_desc", [hog_desc])
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    # svm_model = pickle.load(open(model_path, 'rb'))
    svm_model = joblib.load(model_path)
    pred = svm_model.predict([feature])
    results = svm_model.predict_proba([feature])[0]
    # print(svm_model.classes_)
    # print(results)
    # print(zip(svm_model.classes_, results))
    prob_per_class_dictionary = dict(zip(svm_model.classes_, results))
    # print(prob_per_class_dictionary)
    print(pred)
    if pred:
        print("PROBABILITY: ", prob_per_class_dictionary[pred[0]])
    # results_ordered_by_probability = list(map(lambda x: x[0],
    #                                      sorted(zip(svm_model.classes_, results), key=lambda x: x[1], reverse=True)))
    # print(results_ordered_by_probability)
    return pred[0]

