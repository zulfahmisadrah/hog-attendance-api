import cv2
import math
import numpy as np
from os import path
from numpy import ndarray
import matplotlib.pyplot as plt
from skimage.feature import hog
from sklearn.manifold import TSNE
from tensorflow.keras.models import load_model

from app.core.config import settings
from app.crud import crud_site_setting
from app.utils.file_helper import get_dir

# use_facenet = crud_site_setting.site_setting.use_facenet(db)
# if settings.USE_FACENET:
facenet_model = load_model(settings.ML_MODEL_FACENET)


def resize_image_if_too_big(image, max_size=settings.IMAGE_MAX_SIZE):
    if not isinstance(image, ndarray):
        width, height = image.size
    else:
        height, width = image.shape[:2]
    longer_size = height if height > width else width
    orientation = "portrait" if longer_size == height else "landscape"
    if longer_size > max_size:
        new_longer_size = max_size
        scale = float(new_longer_size / float(longer_size))
        if orientation == "portrait":
            new_width = int(float(width) * scale)
            new_height = new_longer_size
        else:
            new_height = int(float(height * scale))
            new_width = new_longer_size
        if not isinstance(image, ndarray):
            image = image.resize((new_width, new_height))
        else:
            image = cv2.resize(image, (new_width, new_height))
    return image


def euclidean_distance(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return math.sqrt(((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)))


def rotate_point(origin, point, angle):
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return int(qx), int(qy)


def radian_to_degree(radian):
    return (radian * 180) / math.pi


def angle_with_direction(angle, direction):
    if direction == -1:
        angle = 90 - angle
    return direction * angle


def align_eyes(left_eye, right_eye):
    # this function aligns given face in img based on left and right eye coordinates
    left_eye_x, left_eye_y = left_eye
    right_eye_x, right_eye_y = right_eye

    # find rotation direction
    if left_eye_y > right_eye_y:
        point_3rd = (right_eye_x, left_eye_y)
        direction = -1  # rotate same direction to clock
    else:
        point_3rd = (left_eye_x, right_eye_y)
        direction = 1  # rotate inverse direction of clock

    # find length of triangle edges
    a = euclidean_distance(np.array(left_eye), np.array(point_3rd))
    b = euclidean_distance(np.array(right_eye), np.array(point_3rd))
    c = euclidean_distance(np.array(right_eye), np.array(left_eye))

    # apply cosine rule
    if b != 0 and c != 0:  # this multiplication causes division by zero in cos_a calculation
        cos_a = (b * b + c * c - a * a) / (2 * b * c)
        angle = np.arccos(cos_a)
    else:
        angle = 0
    return angle, direction, point_3rd  # angle in radian


def rotate_image(img, angle, center=None):
    (h, w) = img.shape[:2]
    if center:
        (cX, cY) = center
    else:
        (cX, cY) = (w / 2, h / 2)
    matrix = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    rotated_img = cv2.warpAffine(img, matrix, (w, h))
    return rotated_img


def put_bounding_box_and_face_landmarks(img, box, keypoints):
    x, y, w, h = box
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.circle(img, keypoints["left_eye"], 4, (0, 255, 0), 2)
    cv2.circle(img, keypoints["right_eye"], 4, (0, 255, 0), 2)
    cv2.circle(img, keypoints["nose"], 4, (0, 255, 0), 2)
    cv2.circle(img, keypoints["mouth_left"], 4, (0, 255, 0), 2)
    cv2.circle(img, keypoints["mouth_right"], 4, (0, 255, 0), 2)
    return img


def cut_forehead_in_box(box, keypoints):
    x, y, w, h = box
    # Cut half forehead above
    left_eye_y = keypoints["left_eye"][1]
    right_eye_y = keypoints["right_eye"][1]
    highest_eye = right_eye_y if right_eye_y < left_eye_y else left_eye_y
    half_forehead = (highest_eye - y) / 2
    new_y = int(y + half_forehead)  # move y down to half forehead point
    new_h = int(h - half_forehead)  # reduce height because half forehead removed
    return x, new_y, w, new_h


def crop_face(img, box, keypoints, cut_forehead=False):
    x, y, w, h = box
    if cut_forehead:
        # Cut half forehead above
        left_eye_y = keypoints["left_eye"][1]
        right_eye_y = keypoints["right_eye"][1]
        highest_eye = right_eye_y if right_eye_y < left_eye_y else left_eye_y
        half_forehead = (highest_eye - y) / 2
        new_y = int(y + half_forehead)  # move y down to half forehead point
        new_h = int(h - half_forehead)  # reduce height because half forehead removed
        # Crop face
        cropped_face = img[int(new_y):int(new_y + new_h), int(x):int(x + w)]
        return cropped_face, new_y, new_h
    else:
        cropped_face = img[int(y):int(y + h), int(x):int(x + w)]
        return cropped_face


def get_hog_features(
        image,
        orientations=settings.HOG_ORIENTATIONS,
        pixels_per_cell=settings.HOG_PIXELS_PER_CELL,
        cells_per_block=settings.HOG_CELLS_PER_BLOCK,
        transform_sqrt=True,
        block_norm='L2-Hys',
        visualize=True,
        feature_vector=True,
        channel_axis=None
):
    hog_desc, hog_image = hog(
        image,
        orientations=orientations,
        pixels_per_cell=pixels_per_cell,
        cells_per_block=cells_per_block,
        transform_sqrt=transform_sqrt,
        block_norm=block_norm,
        visualize=visualize,
        feature_vector=feature_vector,
        channel_axis=channel_axis
    )
    return hog_desc, hog_image


def enhance_image(image, alpha=settings.IMAGE_ALPHA, beta=settings.IMAGE_BETA):
    enhanced_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return enhanced_image


def convert_to_grayscale(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return gray_image


def resize_input_hog(image):
    resized_image = cv2.resize(image, (settings.HOG_RESIZE_WIDTH, settings.HOG_RESIZE_HEIGHT))
    return resized_image


def get_embedding(face_pixels):
    # scale pixel values
    face_pixels = face_pixels.astype('float32')
    # standardize pixel values across channels (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    # transform face into one sample
    samples = np.expand_dims(face_pixels, axis=0)
    # make prediction to get embedding
    yhat = facenet_model.predict(samples)
    return yhat[0]


def create_scatter_plot(features, labels, filename='plot_scatter.png'):
    embedded = np.array(features)
    targets = np.array(labels)
    tsne = TSNE(n_components=2)
    compressed_features = tsne.fit_transform(embedded)

    colors = [
        '#F44336', '#E91E63', '#9C27B0', '#673AB7', '#3F51B5', '#2196F3', '#03A9F4', '#00BCD4', '#009688', '#4CAF50',
        '#8BC34A', '#CDDC39', '#FFEB3B', '#ffc107', '#FF9800', '#FF5722', '#795548', '#9E9E9E', '#000000', '#607D8B',
        '#B71C1C', '#880E4F', '#4A148C', '#311B92', '#1A237E', '#0D47A1',
    ]

    plt.figure(figsize=(15, 15))

    for i, t in enumerate(set(targets)):
        idx = targets == t
        plt.scatter(compressed_features[idx, 0], compressed_features[idx, 1], label=t, c=colors[i % len(colors)])

    plt.legend(bbox_to_anchor=(1, 1))
    plt.savefig(path.join(get_dir(settings.ML_PLOTS_FOLDER), filename))


def plot_grid_search(cv_results, grid_param_1, grid_param_2, name_param_1, name_param_2,
                     title="Grid Search Scores", filename="plot_grid_search.png"):
    # Get Test Scores Mean and std for each grid search
    scores_mean = cv_results['mean_test_score']
    scores_mean = np.array(scores_mean).reshape(len(grid_param_2), len(grid_param_1))

    scores_sd = cv_results['std_test_score']
    scores_sd = np.array(scores_sd).reshape(len(grid_param_2), len(grid_param_1))

    # Plot Grid search scores
    _, ax = plt.subplots(1, 1)

    # Param1 is the X-axis, Param 2 is represented as a different curve (color line)
    for idx, val in enumerate(grid_param_2):
        plt.plot(grid_param_1, scores_mean[idx, :], '-o', label=name_param_2 + ': ' + str(val))

    ax.set_title(title, fontsize=20, fontweight='bold')
    ax.set_xlabel(name_param_1, fontsize=16)
    ax.set_ylabel("CV Average Score", fontsize=16)
    ax.legend(loc="best")
    ax.grid('on')
    plt.savefig(path.join(get_dir(settings.ML_PLOTS_FOLDER), filename))
