from setuptools import setup, find_packages

setup(
    name="gesture-blocks",
    version="0.1.0",
    description="Block-style gesture control for Arduino + Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    url="https://github.com/yourusername/gesture-blocks",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "mediapipe",
        "pyserial"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
