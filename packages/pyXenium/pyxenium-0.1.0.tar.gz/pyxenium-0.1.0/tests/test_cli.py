from click.testing import CliRunner
from myxenium.__main__ import app

def test_demo():
    runner = CliRunner()
    result = runner.invoke(app, ['demo'])
    assert result.exit_code == 0
