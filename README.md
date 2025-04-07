# KnitVis
![logo](image/README/logo.png)

A Python toolkit for visualizing and designing double knitting patterns.

## Overview

KnitVis helps knitters design and visualize double knitting projects. It provides tools to:
- Create and manipulate knitting charts and canvases
- Visualize patterns as they would appear in the final knitted piece
- Track progress during the knitting process
- Convert between different pattern representations
- Support for colorwork in double knitting projects

![preview](image/README/smile.png)

## Installation

```bash
pip install knitvis
```

## Features

- **Knitting Chart Generation**: Convert patterns to knitting charts with symbols for knit and purl stitches
- **Colorwork Support**: Define custom color palettes for your projects
- **Progress Tracking**: Log your knitting progress with row and section tracking
- **Pattern Visualization**: See how your pattern will look when knitted
- **JSON Import/Export**: Save and load your patterns in JSON format
- **GUI**: Powerful PyQt GUI with support of backgrounds and multiple editing modes
- **Double Knitting Canvas**: Create and manipulate binary patterns for double knitting projects

## Usage Examples

### Basic Usage

```python
"""
Basic KnitVis usage example: Heart pattern

This example demonstrates how to:
1. Create a simple knitted heart pattern
2. Define custom colors for the pattern
3. Render it as a realistic knitted fabric 
4. Also display the standard chart representation
"""

from knitvis.chart import KnittingChart
import numpy as np
import matplotlib.pyplot as plt

# Define a simple heart pattern using a boolean array
heart_colors = np.array([
    [0, 0, 0, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
], dtype=bool)

# Create a pattern with all knit stitches
pattern = np.zeros(heart_colors.shape, dtype=int)

# Define colors for the pattern
colors = np.zeros((*pattern.shape, 3), dtype=int)
colors.fill(180)  # Fill with gray (180,180,180)

# Set heart sections to red
for i in range(pattern.shape[0]):
    for j in range(pattern.shape[1]):
        if heart_colors[i, j]:
            colors[i, j] = [220, 50, 50]  # Red for heart

# Create the knitting chart with our pattern and colors
chart = KnittingChart(pattern, colors)

# Render the pattern as realistic knitted fabric
fig = chart.render_fabric()

# Also show the original chart representation
chart.display_chart()

# Show the visualizations
plt.show()
```

### Loading Patterns from JSON

```python
from knitvis import KnittingChart

# Load a chart from a JSON file
chart = KnittingChart.from_json("my_pattern.json")

# Do something with the chart
```

### GUI

```shell
python3 knitvis/gui/main.py
```

![gui](image/README/gui.png)

## Documentation

For more detailed documentation and examples, see the sample notebooks in the project repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.