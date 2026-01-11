import ttkbootstrap as ttk
from tabs import Dashboard


class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("PO-SKU Bridge")
        self.geometry("640x480")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 1: The dashboard
        self.dashboardTab = Dashboard(self.notebook)
        self.notebook.add(self.dashboardTab, text="Dashboard")

        # Tab 2: Mappings (Placeholder)
        self.mappingsTab = ttk.Frame(self.notebook)
        self.notebook.add(self.mappingsTab, text="Fix mappings")
        self.notebook.hide(1)
        ttk.Label(self.mappingsTab, text="Mappings here").pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
