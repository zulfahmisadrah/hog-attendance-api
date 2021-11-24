import cv2
import pickle
import joblib
from os import path

from skimage import feature
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVC, SVC

from app.core.config import settings
from app.ml.face_detection import detect_face_on_image, detect_face
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
        for (i, image_name) in enumerate(all_images):
            user_directory = path.join(user_directory_path, image_name)
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
    parameters = {
        'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
        'C': [0.5, 1, 10, 100],
        'gamma': ['scale', 1, 0.1, 0.01, 0.001],
        'random_state': [0, 42]
    }

    grid_search = GridSearchCV(estimator=SVC(random_state=0),
                               param_grid=parameters,
                               n_jobs=6,
                               verbose=1,
                               scoring='accuracy')
    grid_search.fit(images, labels)
    print(f"Best Score: {grid_search.best_score_}")
    best_params = grid_search.best_estimator_.get_params()
    print("Best Parameters: ")
    for param in parameters:
        print(f"\t{param}: {best_params[param]}")

    # svm_model = LinearSVC(random_state=42, tol=1e-5)
    # svm_model = SVC(kernel=best_params['kernel'], gamma=best_params['gamma'], C=best_params['C'], random_state=best_params['random_state'])
    # svm_model.fit(images, labels)
    # linear = SVC(kernel='linear', C=1, decision_function_shape='ovo')
    # rbf = SVC(kernel='rbf', gamma=1, C=1, decision_function_shape='ovo')
    # poly = SVC(kernel='poly', degree=3, C=1, decision_function_shape='ovo')
    # sig = SVC(kernel='sigmoid', C=1, decision_function_shape='ovo')
    #
    # linear.fit(images, labels)
    # rbf.fit(images, labels)
    # poly.fit(images, labels)
    # sig.fit(images, labels)

    print('--- TESTING MODEL ---')
    validation_images = []
    validation_labels = []
    # recognized_users = []
    validation_files = get_list_files(settings.ML_VALIDATION_FOLDER)
    for username in validation_files:
        user_validation_directory_path = path.join(settings.ML_VALIDATION_FOLDER, username)
        all_images = get_list_files(user_validation_directory_path)
        for (i, image_name) in enumerate(all_images):
            user_directory = path.join(user_validation_directory_path, image_name)
            user_image = cv2.imread(user_directory)
            cv2.imwrite(path.join(get_hog_outputs_directory(username), f"{username}_val_input.{i + 1}.jpg"),
                        user_image)
            # detected_faces = detect_face_on_image(user_image)
            detected_faces = detect_face(user_directory)
            if detected_faces:
                for detected_face in detected_faces:
                    # detected_face, box = result
                    user_image = cv2.convertScaleAbs(detected_face, alpha=alpha, beta=beta)
                    cv2.imwrite(path.join(get_hog_outputs_directory(username), f"{username}_val_adjusted.{i + 1}.jpg"), user_image)
                    user_image = cv2.cvtColor(user_image, cv2.COLOR_RGB2GRAY)
                    user_image = cv2.resize(user_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
                    # get the HOG descriptor for the image
                    (hog_desc, hog_image) = feature.hog(user_image, orientations=9, pixels_per_cell=(8, 8),
                                                        cells_per_block=(2, 2), transform_sqrt=True, block_norm='L2-Hys',
                                                        visualize=True)
                    user_output_directory = get_hog_outputs_directory(username)
                    output_file_name = f"{username}_val_hog.{i + 1}.jpg"
                    output_path = path.join(user_output_directory, output_file_name)
                    cv2.imwrite(output_path, hog_image * 255.)
                    validation_images.append(hog_desc)
                    validation_labels.append(username)
    # recognized_users = svm_model.predict(validation_images)
    recognized_users = grid_search.predict(validation_images)
    # accuracy_lin = linear.score(validation_images, validation_labels)
    # accuracy_poly = poly.score(validation_images, validation_labels)
    # accuracy_rbf = rbf.score(validation_images, validation_labels)
    # accuracy_sig = sig.score(validation_images, validation_labels)
    # print("Accuracy Linear Kernel:", accuracy_lin)
    # print("Accuracy accuracy_poly Kernel:", accuracy_poly)
    # print("Accuracy accuracy_rbf Kernel:", accuracy_rbf)
    # print("Accuracy accuracy_sig Kernel:", accuracy_sig)
    report = classification_report(validation_labels, recognized_users)
    print(report)
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    joblib.dump(grid_search, model_path)
    # pickle.dump(svm_model, open(model_path, 'wb'))
    print('--- MODEL CREATED ---')
    return model_path
