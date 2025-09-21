from setuptools import setup, find_packages

setup(
    name="maksim_132",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "Pillow>=8.0.0",
    ],
    author="Maksim",
    author_email="your_email@example.com",
    description="Библиотека для создания скриншотов",
    keywords="screenshot image capture",
    python_requires=">=3.6",
)