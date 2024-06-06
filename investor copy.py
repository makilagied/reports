import psycopg2
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
# from reportlab.lib.styles import getSampleStyleSheet




from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib import colors

def connect_to_db(dbname, user, password, host, port):
    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

def fetch_distinct_investors(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT investor_name FROM {table_name}")
    distinct_investors = cursor.fetchall()
    return [investor[0] for investor in distinct_investors]



def fetch_data_for_investor(conn, table_name, investor_name, start_date, end_date):
    cursor = conn.cursor()
    query = f'SELECT * FROM {table_name} WHERE "InvestorName" = %s AND "Date" BETWEEN %s AND %s'
    print("Executing SQL query:", query)
    print("Parameters:", (investor_name, start_date, end_date))
    cursor.execute(query, (investor_name, start_date, end_date))
    data = cursor.fetchall()
    print("Fetched data:", data)
    return data





# def fetch_data_for_investor(conn, table_name, start_date, end_date):
#     cursor = conn.cursor()
#     cursor.execute(f"""
#         SELECT "client_code", "investor_name", "date", "fund_name", "units", "nav", "investment", "fund_nav", "valuation", "gain_or_loss"
#         FROM {table_name}
#         WHERE "date" BETWEEN %s AND %s
#         """, (start_date, end_date))
#     data = cursor.fetchall()
#     return data





# def generate_certificate(data, investor_name, date_range):
#     pdf_name = f'certificate_{investor_name}.pdf'
#     c = canvas.Canvas(pdf_name, pagesize=letter)
#     width, height = letter
    
#     c.setFont("Helvetica", 10)
    
#     # Certificate title
#     c.drawString(200, height - 40, f"Certificate of Investment for {investor_name}")
    
#     # Certificate content
#     y_offset = height - 80
#     line_height = 20
    
#     certificate_text = [
#         f"This is your fund valuation as of {date_range}:",
#         "",  # Add extra space
#     ]
    
#     for row in data:
#         certificate_text.append(f"- {row[2]}: {row[4]} units at NAV {row[6]}")
    
#     # Write certificate content to PDF
#     for line in certificate_text:
#         c.drawString(40, y_offset, line)
#         y_offset -= line_height
    
#     c.save()
#     print(f"Certificate generated: {pdf_name}")







def generate_certificate(investor_data):
    pdf_name = f'certificate_{investor_data["InvestorName"]}.pdf'
    doc = SimpleDocTemplate(pdf_name, pagesize=landscape(A4))
    
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']
    style_heading.alignment = 1  # Center alignment
    
    elements = []
    
    # Add heading
    heading = Paragraph("<b>FUND VALUATION STATEMENT</b>", style_heading)
    elements.append(heading)
    elements.append(Spacer(1, inch))
    
    # Add logo (assuming you have a logo image named 'logo.svg' in the same directory)
    # You need to import the logo here
    
    # Add salutation with client name
    salutation_text = f"Dear {investor_data['InvestorName']},"
    salutation = Paragraph(salutation_text, style_normal)
    elements.append(salutation)
    elements.append(Spacer(1, inch))
    
    # Add body text
    body_text = "This is your fund valuation as of {investor_data['Date']}:"
    body = Paragraph(body_text, style_normal)
    elements.append(body)
    elements.append(Spacer(1, inch))
    
    # Create table data
    table_data = [
        ["Client Code", "Investor Name", "Date", "Fund Name", "Units", "Initial NAV", "Investments", "Current NAV", "Valuation", "Gain / Loss"],
        [investor_data['ClientCode'], investor_data['InvestorName'], investor_data['Date'], investor_data['FundName'], investor_data['Units'], investor_data['InitialNAV'], investor_data['Investments'], investor_data['CurrentNAV'], investor_data['Valuation'], investor_data['GainLoss']]
    ]
    
    # Create table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ])
    
    # Create table
    table = Table(table_data, colWidths=[1.5*inch] * 10)
    table.setStyle(table_style)
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    print(f"Certificate generated: {pdf_name}")






def main():
    dbname = 'DSE_DB'
    user = 'postgres'
    password = 'iTrust123'
    host = '192.168.1.18'
    port = '5432'
    table_name = 'investments'
    start_date = datetime.strptime("2024-05-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-05-31", "%Y-%m-%d")

    conn = connect_to_db(dbname, user, password, host, port)

    distinct_investors = fetch_distinct_investors(conn, table_name)
    for investor_name in distinct_investors:
        data = fetch_data_for_investor(conn, table_name, investor_name, start_date, end_date)
        print(data)  # Print data before generating certificate
        generate_certificate(data)
    
    conn.close()



