from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import tempfile
import json
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

# Create tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_pdf', methods=['POST'])
def add_pdf():
    file = request.files.get('file')
    logger.info(f"Received file: {file.filename if file else 'No file received'}")
    if file and file.filename.lower().endswith('.pdf'):
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
    logger.warning(f"Invalid file type or no file received: {file.filename if file else 'No file'}")
    return jsonify({"error": "Invalid file or no file received"}), 400

@app.route('/compile', methods=['POST'])
def compile():
    data = request.json
    pdfs = data['pdfs']
    cover_sheet_index = data['cover_sheet_index']
    
    logger.info(f"Compiling PDFs. Cover sheet index: {cover_sheet_index}")
    logger.info(f"Number of PDFs to compile: {len(pdfs)}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        output_path = temp_file.name
        try:
            compile_pdfs(pdfs, output_path, cover_sheet_index)
            logger.info(f"PDFs compiled successfully. Output path: {output_path}")
        except Exception as e:
            logger.error(f"Error compiling PDFs: {str(e)}")
            return jsonify({"error": f"Error compiling PDFs: {str(e)}"}), 500
        
    output_name = generate_space_name() + '.pdf'
    return send_file(output_path, as_attachment=True, download_name=output_name)

@app.route('/save_report', methods=['POST'])
def save_report():
    data = request.json
    report = Report(name=data['name'], data=json.dumps(data))
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
        return jsonify(json.loads(report.data))
    return jsonify({"error": "Report not found"}), 404

@app.route('/export_report/<int:report_id>', methods=['GET'])
def export_report(report_id):
    report = Report.query.get(report_id)
    if report:
        return send_file(
            io.BytesIO(json.dumps(json.loads(report.data), indent=2).encode()),
            mimetype='application/json',
            as_attachment=True,
            download_name=f"{report.name}_export.json"
        )
    return jsonify({"error": "Report not found"}), 404

@app.route('/import_report', methods=['POST'])
def import_report():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.json'):
        try:
            data = json.load(file)
            report = Report(name=data['name'], data=json.dumps(data))
            db.session.add(report)
            db.session.commit()
            return jsonify({"message": "Report imported successfully"})
        except Exception as e:
            logger.error(f"Error importing report: {str(e)}")
            return jsonify({"error": f"Error importing report: {str(e)}"}), 400
    return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
