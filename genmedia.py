import os
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
import numpy as np
import cv2
from glob import glob
from moviepy.editor import VideoFileClip

import vdetect
from vdetect import define_loops_custom_3 as define_loops_func
from vdetect import define_main_region_custom_2 as define_main_region_func


def visualize_main_region(im_src, dir_output):

    im = mpimg.imread(im_src)

    main_region = define_main_region_func()

    viz = vdetect.draw_boxes(im, [main_region])
    mpimg.imsave(os.path.join(dir_output, 'mainROI.jpg'), viz)


def visualize_window_search(im_src, dir_output):

    im = mpimg.imread(im_src)

    main_region = define_main_region_func()
    loops = define_loops_func()

    plt.figure(figsize=(20, 12))

    plt.subplot(2, 2, 1)
    plt.imshow( vdetect.draw_boxes(im, [main_region]) )
    plt.axis('off')

    idx = 2
    for loop in loops:

        plt.subplot(2, 2, idx)
        plt.imshow( vdetect.draw_boxes(im, loop) )
        plt.axis('off')
        idx += 1


    plt.tight_layout()
    plt.savefig(os.path.join(dir_output, 'winsearch.jpg'))


def visualize_heatmap(dir_images, dir_ml, dir_output):

    classifiers, extract, scaler, hyperparams = vdetect.load_ml_results(dir_ml)
    images = [mpimg.imread(f) for f in glob(dir_images + '/*.jpg')]

    loops = define_loops_func()

    plt.figure(figsize=(10, 20))
    idx = 1
    for im in images:

        swres = vdetect.sliding_window(im, loops, extract, classifiers.values())

        plt.subplot(6, 2, idx)
        plt.imshow(im)
        plt.axis('off')
        idx += 1

        plt.subplot(6, 2, idx)
        plt.imshow(swres)
        plt.axis('off')
        plt.title('max={}'.format(np.max(swres)))
        idx += 1

    plt.tight_layout()
    plt.savefig(os.path.join(dir_output, 'heatmap.jpg'))


def visualize_classifiers(dir_images, dir_ml, dir_output, extract_features_func=vdetect.extract_features):

    classifiers, extract, scaler, hyperparams = vdetect.load_ml_results(dir_ml, extract_features_func)
    images = [mpimg.imread(f) for f in glob(dir_images + '/*.jpg')]

    loops = define_loops_func()

    n_cols = len(classifiers) + 1
    n_images = len(images)

    plt.figure(figsize=(20, 15))
    idx = 1
    for im in images:

        plt.subplot(n_images, n_cols, idx)
        plt.imshow(im)
        plt.axis('off')
        idx += 1

        for k, clf in classifiers.items():

            heatmap = vdetect.sliding_window(im, loops, extract, [classifiers[k]])

            plt.subplot(n_images, n_cols, idx)
            plt.imshow(heatmap)
            plt.axis('off')
            plt.title(k)
            idx += 1

    plt.tight_layout()
    plt.savefig(os.path.join(dir_output, 'classifiers.jpg'))


def create_processing_func(dir_ml):

    classifiers, extract, _, _ = vdetect.load_ml_results(dir_ml)

    def process(frame):

        heatmap = vdetect.sliding_window(frame, extract, classifiers.values())
        bboxes = vdetect.segment_vehicles(heatmap)

        if bboxes is None:
            return frame

        return vdetect.draw_boxes(frame, bboxes)

    return process


def process_and_save_video(video_fname_src, video_fname_dst, processing_func):

    video_src = VideoFileClip(video_fname_src)

    video_dst = video_src.fl_image(processing_func)
    video_dst.write_videofile(video_fname_dst, audio=False)


if __name__ == '__main__':

    DIR_OUT = 'output_images'
    DIR_TEST_IM = 'test_images'
    CLF_DIR = 'serialize/2018-04-15_113152'

    visualize_window_search('test_images/test3.jpg', DIR_OUT)

    visualize_classifiers(
        DIR_TEST_IM,
        CLF_DIR,
        DIR_OUT
    )

    visualize_heatmap(
        DIR_TEST_IM,
        CLF_DIR,
        DIR_OUT
    )

    exit()

    process = create_processing_func(CLF_DIR)
    process_and_save_video('project_video.mp4', 'output_images/project_video.mp4', process)
