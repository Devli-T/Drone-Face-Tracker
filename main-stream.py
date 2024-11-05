import cv2
import numpy as np
import tensorflow as tf
import socket
import threading
import json

# Specify the local path to the downloaded weights
weights_path = "models/mobilenet_v2_weights_tf_dim_ordering_tf_kernels_1.0_224.h5"

# Load the MobileNetV2 model with local weights
model = tf.keras.applications.MobileNetV2(weights=weights_path, include_top=True)

# Load ImageNet class index from the local file
with open("data/imagenet_class_index.json") as f:
    class_index = json.load(f)

# Tello stream setup
tello_video = cv2.VideoCapture('udp://@0.0.0.0:11111?fifo_size=5000000&overrun_nonfatal=1')

# Tello command setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
tello_address = ('192.168.10.1', 8889)

def send_command(command):
    def run():
        sock.sendto(command.encode(), tello_address)
    threading.Thread(target=run).start()

# Function to decode predictions manually
def decode_predictions(preds, top=5):
    results = []
    for pred in preds:
        top_indices = pred.argsort()[-top:][::-1]
        result = [
            (str(i), class_index[str(i)][1], pred[i]) for i in top_indices
        ]
        results.append(result)
    return results

# Set frame skip for performance
frame_skip = 5
frame_count = 0

while True:
    try:
        ret, frame = tello_video.read()
        if ret:
            frame = cv2.resize(frame, (320, 240))
            frame_count += 1

            if frame_count % frame_skip == 0:
                # Pre-process the frame for MobileNetV2
                resized = cv2.resize(frame, (224, 224))
                img_array = tf.keras.applications.mobilenet_v2.preprocess_input(np.expand_dims(resized, axis=0))

                # Run inference and handle errors
                try:
                    predictions = model.predict(img_array)
                    top_prediction = decode_predictions(predictions, top=1)[0][0]
                except Exception as e:
                    print(f"Prediction Error: {e}")
                    continue

                # Check for person detection
                if top_prediction[1] == 'person' and top_prediction[2] > 0.5:
                    print("found person")
                    centre_x, centre_y = frame.shape[1] // 2, frame.shape[0] // 2
                    
                    # Uncomment and adjust commands for Tello movement
                    # if centre_x < frame.shape[1] // 3:
                    #     send_command('left 20')
                    # elif centre_x > frame.shape[1] * 2 // 3:
                    #     send_command('right 20')
                    # if centre_y < frame.shape[0] // 3:
                    #     send_command('up 20')
                    # elif centre_y > frame.shape[0] * 2 // 3:
                    #     send_command('down 20')

            cv2.imshow('Tello', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error: {e}")
        break

tello_video.release()
cv2.destroyAllWindows()
sock.close()
