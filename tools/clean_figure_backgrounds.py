#!/usr/bin/env python3
"""
clean_figure_backgrounds.py

A general-purpose utility script to remove off-white/grayish backgrounds from images 
and replace them with a specific target color (default: pure white). This is highly 
useful for making PDF screenshots blend seamlessly into academic posters or presentations.

Usage examples:
    python3 clean_figure_backgrounds.py img1.png img2.png
    python3 clean_figure_backgrounds.py img.png --threshold 230 --target-color 255,255,255
"""

import os
import sys
import argparse

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("Error: Required libraries not found. Please run: pip install Pillow numpy")
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="Clean image backgrounds by replacing near-white pixels with a target color.")
    parser.add_argument("images", nargs="+", help="Path(s) to the image files to process.")
    parser.add_argument("--threshold", type=int, default=240, 
                        help="RGB threshold above which pixels are considered 'background'. Default is 240.")
    parser.add_argument("--target-color", type=str, default="255,255,255", 
                        help="Target RGB color to replace the background with, formatted as R,G,B. Default is 255,255,255 (white).")
    parser.add_argument("--suffix", type=str, default="_clean",
                        help="Suffix to append to the cleaned image filename. Default is '_clean'.")
    return parser.parse_args()

def clean_background(input_path, output_path, threshold, target_rgb):
    try:
        img = Image.open(input_path).convert("RGBA")
        data = np.array(img)
        
        # Extract color channels
        r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
        
        # Identify background pixels based on threshold
        mask = (r > threshold) & (g > threshold) & (b > threshold)
        
        # Force these pixels to the target color and fully opaque
        tr, tg, tb = target_rgb
        data[mask, 0] = tr
        data[mask, 1] = tg
        data[mask, 2] = tb
        data[mask, 3] = 255 
        
        # Save as a clean RGB PNG without alpha channel issues
        clean_img = Image.fromarray(data).convert("RGB")
        clean_img.save(output_path, "PNG")
        print(f"[\u2713] Cleaned {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
        
    except Exception as e:
        print(f"[X] Failed to process {input_path}: {e}")

if __name__ == "__main__":
    args = parse_args()
    
    try:
        target_color = tuple(map(int, args.target_color.split(',')))
        if len(target_color) != 3:
            raise ValueError
    except ValueError:
        print("Error: --target-color must be three comma-separated integers (e.g., 255,255,255).")
        sys.exit(1)
        
    for file in args.images:
        if not os.path.exists(file):
            print(f"[X] File not found: {file}")
            continue
            
        base, ext = os.path.splitext(file)
        out_file = f"{base}{args.suffix}{ext}"
        clean_background(file, out_file, args.threshold, target_color)
