document.addEventListener('DOMContentLoaded', () => {
    const pdfFileInput = document.getElementById('pdf-file');
    const addPdfButton = document.getElementById('add-pdf');
    const pdfList = document.getElementById('pdf-files');
    const compilePdfsButton = document.getElementById('compile-pdfs');
    const saveReportButton = document.getElementById('save-report');
    const reportNameInput = document.getElementById('report-name');
    const loadReportSelect = document.getElementById('load-report');

    let pdfs = [];
    let coverSheetIndex = -1;

    addPdfButton.addEventListener('click', () => {
        Array.from(pdfFileInput.files).forEach(file => {
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/add_pdf', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error adding PDF:', data.error);
                    alert(`Error adding PDF: ${data.error}`);
                } else {
                    pdfs.push(data);
                    updatePdfList();
                }
            })
            .catch(error => {
                console.error('Error adding PDF:', error);
                alert('An error occurred while adding the PDF. Please try again.');
            });
        });
    });

    function updatePdfList() {
        pdfList.innerHTML = '';
        pdfs.forEach((pdf, index) => {
            const li = document.createElement('li');
            li.className = 'pdf-item';
            if (index === coverSheetIndex) {
                li.classList.add('cover-sheet');
                // Animate the cover sheet to the top
                li.style.animation = 'moveToCover 0.5s ease-out';
                pdfList.insertBefore(li, pdfList.firstChild);
            } else {
                pdfList.appendChild(li);
            }
            
            const fileInfo = document.createElement('span');
            fileInfo.textContent = `${pdf.filename} (${pdf.pages} pages)`;
            li.appendChild(fileInfo);

            const pageRangeInput = document.createElement('input');
            pageRangeInput.type = 'text';
            pageRangeInput.className = 'page-range-input';
            pageRangeInput.placeholder = 'Page range (e.g., 1-3,5,7-9)';
            pageRangeInput.value = pdf.pageRange || '';
            pageRangeInput.addEventListener('change', (e) => {
                pdf.pageRange = e.target.value;
            });
            li.appendChild(pageRangeInput);

            const setCoverButton = document.createElement('button');
            setCoverButton.textContent = index === coverSheetIndex ? 'Remove Cover' : 'Set as Cover';
            setCoverButton.addEventListener('click', () => {
                if (index === coverSheetIndex) {
                    coverSheetIndex = -1;
                } else {
                    coverSheetIndex = index;
                }
                updatePdfList();
            });
            li.appendChild(setCoverButton);

            const removeButton = document.createElement('button');
            removeButton.textContent = 'Remove';
            removeButton.addEventListener('click', () => {
                pdfs.splice(index, 1);
                if (index === coverSheetIndex) {
                    coverSheetIndex = -1;
                } else if (index < coverSheetIndex) {
                    coverSheetIndex--;
                }
                updatePdfList();
            });
            li.appendChild(removeButton);
        });
    }

    compilePdfsButton.addEventListener('click', async () => {
        const data = {
            pdfs: pdfs.map((pdf) => ({
                ...pdf,
                pageRange: pdf.pageRange || `1-${pdf.pages}`
            })),
            cover_sheet_index: coverSheetIndex
        };
        
        const response = await fetch('/compile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = response.headers.get('Content-Disposition').split('filename=')[1];
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            const errorData = await response.json();
            alert(`Error compiling PDFs: ${errorData.error}`);
        }
    });

    saveReportButton.addEventListener('click', async () => {
        const data = {
            name: reportNameInput.value,
            pdfs: pdfs,
            cover_sheet_index: coverSheetIndex
        };
        
        const response = await fetch('/save_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('Report saved successfully');
            loadReports();
        } else {
            const errorData = await response.json();
            alert(`Error saving report: ${errorData.error}`);
        }
    });

    async function loadReports() {
        const response = await fetch('/load_reports');
        if (response.ok) {
            const reports = await response.json();
            loadReportSelect.innerHTML = '<option value="">Select a report to load</option>';
            reports.forEach(report => {
                const option = document.createElement('option');
                option.value = report.id;
                option.textContent = report.name;
                loadReportSelect.appendChild(option);
            });
        }
    }

    loadReportSelect.addEventListener('change', async (event) => {
        const reportId = event.target.value;
        if (reportId) {
            const response = await fetch(`/load_report/${reportId}`);
            if (response.ok) {
                const report = await response.json();
                pdfs = report.pdfs;
                coverSheetIndex = report.cover_sheet_index;
                updatePdfList();
            }
        }
    });

    loadReports();
});
