#!/usr/bin/env python3

import argparse
import os
import sys

import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware  # 引入 CORS中间件模块

from custom.TextProcessor import TextProcessor
from custom.file_utils import logging, delete_old_files_and_folders, save_upload_to_file
from facefusion import core
from facefusion.jobs import job_helper

os.environ['OMP_NUM_THREADS'] = '1'

result_input_dir = './results/input'
result_output_dir = './results/output'
download_providers = "github"
download_scope = "lite"

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


@app.get("/force_download")
async def force_download():
	try:
		# 下载模型
		sys.argv = [
			"facefusion.py",
			"force-download",
			"--download-providers", download_providers,
			"--download-scope", download_scope
		]
		core.cli()
	except SystemExit as e:
		exit_code = e.code if isinstance(e.code, int) else 1
		if exit_code != 0:
			raise HTTPException(status_code=400, detail=f"force-download failed")


@app.post("/do")
async def do(
	source_file: UploadFile = File(..., description="选择图像或音频路径"),
	target_file: UploadFile = File(..., description="选择图像或视频路径"),
):
	os.makedirs(result_input_dir, exist_ok=True)  # 创建目录（如果不存在）
	os.makedirs(result_output_dir, exist_ok=True)  # 创建目录（如果不存在）

	source_path = await save_upload_to_file(
		input_dir=result_input_dir,
		upload_file=source_file
	)

	target_path = await save_upload_to_file(
		input_dir=result_input_dir,
		upload_file=target_file
	)

	job_id = job_helper.suggest_job_id('api')
	output_path = f"{result_output_dir}/{job_id}.mp4"

	try:
		# 创建草稿作业
		sys.argv = ["facefusion.py", "job-create", job_id]
		core.cli()
	except SystemExit as e:
		exit_code = e.code if isinstance(e.code, int) else 1
		if exit_code != 0:
			raise HTTPException(status_code=400, detail=f"job-create {job_id} failed")

	try:
		# 向草稿作业添加步骤
		sys.argv = [
			"facefusion.py",
			"job-add-step", job_id,
			"--source-paths", source_path,
			"--target-path", target_path,
			"--output-path", output_path,
		]
		core.cli()
	except SystemExit as e:
		exit_code = e.code if isinstance(e.code, int) else 1
		if exit_code != 0:
			raise HTTPException(status_code=400, detail=f"job-add-step {job_id} failed")

	try:
		# 提交草稿作业以成为排队作业
		sys.argv = ["facefusion.py", "job-submit", job_id]
		core.cli()
	except SystemExit as e:
		exit_code = e.code if isinstance(e.code, int) else 1
		if exit_code != 0:
			raise HTTPException(status_code=400, detail=f"job-submit {job_id} failed")

	try:
		# 运行排队的作业
		sys.argv = [
			"facefusion.py",
			"job-run", job_id,
			"--download-providers", download_providers,
			"--execution-providers", "cuda",
		]
		core.cli()
	except SystemExit as e:
		exit_code = e.code if isinstance(e.code, int) else 1
		if exit_code != 0:
			raise HTTPException(status_code=400, detail=f"job-run {job_id} failed")

	delete_old_files_and_folders(result_input_dir, 1)
	delete_old_files_and_folders(result_output_dir, 1)

	# 返回响应
	return JSONResponse({"errcode": 0, "errmsg": "ok", "output_path": output_path})


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--port', type=int, default=7864)
	args = parser.parse_args()

	try:
		uvicorn.run(app="api:app", host="0.0.0.0", port=args.port, workers=1, reload=False, log_level="info")
	except Exception as ex:
		TextProcessor.log_error(ex)
		print(ex)
		exit(0)
