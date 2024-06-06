import psycopg2
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Spacer



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
    query = f'SELECT "client_code", "investor_name", "date", "fund_name", "units", "nav", "investments", "fund_nav", "valuation", "gain_or_loss" FROM {table_name} WHERE "investor_name" = %s AND "date" BETWEEN %s AND %s'
    cursor.execute(query, (investor_name, start_date, end_date))
    data = cursor.fetchall()
    # Convert the fetched data into a dictionary
    keys = ['client_code', 'investor_name', 'date', 'fund_name', 'units', 'nav', 'investments', 'fund_nav', 'valuation', 'gain_or_loss']
    data_dict = [dict(zip(keys, row)) for row in data]
    return data_dict


# def generate_certificate(investor_data):
#     pdf_name = f'certificate_{investor_data[0]["investor_name"]}.pdf'
#     doc = SimpleDocTemplate(pdf_name, pagesize=landscape(A4))

#     styles = getSampleStyleSheet()
#     style_normal = styles['Normal']
#     style_heading = styles['Heading1']
#     style_heading.alignment = 1  # Center alignment

#     elements = []

#     # Add heading
#     heading = Paragraph("<b>FUND VALUATION STATEMENT</b>", style_heading)
#     elements.append(heading)
#     elements.append(Spacer(1, inch))

#     # Add salutation with client name
#     salutation_text = f"Dear {investor_data[0]['InvestorName']},"
#     salutation = Paragraph(salutation_text, style_normal)
#     elements.append(salutation)
#     elements.append(Spacer(1, inch))

#     # Add body text
#     body_text = f"This is your fund valuation as of {investor_data[0]['Date']}:"
#     body = Paragraph(body_text, style_normal)
#     elements.append(body)
#     elements.append(Spacer(1, inch))

#     # Create table data
#     table_data = [
#         ["Client Code", "Investor Name", "Date", "Fund Name", "Units", "Initial NAV", "Investments", "Current NAV", "Valuation", "Gain / Loss"]
#     ]
#     for row in investor_data:
#         table_data.append([row[key] for key in keys])

#     # Create table style
#     table_style = TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#     ])

#     # Create table
#     table = Table(table_data, colWidths=[1.5*inch] * 10)
#     table.setStyle(table_style)
#     elements.append(table)

#     # Build PDF
#     doc.build(elements)
#     print(f"Certificate generated: {pdf_name}")



def generate_certificate(investor_data):
    pdf_name = f'certificate_{investor_data[0]["investor_name"]}.pdf'
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
    salutation_text = f"Dear {investor_data[0]['investor_name']},"
    salutation = Paragraph(salutation_text, style_normal)
    elements.append(salutation)
    elements.append(Spacer(1, inch))
    
    # Add body text
    body_text = f"This is your fund valuation as of {investor_data[0]['date']}:"
    body = Paragraph(body_text, style_normal)
    elements.append(body)
    elements.append(Spacer(1, inch))
    
    # Create table data
    table_data = [
        ["Client Code", "Investor Name", "Date", "Fund Name", "Units", "Initial NAV", "Investments", "Current NAV", "Valuation", "Gain / Loss"]
    ]
    keys = table_data[0]
    
    # Populate table data
    for row in investor_data:
        table_data.append([row[key] for key in keys])
    
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
        generate_certificate(data)

    conn.close()


if __name__ == "__main__":
    main()
