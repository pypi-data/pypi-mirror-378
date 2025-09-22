# hexgraphics

aka 0xg


## installation

`pip install hexgraphics`


## usage

```python
from hexgraphics.constants import COLORMAP

print(COLORMAP)
```

```python
from hexgraphics import Image0xg

# 5x4 image
example = bytes([
    5, 4, # size
    0xe, 0xe, 0xe, 0xe, 0xa,
    0xe, 0xb, 0xe, 0xa, 0xa,
    0xe, 0xe, 0xe, 0xe, 0x1,
    0xa, 0xa, 0xa, 0xa, 0xa,
])

image = Image0xg(example)
# convert to .png
image.convert().save('image.png')
```
