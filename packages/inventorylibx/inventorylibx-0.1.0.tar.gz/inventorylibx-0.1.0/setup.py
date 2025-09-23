from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description (fallback if missing)
readme_path = Path(__file__).parent / "README.md"
long_desc = (
    readme_path.read_text(encoding="utf-8")
    if readme_path.exists()
    else "Inventory management library providing EOQ, ROP, Safety Stock, Total Cost, and Bulk-Discount EOQ."
)

setup(
    name="inventorylibx",  # Make sure this name is unique on PyPI
    version="0.1.0",      # Follow semantic versioning: MAJOR.MINOR.PATCH
    author="Avni Gupta, Samruddhi Jain, Pranav Mantri",
    author_email="guptavni001@gmail.com",  # Main contact email
    description="A Python library for solving Operations Research-based Inventory Management problems.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/avnigupta01/inventorylib",  # GitHub repo
    license="MIT",  # Matches your LICENSE file
    packages=find_packages(include=["inventorylib", "inventorylib.*"]),
    install_requires=[],  # Add dependencies here if needed
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="inventory management eoq rop safety-stock or operations-research",
    project_urls={
        "Source": "https://github.com/avnigupta01/inventorylib",
        "Bug Reports": "https://github.com/avnigupta01/inventorylib/issues",
    },
)
