from setuptools import setup

setup(
    name="tasks-py",
    version="1.0.1",
    description="A simple and fast task queue for executing multiple tasks in parallel.",
    long_description=open('README.md').read(),
    author="Vivek Narayanan",
    author_email="vivek_n@me.com",
    url="https://github.com/vivekn/tasks",
    packages=["tasks"],
    keywords="redis, multiprocessing, task queue",
    install_requires=["redis", "eventlet"],
    licence="BSD")
