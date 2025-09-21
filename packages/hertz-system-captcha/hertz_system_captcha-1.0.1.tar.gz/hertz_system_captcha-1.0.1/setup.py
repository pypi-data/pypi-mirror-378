from setuptools import setup, find_packages
import os

# 读取README文件内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="hertz-system-captcha",  # PyPI上的包名
    version="1.0.1",  # 版本号
    author="yang kunhao",  # 作者名
    author_email="563161210@qq.com",  # 作者邮箱
    description="一个功能强大的Django验证码应用",  # 简短描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django",  # 项目地址
    packages=find_packages(),  # 自动发现所有包
    include_package_data=True,  # 包含MANIFEST.in中定义的文件
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",  # Python版本要求
    install_requires=read_requirements(),  # 依赖包
    keywords="django captcha verification security",  # 关键词
    project_urls={
        "Bug Reports": "http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django/issues",
        "Source": "http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django",
        "Documentation": "http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django#readme",
    },
)
