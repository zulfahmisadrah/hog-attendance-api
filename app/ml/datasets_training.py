import cv2
import pickle
import joblib
from os import path

from skimage import feature
from sklearn.svm import LinearSVC, SVC

from app.core.config import settings
from app.utils.file_helper import get_list_files, get_course_models_directory, get_hog_outputs_directory, \
    get_user_datasets_directory


def train_datasets(semester_code: str, course_code: str):
    print('--- PREPARING DATASETS ---')
    images = []
    labels = []
    alpha = 1.5  # Contrast control (1.0-3.0)
    beta = 0  # Brightness control (0-100)
    # get all the image folder paths
    image_paths = get_list_files(settings.DATASETS_FOLDER)
    for username in image_paths:
        # get all the image names
        user_directory_path = get_user_datasets_directory(username)
        all_images = get_list_files(user_directory_path)
        # iterate over the image names, get the label
        # list_datasets = [path.join(user_dir, filename) for filename in all_images]
        for (i, image) in enumerate(all_images):
            user_directory = path.join(user_directory_path, image)
            user_image = cv2.imread(user_directory)
            user_image = cv2.convertScaleAbs(user_image, alpha=alpha, beta=beta)
            cv2.imwrite(path.join(get_hog_outputs_directory(username), f"{username}_adjusted.{i+1}.jpg"), user_image)
            user_image = cv2.cvtColor(user_image, cv2.COLOR_RGB2GRAY)
            user_image = cv2.resize(user_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
            # get the HOG descriptor for the image
            (hog_desc, hog_image) = feature.hog(user_image, orientations=9, pixels_per_cell=(8, 8),
                                                cells_per_block=(2, 2), transform_sqrt=True, block_norm='L2-Hys',
                                                visualize=True)
            user_output_directory = get_hog_outputs_directory(username)
            output_file_name = f"{username}_hog.{i+1}.jpg"
            output_path = path.join(user_output_directory, output_file_name)
            cv2.imwrite(output_path, hog_image * 255.)
            images.append(hog_desc)
            labels.append(username)
    print('--- TRAINING MODEL ---')
    # svm_model = LinearSVC(random_state=42, tol=1e-5)
    svm_model = SVC(kernel='linear', gamma='scale', random_state=42)
    svm_model.fit(images, labels)
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    joblib.dump(svm_model, model_path)
    # pickle.dump(svm_model, open(model_path, 'wb'))
    print('--- MODEL CREATED ---')
    return model_path
