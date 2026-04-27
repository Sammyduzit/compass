import pytest

from compass.errors import SkeletonError
from compass.skeleton import render_skeletons


def test_render_skeletons_returns_structure_without_body(tmp_path):
	code = 'class Foo:\n    def bar(self):\n        return 42\n'
	f = tmp_path / 'foo.py'
	f.write_text(code)
	result = render_skeletons([str(tmp_path / 'foo.py')])

	assert 'class Foo:' in result[str(f)]
	assert 'return 42' not in result[str(f)]


def test_render_skeletons_skips_unknown_language(tmp_path):
	python_code = 'class Foo:\n    def bar(self):\n        return 42\n'
	txt_code = 'This is a paragraph from a text file.'
	python_file = tmp_path / 'foo.py'
	text_file = tmp_path / 'bar.txt'
	python_file.write_text(python_code)
	text_file.write_text(txt_code)
	result = render_skeletons([str(tmp_path / 'foo.py'), str(tmp_path / 'bar.txt')])

	assert 'class Foo:' in result[str(python_file)]
	assert 'return 42' not in result[str(python_file)]
	assert str(text_file) not in result


def test_render_skeletons_raises_when_all_files_unknown(tmp_path):
	txt_code = 'This is a paragraph from a text file.'
	text_file = tmp_path / 'bar.txt'
	text_file.write_text(txt_code)
	with pytest.raises(SkeletonError):
		render_skeletons([str(tmp_path / 'bar.txt')])


def test_render_skeletons_raises_on_missing_file():
	with pytest.raises(SkeletonError):
		render_skeletons(['/nonexistend/path/foo.py'])
