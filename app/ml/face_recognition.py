import joblib
import pickle
from os import path

import cv2
import numpy
from PIL.JpegImagePlugin import JpegImageFile
from skimage import feature
from sklearn.metrics import accuracy_score

from app.utils.file_helper import get_course_models_directory


def recognize(image: JpegImageFile, semester_code: str, course_code: str):
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.sav"
    model_path = path.join(course_directory, model_name)
    # svm_model = pickle.load(open(model_path, 'rb'))
    svm_model = joblib.load(model_path)
    resized_image = cv2.resize(numpy.array(image), (64, 128))
    # get the HOG descriptor for the test image
    hog_desc = feature.hog(resized_image, orientations=9, pixels_per_cell=(8, 8),
                           cells_per_block=(2, 2), transform_sqrt=True, block_norm='L2-Hys')
    # prediction
    pred = svm_model.predict(hog_desc.reshape(1, -1))

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
