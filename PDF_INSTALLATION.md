# PDF Processing Installation Guide

This application now supports both text-based and image-based PDFs using:
- **PyPDF2**: For text-based PDFs (extracts text directly)
- **pdf2image + pytesseract**: For image-based PDFs (uses OCR)

## Installation Steps

### 1. Install Python Packages

```bash
pip install PyPDF2 pdf2image pytesseract Pillow nltk
```

### 2. Install System Dependencies

#### Windows:
1. Download Poppler for Windows from: https://github.com/oschwartz10612/poppler-windows/releases/
2. Extract the zip file
3. Add the `bin` folder to your system PATH
   - Example: If extracted to `C:\poppler`, add `C:\poppler\Library\bin` to PATH

4. Install Tesseract OCR:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Run the installer
   - Add Tesseract to PATH (usually `C:\Program Files\Tesseract-OCR`)

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install poppler-utils tesseract-ocr tesseract-ocr-eng
```

#### macOS:
```bash
brew install poppler tesseract
```

### 3. Configure Tesseract Path (if needed)

If Tesseract is not in your PATH, you can set it in your code:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# or
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'  # macOS/Linux
```

### 4. Verify Installation

Run this Python script to test:

```python
from pdf2image import convert_from_path
import pytesseract

# Test PDF to image conversion
try:
    images = convert_from_path('test.pdf', dpi=300)
    print("✓ pdf2image works!")
except Exception as e:
    print(f"✗ pdf2image error: {e}")

# Test OCR
try:
    text = pytesseract.image_to_string(images[0] if images else None)
    print("✓ pytesseract works!")
except Exception as e:
    print(f"✗ pytesseract error: {e}")
```

## How It Works

1. **Text-based PDFs**: Uses PyPDF2 to extract text directly (fast)
2. **Image-based PDFs**: 
   - Converts PDF pages to images using pdf2image (requires Poppler)
   - Extracts text from images using pytesseract OCR (requires Tesseract)

The system automatically tries text extraction first, and falls back to OCR if needed.

