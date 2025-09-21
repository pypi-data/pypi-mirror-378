from setuptools import setup, find_packages
import os
import sys
import hashlib
import getpass

# 读取README文件内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# 激活码验证功能
def verify_license_key():
    """验证激活码"""
    try:
        from license_validator import license_validator
    except ImportError:
        # 如果无法导入验证器，使用简单的离线验证
        valid_keys = [
            "HERTZ-CAPTCHA-2024-ABCD1234",
            "HERTZ-CAPTCHA-2024-EFGH5678", 
            "HERTZ-CAPTCHA-2024-IJKL9012",
            "HERTZ-CAPTCHA-2024-MNOP3456",
            "HERTZ-CAPTCHA-2024-QRST7890"
        ]
        
        # 从环境变量获取激活码
        license_key = os.environ.get('HERTZ_CAPTCHA_LICENSE')
        
        # 如果环境变量没有，则提示用户输入
        if not license_key:
            print("\n" + "="*60)
            print("欢迎使用 Hertz System Captcha!")
            print("="*60)
            print("本软件需要有效的激活码才能安装。")
            print("请联系作者获取激活码：yang kunhao (563161210@qq.com)")
            print("="*60)
            
            try:
                license_key = getpass.getpass("请输入您的激活码: ").strip()
            except KeyboardInterrupt:
                print("\n安装已取消。")
                sys.exit(1)
        
        # 验证激活码
        if license_key not in valid_keys:
            print("\n❌ 激活码无效！")
            print("请检查激活码是否正确，或联系作者获取新的激活码。")
            print("作者邮箱：563161210@qq.com")
            sys.exit(1)
        
        print("✅ 激活码验证成功！")
        return True
    
    # 使用高级验证器
    license_key = os.environ.get('HERTZ_CAPTCHA_LICENSE')
    
    # 如果环境变量没有，则提示用户输入
    if not license_key:
        print("\n" + "="*60)
        print("欢迎使用 Hertz System Captcha!")
        print("="*60)
        print("本软件需要有效的激活码才能安装。")
        print("请联系作者获取激活码：yang kunhao (563161210@qq.com)")
        print("="*60)
        
        try:
            license_key = getpass.getpass("请输入您的激活码: ").strip()
        except KeyboardInterrupt:
            print("\n安装已取消。")
            sys.exit(1)
    
    # 验证激活码
    is_valid, message = license_validator.verify_license(license_key)
    
    if not is_valid:
        print(f"\n❌ 激活码验证失败: {message}")
        print("请检查激活码是否正确，或联系作者获取新的激活码。")
        print("作者邮箱：563161210@qq.com")
        sys.exit(1)
    
    # 检查激活码是否过期
    is_not_expired, expiry_message = license_validator.check_license_expiry(license_key)
    if not is_not_expired:
        print(f"\n❌ 激活码已过期: {expiry_message}")
        print("请联系作者获取新的激活码。")
        print("作者邮箱：563161210@qq.com")
        sys.exit(1)
    
    print(f"✅ 激活码验证成功！{message}")
    return True

# 在安装前验证激活码
if 'install' in sys.argv or 'bdist_wheel' in sys.argv :
    verify_license_key()

setup(
    name="hertz-system-captcha",  # PyPI上的包名
    version="1.0.3.1",  # 版本号
    author="yang kunhao",  # 作者名
    author_email="563161210@qq.com",  # 作者邮箱
    description="一个功能强大的Django验证码应用",  # 简短描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django",  # 项目地址
    packages=['hertz_system_captcha'],  # 指定包名
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
