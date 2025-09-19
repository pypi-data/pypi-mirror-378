# invertcolor

`invertcolor` is a lightweight Python library for inverting RGB color values. It makes it simple to generate the complementary color of any RGB input.

## Features

- Invert any RGB color tuple `(R, G, B)`
- Easy to use with a single function call
- Lightweight and dependency-free

## Installation

Install via PyPI:

```bash
pip install invertcolor
```

## Usage

The main function, invert_rgb_color, takes an RGB color tuple and returns its inverted color.
``` python
from invertcolor import invert_rgb_color

# Original color: red
red = (255, 0, 0)

# Inverted color: cyan
inverted_red = invert_rgb_color(red)

print(f"Inverted color: {inverted_red}")
# Output: (0, 255, 255)

# Another example: gray
gray = (128, 128, 128)
inverted_gray = invert_rgb_color(gray)
print(f"Inverted gray: {inverted_gray}")
# Output: (127, 127, 127)
```

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork the repository and submit a pull request. [Repository link](https://github.com/GeorgievIliyan/rgb_color_inverter)

## License

This project is licensed under the MIT License.