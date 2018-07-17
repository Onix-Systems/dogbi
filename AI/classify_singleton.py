import os
import requests

import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn import preprocessing

from pprint import pprint


class Singleton(type):
    CLASSES_COUNT = 120
    INCEPTION_CLASSES_COUNT = 2048
    INCEPTION_OUTPUT_FIELD = 'inception_output'
    LABEL_ONE_HOT_FIELD = 'label_one_hot'
    IMAGE_RAW_FIELD = 'image_raw'
    INCEPTION_INPUT_TENSOR = 'DecodeJpeg/contents:0'
    INCEPTION_OUTPUT_TENSOR = 'pool_3:0'
    OUTPUT_NODE_NAME = 'output_node'
    OUTPUT_TENSOR_NAME = OUTPUT_NODE_NAME + ':0'
    HEAD_INPUT_NODE_NAME = 'x'
    HEAD_INPUT_TENSOR_NAME = HEAD_INPUT_NODE_NAME + ':0'

    DEV_SET_SIZE = 3000
    TRAIN_SAMPLE_SIZE = 3000

    CURRENT_MODEL_NAME = 'stanford_5_64_0001'
    HEAD_MODEL_LAYERS = [INCEPTION_CLASSES_COUNT, 1024, CLASSES_COUNT]
    tensors = None
    breeds = None
    detection_graph = None

    ready_has_run = False

    def ready(self):
        if self.ready_has_run:
            pprint("Not readying up")
            return
        pprint("Readying up")

        def one_hot_label_encoder():
            BASE = os.path.dirname(os.path.abspath(__file__))
            train_Y_orig = pd.read_csv(os.path.join(BASE, "breeds.csv"), dtype={'breed': np.str})
            lb = preprocessing.LabelBinarizer()
            lb.fit(train_Y_orig['breed'])

            def encode(labels):
                return np.asarray(lb.transform(labels), dtype=np.float32)

            def decode(one_hots):
                return np.asarray(lb.inverse_transform(one_hots), dtype=np.str)

            return encode, decode

        def unfreeze_into_current_graph(model_path, tensor_names):
            with tf.gfile.FastGFile(name=model_path, mode='rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, name='')
                g = tf.get_default_graph()

                tensors = {t: g.get_tensor_by_name(t) for t in tensor_names}
                return tensors

        BASE = os.path.dirname(os.path.abspath(__file__))
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            with tf.Session().as_default() as sess_init:
                self.tensors = unfreeze_into_current_graph(
                    os.path.join(BASE, self.CURRENT_MODEL_NAME + '.pb'),
                    tensor_names=[self.INCEPTION_INPUT_TENSOR, self.OUTPUT_TENSOR_NAME])

                _, one_hot_decoder = one_hot_label_encoder()

                self.breeds = one_hot_decoder(np.identity(self.CLASSES_COUNT)).reshape(-1)
        self.ready_has_run = True

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Analyzer(metaclass=Singleton):

    def infer(self, img_raw):
        with tf.Session(graph=Singleton.detection_graph) as sess:
            probs = sess.run(
                Singleton.tensors[Singleton.OUTPUT_TENSOR_NAME],
                feed_dict={Singleton.tensors[Singleton.INCEPTION_INPUT_TENSOR]: img_raw}
            )

            df = pd.DataFrame(data={'prob': probs.reshape(-1), 'breed': Singleton.breeds})
            return df.sort_values(['prob'], ascending=False)

    def classify(self, resource_type, path):
        if resource_type == 'uri':
            response = requests.get(path)
            img_raw = response.text()
        else:
            with open(path, 'rb') as f:
                img_raw = f.read()

        return self.infer(img_raw)

    def get_score(self, path_to_file):
        if not Singleton.ready_has_run:
            Singleton.ready(Singleton)
        path = path_to_file
        probs = self.classify('file', path)
        a = probs.sort_values(['prob'], ascending=False).take(range(5))
        b = []
        b.append(a['breed'].tolist()[:3])
        b.append(a['prob'].tolist()[:3])
        return b
