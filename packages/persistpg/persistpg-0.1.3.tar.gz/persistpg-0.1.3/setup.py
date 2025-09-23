from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent
readme_path = here / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else "PersistPG: Redis-like key/value store on PostgreSQL and asyncpg."

setup(
    name="persistpg",
    version="0.1.3",
    description="A fast, Redis-like key/value store built on PostgreSQL and asyncpg.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests", "bench", "examples")),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "asyncpg>=0.29,<0.30",
    ],
    extras_require={
        "orjson": ["orjson>=3.10"],
    },
    license="MIT",
    keywords=[
        "postgresql",
        "redis",
        "key-value",
        "jsonb",
        "asyncio",
        "asyncpg",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries",
    ],
)