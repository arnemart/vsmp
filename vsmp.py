#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import json
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--force", action="store_true", help="Refresh even if frames are identical")
parser.add_argument("-c", "--clear", action="store_true", help="Clear display")
parser.add_argument("-d", "--debug", action="store_true", help="Debug logging")
parser.add_argument("-s", "--dry", action="store_true", help="Dry run")
parser.add_argument("-i", "--img", help="Display a single image")
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug or args.dry else logging.ERROR)

if args.dry:
  logging.info("Dry run")

from os import listdir, path
dir = path.dirname(path.realpath(__file__))

if not args.dry:
  from PIL import Image
  sys.path.append(path.join(dir, 'lib'))
  from waveshare_epd import epd7in5_V2

def get_image(status):
  return path.join(dir, "movies", status["movie"], "frame_%d.png" % status["frame"])

def next_movie(movie):
  movies = listdir(path.join(dir, "movies"))
  movies.sort()
  if movie in movies:
    return movies[(movies.index(movie) + 1) % len(movies)]
  else:
    return movies[0]

STATUS_FILE_PATH = path.join(dir, "status.json")

def read_status():
  logging.debug("Load status JSON")
  with open(STATUS_FILE_PATH) as status_file:
    try:
      return json.load(status_file)
    except IOError as e:
      logging.error(e)

def save_status(s):
  logging.debug("Save new status JSON")
  with open(STATUS_FILE_PATH, "w") as status_file:
    try:
      json.dump(s, status_file)
    except IOError:
      logging.error(e)

status = read_status()

def with_epd(fn):
  epd = epd7in5_V2.EPD()
  epd.init()
  fn(epd)
  epd.sleep()

if args.img:
  logging.info("Show image: %s" % args.img)
  if not args.dry:
    img = Image.open(args.img)
    with_epd(lambda epd: epd.display(epd.getbuffer(img)))
  status["prev"] = args.img
  save_status(status)
  sys.exit()

if args.clear:
  logging.info("Clearing screen")
  if not args.dry:
    with_epd(lambda epd: epd.Clear())
  status["prev"] = "clear"
  save_status(status)
  sys.exit()

status["frame"] += 1

logging.info("Current movie is %s, next frame is %d" % (status["movie"], status["frame"]))
next_frame = get_image(status)

if not path.exists(next_frame):
  logging.info("Image file for next frame does not exists, go to next movie")
  status["movie"] = next_movie(status["movie"])
  status["frame"] = 1
  logging.info("Next movie is %s" % status["movie"])
  next_frame = get_image(status)

try:
  proceed = True
  
  if not args.dry:
    img = Image.open(next_frame)
    if not args.force and "prev" in status and status["prev"] != "clear" and path.exists(status["prev"]):
      prev_img = Image.open(status["prev"])
      proceed = list(prev_img.getdata()) != list(img.getdata())

  if proceed:
    logging.debug("Display next frame")
    if not args.dry:
      with_epd(lambda epd: epd.display(epd.getbuffer(img)))
  else:
    logging.debug("Frames are identical, do nothing")

except IOError as e:
  logging.error(e)

status["prev"] = next_frame
save_status(status)
