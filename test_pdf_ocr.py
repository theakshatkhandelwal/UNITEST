#!/usr/bin/env python
"""Quick test script to verify PDF OCR functionality"""
import sys

print("Testing PDF OCR dependencies...")
print("-" * 50)

# Test EasyOCR
try:
    import easyocr
    print("[OK] EasyOCR imported successfully")
    HAS_EASYOCR = True
except ImportError as e:
    print(f"[ERROR] EasyOCR not available: {e}")
    HAS_EASYOCR = False

# Test PyMuPDF
try:
    import fitz
    print(f"[OK] PyMuPDF imported successfully (version {fitz.version[0]})")
    HAS_PYMUPDF = True
except ImportError as e:
    print(f"[ERROR] PyMuPDF not available: {e}")
    HAS_PYMUPDF = False

# Test pdf2image
try:
    from pdf2image import convert_from_path
    print("[OK] pdf2image imported successfully")
    HAS_PDF2IMAGE = True
except ImportError as e:
    print(f"[ERROR] pdf2image not available: {e}")
    HAS_PDF2IMAGE = False

# Test pytesseract (may fail due to pandas/numpy issues, but that's OK)
try:
    import pytesseract
    print("[OK] pytesseract imported successfully")
    HAS_TESSERACT = True
except Exception as e:
    print(f"[WARNING] pytesseract not available: {e}")
    print("  (This is OK - EasyOCR is the primary OCR method)")
    HAS_TESSERACT = False

# Test PyPDF2
try:
    import PyPDF2
    print("[OK] PyPDF2 imported successfully")
    HAS_PYPDF2 = True
except ImportError as e:
    print(f"[ERROR] PyPDF2 not available: {e}")
    HAS_PYPDF2 = False

print("-" * 50)
print("\nPDF Processing Capabilities:")
print(f"  Text-based PDFs: {'[OK]' if HAS_PYPDF2 else '[NO]'}")
print(f"  Image-based PDFs (EasyOCR): {'[OK]' if HAS_EASYOCR else '[NO]'}")
print(f"  Image-based PDFs (Tesseract): {'[OK]' if HAS_TESSERACT else '[NO]'}")
print(f"  PDF to Image (pdf2image): {'[OK]' if HAS_PDF2IMAGE else '[NO]'}")
print(f"  PDF to Image (PyMuPDF): {'[OK]' if HAS_PYMUPDF else '[NO]'}")

if HAS_EASYOCR:
    print("\n[INIT] Initializing EasyOCR reader (this may take a moment on first run)...")
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        print("[OK] EasyOCR reader initialized successfully!")
        print("  Ready to process image-based PDFs!")
    except Exception as e:
        print(f"[ERROR] EasyOCR initialization failed: {e}")

print("\n" + "=" * 50)
if HAS_EASYOCR and HAS_PYMUPDF:
    print("[SUCCESS] Your system is ready to process image-based PDFs!")
    print("   Primary method: EasyOCR + PyMuPDF (no system binaries needed)")
elif HAS_EASYOCR:
    print("[SUCCESS] EasyOCR available - will use pdf2image if Poppler is installed")
else:
    print("[WARNING] EasyOCR not available - install with: pip install easyocr")

