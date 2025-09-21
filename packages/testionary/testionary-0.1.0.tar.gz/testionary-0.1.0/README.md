# Testionary

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A library providing tools to inspect dicionaries during testing. 

## Installation

Using pip:
```
pip install testionary
```
or using uv for project management:

```
uv add testionary
```

## Usage
```python
# My library code:
def set_danger(enemy):
    if enemy["type"] == "Rabbit":
        enemy["danger"] = 9000


# My test:
from testionary.basic import BasicTrackingDict

def test_set_danger():
    tracked_dict = BasicTrackingDict({"type": "Rabbit", "danger": 42})
    set_danger(tracked_dict)

    assert "type" in tracked_dict.accessed_keys
    assert "danger" in tracked_dict.modified_keys
```
