# fileslicer

[![PyPI - Version](https://img.shields.io/pypi/v/fileslicer.svg)](https://pypi.org/project/fileslicer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fileslicer.svg)](https://pypi.org/project/fileslicer)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/FlavioAmurrioCS/fileslicer/main.svg)](https://results.pre-commit.ci/latest/github/FlavioAmurrioCS/fileslicer/main)

-----

**fileslicer** is a lightweight Python library for efficiently reading and splitting large files using memory mapping. It allows you to iterate over lines within a file slice and split files into chunks without loading the entire file into memory, making it ideal for processing very large files.

---

## Features

- Memory-efficient line iteration using `mmap`.
- Split large files into chunks while respecting newline boundaries.
- Simple and Pythonic API.
- Works with files of arbitrary size.

---

## Installation

Install via pip:

```bash
pip install fileslicer
````

---

## Usage

### Basic Example: Iterate over a file

```python
from fileslicer import FileSlice

# Create a FileSlice for an entire file
slice = FileSlice.from_file("large_file.txt")

# Iterate over lines in the slice
for line in slice.iter_lines():
    print(line.decode().strip())
```

### Split a File into Chunks

```python
from fileslicer import FileSlice

# Split a file into 4 chunks
chunks = FileSlice.split_file("large_file.txt", splits=4)

for chunk in chunks:
    print(f"Processing bytes {chunk.start_offset}-{chunk.end_offset}")
    for line in chunk.iter_lines():
        print(line.decode().strip())
```

### Create a Custom File Slice

```python
from fileslicer import FileSlice

# Only read bytes 1000 to 5000
slice = FileSlice("large_file.txt", 1000, 5000)

for line in slice.iter_lines():
    print(line.decode().strip())
```

---

## API

### `FileSlice`

* `FileSlice(file_path: str, start_offset: int, end_offset: int)`: Represents a slice of a file.

* `iter_lines() -> Generator[bytes]`: Iterate over lines in the file slice as bytes.

* `@staticmethod from_file(file_path: str) -> FileSlice`: Create a `FileSlice` covering the entire file.

* `@staticmethod split_file(file_path: str, splits: int) -> list[FileSlice]`: Split a file into multiple slices, aligned to newline boundaries.

---

## Why Use fileslicer?

Processing extremely large files with standard file reading can be slow and memory-intensive. **fileslicer** uses memory mapping to efficiently slice and iterate over file data without reading everything into memory. Inspired by the "1 Billion Row Challenge" in Python, it is perfect for data processing pipelines, log analysis, and ETL tasks.

---

## License

`fileslicer` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
