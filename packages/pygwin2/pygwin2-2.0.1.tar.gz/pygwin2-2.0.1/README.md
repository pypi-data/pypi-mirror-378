# Pygwin2

A library for creating GUI-applications on pygame.

[Documentation](https://github.com/MeexReay/pygwin2/blob/main/docs/DOCS.md)

## Usage

Here is a small example of usage (pygame style):

```py
import pygwin2 as pgw

win = pgw.create('Title',(500,500))

run = True
while run:
    for event in pgw.getEvents():
        if event.type == pgw.QUIT:
            run = False

    win.update()
pgw.close()
```

## Installation

The easiest way is to just use pip:

```sh
pip install pygwin2
```
