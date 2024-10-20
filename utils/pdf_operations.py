import PyPDF2
import fitz

def get_pdf_info(file):
    pdf = PyPDF2.PdfReader(file)
    return {
        "filename": file.filename,
        "pages": len(pdf.pages)
    }

def compile_pdfs(pdfs, output_path, use_cover, cover_pages):
    merger = PyPDF2.PdfMerger()
    
    for pdf in pdfs:
        file_path = pdf['filename']
        pages = pdf['pages']
        
        if use_cover and pdf == pdfs[0]:
            cover_range = parse_page_range(cover_pages)
            merger.append(file_path, pages=cover_range)
        
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
