from __future__ import print_function
import cv2 as cv
import copy
import argparse
import numpy as np

#from progress.bar import Bar
parser = argparse.ArgumentParser(description='This program shows how to use background subtraction methods provided by \
                                              OpenCV. You can process both videos and images.')
parser.add_argument('--input', type=str, help='Path to a video or a sequence of image.', default='vtest.avi')
parser.add_argument('--algo', type=str, help='Background subtraction method (KNN, MOG2).', default='MOG2')
args = parser.parse_args()
if args.algo == 'MOG2':
    backSub = cv.createBackgroundSubtractorMOG2()
if args.algo == 'CNT':
    backSub = cv.bgsegm.BackgroundSubtractorCNT()
if args.algo == 'LSBP':
    backSub = cv.bgsegm.createBackgroundSubtractorLSBP()
else:
    backSub = cv.createBackgroundSubtractorKNN()
    backSub.setDetectShadows(False) #Set shadows detection
    backSub.setHistory(90) #Sets the number of last frames that affect the background mode
    backSub.setShadowThreshold(0.5)
capture = cv.VideoCapture(cv.samples.findFileOrKeep(args.input))
if not capture.isOpened():
    print('Unable to open: ' + args.input)
    exit(0)


frame_width = int(capture.get(3))
frame_height = int(capture.get(4))
out = cv.VideoWriter('registroCentros.avi',cv.VideoWriter_fourcc('M','P','4','V'), 10, ( frame_width ,frame_height), 1)

frames = 0
heatmap = 0
heatmapIntAcu = 0
fgMaskAcu = 0

length = int(capture.get(cv.CAP_PROP_FRAME_COUNT)) #
first_iteration_indicator = 1
while True:
    #print("FRAMES: ", length)
    frames +=1
    ret, frame = capture.read()
    
    """ 
    roiy = 136
    roih = 480
    roix = 0
    roiw = 595
    print('size frame antes', frame.dtype)
    frame = frame[roiy:roiy+roih, roix:roix+roiw]
    print('size frame despues', frame.dtype) """
    #fgMask = backSub.apply(frame)

    if frame is None:
        break
    
    if first_iteration_indicator == 1:
        first_frame = copy.deepcopy(frame)
        height, width = frame.shape[:2]
        accum_image = np.zeros((height, width), np.uint8)
        accum_image_heat = np.zeros((height, width), np.uint8)
        first_iteration_indicator = 0
        #cv.imshow('zeros', accum_image)
    
    #[y:y+h, x:x+w]
    
    
    zero_mask = np.zeros((height, width), np.uint8)
    #heatmapMask = frame
    cv.rectangle(frame, (10, 2), (100,20), (255,255,255), -1)
    cv.putText(frame, str(capture.get(cv.CAP_PROP_POS_FRAMES)), (15, 15),
               cv.FONT_HERSHEY_SIMPLEX, 0.5 , (0,0,0))
    #print('Current frame: ',str(capture.get(cv.CAP_PROP_POS_FRAMES)))
    #cnts = cv.findContours(fgMask, cv.RETR_TREE, cv.CHAIN_APPROX_TC89_KCOS)[0]
    #minimumBB = 7000

    for cnt in cnts:
        if cv.contourArea(cnt) > minimumBB:
            x, y, w, h = cv.boundingRect(cnt)
            #cv.rectangle(fgMask, (x,y), (x+w,y+h), (255, 0, 0) , 5)
            cx = int(x+(w/2))
            cy = int(y+(h/2))
            cv.circle(zero_mask,(cx,cy), 5, (255, 255, 255), -1)
            #cv.putText(frame, str((cx,cy)), (x+w, y+h),cv.FONT_HERSHEY_SIMPLEX, 1 , (255,255,255))


    threshold = 1
    maxValue = 100

    #Trajectories
    ret, th1 = cv.threshold(zero_mask, threshold, maxValue, cv.THRESH_BINARY)
    accum_image = cv.add(accum_image, th1)
    color_image_video = cv.applyColorMap(accum_image, cv.COLORMAP_SUMMER)
    print('ndim frame, ndim coolor_image_video', frame.shape, color_image_video.shape)
    video_frame = cv.addWeighted(frame, 0.7, color_image_video, 0.7, 0)#mismo numero de dimensiones, mismo tipo de dato,

    #Heat Map
    ret_heat, th1_heat = cv.threshold(zero_mask, threshold, maxValue, cv.THRESH_BINARY)
    th1_heat = np.asarray(th1_heat, np.uint8)
    accum_image_heat_int = np.asarray(accum_image_heat, np.uint8) ##
    th1_heat_div = np.asarray(th1_heat/ length, np.uint8)
    accum_image_heat = cv.add(accum_image_heat_int, th1_heat_div) 
    accum_image_heat_int = np.asarray(accum_image_heat, np.uint8) ##
    color_image_video_heat = cv.applyColorMap(accum_image_heat_int, cv.COLORMAP_SUMMER)
    video_frame_heat = cv.addWeighted(frame, 0.7, color_image_video_heat, 0.7, 0)

    ##Generacion de video
    cv.imshow('trajectories', video_frame)
    cv.imshow('ROI', frame)
    #cv.imshow('th1_heat_div', th1_heat_div)
    #cv.imshow('frame', frame)


    #cv.imshow('fgMask', fgMask)
    #fgMaskColor = cv.applyColorMap(fgMask, cv.COLORMAP_SUMMER)
    #cv.imshow('fgMaskColor', fgMaskColor)
    out.write(video_frame)
    keyboard = cv.waitKey(30)
    if keyboard == 'q' or keyboard == 27:
        break 
cv.imwrite('TrackCenters1244.jpg', video_frame)