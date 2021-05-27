import numpy as np
import cv2 
import copy

class HeatMap():
    
    def __init__(self, im0s):
        self.im0s=im0s
        self.first_frame = copy.deepcopy(self.im0s)
        self.height, self.width = self.im0s.shape[:2]
        self.accum_image = np.zeros((self.height, self.width), np.uint8)

    def create_image(self, bbox_list):
        #Create empty image
        self.new_image = np.zeros((self.height, self.width), np.uint8)
        #Draw all bboxes on empty image
        for bbox in bbox_list:   
            cv2.rectangle(self.new_image, (bbox[0], bbox[1]), (bbox[2],bbox[3]), (36,255,12), 2)

        
    def acumulate(self):
        self.accum_image = cv2.add(self.accum_image, self.new_image)
    

    def get_hm(self, idx):
        div = np.ones((self.height, self.width, 3), np.uint8) * idx
        ff = self.first_frame      
        accum = cv2.divide(cv2.cvtColor(self.accum_image,cv2.COLOR_GRAY2RGB) , idx/50)
        print(f'shape accum: {accum.shape} shape div: {ff.shape}')
        hm = cv2.add(accum, ff)  ## aqui
        return hm

'''
ret, th1 = cv.threshold(zero_mask, threshold, maxValue, cv.THRESH_BINARY)
accum_image = cv.add(accum_image, th1)s
color_image_video = cv.applyColorMap(accum_image, cv.COLORMAP_SUMMER)
print('ndim frame, ndim coolor_image_video', frame.shape, color_image_video.shape)
video_frame = cv.addWeighted(frame, 0.7, color_image_video, 0.7, 0)#mismo numero de dimensiones, mismo tipo de dato
'''