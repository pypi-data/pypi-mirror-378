from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.md")
with codecs.open(readme_path, encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = "0.0.2"
DESCRIPTION = "Reason-based RAG for Early-Stage Developers for Community-based Prospecting (RE-STEP)"
LONG_DESCRIPTION = (
    "A GenAI prospecting tool for assessing community-based factors, "
    "aiming to assist early-stage developers in the renewable-energy industry."
)

setup(
    name="restep",
    version=VERSION,
    author="Charles Alba",
    author_email="alba@wustl.edu",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests",
        "PyPDF2",
        "python-docx",
        "langchain",
        "tqdm",
        "transformers",
        "torch",
        "accelerate",
        "safetensors",
        "sentencepiece",
        "bitsandbytes",
    ],
    keywords=[
        "Retrieval-augmented generation",
        "Renewable-energy prospecting technologies",
        "Built-environment decision-support systems",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
