from keras.models import load_model
import tensorflow as tf

def load_keras_model():
    """Load in the pre-trained model"""
    global model
    model = load_model('../saved_model.pb')
    # Required for model to work
    global graph
    graph = tf.get_default_graph()
    
load_keras_model()