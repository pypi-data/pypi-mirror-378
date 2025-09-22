from click.testing import CliRunner
from uncloud.cli import main

def test_cli_prints_help_and_exits():
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'Usage: Uncloud' in result.output