"""
Basic KnitVis usage example: Heart pattern

This example demonstrates how to:
1. Create a simple knitted heart pattern
2. Define custom colors for the pattern
3. Render it as a realistic knitted fabric 
4. Also display the standard chart representation
"""

from knitvis.chart import KnittingChart
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Define a simple heart pattern using a boolean array
# (True/1 = heart area, False/0 = background)
heart_colors = np.array([
    [0, 0, 0, 0, 0, 0, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
], dtype=bool)

# Create a pattern with all knit stitches (represented by 0s)
# Currently, the fabric render only supports knit stitches
pattern = np.zeros(heart_colors.shape, dtype=int)

# Define colors for the pattern:
# - Background will be gray
# - Heart shape will be red
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

# Also show the original chart representation for comparison
fig2 = chart.display_chart()

# Add title to the fabric rendering
plt.figure(fig.number)

# Create output directory if needed
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

# Save both renderings
plt.savefig(os.path.join(output_dir, "heart_render.png"))

plt.figure(fig2.number)
plt.savefig(os.path.join(output_dir, "heart_chart.png"))

# Display the images
plt.show()
