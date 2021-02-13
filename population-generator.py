from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import StringVar
import csv

root = Tk()
root.title("Kelley's Population Generator")

# Main window
width = 500
height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
root.geometry("%dx%d+%d+%d" % (width, height, x, y))

# Search Form
searchForm = ttk.Labelframe(root, text='Search Variables')
inputYearLabel = ttk.Label(searchForm, text="US Census Year: ")
year = StringVar()
yearCb = ttk.Combobox(searchForm, textvariable=year, values=('2019', '2018', '2017', '2016', '2015'))
inputStateLabel = ttk.Label(searchForm, text="US State: ")
state = StringVar()
stateCb = ttk.Combobox(searchForm, textvariable=state, values=('AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MP', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UM', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY'))
searchForm.pack()
# Data Output Area
dataOutputArea = ttk.Labelframe(root, text='Data Output')
tree = ttk.Treeview(dataOutputArea)




# Import CSV file function
# def importCsv(inputFile):

#     with open (inputFile):
#         inputObject = csv.DictReader(inputFile, delimiter=',')
#         for row in inputObject:
#             year = row['input_year']
#             state = row['input_state']


if __name__ == '__main__':
    root.mainloop()
    # filedialog.Open(master=None, title="Import CSV")
    # inputFilePath = filedialog.askopenfilename()