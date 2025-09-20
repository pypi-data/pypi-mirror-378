"""
Generate PDF invoices from Excel spreadsheets.

This module reads invoice data from Excel files and creates formatted PDF documents
with headers, tables, totals, and a company logo.

Author: David K Hill  
Created: 2025-09-19
"""

from pathlib import Path
import glob
import os
from fpdf.enums import XPos, YPos
from fpdf import FPDF
import pandas as pd


def generate(
    invoices_path,
    pdfs_path,
    image_path,
    product_id,
    product_name,
    amount_purchased,
    price_per_unit,
    total_price
):
    """
    Generate PDF invoices from Excel spreadsheets.

    This function reads Excel files from a specified directory, extracts invoice data,
    and generates formatted PDF invoices with a company logo and summary totals.

    Args:
        invoices_path (str): Path to the folder containing Excel invoice files.
        pdfs_path (str): Path to the folder where generated PDFs will be saved.
        image_path (str): Path to the folder containing the logo image.
        product_id (str): Column name for product ID in the Excel sheet.
        product_name (str): Column name for product name in the Excel sheet.
        amount_purchased (str): Column name for quantity purchased.
        price_per_unit (str): Column name for unit price.
        total_price (str): Column name for total price per item.

    Returns:
        None
    """
    filepaths = glob.glob(f'{invoices_path}/*xlsx')

    # Process each invoice file
    for filepath in filepaths:

        # Create a new PDF object and add a page
        pdf = FPDF(orientation='P', unit='mm', format="A4")
        pdf.add_page()

        # Extract invoice number and date from the filename
        filename = Path(filepath).stem
        invoice_no, invoice_date = filename.split('-')

        # Add Invoice title
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(50, 8, text=f"Invoice No. {invoice_no}", new_x=XPos.LEFT, new_y=YPos.NEXT)

        # Add Invoice date
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(50, 8, text=f"Date: {invoice_date}", new_x=XPos.LEFT, new_y=YPos.NEXT)

        # Add space between the date and the table.
        pdf.ln(16)

        # Read in the excel spreadsheet on sheet 1.
        df = pd.read_excel(filepath, sheet_name="Sheet 1")

        # Print Table Headers
        cols = df.columns
        cols = [item.replace("_", " ").title() for item in cols]
        
        # Add table header
        pdf.set_font("Times", "B", 10)
        pdf.set_text_color(0, 0, 0)
        
        # Define the width of each column
        pdf.cell(30, 8, text=cols[0], border=1)
        pdf.cell(70, 8, text=cols[1], border=1)
        pdf.cell(35, 8, text=cols[2], border=1)
        pdf.cell(30, 8, text=cols[3], border=1)
        pdf.cell(25, 8, text=cols[4], border=1)
        pdf.ln()

        # Initialize total amount
        total_amount = float(0)
        total_amount += sum(df[total_price])

        # Read each row and print
        for _, row in df.iterrows():
            # Add table rows
            pdf.set_font("Times", "", 10)
            pdf.set_text_color(50, 50, 50)
            
            #  Adjust the width of each cell to match the header
            pdf.cell(30, 8, text=str(row[product_id]), border=1)
            pdf.cell(70, 8, text=str(row[product_name]), border=1)
            pdf.cell(35, 8, text=str(row[amount_purchased]), border=1)
            pdf.cell(30, 8, text=str(row[price_per_unit]), border=1)
            pdf.cell(25, 8, text=str(row[total_price]), border=1)
            pdf.ln()
            
        # Add empty row for spacing
        pdf.cell(30, 8, text=" ", border=1)
        pdf.cell(70, 8, text=" ", border=1)
        pdf.cell(35, 8, text=" ", border=1)

        # Add total amount row
        pdf.set_font("Times", "B", 12)
        pdf.cell(30, 8, text="Total ", border=1, align="R")
        
        # Leave empty cells
        pdf.set_font("Times", "", 10)
        pdf.cell(25, 8, text=str(total_amount), border=1)
        pdf.ln(25)

        #  Add total sum sentence
        pdf.set_font("Times", "B", 12)
        pdf.set_text_color(0, 0, 0)

        # Define dimensions and starting point
        text = "Far West Computer Consulting"
        #  
        text_height = 10
        logo_width = 12
        padding = 5

        # Save starting coordinates
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        # Add the company name first
        pdf.cell(0, text_height, text)

        # Measure the width of the text just added
        text_width = pdf.get_string_width(text)

        # Set cursor to the right of the text, with some padding
        pdf.set_xy(x_start + text_width + padding, y_start)

        # Add the logo to the right of the text
        pdf.image(
            f"{image_path}",
            x=pdf.get_x(),
            y=pdf.get_y(),
            w=logo_width,
            h=logo_width
        )

        # Move to the next line after the tallest element
        pdf.ln(max(text_height, logo_width))

        # Ensure the output directory exists
        os.makedirs(pdfs_path, exist_ok=True)

        # Save the PDF to a file
        pdf.output(f"{pdfs_path}/{filename}.pdf")
