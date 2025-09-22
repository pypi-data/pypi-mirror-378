from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="koxs-color",
    version="0.1.1",
    author="koxs",
    author_email="2931209205@qq.com",  # 可以填一个邮箱
    description="一个实用的终端颜色工具包 - 代号koxs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    keywords="terminal, color, ansi, koxs, termux",
    url="https://github.com/yourusername/koxs-color",  # 如果有GitHub仓库
)