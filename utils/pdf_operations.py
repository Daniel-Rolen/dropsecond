import PyPDF2
import logging

logger = logging.getLogger(__name__)

def get_pdf_info(file):
    pdf = PyPDF2.PdfReader(file)
    return {
        "filename": file.filename,
        "pages": len(pdf.pages)
    }

def compile_pdfs(pdfs, output_path, cover_sheet_index):
    merger = PyPDF2.PdfMerger()
    
    logger.info(f"Starting PDF compilation. Total PDFs: {len(pdfs)}")
    
    if cover_sheet_index >= 0:
        cover_pdf = pdfs[cover_sheet_index]
        file_path = cover_pdf['filename']
        cover_range = parse_page_range(cover_pdf.get('pageRange', f"1-{cover_pdf['pages']}"))
        logger.info(f"Adding cover page from {file_path}. Page range: {cover_range}")
        try:
            merger.append(file_path, pages=cover_range)
        except Exception as e:
            logger.error(f"Error adding cover page from {file_path}: {str(e)}")
            raise
    
    for index, pdf in enumerate(pdfs):
        if index == cover_sheet_index:
            continue
        
        file_path = pdf['filename']
        content_range = parse_page_range(pdf.get('pageRange', f"1-{pdf['pages']}"))
        logger.info(f"Processing PDF {index + 1}: {file_path}. Page range: {content_range}")
        try:
            merger.append(file_path, pages=content_range)
        except Exception as e:
            logger.error(f"Error processing PDF {index + 1} ({file_path}): {str(e)}")
            raise
    
    logger.info(f"Writing compiled PDF to {output_path}")
    try:
        merger.write(output_path)
        merger.close()
        logger.info("PDF compilation completed successfully")
    except Exception as e:
        logger.error(f"Error writing compiled PDF: {str(e)}")
        raise

def parse_page_range(range_str):
    pages = []
    for part in range_str.split(','):
        part = part.strip()
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
