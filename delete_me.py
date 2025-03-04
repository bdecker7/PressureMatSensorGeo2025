import tkinter as tk
from tkinter import filedialog
import pandas as pd

class App:
    def __init__(self, master):
        self.master = master
        master.title("Data Saver")

        self.data = {'col1': [1, 2, 3], 'col2': [4, 5, 6]}  # Example data
        self.df = pd.DataFrame(self.data)

        self.label = tk.Label(master, text="Data to save:")
        self.label.pack()

        self.text_area = tk.Text(master, height=5, width=30)
        self.text_area.insert(tk.END, self.df.to_string())
        self.text_area.config(state="disabled")  # Make it read-only
        self.text_area.pack()


        self.save_button = tk.Button(master, text="Save Data", command=self.save_data)
        self.save_button.pack()

    def save_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            self.df.to_csv(filename, index=False) 
            print(f"Data saved to {filename}")

root = tk.Tk()
app = App(root)
root.mainloop()
