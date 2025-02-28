import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree


class KnittingColorPalette:
    """Stores RGB colors and assigns integer indices based on proximity to reference colors."""

    # Default knitting color names with short tags and reference RGB values
    REFERENCE_COLORS = {
        "White": ("W", (255, 255, 255)),
        "Black": ("B", (0, 0, 0)),
        "Gray": ("Gy", (128, 128, 128)),
        "Red": ("R", (255, 0, 0)),
        "Orange": ("O", (255, 165, 0)),
        "Yellow": ("Y", (255, 255, 0)),
        "Green": ("Gr", (0, 128, 0)),  # Prevents confusion with Gray
        "Blue": ("Bl", (0, 0, 255)),  # Ensures 'B' stays for Black
        "Navy": ("N", (0, 0, 128)),
        "Purple": ("P", (128, 0, 128)),
        "Pink": ("Pi", (255, 182, 193)),
        "Brown": ("Br", (165, 42, 42))
    }

    def __init__(self, colors):
        """
        Initializes the color palette and assigns indices based on proximity.
        :param colors: List of RGB tuples [(R, G, B), ...]
        """
        self.assigned_colors = np.array(
            colors, dtype=int)  # Store colors as NumPy matrix
        self.num_colors = len(colors)  # Track how many colors are assigned

        # Use KDTree to find the closest reference color for each input color
        ref_colors = np.array(
            [v[1] for v in self.REFERENCE_COLORS.values()], dtype=int)
        color_tree = KDTree(ref_colors)

        # Name mapping
        assigned_full_names = []
        assigned_short_tags = []
        name_counts = {}

        for color in colors:
            _, idx = color_tree.query(color)  # Find closest reference color
            base_name, short_tag = list(self.REFERENCE_COLORS.keys())[
                idx], list(self.REFERENCE_COLORS.values())[idx][0]

            # Track multiple shades using a counter
            if base_name in name_counts:
                name_counts[base_name] += 1
                full_name = f"{base_name}{name_counts[base_name]}"
                short_code = f"{short_tag}{name_counts[base_name]}"
            else:
                name_counts[base_name] = 1
                full_name = base_name
                short_code = short_tag

            assigned_full_names.append(full_name)
            assigned_short_tags.append(short_code)

        # Store structured data as NumPy arrays
        self.full_names = np.array(assigned_full_names)
        self.short_tags = np.array(assigned_short_tags)

    def get_index_by_color(self, color):
        """Returns the index of a given RGB color in the palette."""
        color = np.array(color, dtype=int)  # Ensure it's a NumPy array
        matches = np.where((self.assigned_colors == color).all(axis=1))[0]
        return int(matches[0]) if matches.size > 0 else None

    def get_color_by_index(self, index):
        """Returns the RGB value of a color given its assigned integer index."""
        if 0 <= index < self.num_colors:
            return tuple(self.assigned_colors[index].tolist())
        return None  # Invalid index

    def get_color_by_name(self, name):
        """Returns the RGB value given a full color name (e.g., 'White1')."""
        if name in self.full_names:
            idx = np.where(self.full_names == name)[0][0]
            return tuple(self.assigned_colors[idx].tolist())
        return None  # Color not found

    def get_color_by_tag(self, tag):
        """Returns the RGB value given a short tag (e.g., 'W1')."""
        if tag in self.short_tags:
            idx = np.where(self.short_tags == tag)[0][0]
            return tuple(self.assigned_colors[idx].tolist())
        return None  # Tag not found

    def display_palette(self):
        """Returns a Matplotlib figure displaying the assigned color palette."""
        fig, ax = plt.subplots(figsize=(self.num_colors * 0.8, 1.5))
        ax.set_xlim(0, self.num_colors)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])

        for i in range(self.num_colors):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=[
                         c / 255 for c in self.assigned_colors[i]], edgecolor="black"))
            ax.text(
                i + 0.5, -0.2, f"{self.short_tags[i]}", ha='center', va='center', fontsize=10, fontweight="bold")

        return fig  # Return figure instead of showing it

    def __str__(self):
        """Returns a formatted string representation of the color palette."""
        output_lines = []
        for i in range(self.num_colors):
            output_lines.append(
                f"{self.full_names[i]:<8} -> {self.short_tags[i]:<3} -> {tuple(self.assigned_colors[i].tolist())}")
        return "\n".join(output_lines)
