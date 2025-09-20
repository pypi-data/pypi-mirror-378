from setuptools import setup, find_packages

setup(
    name="razicube",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Razi Ramzi",
    description="مكتبة شاملة لحساب المساحة والمحيط للأشكال الثنائية والثلاثية الأبعاد",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)