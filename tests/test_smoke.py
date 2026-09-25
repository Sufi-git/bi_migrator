from pathlib import Path


def test_project_structure():
    assert Path("app.py").exists()
    assert Path("src/bi_migrator").exists()
    assert Path("src/bi_migrator/tableau").exists()
