import cv2
import pickle
import joblib
from os import path

from skimage import feature
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVC, SVC

from app.core.config import settings
from app.ml.face_detection import detect_face_on_image, detect_face_from_image_path
from app.utils.file_helper import get_list_files, get_course_models_directory, get_hog_outputs_directory, \
    get_user_datasets_directory


def train_datasets(semester_code: str, course_code: str):
    print('--- PREPARING DATASETS ---')

    images = []
    labels = []
    # get all the image folder paths
    image_paths = get_list_files(settings.DATASETS_FOLDER)
    total_images = 0
    for username in image_paths:
        # get all the image names
        user_directory_path = get_user_datasets_directory(username)
        all_images = get_list_files(user_directory_path)
        # iterate over the image names, get the label
        # list_datasets = [path.join(user_dir, filename) for filename in all_images]
        total_images += len(all_images)
        for (i, image_name) in enumerate(all_images):
            user_directory = path.join(user_directory_path, image_name)
            user_image = cv2.imread(user_directory)
            user_image = cv2.convertScaleAbs(user_image, alpha=settings.IMAGE_ALPHA, beta=settings.IMAGE_BETA)
            cv2.imwrite(path.join(get_hog_outputs_directory(username), f"{username}_adjusted.{i+1}.jpg"), user_image)
            user_image = cv2.cvtColor(user_image, cv2.COLOR_RGB2GRAY)
            user_image = cv2.resize(user_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
            # get the HOG descriptor for the image
            (hog_desc, hog_image) = feature.hog(user_image, orientations=settings.HOG_ORIENTATIONS, pixels_per_cell=settings.HOG_PIXELS_PER_CELL,
                                                cells_per_block=settings.HOG_CELLS_PER_BLOCK, transform_sqrt=True, blrunock_norm='L2-Hys',
                                                visualize=True)
            user_output_directory = get_hog_outputs_directory(username)
            output_file_name = f"{username}_hog.{i+1}.jpg"
            output_path = path.join(user_output_directory, output_file_name)
            cv2.imwrite(output_path, hog_image * 255.)
            images.append(hog_desc)
            labels.append(username)
    print('{0} images from {1} datasets have been extracted'.format(total_images, len(image_paths)))

    print('--- TRAINING MODEL ---')
    parameters = {
        'kernel': ['linear', 'rbf', 'poly', 'sigmoid'],
        # 'C': [0.5, 1, 10, 100],
        'C': [1e3, 5e3, 1e4, 5e4, 1e5],
        'gamma': ['scale', 1, 0.1, 0.01, 0.001, 0.005],
        # 'gamma': [0.1, 0.01, 0.001, 0.0001, 0.005, 0.0005],
        'random_state': [0, 42]
    }

    # grid_search = GridSearchCV(estimator=SVC(),
    #                            param_grid=parameters,
    #                            n_jobs=6,
    #                            verbose=1,
    #                            scoring='accuracy'
    # )
    # grid_search.fit(images, labels)
    # print(f"Best Score: {grid_search.best_score_}")
    # best_params = grid_search.best_estimator_.get_params()
    # print("Best Parameters: ")
    # for param in parameters:
    #     print(f"\t{param}: {best_params[param]}")

    svm_model = SVC(kernel='sigmoid', C=1000.0, gamma=0.005, random_state=0, probability=True)
    svm_model.fit(images, labels)

    # svm_model = SVC(kernel=best_params['kernel'], gamma=best_params['gamma'], C=best_params['C'], random_state=best_params['random_state'])
    # svm_model.fit(images, labels)

    course_directory = get_course_models_directory(course_code)
    model_name = f"{semester_code}.joblib"
    model_path = path.join(course_directory, model_name)
    # joblib.dump(grid_search, model_path)
    joblib.dump(svm_model, model_path)
    # pickle.dump(svm_model, open(model_path, 'wb'))
    print('--- MODEL CREATED ---')
    return model_path


def validate_model(semester_code: str, course_code: str):
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
            print("DETECTING FACE ON ", image_name)
            detected_faces = detect_face_from_image_path(user_directory, save_preprocessing=True)
            if detected_faces:
                for detected_face in detected_faces:
                    # detected_face, box = result
                    # user_image = detected_face
                    user_image = cv2.convertScaleAbs(detected_face, alpha=settings.IMAGE_ALPHA, beta=settings.IMAGE_BETA)
                    cv2.imwrite(path.join(get_hog_outputs_directory(username), f"{username}_val_adjusted.{i + 1}.jpg"),
                                user_image)
                    user_image = cv2.cvtColor(user_image, cv2.COLOR_RGB2GRAY)
                    cv2.imwrite(path.join(get_hog_outputs_directory(username), f"{username}_val_gray.{i + 1}.jpg"),
                                user_image)
                    user_image = cv2.resize(user_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
                    cv2.imwrite(path.join(get_hog_outputs_directory(username), f"{username}_val_resized.{i + 1}.jpg"),
                                user_image)
                    # get the HOG descriptor for the image
                    (hog_desc, hog_image) = feature.hog(user_image, orientations=settings.HOG_ORIENTATIONS, pixels_per_cell=settings.HOG_PIXELS_PER_CELL,
                                                        cells_per_block=settings.HOG_CELLS_PER_BLOCK, transform_sqrt=True,
                                                        block_norm='L2-Hys',
                                                        visualize=True)
                    user_output_directory = get_hog_outputs_directory(username)
                    output_file_name = f"{username}_val_hog.{i + 1}.jpg"
                    output_path = path.join(user_output_directory, output_file_name)
                    cv2.imwrite(output_path, hog_image * 255.)
                    validation_images.append(hog_desc)
                    validation_labels.append(username)
    model_name = f"{semester_code}.joblib"
    course_directory = get_course_models_directory(course_code)
    model_path = path.join(course_directory, model_name)
    # svm_model = pickle.load(open(model_path, 'rb'))
    svm_model = joblib.load(model_path)
    recognized_users = svm_model.predict(validation_images)
    # recognized_users = grid_search.predict(validation_images)
    # accuracy_lin = linear.score(validation_images, validation_labels)
    # accuracy_poly = poly.score(validation_images, validation_labels)
    # accuracy_rbf = rbf.score(validation_images, validation_labels)
    # accuracy_sig = sig.score(validation_images, validation_labels)
    # print("Accuracy Linear Kernel:", accuracy_lin)
    # print("Accuracy accuracy_poly Kernel:", accuracy_poly)
    # print("Accuracy accuracy_rbf Kernel:", accuracy_rbf)
    # print("Accuracy accuracy_sig Kernel:", accuracy_sig)
    print("recognized_users", recognized_users)
    report = classification_report(validation_labels, recognized_users)
    print(report)
    # print(confusion_matrix(validation_labels, recognized_users, labels=validation_files))


def validate_from_validation_folder(semester_code: str, course_code: str):
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
            detected_faces = detect_face_from_image_path(user_directory)
            if detected_faces:
                for detected_face in detected_faces:
                    # detected_face, box = result
                    # user_image = detected_face
                    user_image = cv2.convertScaleAbs(detected_face, alpha=settings.IMAGE_ALPHA,
                                                     beta=settings.IMAGE_BETA)
                    cv2.imwrite(path.join(get_hog_outputs_directory(username), f"{username}_val_adjusted.{i + 1}.jpg"),
                                user_image)
                    user_image = cv2.cvtColor(user_image, cv2.COLOR_RGB2GRAY)
                    user_image = cv2.resize(user_image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
                    # get the HOG descriptor for the image
                    (hog_desc, hog_image) = feature.hog(user_image, orientations=settings.HOG_ORIENTATIONS, pixels_per_cell=settings.HOG_PIXELS_PER_CELL,
                                                        cells_per_block=settings.HOG_CELLS_PER_BLOCK, transform_sqrt=True,
                                                        block_norm='L2-Hys',
                                                        visualize=True)
                    user_output_directory = get_hog_outputs_directory(username)
                    output_file_name = f"{username}_val_hog.{i + 1}.jpg"
                    output_path = path.join(user_output_directory, output_file_name)
                    cv2.imwrite(output_path, hog_image * 255.)
                    validation_images.append(hog_desc)
                    validation_labels.append(username)
    model_name = f"{semester_code}.joblib"
    course_directory = get_course_models_directory(course_code)
    model_path = path.join(course_directory, model_name)
    # svm_model = pickle.load(open(model_path, 'rb'))
    svm_model = joblib.load(model_path)
    recognized_users = svm_model.predict(validation_images)
    report = classification_report(validation_labels, recognized_users)
    print(report)