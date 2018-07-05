import os
import requests

import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn import preprocessing


def infer(img_raw):
    with tf.Session(graph=const.detection_graph) as sess:

        probs = sess.run(const.tensors[const.OUTPUT_TENSOR_NAME],
                         feed_dict={const.tensors[const.INCEPTION_INPUT_TENSOR]: img_raw})

        df = pd.DataFrame(data={'prob': probs.reshape(-1), 'breed': const.breeds})
        return df.sort_values(['prob'], ascending=False)


def classify(resource_type, path):
    if resource_type == 'uri':
        response = requests.get(path)
        img_raw = response.text()
    else:
        with open(path, 'rb') as f:
            img_raw = f.read()

    return infer(img_raw)


def get_score(path_to_file):
    path = path_to_file
    probs = classify('file', path)
    a = probs.sort_values(['prob'], ascending=False).take(range(5))
    b = []
    b.append(a['breed'].tolist()[:3])
    b.append(a['prob'].tolist()[:3])
    return b


