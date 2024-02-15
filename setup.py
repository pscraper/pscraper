from setuptools import find_packages, setup

setup(
    name = "pscraper",      # pip이 참조하는 이름
    author = "seungsu hwang",
    author_email = "sshwang.intern@ahnlab.com",
    version = "0.1.1",
    entry_point = {
        "console-scripts": ["pscraper=src.pscraper:run"]
    },
    packages = find_packages(where = "src.*")
)