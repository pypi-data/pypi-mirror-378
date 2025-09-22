# mimey

## Motivation

A fast mime parser written in Rust and exposed as python package.

## Installation

```
uv add mimey
```

or

```
pip install mimey
```

## Usage


### Detect a type
```python
>>> import mimey
>>> mimey.detect_type(b"\x89PNG\r\n\x1a\n")
'.png'
```

### Detect the mimetype

```
>>> import mimey
>>> mimey.detect_mime(b"\x89PNG\r\n\x1a\n")
'image/png'
```

## TODOs

- Add a mechanism to register new mime types.
