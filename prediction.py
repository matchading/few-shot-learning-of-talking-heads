import logging
import os

import numpy as np
import imageio
import skimage

from models import GAN


def load_image(path, shape):
    img = imageio.imread(path)
    resized_img = skimage.transform.resize(img, shape, preserve_range=True)
    rescaled_img = resized_img / 127.5 - 1
    return rescaled_img

def predict(lndmk_image_paths, style_frame_paths, style_lndmk_paths):
    frame_shape = (256, 256, 3)
    lndmk_images = np.array([load_image(path, frame_shape) for path in lndmk_image_paths])
    batch_size = lndmk_images.shape[0]
    style_frame_images = np.array([load_image(path, frame_shape) for path in style_frame_paths])
    style_lndmk_images = np.array([load_image(path, frame_shape) for path in style_lndmk_paths])
    style = np.concatenate((style_lndmk_images, style_frame_images), axis=-1)

    gan = GAN(input_shape=frame_shape, num_videos=1, k=1)
    gene = gan.build_generator()
    embe = gan.build_embedder()

    embe.load_weights('trained_models/0_meta_embedder_in_combined.h5')
    gene.load_weights('trained_models/monalisa_fewshot_generator_in_combined.h5')

    style_embedding = embe.predict(style)
    style_embedding = style_embedding.repeat(8, axis=0)  # [512] -> [8, 512]
    fake_images = gene.predict([lndmk_images, style_embedding])
    return fake_images

if __name__ == '__main__':
    frame_shape = (256, 256, 3)

    lndmk_file_paths = ['datasets/voxceleb2-9f/train/lndmks/id00012/21Uxsk56VDQ/{}.jpg'.format(i) for i in range(8)]
    style_frame_paths = ['datasets/fewshot/monalisa/frames/monalisa256-0.jpg']
    style_lndmk_paths = ['datasets/fewshot/monalisa/lndmks/monalisa256-0.jpg']
#    style_frame_paths = ['datasets/voxceleb2-9f/train/frames/id00012/21Uxsk56VDQ/{}.jpg'.format(i) for i in range(8)]
#    style_lndmk_paths = ['datasets/voxceleb2-9f/train/lndmks/id00012/21Uxsk56VDQ/{}.jpg'.format(i) for i in range(8)]
    fake_images = predict(lndmk_file_paths, style_frame_paths, style_lndmk_paths)
    fake_images += 1
    fake_images *= 127.5
    fake_images = fake_images.astype(np.uint8)
    for i in range(fake_images.shape[0]):
        imageio.imwrite('{}.jpg'.format(i), fake_images[i])
