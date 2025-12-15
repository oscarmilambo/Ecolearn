#!/usr/bin/env python
"""
Optimized startup script for Render free tier
"""
import os
import gc
import sys

def optimize_for_render():
    """Optimize Python settings for Render's memory constraints"""
    
    # Force garbage collection
    gc.collect()
    
    # Set Python optimization flags
    os.environ['PYTHONOPTIMIZE'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Reduce Python's memory usage
    if hasattr(sys, 'setswitchinterval'):
        sys.setswitchinterval(0.005)  # Reduce thread switching overhead
    
    print("🚀 Python optimized for Render deployment")

if __name__ == '__main__':
    optimize_for_render()