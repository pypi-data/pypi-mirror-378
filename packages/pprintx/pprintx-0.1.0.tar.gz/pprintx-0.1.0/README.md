# pprintx

A styled console printer with C++ `cout`-like syntax, supporting colors, backgrounds, and text styles.

## Installation
```bash
pip install pprintx
```

## Usage
```python
from pprintx import pprint, color, style, end

pprint << color(2) << style("bold") << "Hello, World!" << end("")
```

## Features
- Foreground and background colors (0–15)
- Styles: bold, italic, underline, blink, reverse
- C++-style chaining with `<<`

## License
MIT
