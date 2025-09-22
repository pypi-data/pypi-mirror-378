"""
ملف إعداد الحزمة لـ PyPI
"""

from setuptools import setup, find_packages
import pathlib

# قراءة محتوى ملف README
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="faisal_salahi_calculator",
    version="0.1.0",
    author="فيصل الصلاحي",
    author_email="contact@faisalsalahi.com",
    description="آلة حاسبة بسيطة لإجراء العمليات الحسابية الأساسية",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/faisalsalahi/faisal-salahi-calculator",
    project_urls={
        "Bug Reports": "https://github.com/faisalsalahi/faisal-salahi-calculator/issues",
        "Source": "https://github.com/faisalsalahi/faisal-salahi-calculator",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="calculator math arithmetic حاسبة رياضيات",
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    package_data={
        "faisal_salahi_calculator": ["*.md", "*.txt"],
    },
    entry_points={
        "console_scripts": [],
    },
)
