import ttkbootstrap as ttk

from src.core.settings import settings
from src.gui.tabs import Dashboard, Registry, Review


class GUI(ttk.Window):
    def __init__(self, backend):
        super().__init__(themename=settings.gui_theme)
        self.title("PO-SKU Bridge")
        self.geometry(settings.resolution)

        self.backend = backend

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Tab 1: The dashboard
        self.dashboardTab = Dashboard(self.notebook, backend)
        self.notebook.add(self.dashboardTab, text="Dashboard")

        # Tab 2: Registry
        self.registryTab = Registry(self.notebook, backend)
        self.notebook.add(self.registryTab, text="Registry")

        # Tab 3: Mappings
        self._check_worker()

    def _on_tab_changed(self, event):
        """Refreshes content when tabs are switched"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")

        if tab_text == "Registry":
            self.registryTab.refresh_data()

    def _check_worker(self):
        """Checks the backend for pending reviews"""
        if self.backend.needs_review:
            # Lower the flag
            self.backend.needs_review = False

            data = self.backend.current_review_payload

            # 1. Create the tab
            print("Creating new tab")
            self.reviewTab = Review(
                self,
                backend=self.backend,
                supplier=data["supplier"],
                rows_data=data["rows"],
                stats=data["stats"],
            )
            # 2. Add tab to notebook and focus
            self.notebook.add(self.reviewTab, text="Review mappings")
            self.notebook.select(self.reviewTab)

        self.after(500, self._check_worker)
