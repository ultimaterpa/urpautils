import pathlib
from setuptools import setup

here = pathlib.Path(__file__).parent
readme = (here / "README.md").read_text(encoding="utf-8")

about = {}
with open(here / "urpautils" / "__about__.py") as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    license=about["__license__"],
    keywords="Robotic Process Automation, RPA, UltimateRPA, utilities",
    packages_data={"urpautils": ["py.typed"]},
    packages=["urpautils"],
    install_requires=["urpatimeout", "holidays"],
    python_requires=">=3.7",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    include_package_data=True,
)
