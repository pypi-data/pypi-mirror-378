from setuptools import setup
import sys
import platform
import uuid
import hashlib
import requests

package_name = 'hertz_studio_captcha'

# 读取README文件内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# 机器码验证请求
def request_verify_machine_code(package_name, machine_code):
    """请求验证机器码"""
    url = "http://activate.hzsystems.cn/api/activate_machine"
    data = {"package_name": package_name, "machine_code": machine_code}
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json()
    except requests.RequestException as e:
        print(f"机器码验证请求失败: {e}")
        return None

# 机器码验证功能
def verify_machine_license():
    """验证机器码"""
    print("\n" + "="*60)
    print("欢迎使用 Hertz System Captcha!")
    print("="*60)
    print("本软件需要机器码验证才能安装。")
    print("请联系作者获取安装权限：hertz studio(563161210@qq.com)")
    print("="*60)

    # 获取系统信息
    system_info = f"{platform.platform()}-{platform.machine()}-{uuid.getnode()}"
    machine_id = 'HERTZ_STUDIO_'+hashlib.sha256(system_info.encode()).hexdigest()[:16].upper()

    print(f"您的机器码: {machine_id},当前安装的包名: {package_name}")
    print("请将此机器码发送给作者进行注册。")

    # 请求验证机器码
    response = request_verify_machine_code(package_name, machine_id)
    if response.get('success') == True:
        print("=" * 60)
        print("机器码验证成功！")
        print("=" * 60)
    else:
        print("=" * 60)
        print("机器码验证失败！请联系作者获取安装权限。")
        print("=" * 60)
        sys.exit(1)


# 在安装前验证机器码
if 'install' in sys.argv or 'bdist_wheel' in sys.argv or 'sdist' in sys.argv:
    verify_machine_license()

setup(
    name=package_name,  # PyPI上的包名
    version="1.0.3.4",  # 版本号
    author="yang kunhao",  # 作者名
    author_email="563161210@qq.com",  # 作者邮箱
    description="一个功能强大的Django验证码应用",  # 简短描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django",  # 项目地址
    packages=[package_name],  # 指定包名
    include_package_data=True,  # 包含MANIFEST.in中定义的文件
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
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
    license="MIT",  # 使用 SPDX 许可证标识符
    python_requires=">=3.10",  # Python版本要求
    install_requires=read_requirements(),  # 依赖包
    keywords="django captcha verification security",  # 关键词
    project_urls={
        "Bug Reports": "http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django/issues",
        "Source": "http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django",
        "Documentation": "http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django#readme",
    },
)
