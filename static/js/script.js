document.addEventListener('DOMContentLoaded', () => {
    const addPdfButton = document.getElementById('add-pdf');
    const pdfFileInput = document.getElementById('pdf-file');
    const pdfList = document.getElementById('pdf-files');
    const compilePdfsButton = document.getElementById('compile-pdfs');
    const useCoverCheckbox = document.getElementById('use-cover');
    const coverPagesInput = document.getElementById('cover-pages');
    const saveReportButton = document.getElementById('save-report');
    const loadReportSelect = document.getElementById('load-report');
    const reportNameInput = document.getElementById('report-name');

    let pdfs = [];

    function createParticles() {
        const particlesContainer = document.getElementById('particles');
        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.top = `${Math.random() * 100}%`;
            particle.style.animationDuration = `${Math.random() * 3 + 2}s`;
            particlesContainer.appendChild(particle);
        }
    }

    createParticles();

    addPdfButton.addEventListener('click', () => {
        pdfFileInput.click();
    });

    pdfFileInput.addEventListener('change', async (event) => {
        const files = event.target.files;
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/add_pdf', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const pdfInfo = await response.json();
                pdfs.push({...pdfInfo, pages: `1-${pdfInfo.pages}`});
                updatePdfList();
            }
        }
    });

    function updatePdfList() {
        pdfList.innerHTML = '';
        pdfs.forEach((pdf, index) => {
            const li = document.createElement('li');
            li.className = 'glitch';
            li.setAttribute('data-text', pdf.filename);
            
            const fileInfo = document.createElement('span');
            fileInfo.textContent = `${pdf.filename} (${pdf.pages} pages)`;
            li.appendChild(fileInfo);
            
            const pageRangeInput = document.createElement('input');
            pageRangeInput.type = 'text';
            pageRangeInput.value = pdf.pages;
            pageRangeInput.placeholder = 'Page range (e.g., 1-5,7,9-12)';
            pageRangeInput.addEventListener('change', (e) => {
                pdfs[index].pages = e.target.value;
            });
            li.appendChild(pageRangeInput);
            
            const removeButton = document.createElement('button');
            removeButton.textContent = 'Remove';
            removeButton.addEventListener('click', () => {
                pdfs.splice(index, 1);
                updatePdfList();
            });
            
            li.appendChild(removeButton);
            pdfList.appendChild(li);
        });
    }

    compilePdfsButton.addEventListener('click', async () => {
        const data = {
            pdfs: pdfs,
            use_cover: useCoverCheckbox.checked,
            cover_pages: coverPagesInput.value
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
        }
    });

    saveReportButton.addEventListener('click', async () => {
        const data = {
            name: reportNameInput.value,
            pdfs: pdfs,
            use_cover: useCoverCheckbox.checked,
            cover_pages: coverPagesInput.value
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
                useCoverCheckbox.checked = report.use_cover;
                coverPagesInput.value = report.cover_pages;
                updatePdfList();
            }
        }
    });

    loadReports();
});
