from setuptools import setup, find_packages

setup(
    name="Ctoolbox",  # 包名（必须唯一，PyPI上没被用过）
    version="0.0.1",        # 版本号（每次更新要改，比如0.0.2）
    packages=find_packages(),
    author="Jiaxiu Han",
    author_email="hanjx@baqis.ac.cn",
    description="Initial version for beginners",  # 简短描述
    classifiers=[  # 分类信息，帮助别人找到你的包
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 支持的Python版本
)