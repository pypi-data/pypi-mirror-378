#!/usr/bin/env bash

set -e

# Base directories
NOTEBOOKS_DIR="notebooks"
OUTPUT_BASE="docs/examples"

# Find all .ipynb files and convert them
find "$NOTEBOOKS_DIR" -name "*.ipynb" | while read -r notebook; do
    # Get relative path from notebooks dir
    rel_path="${notebook#$NOTEBOOKS_DIR/}"
    
    # Get directory part of the relative path
    dir_part=$(dirname "$rel_path")
    
    # Create output directory structure
    output_dir="$OUTPUT_BASE/$dir_part"
    mkdir -p "$output_dir"
    
    # Convert notebook
    echo "Converting: $notebook -> $output_dir"
    jupyter nbconvert --to html --output-dir "$output_dir" "$notebook"
done

echo "Conversion complete!"
