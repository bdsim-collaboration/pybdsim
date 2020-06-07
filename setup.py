from setuptools import setup, find_packages

setup(
    name='pybdsim',
    version='2.2.0',
    packages=find_packages(exclude=["docs", "tests", "obsolete"]),
    # Not sure how strict these need to be...
    install_requires=["future",
                      "matplotlib",
                      "numpy",
                      "scipy",
                      "fortranformat",
                      "pymadx",
                      "pymad8",
                      "pytransport"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    python_requires=">=2.7.*",

    author='JAI@RHUL',
    author_email='laurie.nevay@rhul.ac.uk',
    description=("Python utilities for the Monte Carlo Particle accelerator code BDSIM."),
    license="GPL3",
    url='https://bitbucket.org/jairhul/pybdsim/'
)
