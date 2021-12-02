from setuptools import setup
from pathlib import Path

THIS_DIR = Path(__file__).parent
PROJECT_ROOT = THIS_DIR
REQUIREMENTS_TXT_FPATH = PROJECT_ROOT / "requirements.txt"

def load_install_requires():
    requirements_txt: str = REQUIREMENTS_TXT_FPATH.read_text().strip()
    requirements = requirements_txt.splitlines()
    return requirements

if __name__ == "__main__":
    setup(
        install_requires=load_install_requires()
    )