import os
import tempfile

from facefusion.filesystem import create_directory, is_directory, is_file, remove_directory
from facefusion.temp_helper import get_base_directory_path
from facefusion.typing import JobStatus


def is_test_job_file(file_path: str, job_status: JobStatus) -> bool:
	return is_file(get_test_job_file(file_path, job_status))


def get_test_job_file(file_path: str, job_status: JobStatus) -> str:
	return os.path.join(get_test_jobs_directory(), job_status, file_path)


def get_test_jobs_directory() -> str:
	return os.path.join(tempfile.gettempdir(), 'facefusion-test-jobs')


def get_test_example_file(file_path: str) -> str:
	return os.path.join(get_test_examples_directory(), file_path)


def get_test_examples_directory() -> str:
	return os.path.join(tempfile.gettempdir(), 'facefusion-test-examples')


def is_test_output_file(file_path: str) -> bool:
	return is_file(get_test_output_file(file_path))


def get_test_output_file(file_path: str) -> str:
	return os.path.join(get_test_outputs_directory(), file_path)


def get_test_outputs_directory() -> str:
	return os.path.join(tempfile.gettempdir(), 'facefusion-test-outputs')


def prepare_test_output_directory() -> bool:
	test_outputs_directory = get_test_outputs_directory()
	remove_directory(test_outputs_directory)
	create_directory(test_outputs_directory)
	return is_directory(test_outputs_directory)


def get_jobs_directory() -> str:
	return os.path.join(get_base_directory_path(), 'test-jobs')


def get_input_file(file_path: str) -> str:
	return os.path.join(get_input_directory(), file_path)


def get_input_directory() -> str:
	return os.path.join(get_base_directory_path(), 'input')


def is_output_file(file_path: str) -> bool:
	return is_file(get_output_file(file_path))


def get_output_file(file_path: str) -> str:
	return os.path.join(get_output_directory(), file_path)


def get_output_directory() -> str:
	return os.path.join(get_base_directory_path(), 'output')


def prepare_output_directory() -> bool:
	output_directory = get_output_directory()
	remove_directory(output_directory)
	create_directory(output_directory)
	return is_directory(output_directory)
