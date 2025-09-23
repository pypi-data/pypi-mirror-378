from click.testing import CliRunner
from my_package.cli import hello

def test_hello_default():
    runner = CliRunner()
    result = runner.invoke(hello, [])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output
