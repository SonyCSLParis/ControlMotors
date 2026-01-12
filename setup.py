from setuptools import setup, find_packages


install_requires = [
    'pyserial',
    'argparse',
    'numpy'
]


setup(
    name="ContolMotors",
    version="0.0.1",
    description="Control motors via Arduino-Python serial interface",
    author="Peter Hanappe, Ali Ruyer-Thompson, Aliénor Lahlou",
    author_email="peter@hanappe.com",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.7",
    license="GPLv3",
)