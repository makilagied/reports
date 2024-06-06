import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def connect_to_db(dbname, user, password, host, port):
    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )

def fetch_bond_numbers(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f'SELECT DISTINCT "BondNo" FROM {table_name}')
    bond_numbers = cursor.fetchall()
    return [bn[0] for bn in bond_numbers]

def fetch_data_for_bond(conn, table_name, bond_no):
    cursor = conn.cursor()
    cursor.execute(f'SELECT "BondNo", "Term", "Coupon", "IssueDate", "MaturityDate", "Deals", "TradeDate", "Amount", "Price", "Yield" FROM {table_name} WHERE "BondNo" = %s', (bond_no,))
    data = cursor.fetchall()
    return data

def generate_pdf(data, bond_no):
    pdf_name = f'bond_{bond_no}.pdf'
    c = canvas.Canvas(pdf_name, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica", 10)
    
    # Title
    c.drawString(200, height - 40, f"Bond Report for {bond_no}")
    
    # Table header
    headers = ["BondNo", "Term_Years", "Coupon", "Issue_Date", "Maturity_Date", "Deals", "Trade_Date", "Amount_Bln_TZS", "Price", "Yield"]
    x_offset = 40
    y_offset = height - 80
    row_height = 20
    
    c.setFillColor(colors.gray)
    c.rect(x_offset, y_offset, width - 80, row_height, fill=1)
    c.setFillColor(colors.white)
    for i, header in enumerate(headers):
        c.drawString(x_offset + i * 70, y_offset + 5, header)
    
    # Table rows
    y_offset -= row_height
    for row in data:
        if y_offset < 40:
            c.showPage()
            c.setFont("Helvetica", 10)
            y_offset = height - 40
        
        for i, cell in enumerate(row):
            c.setFillColor(colors.black)
            c.drawString(x_offset + i * 70, y_offset + 5, str(cell))
        
        y_offset -= row_height

    c.save()
    print(f"PDF report generated: {pdf_name}")

def main():
    dbname = 'DSE_DB'
    user = 'postgres'
    password = 'iTrust123'
    host = '192.168.1.18'
    port = '5432'
    table_name = 'bond_data'
    
    conn = connect_to_db(dbname, user, password, host, port)
    
    # Fetch distinct bond numbers
    bond_numbers = fetch_bond_numbers(conn, table_name)
    
    # Generate PDF for each bond number
    for bond_no in bond_numbers:
        data = fetch_data_for_bond(conn, table_name, bond_no)
        generate_pdf(data, bond_no)
    
    conn.close()

if __name__ == "__main__":
    main()
