import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import tensorflow as tf


class FireAgent:
    def __init__(self):
        self.model = tf.saved_model.load(os.path.abspath(os.path.join('models', 'fire_classification_mobilenet_v3')))

    def check(self, frame):
        input_tensor = tf.convert_to_tensor(frame, dtype=tf.float32)
        input_tensor = input_tensor[tf.newaxis, ...]
        preds = self.model(input_tensor)
        prediction = tf.argmax(preds[0]).numpy()

        return prediction == 1

