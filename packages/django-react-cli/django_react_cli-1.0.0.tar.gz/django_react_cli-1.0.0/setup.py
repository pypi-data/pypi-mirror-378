from setuptools import setup, find_packages

setup(
    name="django-react-cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "django-react-cli=django_react_cli.cli:main"
        ]
    },
    author="code530pro",
    author_email="hugo39452@gmail.com",
    description="A starter template for building full-stack web applications using Django (backend), React (frontend), and TailwindCSS. Comes pre-configured with REST API support, authentication, and ready-to-use development and production settings.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
