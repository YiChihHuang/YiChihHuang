"""
Cursor Image Generator
======================

Automatically generates a cursor image if not found.
Creates a simple arrow cursor using PIL.
"""

from pathlib import Path

from PIL import Image, ImageDraw


def generate_cursor_image(
    output_path: Path,
    size: int = 32,
    color: str = "#000000",
    outline_color: str = "#FFFFFF",
) -> Path:
    """
    Generate a simple arrow cursor image.

    Args:
        output_path: Path to save the cursor image
        size: Size of the cursor in pixels
        color: Fill color (hex)
        outline_color: Outline color (hex)

    Returns:
        Path to the generated image
    """
    # Create transparent image
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Arrow cursor points (classic Windows-style arrow)
    # Normalized to 0-1 range, then scaled to size
    arrow_points = [
        (0.0, 0.0),      # Top point
        (0.0, 0.75),     # Left side bottom
        (0.20, 0.55),    # Inner corner left
        (0.35, 0.90),    # Bottom left of stem
        (0.50, 0.85),    # Bottom right of stem
        (0.35, 0.50),    # Inner corner right
        (0.55, 0.50),    # Right wing
    ]

    # Scale points to image size
    scaled_points = [
        (int(x * size * 0.9) + 1, int(y * size * 0.9) + 1)
        for x, y in arrow_points
    ]

    # Draw outline (slightly larger)
    outline_points = [
        (int(x * size * 0.9) + 1, int(y * size * 0.9) + 1)
        for x, y in arrow_points
    ]
    draw.polygon(outline_points, fill=outline_color, outline=outline_color)

    # Draw fill (main arrow)
    # Slightly inset for the fill
    fill_offset = 1
    fill_points = [
        (x + fill_offset, y + fill_offset)
        for x, y in scaled_points
    ]
    fill_points = [
        (max(0, min(size - 1, x)), max(0, min(size - 1, y)))
        for x, y in fill_points
    ]

    # Redraw at original scale
    draw.polygon(scaled_points, fill=color, outline=outline_color)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save with transparency
    img.save(output_path, "PNG")

    return output_path


def ensure_cursor_image(
    assets_dir: Path,
    filename: str = "cursor.png",
    size: int = 32,
) -> Path:
    """
    Ensure a cursor image exists, generating one if needed.

    Args:
        assets_dir: Directory for assets
        filename: Cursor filename
        size: Cursor size in pixels

    Returns:
        Path to the cursor image
    """
    cursor_path = assets_dir / filename

    if cursor_path.exists():
        return cursor_path

    # Generate cursor
    from rich.console import Console
    console = Console()
    console.print(f"[yellow]Cursor image not found. Generating: {cursor_path}[/yellow]")

    return generate_cursor_image(cursor_path, size=size)


def create_enhanced_cursor(
    output_path: Path,
    size: int = 48,
    style: str = "modern",
) -> Path:
    """
    Create an enhanced cursor with more detail.

    Args:
        output_path: Path to save the cursor
        size: Size in pixels
        style: Cursor style ("modern", "classic", "minimal")

    Returns:
        Path to the generated image
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if style == "modern":
        # Modern style with gradient-like effect
        points = [
            (0, 0),
            (0, int(size * 0.8)),
            (int(size * 0.2), int(size * 0.6)),
            (int(size * 0.4), int(size * 0.95)),
            (int(size * 0.55), int(size * 0.85)),
            (int(size * 0.4), int(size * 0.55)),
            (int(size * 0.6), int(size * 0.55)),
        ]

        # Shadow
        shadow_offset = 2
        shadow_points = [(x + shadow_offset, y + shadow_offset) for x, y in points]
        draw.polygon(shadow_points, fill=(0, 0, 0, 80))

        # Main cursor
        draw.polygon(points, fill="#2B579A", outline="#FFFFFF")

        # Highlight
        highlight_points = [
            (2, 2),
            (2, int(size * 0.3)),
            (int(size * 0.15), int(size * 0.3)),
        ]
        draw.polygon(highlight_points, fill=(255, 255, 255, 100))

    elif style == "classic":
        # Classic Windows-style
        points = [
            (0, 0),
            (0, int(size * 0.75)),
            (int(size * 0.18), int(size * 0.58)),
            (int(size * 0.33), int(size * 0.92)),
            (int(size * 0.48), int(size * 0.84)),
            (int(size * 0.35), int(size * 0.52)),
            (int(size * 0.55), int(size * 0.52)),
        ]
        draw.polygon(points, fill="#FFFFFF", outline="#000000")

    else:  # minimal
        # Minimal dot cursor
        center = size // 2
        radius = size // 4
        draw.ellipse(
            [center - radius, center - radius, center + radius, center + radius],
            fill="#FF4444",
            outline="#FFFFFF",
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")

    return output_path
