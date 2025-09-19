from setuptools import setup, find_packages

setup(
    name='warlock_waker',
    version='0.2.3',
    packages=find_packages(),
    install_requires=[
        # "redis==5.0.7",
        # "python-dotenv==1.0.1",
        # "loguru==0.7.2",
        # "pymongo==4.8.0",
        # "cachetools==5.3.3",
        # "PyMySQL==1.1.1",
        # "kafka-python==2.0.2",
        # "pytz==2023.3.post1",
        # "requests==2.28.1",
        # "avro==1.11.3",
        # "pandas==2.2.2",
        # "openpyxl==3.1.5",
        # "schedule==1.2.2",
        # "lxml==5.2.2",
        # "bs4==0.0.2",
        # "python-snappy==0.7.2",
        # "PyExecJS==1.5.1",
        # "curl-cffi==0.7.0",
        # "psutil==6.0.0",
        # "memory_profiler==0.61.0",
    ],
    author='zqyu14',
    author_email='zqyu14@iflytek.com',
    description='a log structure obj',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com',
    classifiers=[
        # 包的分类和许可证等信息
    ],
)