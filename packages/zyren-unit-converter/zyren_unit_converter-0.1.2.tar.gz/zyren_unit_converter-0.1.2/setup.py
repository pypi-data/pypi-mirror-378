from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='zyren-unit-converter',
    version='0.1.2',
    description='مكتبة لتحويل الوحدات (طول، وزن، حجم، حرارة، زمن)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Zyren_King',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.6',
)
