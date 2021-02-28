import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror, showinfo
from state_code_mappings import state_code_mappings
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from api_key import key
import argparse
import csv
import requests
import json


class SearchResult:
    def __init__(self, id: int, year: int, state_code: str, population_size: int, product_category: str):
        self.id = id
        self.year = year
        self.state_code = state_code
        self.population_size = population_size
        self.product_category = product_category


class SearchResults:
    def __init__(self):
        self.latest_search_result_id = 0
        self.data = []  # store a list of search results

    def add_result(self, year: int, state_code: str, population_size: int, product_category: str) -> None:
        self.latest_search_result_id += 1
        result = SearchResult(id=self.latest_search_result_id,
                              year=year,
                              state_code=state_code,
                              population_size=population_size,
                              product_category=product_category)
        self.data.append(result)

    def get_latest_result(self) -> SearchResult:
        if len(self.data) == 0:
            return None

        return self.data[len(self.data) - 1]


class PopulationGenerator:
    def __init__(self, filename, search_results):
        # main window
        self.window = tk.Tk()
        self.window.title("Kelley's Population Generator")
        self.configure_window()
        # search form
        self.search_results = search_results
        self.years = tuple(reversed([str(year) for year in range(2010, 2020)]))
        self.states = tuple([
            state_code_mapping['state_code']
            for state_code_mapping in state_code_mappings
        ])
        self.product_categories = self.get_product_categories()
        self.product_category_strvar = tk.StringVar()
        self.state_code_strvar = tk.StringVar()
        self.state_code_combobox = None
        self.year_strvar = tk.StringVar()
        self.year_combobox = None
        self.create_search_form()
        # data table
        self.table = None
        self.create_data_output_area()

        if filename:
            self.handle_import_csv(filename)
            self.handle_submit()
            self.handle_export_csv()

    def start(self) -> None:
        # Run server (in its own thread)
        self.run_server()
        # Start up the GUI
        self.window.mainloop()

    def get_product_categories(self) -> list:
        # url = "localhost:8000/cgi-bin/categories"
        # response = requests.get(url)
        # return response

        # temporary process to emulate response from Kelley R.'s server
        with open('./sample_product_categories.json') as jsonfile:
            data = json.load(jsonfile)
            product_categories = tuple(data['sample_product_categories'])

        return product_categories

    def configure_window(self) -> None:
        width = 550
        height = 450
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.window.geometry("%dx%d+%d+%d" % (width, height, x, y))

    def create_search_form(self) -> None:
        search_form = tk.LabelFrame(master=self.window,
                                    text="Search Variables")
        search_frame = tk.Frame(master=search_form)

        input_year_label = tk.Label(search_frame, text="US Census Year:")
        self.year_combobox = ttk.Combobox(search_frame,
                                          textvariable=self.year_strvar,
                                          values=self.years)

        input_state_label = tk.Label(search_frame, text="US State:")
        self.state_code_combobox = ttk.Combobox(
            search_frame,
            textvariable=self.state_code_strvar,
            values=self.states)

        input_product_category_label = tk.Label(search_frame, text="Product Category:")
        self.product_category_combobox = ttk.Combobox(
            search_frame,
            textvariable=self.product_category_strvar,
            values=self.product_categories)

        btn_import = tk.Button(master=search_frame,
                               text="Import CSV",
                               width=10,
                               height=0,
                               fg="blue",
                               command=self.handle_import_csv)

        btn_submit = tk.Button(master=search_frame,
                               text="Submit",
                               width=5,
                               height=0,
                               fg="blue",
                               command=self.handle_submit)

        input_year_label.grid(row=0, column=0)
        self.year_combobox.grid(row=0, column=1)
        input_state_label.grid(row=1, column=0)
        self.state_code_combobox.grid(row=1, column=1)
        input_product_category_label.grid(row=2, column=0)
        self.product_category_combobox.grid(row=2, column=1)
        btn_import.grid(row=3, column=0, pady=10, sticky="w")
        btn_submit.grid(row=3, column=1, pady=10, sticky="e")
        search_frame.grid(row=0, column=0, padx=20, pady=10, sticky="n")
        search_form.grid(row=0, column=0, padx=20, pady=30, sticky="n")

    def create_data_output_area(self) -> None:
        data_area = tk.LabelFrame(master=self.window, text="Output Data")
        data_frame = tk.Frame(master=data_area)
        self.table = ttk.Treeview(data_frame, height=2)
        # define columns
        self.table['columns'] = ("input_year", "input_state",
                                 "output_population_size")
        # format columns
        self.table.column("#0", width=0, minwidth=0)
        self.table.column('input_year', anchor="w", width=120, minwidth=25)
        self.table.column('input_state', width=120, minwidth=25, anchor="w")
        self.table.column('output_population_size',
                          width=180,
                          minwidth=50,
                          anchor="w")
        # create headings
        self.table.heading('input_year', text="US Census Year", anchor="w")
        self.table.heading('input_state', text="US State", anchor="w")
        self.table.heading('output_population_size',
                           text="Population Size",
                           anchor="w")
        # insert data into the tree
        search_result = self.search_results.get_latest_result()
        if search_result:
            table_values = (search_result.year, search_result.state_code, search_result.population_size)
            self.table.insert(parent='',
                              index=0,
                              id=str(search_result.id),
                              values=table_values)
        else:
            # insert a blank row as a placeholder
            self.table.insert(parent='',
                              index=0,
                              id="0",
                              values=("", "", ""))
        # create export button
        btn_export = tk.Button(master=data_frame,
                               text="Export as CSV",
                               width=15,
                               height=0,
                               bg="green",
                               fg="blue",
                               command=self.handle_export_csv)

        self.table.grid(row=1, column=1, padx=20, pady=0, sticky="n")
        btn_export.grid(row=2, column=1, pady=10, padx=20, sticky="e")
        data_frame.grid(row=1, column=0, padx=20, pady=30, sticky="n")
        data_area.grid(row=1, column=0, padx=20, pady=30, sticky="n")

    def handle_import_csv(self, filename: str = None):
        if not filename:
            filename = askopenfilename()
        try:
            # import values from input.csv
            reader = csv.DictReader(open(filename))
            for row in reader:
                self.set_year(row['input_year'])
                self.set_state_code(row['input_state'])
                self.set_product_category(row['input_product_category'])
        except Exception:
            showerror(message="Sorry, failed to read file")
        self.window.update()

    def handle_export_csv(self) -> None:
        try:
            filename = tk.filedialog.asksaveasfilename()
            if filename:
                # ensure the file ending is ".csv"
                filename = f'{filename}.csv' if "csv" not in filename else filename
                search_result = self.search_results.get_latest_result()
                # write the output file
                with open(filename, 'w') as output_csv:
                    fields = [
                        'input_year', 'input_state', 'output_population_size', 'input_product_category'
                    ]
                    output_writer = csv.DictWriter(output_csv,
                                                   fieldnames=fields)
                    output_writer.writeheader()
                    output_writer.writerow({
                        'input_year': search_result.year,
                        'input_state': search_result.state_code,
                        'output_population_size': search_result.population_size,
                        'input_product_category': search_result.product_category
                    })
                showinfo(message="File saved successfully!")
        except Exception:
            showerror(message="Error saving file. Please try again.")
        self.window.update()

    def handle_submit(self) -> None:
        baseUrl = "https://api.census.gov/data"
        dataset = "acs/acs1"
        variables = "B01003_001E"
        state_code = self.state_code_strvar.get()
        year = self.year_strvar.get()
        product_category = self.product_category_strvar.get()
        state_fips_code = self.get_fips_from_state_code(state_code)
        url = f"{baseUrl}/{year}/{dataset}?get=NAME,{variables}&for=state:{state_fips_code}&key={key}"
        response = requests.get(url)

        if response.status_code == 404:
            showerror(message="Sorry, no data was found for these variables.")
            self.window.update()
            return
        elif response.status_code >= 400:
            showerror(
                message="Whoops! Something bad happened. Please check your inputs and try again."
            )
            self.window.update()
            return

        body = response.json()
        self.search_results.add_result(year=int(year),
                                       state_code=state_code,
                                       population_size=int(body[1][1]),
                                       product_category=product_category)
        search_result = search_results.get_latest_result()
        table_values = (search_result.year, search_result.state_code, search_result.population_size, search_result.product_category)
        self.table.delete(self.table.get_children())
        # search_result_id += 1
        self.table.insert(parent='',
                          index=0,
                          id=str(search_result.id),
                          values=table_values)
        self.window.update()

    def set_year(self, year: str) -> None:
        self.year_strvar.set(year)

    def set_state_code(self, state_code: str) -> None:
        self.state_code_strvar.set(state_code)

    def set_product_category(self, product_category: str) -> None:
        self.product_category_strvar.set(product_category)

    def get_fips_from_state_code(self, state_code: str) -> str:
        state_fips_code = [
            state_code_mapping["fips"]
            for state_code_mapping in state_code_mappings
            if state_code_mapping["state_code"] == state_code
        ][0]
        return state_fips_code

    def make_handler_class_with_args(self):

        search_results = self.search_results

        class HTTPRequestHandler(SimpleHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            search_results = search_results

            def do_GET(self):
                search_result = HTTPRequestHandler.search_results.get_latest_result()
                try:
                    response_obj = {
                        'state': search_result.state_code,
                        'year': search_result.year,
                        'population_size': search_result.population_size,
                        'selected_product_category': search_result.product_category
                    }
                    response_str = json.dumps(response_obj).encode("utf8")
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Content-Length", len(response_str))
                    self.end_headers()
                    self.wfile.write(response_str)
                except Exception:
                    self.send_error(404, "The user probably hasn't submitted info yet")

        return HTTPRequestHandler

    def run_server(self) -> None:
        host = "localhost"
        port = 6000
        server_address = (host, port)
        my_server = HTTPServer(
            server_address=server_address,
            RequestHandlerClass=self.make_handler_class_with_args())
        print(f"Starting http server on {host}:{port}")

        # Create a new thread and run server in it
        server_thread = Thread(target=my_server.serve_forever, args=())
        server_thread.start()


if __name__ == '__main__':
    # allow an optional filename to be passed as a position argument
    parser = argparse.ArgumentParser(
        description="This GUI will search the US Census Bureau API for population data.")
    parser.add_argument(
        'input_csv',
        metavar='input.csv',
        type=str,
        nargs="?",
        help='Path to csv with input_year, input_state, and input_product_category columns')
    args = parser.parse_args()

    search_results = SearchResults()
    population_generator = PopulationGenerator(filename=args.input_csv, search_results=search_results)
    population_generator.start()
