import numpy
import subprocess as sp

FFMPEG_BIN = "ffmpeg.exe"


command = [ FFMPEG_BIN,
            '-i', '003_camera_p3.mp4',
            '-f', 'image2pipe',
            '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo', '-']
pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)


# read 420*360*3 bytes (= 1 frame)
raw_image = pipe.stdout.read(420*360*3)
# transform the byte read into a numpy array
image = numpy.fromstring(raw_image, dtype='uint8')
image = image.reshape((360,420,3))
# throw away the data in the pipe's buffer.
pipe.stdout.flush()

