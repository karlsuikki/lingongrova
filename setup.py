from setuptools import setup, find_packages

setup(
    name="lingongrova-bot",
    version="1.0.0",
    description="Bot for lingongrova bubble shooter game",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.40.0",
        "opencv-python>=4.8.1.78",
        "numpy>=1.24.3",
        "Pillow>=10.0.1",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
)