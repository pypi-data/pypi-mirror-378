from setuptools import setup, find_packages

setup(
    name="hedayat_media",  # نام پکیج
    version="1.0.0",       # نسخه پکیج
    author="امیرحسین خزاعی",
    author_email="amirhossein@example.com",
    description="یک کتابخانه جامع برای دسترسی به احادیث، قرآن، ذکر و اطلاعات جغرافیایی مساجد",
    long_description=open("README.md", encoding="utf-8").read(),  # توضیحات کامل از فایل README
    long_description_content_type="text/markdown",
    url="https://github.com/amirhossinpython/hedayat_media",  # لینک پروژه (اختیاری)
    packages=find_packages(),  # پیدا کردن خودکار تمام پکیج‌ها
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "deep-translator>=1.8.1",
        "geopy>=2.3.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
