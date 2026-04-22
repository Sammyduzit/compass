import pytest

from compass.errors import TemplateNotFoundError
from compass.prompts.loader import load_template


def test_extract_rules_python_contains_shared_and_language():
	result = load_template('extract_rules', 'python')
	assert '# Rules Extraction Prompt' in result
	assert 'Python' in result
	assert 'LANGUAGE' not in result


def test_extract_rules_typescript():
	result = load_template('extract_rules', 'typescript')
	assert '# Rules Extraction Prompt' in result
	assert 'TypeScript' in result
	assert 'LANGUAGE' not in result


def test_extract_rules_generic():
	result = load_template('extract_rules', 'generic')
	assert '# Rules Extraction Prompt' in result
	assert 'LANGUAGE' not in result


def test_extract_rules_unknown_lang_falls_back_to_generic():
	generic = load_template('extract_rules', 'generic')
	unknown = load_template('extract_rules', 'rust')
	assert generic == unknown


def test_summary_python():
	result = load_template('summary', 'python')
	assert 'Python' in result
	assert 'LANGUAGE' not in result


def test_summary_typescript():
	result = load_template('summary', 'typescript')
	assert 'TypeScript' in result
	assert 'LANGUAGE' not in result


def test_summary_unknown_lang_falls_back_to_generic():
	generic = load_template('summary', 'generic')
	unknown = load_template('summary', 'go')
	assert generic == unknown


def test_reconciliation_returned_as_is():
	result = load_template('reconciliation', 'python')
	assert len(result) > 0
	assert 'LANGUAGE' not in result


def test_reconciliation_same_regardless_of_lang():
	assert load_template('reconciliation', 'python') == load_template('reconciliation', 'typescript')


def test_unknown_template_raises():
	with pytest.raises(TemplateNotFoundError, match="'nonexistent'"):
		load_template('nonexistent', 'python')


def test_metadata_comment_stripped():
	for tmpl in ('extract_rules', 'summary', 'reconciliation'):
		result = load_template(tmpl, 'python')
		assert not result.startswith('<!--')
