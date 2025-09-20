from setuptools import setup, find_packages

setup(
    name="dolphins",
    version="0.1.0",
    author="Δrj★n",
    packages=find_packages(),
    package_data={
        'dolphins': ['data/*.csv'],  
    },
    include_package_data=True,
    description="The thrill isn’t in winning—it’s in bending the system without leaving a mark.",
    python_requires=">=3.6",
)