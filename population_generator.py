import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from state_code_mappings import state_code_mappings
from api_key import key
import argparse
import csv
import requests


class PopulationGenerator:

    def __init__(self, filename):
        # main window
        self.window = tk.Tk()
        self.window.title("Kelley's Population Generator")
        self.configure_window()
        # search form
        self.search_result_id = 0
        self.search_result = ("", "", "")
        self.years = tuple(reversed([str(year) for year in range(2010, 2020)]))
        self.states = tuple([state_code_mapping['state_code'] for state_code_mapping in state_code_mappings])
        self.state_code = tk.StringVar()
        self.state_code_combobox = None
        self.year = tk.StringVar()
        self.year_combobox = None
        self.create_search_form()
        # data table
        self.table = None
        self.create_data_output_area()

        if filename:
            self.handle_import_csv(filename)
            self.handle_submit(year=self.year.get(), state_code=self.state_code.get())

    def start(self):
        self.window.mainloop()

    def configure_window(self):
        width = 550
        height = 450
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.window.geometry("%dx%d+%d+%d" % (width, height, x, y))

    def create_search_form(self):
        search_form = tk.LabelFrame(master=self.window, text="Search Variables")
        search_frame = tk.Frame(master=search_form)

        input_year_label = tk.Label(search_frame, text="US Census Year:")
        self.year_combobox = ttk.Combobox(search_frame, textvariable=self.year, values=self.years)

        input_state_label = tk.Label(search_frame, text="US State:")
        self.state_code_combobox = ttk.Combobox(search_frame, textvariable=self.state_code, values=self.states)

        btn_import = tk.Button(
            master=search_frame,
            text="Import CSV",
            width=10,
            height=0,
            fg="blue",
            command=self.handle_import_csv
        )

        btn_submit = tk.Button(
            master=search_frame,
            text="Submit",
            width=5,
            height=0,
            fg="blue",
            command=lambda: self.handle_submit(year=self.year.get(), state_code=self.state_code.get())
        )

        input_year_label.grid(row=0, column=0)
        self.year_combobox.grid(row=0, column=1)
        input_state_label.grid(row=1, column=0)
        self.state_code_combobox.grid(row=1, column=1)
        btn_import.grid(row=3, column=0, pady=10, sticky="w")
        btn_submit.grid(row=3, column=1, pady=10, sticky="e")
        search_frame.grid(row=0, column=0, padx=20, pady=10, sticky="n")
        search_form.grid(row=0, column=0, padx=20, pady=30, sticky="n")

    def create_data_output_area(self):
        data_area = tk.LabelFrame(master=self.window, text="Output Data")
        data_frame = tk.Frame(master=data_area)
        self.table = ttk.Treeview(data_frame, height=2)
        # define columns
        self.table['columns'] = ("input_year", "input_state", "output_population_size")
        # format columns
        self.table.column("#0", width=0, minwidth=0)
        self.table.column('input_year', anchor="w", width=120, minwidth=25)
        self.table.column('input_state', width=120, minwidth=25, anchor="w")
        self.table.column('output_population_size', width=180, minwidth=50, anchor="w")
        # create headings
        self.table.heading('input_year', text="US Census Year", anchor="w")
        self.table.heading('input_state', text="US State", anchor="w")
        self.table.heading('output_population_size', text="Population Size", anchor="w")
        # insert data into the tree
        self.table.insert(parent='', index=0, id=str(self.search_result_id), values=self.search_result)
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

        self.table.grid(row=1, column=1, padx=20, pady=0, sticky="n")
        btn_export.grid(row=2, column=1, pady=10, padx=20, sticky="e")
        data_frame.grid(row=1, column=0, padx=20, pady=30, sticky="n")
        data_area.grid(row=1, column=0, padx=20, pady=30, sticky="n")

    def handle_import_csv(self, filename):
        if not filename:
            filename = askopenfilename()
        try:
            # import values from input.csv
            reader = csv.DictReader(open(filename))
            for row in reader:
                self.set_year(row['input_year'])
                self.set_state_code(row['input_state'])
        except Exception:
            showerror(message="Sorry, failed to read file")

    # def handle_export_csv(self):
        # write output.csv
        # writer = csv.DictWriter(fieldnames=['input_year', 'input_state', 'output_population_size'])
        # writer.writeheader()
        # writer.writerow({'input_year': tree.get(0), 'input_state': tree.get(1), 'output_population_size': tree.get(2) })
        # output_csv_url = writer

    def handle_submit(self, year, state_code):
        baseUrl = "https://api.census.gov/data"
        dataset = "acs/acs1"
        variables = "B01003_001E"
        state_fips_code = self.get_fips_from_state_code(state_code)
        url = f"{baseUrl}/{year}/{dataset}?get=NAME,{variables}&for=state:{state_fips_code}&key={key}"
        response = requests.get(url)

        if response.status_code == 404:
            showerror(message="Sorry, no data was found for these variables.")
        elif response.status_code >= 400:
            showerror(message="Whoops! Something bad happened. Please check your inputs and try again.")

        body = response.json()
        self.search_result = (year, state_code, body[1][1])
        self.search_result_id += 1
        self.table.insert(parent='', index=0, id=str(self.search_result_id), values=self.search_result)

    def set_year(self, year):
        self.year.set(year)
    
    def set_state_code(self, state_code):
        self.state_code.set(state_code)

    def get_fips_from_state_code(self, state_code):
        state_fips_code = [state_code_mapping["fips"] for state_code_mapping in state_code_mappings if state_code_mapping["state_code"] == state_code][0]
        return state_fips_code


if __name__ == '__main__':
    # allow an optional filename to be passed as a position argument
    parser = argparse.ArgumentParser(description="This GUI will search the US Census Bureau API for population data.")
    parser.add_argument('input_csv', metavar='input.csv', type=str, nargs="?",
                        help='Path to csv with input_year and input_state columns')
    args = parser.parse_args()

    p = PopulationGenerator(filename=args.input_csv)
    p.start()