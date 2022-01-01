import cv2
import joblib
from os import path

from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

from app.core.config import settings
from app.ml.face_detection import detect_face_from_image_path
from app.services.image_processing import get_hog_features, enhance_image, convert_to_grayscale
from app.utils.commons import get_current_datetime
from app.utils.file_helper import get_list_files, get_course_models_directory, get_extracted_images_directory, \
    get_user_datasets_directory, get_dir, get_user_validation_directory


def prepare_datasets(save_preprocessing: bool = False):
    print('--- PREPARING DATASETS ---')
    preprocessed_images_dir = get_dir(settings.ML_PREPROCESSED_IMAGES_FOLDER)

    images = []
    labels = []
    datasets = get_list_files(settings.DATASETS_FOLDER)
    total_images = 0
    for username in datasets:
        user_directory_path = get_user_datasets_directory(username)
        extracted_images_dir = get_extracted_images_directory(username)

        all_images = get_list_files(user_directory_path)
        total_images += len(all_images)
        for (i, image_name) in enumerate(all_images):
            counter = i + 1
            current_datetime = get_current_datetime()

            image_path = path.join(user_directory_path, image_name)
            image = cv2.imread(image_path)

            # Image Enhancement
            enhanced_image = enhance_image(image)
            if save_preprocessing:
                enhanced_image_path = path.join(preprocessed_images_dir, f"{current_datetime}_{counter}.4_enhanced.jpg")
                cv2.imwrite(enhanced_image_path, enhanced_image)

            # Grayscaling
            gray_image = convert_to_grayscale(enhanced_image)
            if save_preprocessing:
                gray_image_path = path.join(preprocessed_images_dir, f"{current_datetime}_{counter}.5_gray.jpg")
                cv2.imwrite(gray_image_path, gray_image)

            # Resize
            resized_image = cv2.resize(gray_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
            if save_preprocessing:
                resized_image_path = path.join(preprocessed_images_dir, f"{current_datetime}_{counter}.6_resized.jpg")
                cv2.imwrite(resized_image_path, resized_image)

            # HOG Features
            (hog_desc, hog_image) = get_hog_features(resized_image)
            if save_preprocessing:
                hog_path = path.join(preprocessed_images_dir, f"{current_datetime}_{counter}.7_hog.jpg")
                cv2.imwrite(hog_path, hog_image * 255.)
            output_path = path.join(extracted_images_dir, f"{image_name}_hog.jpg")
            cv2.imwrite(output_path, hog_image * 255.)

            images.append(hog_desc)
            labels.append(username)
    print('{0} images from {1} datasets have been extracted'.format(total_images, len(datasets)))
    return images, labels


def train_datasets(semester_code: str, course_code: str, save_preprocessing: bool = False, grid_search: bool = False):
    images, labels = prepare_datasets(save_preprocessing)
    print('--- TRAINING MODEL ---')
    if grid_search:
        parameters = {
            'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
            'C': [0.5, 1.0, 10, 50, 100, 1000],
            'gamma': ['scale', 1, 0.1, 0.01, 0.001, 0.005],
            'random_state': [0]
        }
        grid_search = GridSearchCV(estimator=SVC(), param_grid=parameters, n_jobs=6, verbose=1, scoring='accuracy')
        grid_search.fit(images, labels)
        print(f"Best Score: {grid_search.best_score_}")
        best_params = grid_search.best_estimator_.get_params()
        print("Best Parameters: ")
        for param in parameters:
            print(f"\t{param}: {best_params[param]}")
        svm_model = SVC(kernel=best_params['kernel'], gamma=best_params['gamma'], C=best_params['C'],
                        random_state=best_params['random_state'], probability=True)
    else:
        svm_model = SVC(kernel='sigmoid', C=50, gamma=0.01, random_state=0, probability=True)
        # svm_model = SVC(kernel='sigmoid', C=1000.0, gamma=0.005, random_state=0, probability=True)
    svm_model.fit(images, labels)
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    joblib.dump(svm_model, model_path)
    print('--- MODEL CREATED ---')
    return model_path


def validate_model(semester_code: str, course_code: str, save_preprocessing=False):
    print('--- TESTING MODEL ---')
    preprocessed_images_dir = get_dir(settings.ML_PREPROCESSED_IMAGES_FOLDER)

    validation_images = []
    validation_labels = []
    validation_files = get_list_files(settings.ML_VALIDATION_FOLDER)
    total_images = 0
    for username in validation_files:
        user_validation_directory_path = get_user_validation_directory(username)
        extracted_images_dir = get_extracted_images_directory(username)

        all_images = get_list_files(user_validation_directory_path)
        total_images += len(all_images)
        for (i, image_name) in enumerate(all_images):
            counter = i + 1
            current_datetime = get_current_datetime()

            user_directory = path.join(user_validation_directory_path, image_name)
            user_image = cv2.imread(user_directory)
            if save_preprocessing:
                input_path = path.join(preprocessed_images_dir, f"{current_datetime}_val_{counter}.0_input.jpg")
                cv2.imwrite(input_path, user_image)

            detected_faces = detect_face_from_image_path(user_directory, save_preprocessing)
            if detected_faces:
                for detected_face in detected_faces:
                    # Image Enhancement
                    enhanced_image = enhance_image(detected_face)
                    if save_preprocessing:
                        file_name = f"{current_datetime}_val_{counter}.4_enhanced.jpg"
                        enhanced_path = path.join(preprocessed_images_dir, file_name)
                        cv2.imwrite(enhanced_path, enhanced_image)

                    # Grayscaling
                    gray_image = convert_to_grayscale(enhanced_image)
                    if save_preprocessing:
                        file_name = f"{current_datetime}_val_{counter}.5_gray.jpg"
                        gray_image_path = path.join(preprocessed_images_dir, file_name)
                        cv2.imwrite(gray_image_path, gray_image)

                    # Resize
                    resized_image = cv2.resize(gray_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
                    if save_preprocessing:
                        file_name = f"{current_datetime}_val_{counter}.6_resized.jpg"
                        resized_image_path = path.join(preprocessed_images_dir, file_name)
                        cv2.imwrite(resized_image_path, resized_image)

                    # HOG Features
                    (hog_desc, hog_image) = get_hog_features(resized_image)
                    if save_preprocessing:
                        hog_path = path.join(preprocessed_images_dir, f"{current_datetime}_{counter}.7_hog.jpg")
                        cv2.imwrite(hog_path, hog_image * 255.)
                    output_path = path.join(extracted_images_dir, f"{username}_{counter}_val_hog.jpg")
                    cv2.imwrite(output_path, hog_image * 255.)

                    validation_images.append(hog_desc)
                    validation_labels.append(username)

    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    svm_model = joblib.load(model_path)
    recognized_users = svm_model.predict(validation_images)
    print("recognized_users", recognized_users)
    report = classification_report(validation_labels, recognized_users)
    print(report)
    report = classification_report(validation_labels, recognized_users, output_dict=True)
    return report["accuracy"]
