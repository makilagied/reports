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


def fetch_investments_for_investor(conn, table_name, investor_name, start_date, end_date):
    cursor = conn.cursor()
    query = f'SELECT "date", "fund_name", "units", "nav", "investment", "fund_nav", "valuation", "gain_or_loss" FROM {table_name} WHERE "investor_name" = %s AND "date" BETWEEN %s AND %s'
    cursor.execute(query, (investor_name, start_date, end_date))
    return cursor.fetchall()


# def generate_certificate(investor_name, investor_investments, start_date, end_date):
#     if not investor_investments:
#         print(f"No data found for investor: {investor_name}")
#         return

#     pdf_name = f'certificate_{investor_name}.pdf'
#     doc = SimpleDocTemplate(pdf_name, pagesize=landscape(A4))
#     elements = []

#     # Add heading
#     styles = getSampleStyleSheet()
#     elements.append(Paragraph("<b>FUND VALUATION STATEMENT</b>", style=styles['Heading1']))
#     elements.append(Spacer(1, 0.5 * inch))

#     # Add salutation with client name and date range
#     salutation_text = f"Dear <b> {investor_name}</b>,<br/>This is your fund valuation for the period {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}."
#     elements.append(Paragraph(salutation_text, style=styles['Normal']))
#     elements.append(Spacer(1, 0.5 * inch))

#     # Create table data
#     table_data = [
#         ["Date", "Fund Name", "Units", "Initial NAV", "Investment", "Current NAV", "Valuation", "Gain / Loss"]
#     ]
    
#     # Populate table data
#     for investment in investor_investments:
#         table_data.append(investment)

#     # Create table style
#     table_style = TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#     ])

#     # Create table
#     table = Table(table_data, colWidths=[1.2*inch] * 8)
#     table.setStyle(table_style)
#     elements.append(table)

#     # Build PDF
#     doc.build(elements)
#     print(f"Certificate generated: {pdf_name}")




def generate_certificate(investor_name, investor_investments, start_date, end_date):
    if not investor_investments:
        print(f"No data found for investor: {investor_name}")
        return

    pdf_name = f'certificate_{investor_name}.pdf'
    doc = SimpleDocTemplate(pdf_name, pagesize=landscape(A4))
    elements = []

    # Add logo
    logo_path = "logo.png"  # Change this to the path of your logo file
    logo = Image(logo_path, width=1.2*inch, height=0.35*inch)
    elements.append(logo)

    # Add heading
    styles = getSampleStyleSheet()
    heading = Paragraph("<b>FUND VALUATION STATEMENT</b>", style=styles['Heading1'])
    elements.append(heading)
    elements.append(Spacer(1, 0.5 * inch))

    # Add salutation with client name and date range
    salutation_text = f"Dear <b>{investor_name}</b>,<br/>This is your fund valuation for the period <b>{start_date.strftime('%Y-%m-%d')}</b> to <b>{end_date.strftime('%Y-%m-%d')}</b>."
    elements.append(Paragraph(salutation_text, style=styles['Normal']))
    elements.append(Spacer(1, 0.5 * inch))

    # Create table data
    table_data = [
        ["Date", "Fund Name", "Units", "Initial NAV", "Investment", "Current NAV", "Valuation", "Gain /(Loss)"]
    ]
    
    # Populate table data
    for investment in investor_investments:
        table_data.append(investment)

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
    table = Table(table_data, colWidths=[1.2*inch] * 8)
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
    start_date = datetime.strptime("2024-03-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-05-31", "%Y-%m-%d")

    conn = connect_to_db(dbname, user, password, host, port)

    distinct_investors = fetch_distinct_investors(conn, table_name)
    for investor_name in distinct_investors:
        data = fetch_investments_for_investor(conn, table_name, investor_name, start_date, end_date)
        generate_certificate(investor_name, data, start_date, end_date)

    conn.close()

if __name__ == "__main__":
    main()
