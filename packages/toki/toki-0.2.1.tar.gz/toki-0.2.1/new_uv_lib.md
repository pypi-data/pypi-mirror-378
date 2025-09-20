# How to spin up a new UV library

Make a new folder
```bash
uv init --lib mylib
cd mylib
```

Or make inside an existing folder
```bash
cd mylib
uv init --lib
```

Adjust the structure to be flatter (match poetry)
```bash
mv src/mylib mylib
```
Add the following line to `pyproject.toml`
```toml
[tool.hatch.build.targets.wheel]
packages = ["toki"]
```