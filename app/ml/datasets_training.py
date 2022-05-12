import cv2
import joblib
from os import path

from sklearn.svm import SVC
from sqlalchemy.orm import Session
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV

from app.api import deps
from app.core.config import settings
from app.crud import crud_site_setting
from app.crud.crud_course import course
from app.resources.enums import DatasetType
from app.services.image_processing import get_hog_features, enhance_image, convert_to_grayscale, get_embedding, \
    create_scatter_plot
from app.utils.file_helper import get_list_files, get_course_models_directory, get_extracted_images_directory, \
    get_user_datasets_directory, get_user_preprocessed_images_directory, get_file_name_without_extension


def prepare_datasets(db: Session, course_code: str, dataset_type: DatasetType = DatasetType.TRAINING,
                     save_preprocessing: bool = False):
    use_facenet = crud_site_setting.site_setting.use_facenet(db)

    features = []
    labels = []

    course_data = course.get_course(db, code=course_code)
    semester = deps.get_active_semester(db)
    list_students = course.get_course_students(db, course_id=course_data.id, semester_id=semester.id)

    datasets = [student.user.username for student in list_students]
    total_labels = 0
    for user_index, username in enumerate(datasets):
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
                    output_path = path.join(extracted_images_dir, f"{dataset_type}_{file_name}_hog.jpg")
                    cv2.imwrite(output_path, hog_image * 255.)
                features.append(feature)
                labels.append(username)
    print('{0} images from {1} labels have been extracted'.format(len(features), total_labels))
    return features, labels


def train_datasets(db: Session, semester_code: str, course_code: str, save_preprocessing: bool = False,
                   grid_search: bool = False):
    print('--- PREPARING TRAINING DATASETS ---')
    use_facenet = crud_site_setting.site_setting.use_facenet(db)
    print("use_facenet", use_facenet)
    features, labels = prepare_datasets(db, course_code, DatasetType.TRAINING, save_preprocessing)
    print('--- TRAINING MODEL ---')
    if grid_search:
        parameters = {
            'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
            'C': [0.5, 1.0, 10, 50, 100, 1000],
            'gamma': ['scale', 1, 0.1, 0.01, 0.001, 0.005],
            'random_state': [0]
        }
        grid_search = GridSearchCV(estimator=SVC(), param_grid=parameters, n_jobs=6, verbose=1, scoring='accuracy')
        grid_search.fit(features, labels)
        print(f"Best Score: {grid_search.best_score_}")
        best_params = grid_search.best_estimator_.get_params()
        print("Best Parameters: ")
        for param in parameters:
            print(f"\t{param}: {best_params[param]}")
        svm_model = SVC(kernel=best_params['kernel'], gamma=best_params['gamma'], C=best_params['C'],
                        random_state=best_params['random_state'], probability=True)
    else:
        if use_facenet:
            # svm_model = SVC(kernel='rbf', C=50, gamma=0.001, random_state=0, probability=True)  # 98% 2020
            # svm_model = SVC(kernel='linear', C=0.5, gamma='scale', random_state=0, probability=True)  # 100%, 98% val 10, 100% 5
            svm_model = SVC(kernel='rbf', C=10, gamma=0.01, random_state=0, probability=True)  # mask 92%
            # svm_model = SVC(kernel='rbf', C=50, gamma=0.005, random_state=0, probability=True)  # mask only 73%
        else:
            svm_model = SVC(kernel='rbf', C=50, gamma=0.005, random_state=0, probability=True)  # 95%
            # svm_model = SVC(kernel='poly', C=0.5, gamma='scale', random_state=0, probability=True) # 90% val 10
            # svm_model = SVC(kernel='sigmoid', C=50, gamma=0.01, random_state=0, probability=True) # mask 67%, mask only 63%, 5 84%
    svm_model.fit(features, labels)
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    joblib.dump(svm_model, model_path)
    print('--- MODEL CREATED ---')
    create_scatter_plot(features, labels)
    return model_path


def validate_model(db: Session, semester_code: str, course_code: str, save_preprocessing=False):
    print('--- PREPARING TESTING DATASETS ---')
    validation_images, validation_labels = prepare_datasets(db, course_code, DatasetType.VALIDATION, save_preprocessing)
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
