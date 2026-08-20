import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

def json_to_pdf(json_data, output_pdf_path, title, is_failed_report=False):
    """
    Converts the monitor JSON report data into a formatted PDF.
    """
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = styles['Heading1']
    h2_style = styles['Heading2']
    h2_style.textColor = HexColor("#2c3e50")
    
    normal_style = styles['Normal']
    
    job_style = ParagraphStyle(
        'JobStyle',
        parent=styles['Normal'],
        leftIndent=20,
        spaceAfter=5
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    if is_failed_report:
        for item in json_data:
            c_name = item.get("company", "Unknown")
            ats = item.get("ats", "Unknown")
            status = item.get("status", "")
            msg = item.get("message", "")
            
            elements.append(Paragraph(f"<b>[{ats.upper()}] {c_name}</b>", h2_style))
            elements.append(Paragraph(f"<b>Status:</b> {status}", normal_style))
            elements.append(Paragraph(f"<b>Message:</b> {msg}", normal_style))
            elements.append(Spacer(1, 10))
    else:
        with_jobs = json_data.get("with_yesterday_jobs", [])
        no_jobs = json_data.get("no_yesterday_jobs", [])
        
        elements.append(Paragraph(f"Companies with New Jobs: {len(with_jobs)}", h2_style))
        elements.append(Spacer(1, 10))
        
        for item in with_jobs:
            c_name = item.get("company", "Unknown")
            ats = item.get("ats", "Unknown")
            jobs = item.get("yesterdays_jobs", [])
            
            elements.append(Paragraph(f"<b>[{ats.upper()}] {c_name} ({len(jobs)} jobs)</b>", normal_style))
            elements.append(Spacer(1, 5))
            
            for job in jobs:
                j_title = job.get("title", "")
                j_loc = job.get("location", "")
                j_url = job.get("url", "")
                
                # Encode & escape characters like & properly for reportlab if needed, but reportlab platypus handles standard strings
                # Actually, in ReportLab Paragraph, characters like & < > need to be escaped.
                j_title = str(j_title).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                j_url_escaped = str(j_url).replace('&', '&amp;').replace('\"', '%22').replace(\"'\", '%27')
                
                link_text = f'<a href="{j_url_escaped}" color="blue">{j_title}</a> ({j_loc})'
                elements.append(Paragraph(link_text, job_style))
            
            elements.append(Spacer(1, 10))
            
        elements.append(Paragraph(f"Companies with No New Jobs: {len(no_jobs)}", h2_style))
        elements.append(Spacer(1, 10))
        
        if no_jobs:
            no_jobs_names = [f"{i.get('company')} ({i.get('ats')})" for i in no_jobs]
            elements.append(Paragraph(", ".join(no_jobs_names), normal_style))
            
    doc.build(elements)
