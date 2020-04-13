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

        # Not sure what this does but it fixes my issue with tensors not being an element in a graph
        config = tf.ConfigProto(
                    # device_count={'GPU': 1},
                    intra_op_parallelism_threads=1,
                    allow_soft_placement=True
                    )

        config.gpu_options.allow_growth = True
        config.gpu_options.per_process_gpu_memory_fraction = 0.6

        self.session = tf.Session(config=config)

        backend.set_session(self.session)

        self.conv_model = load_model("/home/fizzer/Desktop/353_ws/neural_net/alphanumeric_model.h5")
        self.alphanumeric = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        self.int_to_char = dict((i, c) for i, c in enumerate(self.alphanumeric))

    def plateLabel(self, image, plate_type):
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
            print("Invalid")
        
        for i in range(self.plate_length):      
            imgset.append(image[self.position_set[i][1]:self.position_set[i][3], self.position_set[i][0]:self.position_set[i][2]])
            # imgset.append(np.array(pil_im.crop(self.position_set[i])))      
        
        checkset = np.array(imgset)/255.0

        for i, e in enumerate(checkset):
            img_aug = np.expand_dims(checkset[i], axis=0)
            with self.session.as_default():
                with self.session.graph.as_default():
                    predict = self.conv_model.predict(img_aug)[0]
                    prediction.append(self.get_char(np.argmax(predict)))

            plt.figure()
            plt.imshow(checkset[i])
            caption = ("Character\n Predicted: {:.2}"
                        .format(self.get_char(np.argmax(predict))))
            plt.text(0.5, 0.5, caption, color='orange', fontsize = 16,
            horizontalalignment='left', verticalalignment='bottom') 


            # self.predictChar(i, prediction, checkset)

        return prediction

    # def predictChar(self, index, prediction, image_set):
    #     img_aug = np.expand_dims(image_set[index], axis=0)
    #     predict = self.conv_model.predict(img_aug)[0]
    #     prediction.append(self.get_char(np.argmax(predict)))

    #     plt.figure()
    #     plt.imshow(image_set[index])
    #     caption = ("Character\n Predicted: {:.2}"
    #                 .format(self.get_char(np.argmax(predict))))
    #     plt.text(0.5, 0.5, caption, color='orange', fontsize = 16,
    #     horizontalalignment='left', verticalalignment='bottom') 

    def get_char(self, char):
        return self.int_to_char[char]