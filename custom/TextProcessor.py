import datetime
import os
import traceback

from custom.file_utils import logging


class TextProcessor:
	"""
	文本处理工具类，提供多种文本相关功能。
	"""

	@staticmethod
	def log_error(exception: Exception, log_dir='error'):
		"""
		记录错误信息到指定目录，并按日期小时命名文件。

		:param exception: 捕获的异常对象
		:param log_dir: 错误日志存储的目录，默认为 'error'
		"""
		# 确保日志目录存在
		os.makedirs(log_dir, exist_ok=True)
		# 获取当前日期和小时，作为日志文件名的一部分
		timestamp_hour = datetime.datetime.now().strftime('%Y-%m-%d_%H')  # 到小时
		# 获取当前时间戳，格式化为 YYYY-MM-DD_HH-MM-SS
		timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		# 创建日志文件路径
		log_file_path = os.path.join(log_dir, f'error_{timestamp_hour}.log')
		# 使用 traceback 模块获取详细的错误信息
		error_traceback = traceback.format_exc()
		# 写入错误信息到文件，使用追加模式 'a'
		with open(log_file_path, 'a') as log_file:
			log_file.write(f"错误发生时间: {timestamp}\n")
			log_file.write(f"错误信息: {str(exception)}\n")
			log_file.write("堆栈信息:\n")
			log_file.write(error_traceback + '\n')

		logging.info(f"发生错误: {str(exception)}\n错误信息已保存至: {log_file_path}")
