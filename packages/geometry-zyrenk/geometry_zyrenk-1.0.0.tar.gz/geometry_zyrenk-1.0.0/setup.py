from setuptools import setup, find_packages

setup(
    name="geometry_zyrenk",  # نفس الاسم الذي ستستورد به
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    author="Zyren_King",
    description="مكتبة شاملة لحساب المساحة والمحيط للأشكال الثنائية والثلاثية الأبعاد",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
