import pytest
from unittest.mock import patch
from compass.collectors.docs_reader import DocsReaderCollector
from compass.errors import CollectorError


async def test_docs_reader_finds_contributing(tmp_path):
	contributing = tmp_path / 'CONTRIBUTING.md'
	contributing.write_text('# Contributing')

	collector = DocsReaderCollector()
	result = await collector.collect(tmp_path)

	assert result['CONTRIBUTING.md'] == '# Contributing'


async def test_docs_reader_raises_on_read_error(tmp_path):
	contributing = tmp_path / 'CONTRIBUTING.md'
	contributing.write_text('# Contributing')

	with patch.object(
		contributing.__class__, 'read_text', side_effect=OSError('permission denied')
	):
		collector = DocsReaderCollector()
		with pytest.raises(CollectorError):
			await collector.collect(tmp_path)
