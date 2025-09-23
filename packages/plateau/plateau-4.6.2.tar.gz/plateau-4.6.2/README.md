# plateau

_flat files, flat land_

[![Build Status](https://github.com/data-engineering-collective/plateau/workflows/CI/badge.svg)](https://github.com/data-engineering-collective/plateau/actions?query=branch%3Amain)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/minimalkv?logoColor=white&logo=conda-forge)](https://prefix.dev/channels/conda-forge/packages/minimalkv)
[![pypi-version](https://img.shields.io/pypi/v/minimalkv.svg?logo=pypi&logoColor=white)](https://pypi.org/project/minimalkv)
[![python-version](https://img.shields.io/pypi/pyversions/minimalkv?logoColor=white&logo=python)](https://pypi.org/project/minimalkv)
[![Documentation Status](https://readthedocs.org/projects/plateau/badge/?version=stable)](https://plateau.readthedocs.io/en/stable/?badge=stable)
[![codecov.io](https://codecov.io/github/data-engineering-collective/plateau/coverage.svg?branch=master)](https://codecov.io/github/data-engineering-collective/plateau)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/data-engineering-collective/plateau/blob/master/LICENSE.txt)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/plateau/badges/downloads.svg)](https://anaconda.org/conda-forge/plateau)

`plateau` is a Python library to manage (create, read, update, delete) large
amounts of tabular data in a blob store. It stores data as datasets, which
it presents as pandas DataFrames to the user. Datasets are a collection of
files with the same schema that reside in a blob store. plateau uses a metadata
definition to handle these datasets efficiently. For distributed access and
manipulation of datasets plateau offers a [Dask](https://dask.org) interface.

Storing data distributed over multiple files in a blob store (S3, ABS, GCS,
etc.) allows for a fast, cost-efficient and highly scalable data infrastructure.
A downside of storing data solely in an object store is that the storages
themselves give little to no guarantees beyond the consistency of a single file.
In particular, they cannot guarantee the consistency of your dataset. If we
demand a consistent state of our dataset at all times, we need to track the
state of the dataset. plateau frees us from having to do this manually.

The `plateau.io` module provides building blocks to create and modify these
datasets in data pipelines. plateau handles I/O, tracks dataset partitions
and selects subsets of data transparently.

## Installation

This project is managed by [pixi](https://pixi.sh).
You can install the package in development mode using:

```bash
git clone https://github.com/data-engineering-collective/plateau
cd plateau

pixi run pre-commit-install
pixi run postinstall
pixi run test
```

Plateau is also [available on PyPI](http://pypi.python.org/pypi/plateau/) and
can be installed through `pip`:

```bash
pip install plateau
```

## Contributing

Find details on how to contribute [here](CONTRIBUTING.md).
