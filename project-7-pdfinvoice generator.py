from tkinter import *
from fpdf import FPDF
 
# Create the main window
window = Tk()
window.title("Invoice Generator")
 
# Initialize variables
medicines = {
    "Medicine A": 10,
    "Medicine B": 20,
    "Medicine C": 15,
    "Medicine D": 25
}
invoice_items = []
total_amount = 0.0
 
# Function to add medicine to the invoice
 
 
def add_medicine():
    selected_medicine = medicine_listbox.get(ANCHOR)
    if selected_medicine:
        quantity = int(quantity_entry.get())
        price = medicines[selected_medicine]
        item_total = price * quantity
        invoice_items.append((selected_medicine, quantity, item_total))
        total_amount_entry.delete(0, END)
        total_amount_entry.insert(END, str(calculate_total()))
        update_invoice_text()
 
# Function to calculate the total amount
 
 
def calculate_total():
    total = 0.0
    for item in invoice_items:
        total += item[2]
    return total
 
# Function to generate and save the invoice as PDF
 
 
def generate_invoice():
    customer_name = customer_entry.get()
 
    pdf = FPDF()
    pdf.add_page()
 
    # Set up PDF formatting
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, text="Invoice", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 10, text="Customer: " + customer_name,
             new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.cell(0, 10, text="", new_x="LMARGIN", new_y="NEXT")
 
    # Add invoice items to PDF
    for item in invoice_items:
        medicine_name, quantity, item_total = item
        pdf.cell(
            0, 10, text=f"Medicine: {medicine_name}, Quantity: {quantity}, Total: {item_total}", new_x="LMARGIN", new_y="NEXT", align="L")
 
    # Add total amount to PDF
    pdf.cell(0, 10, text="Total Amount: " +
             str(calculate_total()), new_x="LMARGIN", new_y="NEXT", align="L")
 
    # Save the PDF file
    pdf.output("invoice.pdf")
 
 
# GUI layout
medicine_label = Label(window, text="Medicine:")
medicine_label.pack()
 
medicine_listbox = Listbox(window, selectmode=SINGLE)
for medicine in medicines:
    medicine_listbox.insert(END, medicine)
medicine_listbox.pack()
 
quantity_label = Label(window, text="Quantity:")
quantity_label.pack()
 
quantity_entry = Entry(window)
quantity_entry.pack()
 
add_button = Button(window, text="Add Medicine", command=add_medicine)
add_button.pack()
 
total_amount_label = Label(window, text="Total Amount:")
total_amount_label.pack()
 
total_amount_entry = Entry(window)
total_amount_entry.pack()
 
customer_label = Label(window, text="Customer Name:")
customer_label.pack()
 
customer_entry = Entry(window)
customer_entry.pack()
 
generate_button = Button(
    window, text="Generate Invoice", command=generate_invoice)
generate_button.pack()
 
invoice_text = Text(window, height=10, width=50)
invoice_text.pack()
 
# Function to update the invoice text
 
 
def update_invoice_text():
    invoice_text.delete(1.0, END)
    for item in invoice_items:
        invoice_text.insert(
            END, f"Medicine: {item[0]}, Quantity: {item[1]}, Total: {item[2]}\n")
 
 
# Start the GUI event loop
window.mainloop()