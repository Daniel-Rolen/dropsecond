# The Binder

A Python-based desktop application for PDF compilation with local file handling and a fun, user-friendly interface.

## Features

- PDF Compilation: Combine multiple PDF files into a single document.
- Page Selection: Choose specific pages from each PDF to include in the final compilation.
- Cover Page Settings: Add custom cover pages to your compiled PDF.
- Fun Naming: Automatically generate unique, space-themed names for output files.
- Report Saving and Loading: Save your compilation settings as reports and load them later.
- User-Friendly GUI: Colorful and intuitive interface for easy navigation and use.

## Known Issues

1. The Flask application shows a warning about being a development server, which is expected and not an issue for our current development work.
2. The Electron app is currently failing to start due to a missing shared library (libxshmfence.so.1).
3. Unable to select specific PDFs from "The Binder's Cosmic Collection" list to modify page numbers or ranges.
4. The "Remove PDF" button functionality is inconsistent.
5. Some features are still not fully implemented, such as actual PDF compilation and file handling.
6. Need to implement functionality to add a cover page with new page numbers and a cover letter to the final compiled PDF.
7. Space in file names may cause issues with PDF compilation and handling.
8. ModuleNotFoundError: No module named 'frontend' when running main.py. This might be due to a missing or incorrectly installed dependency.
9. ModuleNotFoundError: No module named '_tkinter' when running main.py. This is likely due to tkinter not being installed or properly configured.
10. On lower-end devices, the animated background and UI effects may cause slight performance issues.
11. The shiny, reflective surface effect on UI elements may not be visible on devices with lower screen resolutions or older graphics cards.
12. Need to redesign the GUI to better express the table of contents file as the ordinal 1st file.
13. Improve the interface to allow more intuitive cover sheet file specification.

## Installation

[Installation instructions to be added]

## Usage

[Usage instructions to be added]

## License

This project is licensed under the MIT License - see the LICENSE file for details.
