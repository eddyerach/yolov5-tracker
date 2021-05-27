#!/bin/bash
dir="/home/ubuntu/docker/input_videos_largos/*"
for video in $dir
do
  echo $video
  IFS="/" read -r -a array <<< "$video" 
  echo "${array[3]}"
  python detect.py --source $video --class 0
done
