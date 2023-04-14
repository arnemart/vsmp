#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import json
import logging
from PIL import Image
from os import listdir, path
import argparse
dir = path.dirname(path.realpath(__file__))
sys.path.append(path.join(dir, 'lib'))
from waveshare_epd import epd7in5_V2

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--force", action="store_true", help="Refresh even if frames are identical")
parser.add_argument("-c", "--clear", action="store_true", help="Clear display")
parser.add_argument("-d", "--debug", action="store_true", help="Debug logging")
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug else logging.ERROR)

if args.clear:
  epd = epd7in5_V2.EPD()
  epd.init()
  epd.Clear()
  epd.sleep()
  sys.exit()

def get_image(movie, frame):
  return path.join(dir, "movies", movie, "frame_%d.png" % frame)

def next_movie(movie):
  movies = listdir(path.join(dir, "movies"))
  movies.sort()
  if movie in movies:
    return movies[(movies.index(movie) + 1) % len(movies)]
  else:
    return movies[0]

STATUS_FILE_PATH = path.join(dir, "status.json")

logging.debug("Load status JSON")
with open(STATUS_FILE_PATH) as status_file:
  status = json.load(status_file)

prev_frame = get_image(status["movie"], status["frame"])

status["frame"] += 1

logging.info("Current movie is %s, next frame is %d" % (status["movie"], status["frame"]))
next_frame = get_image(status["movie"], status["frame"])

if not path.exists(next_frame):
  logging.info("Image file for next frame does not exists, go to next movie")
  status["movie"] = next_movie(status["movie"])
  logging.info("Next movie is %s" % status["movie"])
  status["frame"] = 1
  next_frame = get_image(status["movie"], 1)

logging.debug("Save new status JSON")
with open(STATUS_FILE_PATH, "w") as status_file:
  json.dump(status, status_file)

try:
  prev_img = Image.open(prev_frame)
  img = Image.open(next_frame)
  if args.force or list(prev_img.getdata()) != list(img.getdata()):
    logging.debug("Display next frame")
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.display(epd.getbuffer(img))
    epd.sleep()
  else:
    logging.debug("Frames are identical, do nothing")

except IOError as e:
  logging.error(e)
