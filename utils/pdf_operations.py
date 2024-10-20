import PyPDF2
import fitz

def get_pdf_info(file):
    pdf = PyPDF2.PdfReader(file)
    return {
        "filename": file.filename,
        "pages": len(pdf.pages)
    }

def compile_pdfs(pdfs, output_path, use_cover, cover_pages, cover_sheet_index):
    merger = PyPDF2.PdfMerger()
    
    if use_cover and cover_sheet_index >= 0:
        cover_pdf = pdfs[cover_sheet_index]
        file_path = cover_pdf['filename']
        cover_range = parse_page_range(cover_pages)
        merger.append(file_path, pages=cover_range)
    
    for index, pdf in enumerate(pdfs):
        if index == cover_sheet_index and use_cover:
            continue
        
        file_path = pdf['filename']
        pages = pdf['pages']
        content_range = parse_page_range(pages)
        merger.append(file_path, pages=content_range)
    
    merger.write(output_path)
    merger.close()

def parse_page_range(range_str):
    pages = []
    for part in range_str.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.extend(range(start - 1, end))
        else:
            pages.append(int(part) - 1)
    return pages

def validate_pdf(file):
    try:
        PyPDF2.PdfReader(file)
        file.seek(0)  # Reset file pointer
        return True
    except PyPDF2.errors.PdfReadError:
        return False
