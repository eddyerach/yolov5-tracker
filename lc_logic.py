import numpy as np
import cv2 as cv
from deep_sort_pytorch.utils.draw import draw_boxes
import random

class Line_cross():
    """Class used to manage all the processes related with the determination of direction and the in and out count of each person."""
    def __init__(self, coordenates ):
        self.track = {}
        self.coordenates = coordenates
        self.x1 = self.coordenates[0][0]
        self.y1 = self.coordenates[0][1]
        self.x2 = self.coordenates[1][0]
        self.y2 = self.coordenates[1][1]
        self.count_salida = 0
        self.count_entrada = 0
        self.counted = []
        self.color = self.compute_color_for_labels()
 
    """ Method to get the direction of a person. It compares the x of the coordenates and the x of the point.
    It returns "right" or "left" depending on which of the x's is greater.  """
    def get_direction(self,point):
        line_x=self.coordenates[0][0]
        # print(f'value of point:{point}')
        point_x=point[0]
        point_y=point[1]
        side=None
        offset = 50
        offset_circle = 5 #Define ancho del linecross.
        if (point_x<=line_x+offset) and (point_x>=line_x-offset):
            if (point_y<=self.coordenates[1][1]) and (point_y>=self.coordenates[0][1]):
                if line_x + offset_circle < point_x:# - offset_circle/2 -0.1:
                    side="right"
                elif line_x - offset_circle >point_x:# + offset_circle/2 +0.1:
                    side="left"

        return side 
    
    """ Method to get de direction of each person using its center point and its id  """   
    def get_ids_directions(self,center_points,identities_person):
        ids_directions={}
        # for i,point in enumerate(center_points):
        for i, point in enumerate(center_points):
            ids_directions[identities_person[i]]=self.get_direction(point)

        return ids_directions

    def compute_color_for_labels(self):
        """
        Simple function that adds fixed color depending on the class
        """
        palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)
        label =  random.randint(1, 1000)
        color = [int((p * (label ** 2 - label + 1)) % 255) for p in palette]
        return color


    
    """ Method to count people in and people out. It iterates over a dictionary."""
    def count(self):
        for k, v in self.track.items():
                
            if len(v) ==2 and k not in self.counted:
                if v[0] == 'left' and v[1] == 'right':
                    self.count_salida += 1
                    self.counted.append(k)

                elif  v[0] == 'right' and v[1] == 'left':
                    self.count_entrada += 1
                    self.counted.append(k)


        for id in self.counted:
            del self.track[id]
            #Reemplazar la primera direccion con la segunda.
            #self.track[id[0]]=self.track[id[1]]
            #self.track[id[1]]=None  
            #self.track[id][0]=self.track[id][1]
            #self.track[id].pop(1)

        
        self.counted = []

        '''
        orig
        [r,l] -> in 2 -> []
        [r,]
        [r,l]->in 3

        cambio
        [r,l] -> in 2 -> [l,]
        [l,r] -> out +1 -> [r,]
        [r,l]  -> in 3
        '''

    def get_results(self, output_name):
        input_count = self.count_entrada
        output_count = self.count_salida
        file1 = open(output_name + ".txt","w")
        L = ["Counting Results on video: ", str(output_name),"\n","total input count: ",str(input_count),"\n","total output count: ",str(output_count)] 
        file1.writelines(L)
        file1.close()

    




        ...
""" Class used to manage people data like id, direction and trajectory."""
class Person():
    def __init__(self, id, trajectory):
        self.id = id
        self.direction = None
        self.trajectory = trajectory


class InferenceLC():
    def __init__(self, lcs):
        self.lcs = lcs
        
    def draw_lcs(self, frame):
        for lc in self.lcs:
            cv.line(frame,(lc.x1,lc.y1),(lc.x2,lc.y2),lc.color,2)

    def xyxy2xywh(self, bbox_results):
        w = bbox_results[:,2]-bbox_results[:,0]
        h = bbox_results[:,3]-bbox_results[:,1]

        bbox_results[:, 0] = bbox_results[:, 0] + (w/2)
        bbox_results[:, 1] = bbox_results[:, 1] + (h/2)
        bbox_results[:, 2] = w
        bbox_results[:, 3] = h

        return bbox_results

    def draw_tracker(self, outputs_person, frame):
        self.bbox_xyxy_person = outputs_person[:, :4]
        self.identities_person = outputs_person[:, -1]
        frame = draw_boxes(
                    frame, self.bbox_xyxy_person, self.identities_person)
        return frame

    def get_centers(self):
        center_point_x = (self.bbox_xyxy_person[:, 0] + ((self.bbox_xyxy_person[:, 2]-self.bbox_xyxy_person[:, 0])/2))
        center_point_y = (self.bbox_xyxy_person[:, 1] + ((self.bbox_xyxy_person[:, 3]-self.bbox_xyxy_person[:, 1])/2))
        center_point = list(zip(center_point_x, center_point_y))

        return center_point

    def id_directions(self, center_point):
        directions = []
        for lc in self.lcs:
            directions.append(lc.get_ids_directions(center_point, self.identities_person))
        return directions

    def draw_circles(self, center_point, frame):
        for item in center_point:
            cx = int(item[0])
            cy = int(item[1])
            cv.circle(frame,(cx,cy), 5, (255, 255, 255), -1)
    
    def track_directions(self, center_point):
        directions = self.id_directions(center_point)

        for id in self.identities_person:
            for idx, lc in enumerate(self.lcs):
                if not id in lc.track:
                    lc.track[id] = []
                if (directions[idx][id] not in lc.track[id]) and (directions[idx][id] != None):
                    lc.track[id].append(directions[idx][id])

    def count_lcs(self):
        for lc in self.lcs:
            lc.count()
    
    def draw_count_results(self, frame):
        for lc in self.lcs:
            cv.putText(frame, ('i' + str(lc.count_entrada)), (lc.x1,lc.y1),cv.FONT_HERSHEY_SIMPLEX, 1 , lc.color, thickness=3) 
            cv.putText(frame, ('o' + str(lc.count_salida)), (lc.x2,lc.y2),cv.FONT_HERSHEY_SIMPLEX, 1 , lc.color, thickness=3)
