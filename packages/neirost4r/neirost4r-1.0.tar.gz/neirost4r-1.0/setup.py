# setup.py
from setuptools import setup, find_packages

setup(
    name="neirost4r",            # название пакета
    version="1.0",                  # версия
    author="FENST4R",                # автор
    author_email="ddejjcat@internet.ru",    # email автора
    description="Python client for fenst4r.life API",  # описание
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://fenst4r.life",       # ссылка на сайт/репозиторий
    packages=find_packages(),          # автоматически найдёт все пакеты
    install_requires=[
        "requests>=2.28.0"            # зависимость
    ],
    python_requires=">=3.8",          # минимальная версия Python
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
