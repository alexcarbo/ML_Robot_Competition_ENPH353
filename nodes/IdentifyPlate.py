import numpy as np
import constants as const
import cv2
import tensorflow as tf
from PIL import Image
from matplotlib import pyplot as plt
from keras.models import load_model
from keras import backend



class IdentifyPlate:
    def __init__(self):
        self.plateset = []
        self.position_set = []
        self.plate_length = 0
        self.check_crop = False

        ### Not sure what this does but it fixes my issue with tensors not being an element in a graph
        config = tf.ConfigProto(
                    # device_count={'GPU': 1},
                    intra_op_parallelism_threads=1,
                    allow_soft_placement=True
                    )

        config.gpu_options.allow_growth = True
        config.gpu_options.per_process_gpu_memory_fraction = 0.6

        self.session = tf.Session(config=config)

        backend.set_session(self.session)
        ###

        # Load the model to use and setup the one hot encoding
        self.conv_model = load_model("/home/fizzer/Desktop/353_ws/neural_net/Apr14.h5")
        self.alphanumeric = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        self.int_to_char = dict((i, c) for i, c in enumerate(self.alphanumeric))

    def plateLabel(self, image, plate_type):
        # Prepare image to be spliced into sections
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imgset = []
        prediction = []
        pil_im = Image.fromarray(rgb_image)

        if plate_type == "license":
            self.position_set = const.LICENSE_CHAR
            self.plate_length = 4

        elif plate_type == "parking":
            self.position_set = const.PARKING_CHAR
            self.plate_length = 3

        else:
            print("Invalid plate type")
        
        # Add characters from the plates to a list
        for i in range(self.plate_length):      
            imgset.append(image[self.position_set[i][1]:self.position_set[i][3], self.position_set[i][0]:self.position_set[i][2]])   

        # Used for debugging the character locations on the splices
        if self.check_crop and plate_type == "parking":    
            cv2.imshow("char 0", imgset[0])
            cv2.imshow("char 1", imgset[1])
            cv2.imshow("char 2", imgset[2])
            if plate_type == "license":
                cv2.imshow("char 3", imgset[3])
            cv2.waitKey(3)

        checkset = np.array(imgset)/255.0

        # Get the predictions from the model
        for i, e in enumerate(checkset):
            img_aug = np.expand_dims(checkset[i], axis=0)
            ### These two with statement are also added to fix the issue
            with self.session.as_default():
                with self.session.graph.as_default():
                    predict = self.conv_model.predict(img_aug)[0]
                    prediction.append(self.get_char(np.argmax(predict))) 

        return prediction

    def get_char(self, char):
        return self.int_to_char[char]