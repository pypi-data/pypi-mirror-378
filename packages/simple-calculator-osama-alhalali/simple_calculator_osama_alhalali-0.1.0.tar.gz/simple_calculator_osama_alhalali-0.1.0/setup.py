from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simple-calculator-osama-alhalali",
    version="0.1.0",
    author="اسامة الحللي",
    author_email="osama.alhalali@example.com", # يمكنك تغيير هذا البريد الإلكتروني لاحقًا
    description="حزمة آلة حاسبة بسيطة لعمليات الرياضيات الأساسية.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/osama-alhalali/simple-calculator", # يمكنك تغيير هذا الرابط لاحقًا
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


