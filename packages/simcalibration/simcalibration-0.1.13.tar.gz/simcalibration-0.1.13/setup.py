from setuptools import setup, find_packages

setup(
    name="simcalibration",
    version="0.1.13",
    description="Simulation Calibration framework",
    author="Mostafa Alwash",
    author_email="malwash@gmail.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.20.2",
        "pandas>=1.5.3",
        "igraph==0.11.6",
        "scikit-learn==1.3.2",
        "scipy>=1.6.2",
        "graphviz>=0.20.3",
        "seaborn>=0.11.2",
        "tabulate>=0.8.9",
        "matplotlib~=3.5.1",
        "dagsim~=1.0.6",
        "bnlearn==0.8.2",
        "statsmodels~=0.13.2",
        "rpy2==3.4.5; platform_system != 'Windows'",
    ],
    extras_require={
        "dev": [
            "ipython>=7.27.0",
            "pytest>=7",
            "pytest-cov",
            "ruff",
            "black",
            "build",
            "twine",
        ]
    },
    entry_points={
        "console_scripts": [
            "simcalibration=simcalibration.main:main",
        ],
    },
)
