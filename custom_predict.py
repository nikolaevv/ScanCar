import numpy as np
import tensorflow as tf

#from google.colab import drive
#drive.mount('/gdrive')

saved_model_path  = "/root/scanauto/additional_car_model" # моделька

converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_path)
lite_model_content = converter.convert()

#with open("/gdrive/My Drive/lite_car_model", "wb") as f:
#f.write(lite_model_content)

interpreter = tf.lite.Interpreter(model_content=lite_model_content)

# This little helper wraps the TF Lite interpreter as a numpy-to-numpy function.
def lite_model(images):
    interpreter.allocate_tensors()
    interpreter.set_tensor(interpreter.get_input_details()[0]['index'], images)
    interpreter.invoke()
    return interpreter.get_tensor(interpreter.get_output_details()[0]['index'])

def preprocess_image(image):
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [224, 224])
    image /= 255.0  # normalize to [0,1] range

    return image

def load_and_preprocess_image(path):
    image = tf.io.read_file(path)
    return preprocess_image(image)

input_arr = load_and_preprocess_image('/root/tiguan.jpg')

probs_lite = lite_model(input_arr[None, ...])[0]
print(np.argmax(probs_lite))
print(probs_lite)