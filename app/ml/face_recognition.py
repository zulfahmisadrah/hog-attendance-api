import joblib
import pickle
from os import path

import cv2
import numpy
from PIL.JpegImagePlugin import JpegImageFile
from skimage import feature
from sklearn.metrics import accuracy_score

from app.core.config import settings
from app.utils.commons import get_current_datetime
from app.utils.file_helper import get_course_models_directory


def recognize(image, semester_code: str, course_code: str):
    alpha = 1.5  # Contrast control (1.0-3.0)
    beta = 0  # Brightness control (0-100)
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    # svm_model = pickle.load(open(model_path, 'rb'))
    svm_model = joblib.load(model_path)
    current_datetime = get_current_datetime()
    user_image = image
    capture_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_1.face.jpg")
    cv2.imwrite(capture_path, user_image)
    user_image = cv2.convertScaleAbs(user_image, alpha=alpha, beta=beta)
    adjusted_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_2.adjusted.jpg")
    cv2.imwrite(adjusted_path, user_image)
    user_image = cv2.cvtColor(user_image, cv2.COLOR_RGB2GRAY)
    gray_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_3.gray.jpg")
    cv2.imwrite(gray_path, user_image)
    resized_image = cv2.resize(user_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
    resized_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_4.resized.jpg")
    cv2.imwrite(resized_path, resized_image)
    # get the HOG descriptor for the test image
    (hog_desc, hog_image) = feature.hog(resized_image, orientations=9, pixels_per_cell=(8, 8),
                                        cells_per_block=(2, 2), transform_sqrt=True, block_norm='L2-Hys',
                                        visualize=True)
    hog_path = path.join(settings.ML_TEST_FOLDER, f"{current_datetime}_5.hog.jpg")
    cv2.imwrite(hog_path, hog_image * 255.)
    # print(hog_desc)
    # prediction
    # pred = svm_model.predict(hog_desc.reshape(1, -1))
    pred = svm_model.predict([hog_desc])

    # convert the HOG image to appropriate data type. We do...
    # ... this instead of rescaling the pixels from 0. to 255.
    # put the predicted text on the test image
    # print("ACCURACY", accuracy_score(resized_image, pred))
    return pred
    # cv2.putText(image, pred.title(), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
    #             (0, 255, 0), 2)
    # cv2.imshow('Test Image', image)
    # cv2.imwrite(f"outputs/{args['path']}_hog_{i}.jpg",
    #             hog_image * 255.)  # multiply by 255. to bring to OpenCV pixel range
    # cv2.imwrite(f"outputs/{args['path']}_pred_{i}.jpg", image)
