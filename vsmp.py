#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import json
import logging
from PIL import Image
from os import listdir, path
dir = path.dirname(path.realpath(__file__))
sys.path.append(path.join(dir, 'lib'))
from waveshare_epd import epd7in5_V2

logging.basicConfig(level=logging.ERROR)


with open("status.json") as status_file:
  status = json.load(status_file)

prev_frame = path.join(dir, "movies", status["movie"], "frame_%d.png" % (status["frame"]))

status["frame"] += 1

next_frame = path.join(dir, "movies", status["movie"], "frame_%d.png" % (status["frame"]))

if not path.exists(next_frame):
  movies = listdir("movies")
  movies.sort()
  if status["movie"] in movies:
    status["movie"] = movies[(movies.index(status["movie"]) + 1) % len(movies)]
  else:
    status["movie"] = movies[0]
  status["frame"] = 1
  next_frame = path.join(dir, "movies", status["movie"], "frame_1.png")

with open("status.json", "w") as status_file:
  json.dump(status, status_file)

try:
  prev_img = Image.open(prev_frame)
  img = Image.open(next_frame)
  if list(prev_img.getdata()) == list(img.getdata()):
    logging.info("Frames are identical, do nothing")
  else:
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.display(epd.getbuffer(img))
    epd.sleep()
    
except IOError as e:
  logging.info(e)
