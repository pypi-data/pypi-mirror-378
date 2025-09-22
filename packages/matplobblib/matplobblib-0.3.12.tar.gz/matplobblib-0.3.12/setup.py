from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r', encoding='utf-8') as f:
    return f.read()

with open('version.txt','r') as f:
    version = f.read().strip()


setup(
    name='matplobblib',
    version=version,
    packages=find_packages(),
    description='Just a library for some subjects',
    author='Ackrome',
    author_email='ivansergeyevicht@gmail.com',
    url='https://github.com/Ackrome/matplobblib',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in or package_data
    # spackage_data=package_data,
    install_requires=[
        "numpy",
        "sympy",
        "pandas",
        "scipy",
        "pyperclip",
        "PyMuPDF",
        "graphviz",
        "statsmodels",
        "fitz",
        "cvxopt",
        "beautifulsoup4",
        "matplotlib",
        "numba",
        "tools",
        "frontend",
        "IPython",
        "tqdm",
        "scikit-learn",
        "scikit-image"
    ],
    license='MIT'
)
