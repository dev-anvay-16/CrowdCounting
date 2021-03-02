# import the necessary packages
import numpy as np
import imutils
from imutils.video import VideoStream
import threading
import argparse
import datetime
import core.utils as utils
from core.functions import *
import time
import cv2
import tensorflow as tf
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

from core.config import cfg




class Camera:

    def __init__(self,ip):
        self.ip = ip

    lock = threading.Lock()
    outputFrame_camera = None
    saved_model_loaded = tf.saved_model.load('./checkpoints/yolov4-416')
    infer = saved_model_loaded.signatures['serving_default']
    
    def generate_camera1(self):
    # grab global references to the output frame and lock variables
        global outputFrame_camera, lock
    # loop over frames from the output stream
        while True:
        # wait until the lock is acquired
            with self.lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
                if self.outputFrame_camera is None:
                    continue
            # encode the frame in JPEG format
                (flag, encodedImage) = cv2.imencode(".jpg", self.outputFrame_camera)
            # ensure the frame was successfully encoded
                if not flag:
                    continue
        # yield the output frame in the byte format
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n') 
    
    def detect_motion_camera2(self,frameCount):
        global outputFrame_camera, lock
        config = ConfigProto()
        config.gpu_options.allow_growth = True
        session = InteractiveSession(config=config)

        vs_1 = VideoStream(f'http://{self.ip}:8080/video').start()
        time.sleep(2.0)
        total = 0
        frame_num = 0
        input_size = 416
        while True:
            # read the next frame from the video stream, resize it,
            # convert the frame to grayscale, and blur it

            frame = vs_1.read()
            frame = imutils.resize(frame, width=400)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_num += 1

            frame_size = frame.shape[:2]
            image_data = cv2.resize(frame, (input_size, input_size))
            image_data = image_data / 255.
            image_data = image_data[np.newaxis, ...].astype(np.float32)
            start_time = time.time()

            batch_data = tf.constant(image_data)
            pred_bbox = self.infer(batch_data)
            for key, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]

            boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
                boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
                scores=tf.reshape(
                    pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
                max_output_size_per_class=50,
                max_total_size=50,
                iou_threshold=0.45,
                score_threshold=0.50
            )

            # format bounding boxes from normalized ymin, xmin, ymax, xmax ---> xmin, ymin, xmax, ymax
            original_h, original_w, _ = frame.shape
            bboxes = utils.format_boxes(boxes.numpy()[0], original_h, original_w)

            pred_bbox = [bboxes, scores.numpy()[0], classes.numpy()[0], valid_detections.numpy()[0]]

            # read in all class names from config
            class_names = utils.read_class_names(cfg.YOLO.CLASSES)

            # by default allow all classes in .names file
            allowed_classes = list(class_names.values())

            counted_classes = self.count_objects(pred_bbox, by_class=False, allowed_classes=allowed_classes)
            # loop through dict and print
            for key, value in counted_classes.items():
                print("Number of {}s: {}".format(key, value))
            # frame = cv2.rotate(frame.copy(), cv2.ROTATE_180)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            image = utils.draw_bbox(frame, pred_bbox, False, counted_classes, allowed_classes=allowed_classes,
                                    read_plate=False)

            timestamp = datetime.datetime.now()
            cv2.putText(frame, timestamp.strftime(
                "%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

            with self.lock:
                outputFrame_camera2 = image

            fps = 1.0 / (time.time() - start_time)
            print("FPS: %.2f" % fps)
