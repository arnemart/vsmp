# VSMP

Put movies in `movies`-folder, one movie per folder.

Put frames as 1-bit 800x480 png-files inside each movie folder, named `frame_1.png` and onward, no frame gaps are allowed.

## Converting a movie to cropped 800x480 png.files using ffmpeg:

```
ffmpeg -i input.file -vf "scale=(iw*sar)*max(800/(iw*sar)\,480/ih):ih*max(800/(iw*sar)\,480/ih), crop=800:480" "frame_%d.png"
```

## Converting all frames to 1-bit with Floyd-Steinberg dithering using imagemagick:

```
find . -name "*.png" -exec convert {} -dither FloydSteinberg -remap pattern:gray50 {} \;
```