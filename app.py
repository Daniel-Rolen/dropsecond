from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import tempfile
from utils.pdf_operations import compile_pdfs, validate_pdf, get_pdf_info
from utils.name_generator import generate_space_name
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import models after initializing db
from models import Report
db.Model = Report

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_pdf', methods=['POST'])
def add_pdf():
    file = request.files['file']
    logger.info(f"Received file: {file.filename}")
    if file and file.filename.endswith('.pdf'):
        try:
            logger.info(f"Validating PDF: {file.filename}")
            if validate_pdf(file):
                logger.info(f"PDF validated successfully: {file.filename}")
                pdf_info = get_pdf_info(file)
                logger.info(f"PDF info: {pdf_info}")
                return jsonify(pdf_info)
            else:
                logger.warning(f"Invalid PDF file: {file.filename}")
                return jsonify({"error": "Invalid PDF file"}), 400
        except Exception as e:
            logger.error(f"Error processing PDF {file.filename}: {str(e)}")
            return jsonify({"error": str(e)}), 400
    logger.warning(f"Invalid file type: {file.filename}")
    return jsonify({"error": "Invalid file"}), 400

@app.route('/compile', methods=['POST'])
def compile():
    data = request.json
    pdfs = data['pdfs']
    use_cover = data['use_cover']
    cover_sheet_index = data['cover_sheet_index']
    cover_page_range = data.get('cover_page_range', '')
    
    logger.info(f"Compiling PDFs. Use cover: {use_cover}, Cover sheet index: {cover_sheet_index}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        output_path = temp_file.name
        try:
            compile_pdfs(pdfs, output_path, use_cover, cover_sheet_index, cover_page_range)
            logger.info(f"PDFs compiled successfully. Output path: {output_path}")
        except Exception as e:
            logger.error(f"Error compiling PDFs: {str(e)}")
            return jsonify({"error": f"Error compiling PDFs: {str(e)}"}), 500
        
    output_name = generate_space_name() + '.pdf'
    return send_file(output_path, as_attachment=True, download_name=output_name)

@app.route('/save_report', methods=['POST'])
def save_report():
    data = request.json
    report = Report(name=data['name'], data=str(data))
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Report saved successfully"})

@app.route('/load_reports', methods=['GET'])
def load_reports():
    reports = Report.query.all()
    return jsonify([{"id": r.id, "name": r.name} for r in reports])

@app.route('/load_report/<int:report_id>', methods=['GET'])
def load_report(report_id):
    report = Report.query.get(report_id)
    if report:
        return jsonify(eval(report.data))
    return jsonify({"error": "Report not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
