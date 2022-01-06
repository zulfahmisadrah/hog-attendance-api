import cv2
import joblib
from os import path

from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

from app.core.config import settings
from app.resources.enums import DatasetType
from app.services.image_processing import get_hog_features, enhance_image, convert_to_grayscale
from app.utils.file_helper import get_list_files, get_course_models_directory, get_extracted_images_directory, \
    get_user_datasets_directory, get_datasets_directory, get_user_preprocessed_images_directory, \
    get_file_name_without_extension


def prepare_datasets(dataset_type: DatasetType = DatasetType.TRAINING, save_preprocessing: bool = False):
    print('--- PREPARING DATASETS ---')

    images = []
    labels = []
    datasets = get_list_files(get_datasets_directory(dataset_type))
    total_labels = 0
    for username in datasets:
        user_datasets_dir = get_user_datasets_directory(dataset_type, username)
        preprocessed_images_dir = get_user_preprocessed_images_directory(dataset_type, username)
        extracted_images_dir = get_extracted_images_directory(username)

        list_datasets = get_list_files(user_datasets_dir)
        if list_datasets:
            total_labels += 1
            for (i, image_name) in enumerate(list_datasets):
                counter = i + 1
                file_name = get_file_name_without_extension(image_name)
                file_name_prefix = f"{file_name}.{counter}"

                image_path = path.join(user_datasets_dir, image_name)
                image = cv2.imread(image_path)

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
                (hog_desc, hog_image) = get_hog_features(resized_image)
                if save_preprocessing:
                    hog_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.7_hog.jpg")
                    cv2.imwrite(hog_path, hog_image * 255.)
                output_path = path.join(extracted_images_dir, f"{dataset_type}_{file_name}_hog.jpg")
                cv2.imwrite(output_path, hog_image * 255.)

                images.append(hog_desc)
                labels.append(username)
    print('{0} images from {1} labels have been extracted'.format(len(images), total_labels))
    return images, labels


def train_datasets(semester_code: str, course_code: str, save_preprocessing: bool = False, grid_search: bool = False):
    images, labels = prepare_datasets(DatasetType.TRAINING, save_preprocessing)
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
        # svm_model = SVC(kernel='sigmoid', C=50, gamma=0.01, random_state=0, probability=True)
        svm_model = SVC(kernel='linear', C=0.5, gamma='scale', random_state=0, probability=True)
        # svm_model = SVC(kernel='sigmoid', C=1000.0, gamma=0.005, random_state=0, probability=True)
    svm_model.fit(images, labels)
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    joblib.dump(svm_model, model_path)
    print('--- MODEL CREATED ---')
    return model_path


def validate_model(semester_code: str, course_code: str, save_preprocessing=False):
    validation_images, validation_labels = prepare_datasets(DatasetType.VALIDATION, save_preprocessing)
    print('--- TESTING MODEL ---')
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
