import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from utils.pdf_operations import compile_pdfs, get_pdf_info, validate_pdf
from utils.name_generator import generate_space_name
import tempfile

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///binder.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    import models
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_pdf', methods=['POST'])
def add_pdf():
    file = request.files['file']
    if file and file.filename.endswith('.pdf'):
        try:
            if validate_pdf(file):
                pdf_info = get_pdf_info(file)
                return jsonify(pdf_info)
            else:
                return jsonify({"error": "Invalid PDF file"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"error": "Invalid file"}), 400

@app.route('/compile', methods=['POST'])
def compile():
    data = request.json
    pdfs = data['pdfs']
    use_cover = data['use_cover']
    cover_sheet_index = data['cover_sheet_index']
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        output_path = temp_file.name
        compile_pdfs(pdfs, output_path, use_cover, cover_sheet_index)
        
    output_name = generate_space_name() + '.pdf'
    return send_file(output_path, as_attachment=True, download_name=output_name)

@app.route('/save_report', methods=['POST'])
def save_report():
    data = request.json
    report = models.Report(name=data['name'], data=str(data))
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Report saved successfully"})

@app.route('/load_reports', methods=['GET'])
def load_reports():
    reports = models.Report.query.all()
    return jsonify([{"id": r.id, "name": r.name} for r in reports])

@app.route('/load_report/<int:report_id>', methods=['GET'])
def load_report(report_id):
    report = models.Report.query.get(report_id)
    if report:
        return jsonify(eval(report.data))
    return jsonify({"error": "Report not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
