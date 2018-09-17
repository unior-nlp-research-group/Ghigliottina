# -*- coding: utf-8 -*-

import m3u8
import requests

rai1_url_base = 'http://b2.stream14.rai.it/italy/rai1_1200/'
rai1_url = rai1_url_base + 'chunklist.m3u8'

m3u8_obj = m3u8.load(rai1_url)
print m3u8_obj.segments
print m3u8_obj.target_duration

last_segment_id = str(m3u8_obj.segments[-1]).split(',')[1]
last_segment_url = rai1_url_base + last_segment_id

print "Fetching segment from url {}".format(last_segment_url)

response = requests.get(last_segment_url)
with open('segment.ts', 'wb') as out:
    for block in response.iter_content(1024):
        out.write(block)

import subprocess as sp
FFMPEG_BIN = "ffmpeg"
command = [ FFMPEG_BIN,
        '-y', # (optional) overwrite output file if it exists
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        #'-s', '420x360', # size of one frame
        '-pix_fmt', 'rgb24',
        '-r', '24', # frames per second
        '-i', '-', # The imput comes from a pipe
        '-an', # Tells FFMPEG not to expect any audio
        '-vcodec', 'mpeg',
        'my_output_videofile.mp4' ]

pipe = sp.Popen( command, stdin=sp.PIPE, stderr=sp.PIPE)

