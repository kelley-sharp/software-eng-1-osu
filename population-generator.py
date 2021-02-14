import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
import csv
import requests

window = tk.Tk()
window.title("Kelley's Population Generator")

def handle_import_csv():
    fname = askopenfilename()
    if fname:
        try:
            # import values from input.csv
            reader = csv.DictReader(open(fname))
            for row in reader:
                year_cb.insert(0, row['input_year'])
                state_cb.insert(0, row['input_state'])
            # write output.csv
            writer = csv.DictWriter(fieldnames=['input_year', 'input_state', 'output_population_size'])
            print(writer)
            # writer.writeheader()
            # writer.writerow({'input_year': tree.get(0), 'input_state': tree.get(1), 'output_population_size': tree.get(2) })
            # ouput_csv_url = writer
        except:
            showerror(message="Sorry, failed to read file")


# output_csv_url = {}
# def download_csv():
#     response = requests.get(output_csv_url)


# Main window
width = 550
height = 450
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width / 2) - (width / 2)
y = (screen_height / 2) - (height / 2)
window.geometry("%dx%d+%d+%d" % (width, height, x, y))

# Search Form
search_form = tk.LabelFrame(master=window, text="Search Variables")
search_frame = tk.Frame(master=search_form)
input_year_label = tk.Label(search_frame, text="US Census Year:")
year = tk.StringVar()
year_cb = ttk.Combobox(search_frame, textvariable=year, values=('2019', '2018', '2017', '2016', '2015'))
input_state_label = tk.Label(search_frame, text="US State:")
state = tk.StringVar()
states = ('AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MP', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UM', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY')
state_cb = ttk.Combobox(search_frame, textvariable=state, values=states)
btn_import = tk.Button(
    master=search_frame,
    text="Import CSV",
    width=10,
    height=0,
    fg="blue",
    command=handle_import_csv
)
btn_submit = tk.Button(
    master=search_frame,
    text="Submit",
    width=5,
    height=0,
    fg="blue"
    # command=handle_submit
)

input_year_label.grid(row=0, column=0)
year_cb.grid(row=0, column=1)
input_state_label.grid(row=1, column=0)
state_cb.grid(row=1, column=1)
btn_import.grid(row=3, column=0, pady=10, sticky="w")
btn_submit.grid(row=3, column=1, pady=10, sticky="e")
search_frame.grid(row=0, column=0, padx=20, pady=10, sticky="n")
search_form.grid(row=0, column=0, padx=20, pady=30, sticky="n")


# Data Output Area
data_area = tk.LabelFrame(master=window, text="Output Data")
data_frame = tk.Frame(master=data_area)
tree = ttk.Treeview(data_frame, height=2)
# define columns
tree['columns'] = ("input_year", "input_state", "output_population_size")
# format columns
tree.column("#0", width=0, minwidth=0)
tree.column('input_year',  anchor="w", width=120, minwidth=25)
tree.column('input_state', width=120, minwidth=25, anchor="w")
tree.column('output_population_size', width=180, minwidth=50, anchor="w")
# create headings
tree.heading('input_year', text="US Census Year", anchor="w")
tree.heading('input_state', text="US State", anchor="w")
tree.heading('output_population_size', text="Population Size", anchor="w")
# dummy data for the tree
tree.insert(parent='', index=0, id='1', values=("2015", "AK", "731,545"))
# create export button
btn_export = tk.Button(
    master=data_frame,
    text="Export as CSV",
    width=15,
    height=0,
    bg="green",
    fg="blue",
    # command=download_csv
)

tree.grid(row=1, column=1, padx=20, pady=0, sticky="n")
btn_export.grid(row=2, column=1, pady=10, padx=20, sticky="e")
data_frame.grid(row=1, column=0, padx=20, pady=30, sticky="n")
data_area.grid(row=1, column=0, padx=20, pady=30, sticky="n")












if __name__ == '__main__':
    window.mainloop()
