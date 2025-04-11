#!/usr/bin/env python3

import argparse
import os

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware  # 引入 CORS中间件模块

from custom.file_utils import logging, delete_old_files_and_folders
from facefusion import core
from facefusion.args import collect_step_args
from facefusion.jobs import job_helper, job_manager, job_runner, job_store
from facefusion.typing import Args
from tests.helper import get_output_file

os.environ['OMP_NUM_THREADS'] = '1'


def create_and_run_job(step_args: Args) -> bool:
	job_id = job_helper.suggest_job_id('ui')
	step_args['output_path'] = get_output_file(job_id + '.mp4')

	for key in job_store.get_job_keys():
		state_manager.sync_item(key)  # type:ignore
	return job_manager.create_job(job_id) and job_manager.add_step(job_id, step_args) and job_manager.submit_job(
		job_id) and job_runner.run_job(job_id, core.process_step)


# 设置允许访问的域名
origins = ["*"]  # "*"，即为所有。

app = FastAPI(docs_url=None)
# noinspection PyTypeChecker
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,  # 设置允许的origins来源
	allow_credentials=True,
	allow_methods=["*"],  # 设置允许跨域的http方法，比如 get、post、put等。
	allow_headers=["*"])  # 允许跨域的headers，可以用来鉴别来源等作用。
# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


# 使用本地的 Swagger UI 静态资源
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
	logging.info("Custom Swagger UI endpoint hit")
	return get_swagger_ui_html(
		openapi_url="/openapi.json",
		title="Custom Swagger UI",
		swagger_js_url="/static/swagger-ui/5.9.0/swagger-ui-bundle.js",
		swagger_css_url="/static/swagger-ui/5.9.0/swagger-ui.css",
	)


@app.get("/", response_class=HTMLResponse)
async def root():
	return """
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset=utf-8>
            <title>Api information</title>
        </head>
        <body>
            <a href='./docs'>Documents of API</a>
        </body>
    </html>
    """


@app.get('/test')
async def test():
	"""
	测试接口，用于验证服务是否正常运行。
	"""
	return PlainTextResponse('success')


result_input_dir = './result/input'
result_output_dir = './result/output'


@app.get("/do")
async def do(source_path: str, target_path: str):
	step_args = collect_step_args()
	step_args['source_paths'] = [source_path]
	step_args['target_path'] = target_path
	
	create_and_run_job(step_args)

	delete_old_files_and_folders(result_input_dir, 1)
	delete_old_files_and_folders(result_output_dir, 1)

	return PlainTextResponse(step_args['output_path'])


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--port", type=int, default=7864)

	argsMain = parser.parse_args()

	try:
		uvicorn.run(app=app, host="0.0.0.0", port=argsMain.port, workers=1)
	except Exception as e:
		print(e)
		exit(0)
