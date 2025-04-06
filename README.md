# KnitVis

A Python toolkit for visualizing and designing double knitting patterns.

## Overview

KnitVis helps knitters design and visualize double knitting projects. It provides tools to:
- Create and manipulate knitting charts and canvases
- Visualize patterns as they would appear in the final knitted piece
- Track progress during the knitting process
- Convert between different pattern representations
- Support for colorwork in double knitting projects

## Installation

```bash
pip install knitvis
```

## Features

- **Double Knitting Canvas**: Create and manipulate binary patterns for double knitting projects
- **Knitting Chart Generation**: Convert patterns to knitting charts with symbols for knit and purl stitches
- **Colorwork Support**: Define custom color palettes for your projects
- **Progress Tracking**: Log your knitting progress with row and section tracking
- **Pattern Visualization**: See how your pattern will look when knitted
- **JSON Import/Export**: Save and load your patterns in JSON format

## Usage Examples

### Basic Usage

```python
import numpy as np
from knitvis import DoubleKnittingCanvas, KnittingChart

# Create a simple pattern
pattern = np.zeros((10, 10), dtype=bool)
pattern[2:8, 2:8] = True  # Create a square

# Create a canvas with colors
canvas = DoubleKnittingCanvas(pattern, front_color="blue", back_color="grey")

# Display the canvas
canvas.display()

# Get a knitting chart
chart = canvas.get_knitting_chart()

# Display the knitting pattern
canvas.display_knitting_pattern()
```

### Loading Patterns from JSON

```python
from knitvis import KnittingChart

# Load a chart from a JSON file
chart = KnittingChart.from_json("my_pattern.json")

# Do something with the chart
```

### Progress Tracking

```python
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(filename='knitting_log.txt', level=logging.INFO)

# Log your progress
row = 5
part = "left"
direction = "->"
log_message = f'{datetime.now()} - Rows {row} and {row+1}, {part} part {direction}'
logging.info(log_message)
```

## Documentation

For more detailed documentation and examples, see the sample notebooks in the project repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.