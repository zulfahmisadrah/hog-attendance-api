import joblib
from os import path

import cv2
from skimage import feature

from app.core.config import settings
from app.utils.commons import get_current_datetime
from app.utils.file_helper import get_course_models_directory


def recognize(image, semester_code: str, course_code: str):
    current_datetime = get_current_datetime()
    user_image = image
    capture_path = path.join(settings.ML_PREPROCESSED_IMAGES_FOLDER, f"{current_datetime}_1.face.jpg")
    cv2.imwrite(capture_path, user_image)
    user_image = cv2.convertScaleAbs(user_image, alpha=settings.IMAGE_ALPHA, beta=settings.IMAGE_BETA)
    adjusted_path = path.join(settings.ML_PREPROCESSED_IMAGES_FOLDER, f"{current_datetime}_2.adjusted.jpg")
    cv2.imwrite(adjusted_path, user_image)
    user_image = cv2.cvtColor(user_image, cv2.COLOR_RGB2GRAY)
    gray_path = path.join(settings.ML_PREPROCESSED_IMAGES_FOLDER, f"{current_datetime}_3.gray.jpg")
    cv2.imwrite(gray_path, user_image)
    resized_image = cv2.resize(user_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
    resized_path = path.join(settings.ML_PREPROCESSED_IMAGES_FOLDER, f"{current_datetime}_4.resized.jpg")
    cv2.imwrite(resized_path, resized_image)
    # get the HOG descriptor for the test image
    (hog_desc, hog_image) = feature.hog(resized_image, orientations=settings.HOG_ORIENTATIONS, pixels_per_cell=settings.HOG_PIXELS_PER_CELL,
                                        cells_per_block=settings.HOG_CELLS_PER_BLOCK, transform_sqrt=True, block_norm='L2-Hys',
                                        visualize=True)
    hog_path = path.join(settings.ML_PREPROCESSED_IMAGES_FOLDER, f"{current_datetime}_5.hog.jpg")
    cv2.imwrite(hog_path, hog_image * 255.)
    # pred = svm_model.predict(hog_desc.reshape(1, -1))
    # print("hog_desc", [hog_desc])
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    # svm_model = pickle.load(open(model_path, 'rb'))
    svm_model = joblib.load(model_path)
    pred = svm_model.predict([hog_desc])
    results = svm_model.predict_proba([hog_desc])[0]
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

