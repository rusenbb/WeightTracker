import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
# set the style of the plots
sns.set(rc={'axes.facecolor':'#6c7c96', 'figure.facecolor':'#c29380'})

class DietTracker:
    def __init__(self):
        # Create the main window with a flexible layout
        self.root = tk.Tk()
        self.root.resizable(True, True)
        self.root.title("Weight Tracker")
        self.root.geometry("500x500")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Create the main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        # Create a notebook widget to hold the tabs
        self.window  = ttk.Notebook(self.main_frame)
        self.window.pack(fill='both', expand=True)

        # # Create the about tab that will hold the text information about the app
        # self.about_tab = ttk.Frame(self.window)
        # about_text = "This app is a simple weight tracker that allows you to add your weight and date to a database and view the data in a table or plot."
        # self.window.add(self.about_tab, text="About")
        # tk.Label(self.about_tab, text=about_text).pack()


        # Create database connection and table
        self.conn = sqlite3.connect("weight.db")
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS weights(date TEXT, weight REAL)")

        # Create GUI widgets
        tk.Label(self.window, text="Enter your weight:").pack()
        self.weight_entry = tk.Entry(self.window)
        self.weight_entry.pack()

        tk.Label(self.window, text="Enter the date (YYYY-MM-DD):").pack()
        self.date_entry = tk.Entry(self.window)
        self.date_entry.pack()

        # make buttons with size 20x2
        tk.Button(self.window, text="Add record", command=self.add_record , width=20, height=2).pack()

        tk.Button(self.window, text="View table", command=self.view_table , width=20, height=2).pack()

        tk.Button(self.window, text="View plot", command=self.view_plot , width=20, height=2).pack()

    def add_record(self):
        weight = self.weight_entry.get()
        date = self.date_entry.get()

        # check if date is valid
        try:
            pd.to_datetime(date)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid date")
            return
        
        if not weight or not date:
            messagebox.showerror("Error", "Please enter both weight and date")
            return

        try:
            weight = float(weight)
        except ValueError:
            messagebox.showerror("Error", "Weight must be a number")
            return

        # if date already exists, update the record
        if self.c.execute("SELECT * FROM weights WHERE date=?", (date,)).fetchone():
            self.c.execute("UPDATE weights SET weight=? WHERE date=?", (weight, date))
            self.conn.commit()
            messagebox.showinfo("Success", "Record updated successfully")
            return
        
        self.c.execute("INSERT INTO weights VALUES (?, ?)", (date, weight))
        self.conn.commit()

        messagebox.showinfo("Success", "Record added successfully")

    def view_table(self):
        self.c.execute("SELECT * FROM weights")
        rows = self.c.fetchall()

        if not rows:
            messagebox.showwarning("Warning", "No records found")
            return

        # Create a new window to display the table
        table_window = tk.Toplevel(self.window)
        table_window.title("Weight Records")
        table_window.geometry("400x400")

        # Create a pandas dataframe widget
        table = pd.DataFrame(rows, columns=["Date", "Weight"])

        # sort the table by date in ascending order, first convert the date column to datetime
        table["Date"] = pd.to_datetime(table["Date"])
        table.sort_values(by="Date", inplace=True)
        table.reset_index(drop=True, inplace=True)
        frame = tk.Frame(table_window)
        frame.pack(fill="both", expand=True)
        table_widget = tk.Label(frame, text=table.to_string(), justify="left")
        table_widget.pack()

    def view_plot(self):
        self.c.execute("SELECT * FROM weights")
        rows = self.c.fetchall()

        if not rows:
            messagebox.showwarning("Warning", "No records found")
            return

        # Create a pandas dataframe from the database rows
        df = pd.DataFrame(rows, columns=["Date", "Weight"])

        # Create a plot using seaborn
        fig, ax = plt.subplots()
        sns.lineplot(x="Date", y="Weight", data=df, ax=ax, color="#CE1D6A", linewidth=3)
        ax.set_title("Weight over time", fontsize=16)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Weight", fontsize=14)
        # name the figure
        fig.canvas.manager.window.wm_title("Weight Progress Plot")
        plt.show()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    tracker = DietTracker()
    tracker.run()
