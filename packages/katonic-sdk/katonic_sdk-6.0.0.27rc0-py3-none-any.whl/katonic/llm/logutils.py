#!/usr/bin/env python
# Script            : Main script for model deployment
# Component         : GenAi model deployment
# Author            : Vinay Namani & Bijoy Kumar Roy
# Copyright (c)     : 2024 Katonic Pty Ltd. All rights reserved.

import sys
import traceback
from pathlib import Path

def handle_exception():
    """
    Handle exceptions with comprehensive error handling
    
    Returns:
        str: Formatted error message
    """
    try:
        error_traceback = traceback.format_exc()
        if not error_traceback:
            return "An unknown error occurred."
            
        traceback_lines = error_traceback.splitlines()
        if not traceback_lines:
            return "An error occurred but no traceback available."
            
        # Get the last line which typically contains the actual error
        error_traceback = traceback_lines[-1]
        error_message = "An error occurred. Traceback:\n" + error_traceback
        return str(error_message)
        
    except Exception as e:
        # Fallback error message if traceback handling fails
        return f"Error in exception handling: {str(e)}"