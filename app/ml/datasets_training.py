import cv2
import pickle
from skimage import feature
from sklearn.svm import LinearSVC

from app.core.config import settings
from app.utils.file_helper import get_list_files


def train_datasets():
    images = []
    labels = []
    # get all the image folder paths
    image_paths = get_list_files(settings.DATASETS_FOLDER)
    for path in image_paths:
        # get all the image names
        all_images = get_list_files(f"{settings.DATASETS_FOLDER}/{path}")
        # iterate over the image names, get the label
        # list_datasets = [path.join(user_dir, filename) for filename in all_images]
        for (i, image) in enumerate(all_images):
            image_path = f"{settings.DATASETS_FOLDER}/{path}/{image}"
            image = cv2.imread(image_path)
            image = cv2.resize(image, (64, 128))
            # get the HOG descriptor for the image
            (hog_desc, hog_image) = feature.hog(image, orientations=9, pixels_per_cell=(8, 8),
                                                cells_per_block=(2, 2), transform_sqrt=True, block_norm='L2-Hys',
                                                visualize=True)

            cv2.imwrite(f"{settings.ML_OUTPUTS_FOLDER}/{path}/{path}_hog.{i}.jpg", hog_image * 255.)
            # update the data and labels
            images.append(hog_desc)
            labels.append(path)
    print('Training on train images...')
    svm_model = LinearSVC(random_state=42, tol=1e-5)
    svm_model.fit(images, labels)
    pickle.dump(svm_model, open(f"{settings.ML_MODELS_FOLDER}/1.sav", 'wb'))
