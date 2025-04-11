#!/usr/bin/env python3

import os
from fastapi import FastAPI
import uvicorn
from tests.helper import get_input_file, get_input_directory, get_jobs_directory, get_output_file, is_output_file, prepare_output_directory
import subprocess
import sys
from facefusion.jobs.job_manager import clear_jobs, init_jobs
import argparse

os.environ['OMP_NUM_THREADS'] = '1'

from facefusion import core

# if __name__ == '__main__':
# 	core.cli()
# core.cli()
app = FastAPI()

@app.get("/do")
async def do():
	before_all()
	before_each()
	swap_face_to_video()

def before_all():
	print('before_all')
	# conditional_download(get_input_directory(),
	# [
	# 	'https://github.com/facefusion/facefusion-assets/releases/download/examples-3.0.0/source.jpg',
	# 	'https://github.com/facefusion/facefusion-assets/releases/download/examples-3.0.0/target-240p.mp4'
	# ])
	subprocess.run([ 'ffmpeg', '-i', get_input_file('cxk.mp4'), '-vframes', '1', get_input_file('cxk.jpg') ])
	print('before_all_end')

def before_each():
	print('before_each')
	clear_jobs(get_jobs_directory())
	init_jobs(get_jobs_directory())
	prepare_output_directory()
	print('before_each_end')

def swap_face_to_video():
	print('test_swap_face_to_video_start')
	commands = [ sys.executable, 'facefusion.py', 'headless-run', '-j', get_jobs_directory(), '--processors', 'face_swapper', '-s', get_input_file('mbg2.png'), '-t', get_input_file('cxk.mp4'), '-o', get_output_file('test-swap-face-to-video.mp4'), '--trim-frame-end', '1' ]

	assert subprocess.run(commands).returncode == 0
	assert is_output_file('test-swap-face-to-video.mp4') is True
	print('test_swap_face_to_video_end')

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--port", type=int, default=7864)
	# parser.add_argument("--webui",type=bool,default=False)
	global args
	args = parser.parse_args()
	try:
		uvicorn.run(app=app, host="0.0.0.0", port=7864, workers=1)
	except Exception as e:
		print(e)
		exit(0)
