## Update the version number in setup.py or pyproject.toml. Example:

version="0.1.1"  # increment from 0.1.0


## Rebuild the package:
```
python setup.py sdist bdist_wheel
```

## Upload the new version to PyPI:
```
twine upload dist/*
```


## Install the new version in your nodes:

```
pip install --upgrade tracker-utils-tl
```

## Token --> 
```
pypi-AgEIcHlwaS5vcmcCJDY0ZDc3MDJhLWRlMTItNDgxNy1iN2RiLTNjYWY4NmFkNjc1NgACKlszLCI2NzQyMjRjZi05ZjFhLTQwNmEtYWU5Mi1kYmY4NzU0OTM2MGEiXQAABiDYHFAyGPe2mBswKa0-t6Z4s_gXtsB50eDGamfchkNWag
```