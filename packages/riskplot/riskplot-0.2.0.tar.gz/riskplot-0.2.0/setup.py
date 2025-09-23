from setuptools import setup, find_packages

setup(
    name="riskplot",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    packages=find_packages(),
    python_requires=">=3.8",
)