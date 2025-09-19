# Instructions to Building the Package

```bash
pip install build twine
python -m build
# confirm you have pypi token configured.
cat ~/.pypirc
twine upload dist/*
```
