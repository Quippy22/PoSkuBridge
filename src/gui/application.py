import ttkbootstrap as ttk

from src.gui.tabs.dashboard import Dashboard
from src.core.settings import settings


class GUI(ttk.Window):
    def __init__(self, backend):
        super().__init__(themename=settings.gui_theme)
        self.title("PO-SKU Bridge")
        self.geometry(settings.resolution)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 1: The dashboard
        self.dashboardTab = Dashboard(self.notebook, backend)
        self.notebook.add(self.dashboardTab, text="Dashboard")

        # Tab 2: Mappings (Placeholder)
        self.mappingsTab = ttk.Frame(self.notebook)
        self.notebook.add(self.mappingsTab, text="Fix mappings")
        self.notebook.hide(1)
        ttk.Label(self.mappingsTab, text="Mappings here").pack(pady=10)
