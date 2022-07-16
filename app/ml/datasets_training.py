import cv2
import joblib
import json
import numpy as np
from fastapi.logger import logger
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
    create_scatter_plot, plot_grid_search
from app.utils.commons import list_dict_to_csv
from app.utils.file_helper import get_list_files, get_course_models_directory, get_extracted_images_directory, \
    get_user_datasets_directory, get_user_preprocessed_images_directory, get_file_name_without_extension


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """

    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32,
                              np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def prepare_datasets(db: Session, course_code: str, dataset_type: DatasetType = DatasetType.TRAINING,
                     save_preprocessing: bool = False, regenerate_file: bool = True, params=None):
    if params is None:
        params = {}
    use_facenet = crud_site_setting.site_setting.use_facenet(db)
    course_directory = get_course_models_directory(course_code)
    datasets_features_name = f"{dataset_type}.joblib"
    datasets_features_path = path.join(course_directory, datasets_features_name)
    datasets_features_path_json = path.join(course_directory, f"{dataset_type}.json")
    if regenerate_file or not path.exists(datasets_features_path):
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
                        if params.get('alpha') and params.get('beta'):
                            enhanced_image = enhance_image(image, params['alpha'], params['beta'])
                        else:
                            enhanced_image = enhance_image(image)
                        # enhanced_image = image
                        if save_preprocessing:
                            enhanced_image_path = path.join(preprocessed_images_dir,
                                                            f"{file_name_prefix}.4_enhanced.jpg")
                            cv2.imwrite(enhanced_image_path, enhanced_image)

                        # Grayscaling
                        gray_image = convert_to_grayscale(enhanced_image)
                        if save_preprocessing:
                            gray_image_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.5_gray.jpg")
                            cv2.imwrite(gray_image_path, gray_image)

                        # Resize
                        if params.get('hog_width_height'):
                            resized_image = cv2.resize(gray_image, params['hog_width_height'])
                        else:
                            resized_image = cv2.resize(gray_image,
                                                       (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
                        if save_preprocessing:
                            resized_image_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.6_resized.jpg")
                            cv2.imwrite(resized_image_path, resized_image)

                        # HOG Features
                        if params.get('hog_ppc') and params.get('hog_cpb'):
                            (feature, hog_image) = get_hog_features(resized_image, pixels_per_cell=params['hog_ppc'],
                                                                    cells_per_block=params['hog_cpb'])
                        else:
                            (feature, hog_image) = get_hog_features(resized_image)
                        if save_preprocessing:
                            hog_path = path.join(preprocessed_images_dir, f"{file_name_prefix}.7_hog.jpg")
                            cv2.imwrite(hog_path, hog_image * 255.)
                        output_path = path.join(extracted_images_dir, f"{dataset_type}_{file_name}_hog.jpg")
                        cv2.imwrite(output_path, hog_image * 255.)
                    features.append(feature)
                    labels.append(username)
        logger.info('{0} images from {1} labels have been extracted'.format(len(features), total_labels))
        features_labels = features, labels
        joblib.dump(features_labels, datasets_features_path)
        json.dump(features_labels, open(datasets_features_path_json, 'w'), cls=NumpyEncoder)
        return features_labels
    else:
        features_labels = joblib.load(datasets_features_path)
        return features_labels


def train_datasets(db: Session, semester_code: str, course_code: str, save_preprocessing: bool = False,
                   grid_search: bool = False, return_score: bool = False, analyze: bool = False,
                   params_key: str = "default"):
    logger.info('--- PREPARING TRAINING DATASETS ---')
    use_facenet = crud_site_setting.site_setting.use_facenet(db)

    if analyze:
        test_results = []
        datasets_params = {
            'alpha': [1.0, 1.5, 2.0],
            'beta': [0, 10, 15, 20],
            # 'hog_width_height': [(50, 50), (60, 60), (70, 70), (80, 80), (90, 90)],
            # 'hog_ppc': [(8, 8), (9, 9), (10, 10)],
            # 'hog_cpb': [(2, 2), (3, 3)]
            # 'alpha': [1.5],
            # 'beta': [10],
            'hog_width_height': [(70, 70), (80, 80), (90, 90)],
            'hog_ppc': [(8, 8), (9, 9), (10, 10)],
            'hog_cpb': [(2, 2), (3, 3)]
        }

        list_params = []
        for a in datasets_params['alpha']:
            for b in datasets_params['beta']:
                for c in datasets_params['hog_width_height']:
                    for e in datasets_params['hog_ppc']:
                        for f in datasets_params['hog_cpb']:
                            params = {
                                'alpha': a,
                                'beta': b,
                                'hog_width_height': c,
                                'hog_ppc': e,
                                'hog_cpb': f
                            }
                            list_params.append(params)

        for (i, params) in enumerate(list_params):
            logger.info(f"Processing {i + 1}/{len(list_params)} %s" % params)

            features, labels = prepare_datasets(db, course_code, DatasetType.TRAINING,
                                                save_preprocessing=save_preprocessing, params=params)
            val_features, val_labels = prepare_datasets(db, course_code, DatasetType.VALIDATION,
                                                        save_preprocessing=save_preprocessing, params=params)

            svm_params = settings.svm_params.get(params_key) if settings.svm_params.get(params_key) else \
                settings.svm_params['default']
            svm_model = SVC(kernel=svm_params['kernel'], gamma=svm_params['gamma'], C=svm_params['C'],
                            random_state=svm_params['random_state'], probability=True)
            svm_model.fit(features, labels)

            predicted_labels = svm_model.predict(val_features)
            report = classification_report(val_labels, predicted_labels, output_dict=True)
            test_result = {
                'alpha': params['alpha'],
                'beta': params['beta'],
                'hog_width_height': params['hog_width_height'],
                'hog_ppc': params['hog_ppc'],
                'hog_cpb': params['hog_cpb'],
                'accuracy': report["accuracy"]
            }
            test_results.append(test_result)
        list_dict_to_csv(test_results, filename='test_results_hog.csv')
    else:
        params = settings.hog_params.get(params_key) if settings.hog_params.get(params_key) else settings.hog_params[
            'default']
        features, labels = prepare_datasets(db, course_code, DatasetType.TRAINING, save_preprocessing, params=params)
        val_features, val_labels = prepare_datasets(db, course_code, DatasetType.VALIDATION,
                                                    save_preprocessing=save_preprocessing, params=params)
        logger.info('--- TRAINING MODEL ---')
        if grid_search:
            kernels = ['linear', 'rbf', 'poly', 'sigmoid']
            parameters = {
                'C': [0.5, 1.0, 10, 50, 100, 1000],
                'gamma': ['scale', 1, 0.1, 0.01, 0.001, 0.005],
                'random_state': [0]
            }

            test_results = []
            best_svm_params = {}
            current_best_accuracy = 0
            for kernel in kernels:
                grid_search = GridSearchCV(estimator=SVC(kernel=kernel), param_grid=parameters, n_jobs=6,
                                           scoring='accuracy')
                grid_search.fit(features, labels)
                logger.info(f"Best Score: {grid_search.best_score_} ({kernel})")
                best_params = grid_search.best_estimator_.get_params()
                svm_model = SVC(kernel=kernel, gamma=best_params['gamma'], C=best_params['C'],
                                random_state=best_params['random_state'], probability=True)
                svm_model.fit(features, labels)

                predicted_labels = svm_model.predict(val_features)
                report = classification_report(val_labels, predicted_labels, output_dict=True)
                training_accuracy = grid_search.best_score_
                testing_accuracy = report["accuracy"]
                test_result = {
                    'kernel': kernel,
                    'C': best_params['C'],
                    'gamma': best_params['gamma'],
                    'training_accuracy': training_accuracy,
                    'testing_accuracy': testing_accuracy
                }
                test_results.append(test_result)
                if testing_accuracy > current_best_accuracy:
                    current_best_accuracy = testing_accuracy
                    best_svm_params = {
                        'kernel': kernel,
                        'C': best_params['C'],
                        'gamma': best_params['gamma'],
                        'random_state': best_params['random_state']
                    }
                elif testing_accuracy == 0 and training_accuracy > current_best_accuracy:
                    current_best_accuracy = training_accuracy
                    best_svm_params = {
                        'kernel': kernel,
                        'C': best_params['C'],
                        'gamma': best_params['gamma'],
                        'random_state': best_params['random_state']
                    }
                # plot_grid_search(grid_search.cv_results_, parameters['C'], parameters['gamma'], 'C', 'Gamma',
                #                  title=f"Grid Search Scores - ({kernel})", filename=f"plot_grid_search_{kernel}.png")
            list_dict_to_csv(test_results, filename='test_results_svm.csv')

            best_params = best_svm_params
            logger.info("Best Parameters: ")
            for param in best_params:
                logger.info(f"\t{param}: {best_params[param]}")
            svm_model = SVC(kernel=best_params['kernel'], gamma=best_params['gamma'], C=best_params['C'],
                            random_state=best_params['random_state'], probability=True)
        else:
            if use_facenet:
                # svm_model = SVC(kernel='rbf', C=50, gamma=0.001, random_state=0, probability=True)  # 98% 2020
                # svm_model = SVC(kernel='linear', C=0.5, gamma='scale', random_state=0, probability=True)  # 100%, 98% val 10, 100% 5
                svm_model = SVC(kernel='rbf', C=10, gamma=0.01, random_state=0, probability=True)  # mask 92%
                # svm_model = SVC(kernel='rbf', C=50, gamma=0.005, random_state=0, probability=True)  # mask only 73%
            else:
                params = settings.svm_params.get(params_key) if settings.svm_params.get(params_key) else \
                    settings.svm_params['default']
                svm_model = SVC(kernel=params['kernel'], gamma=params['gamma'], C=params['C'],
                                random_state=params['random_state'], probability=True)
        svm_model.fit(features, labels)
        course_directory = get_course_models_directory(course_code)
        model_name = f"{semester_code}.joblib"
        model_path = path.join(course_directory, model_name)
        joblib.dump(svm_model, model_path)
        logger.info('--- MODEL CREATED ---')
        create_scatter_plot(features, labels)
        if grid_search and return_score:
            return model_path, grid_search.best_score_
        else:
            return model_path


def validate_model(db: Session, semester_code: str, course_code: str, save_preprocessing=False,
                   params_key: str = "default"):
    logger.info('--- PREPARING TESTING DATASETS ---')
    params = settings.hog_params.get(params_key) if settings.hog_params.get(params_key) else settings.hog_params[
        'default']
    val_features, val_labels = prepare_datasets(db, course_code, DatasetType.VALIDATION, save_preprocessing,
                                                params=params)
    logger.info('--- TESTING MODEL ---')
    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    svm_model = joblib.load(model_path)
    predicted_labels = svm_model.predict(val_features)
    logger.info("predicted_labels: " + str(predicted_labels))
    report = classification_report(val_labels, predicted_labels)
    logger.info(report)
    report = classification_report(val_labels, predicted_labels, output_dict=True)
    return report["accuracy"]


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
