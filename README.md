[![Build Status][ci-badge]][ci-link]
[![Coverage Status][cov-badge]][cov-link]
[![Docs status][docs-badge]][docs-link]
[![PyPI version][pypi-badge]][pypi-link]

# aiida-skeaf

AiiDA plugin for the Supercell K-space Extremal Area Finder (SKEAF) code.

## Installation

```shell
pip install aiida-skeaf
verdi quicksetup  # better to set up a new profile
verdi plugin list aiida.calculations  # should now show your calclulation plugins
```


## Usage

Here goes a [complete example](examples/run_skeaf.py) of how to submit a test calculation using this plugin.

A quick demo of how to submit a calculation:
```shell
verdi daemon start     # make sure the daemon is running
cd examples
./run_skeaf.py         # run test calculation
verdi process list -a  # check record of calculation
```

## Development

```shell
git clone https://github.com/qiaojunfeng/aiida-skeaf .
cd aiida-skeaf
pip install flit
flit install -s .[pre-commit,testing]  # install extra dependencies
pre-commit install  # install pre-commit hooks
pytest -v  # discover and run all tests
```

See the [developer guide](http://aiida-skeaf.readthedocs.io/en/latest/developer_guide/index.html) for more information.

## License

MIT
## Contact

qiaojunfeng@outlook.com


[ci-badge]: https://github.com/qiaojunfeng/aiida-skeaf/workflows/ci/badge.svg?branch=master
[ci-link]: https://github.com/qiaojunfeng/aiida-skeaf/actions
[cov-badge]: https://coveralls.io/repos/github/qiaojunfeng/aiida-skeaf/badge.svg?branch=master
[cov-link]: https://coveralls.io/github/qiaojunfeng/aiida-skeaf?branch=master
[docs-badge]: https://readthedocs.org/projects/aiida-skeaf/badge
[docs-link]: http://aiida-skeaf.readthedocs.io/
[pypi-badge]: https://badge.fury.io/py/aiida-skeaf.svg
[pypi-link]: https://badge.fury.io/py/aiida-skeaf
