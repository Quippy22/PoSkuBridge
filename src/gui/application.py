import ttkbootstrap as ttk

from src.core.settings import settings
from src.gui.tabs import Dashboard, Registry, Review, AddCode


class GUI(ttk.Window):
    def __init__(self, backend):
        super().__init__(themename=settings.gui_theme)
        self.title("PO-SKU Bridge")
        self.geometry(settings.resolution)

        self.backend = backend

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Tab 1: Dashboard
        self.dashboardTab = Dashboard(self.notebook, backend)
        self.notebook.add(self.dashboardTab, text="Dashboard")

        # Tab 2: Registry
        self.registryTab = Registry(self.notebook, backend)
        self.registryTab.bind("<<OpenAddCode>>", lambda e: self.open_add_code())
        self.notebook.add(self.registryTab, text="Registry")

        # Tab 3: Add Code (Not added to notebook yet)
        self.addCodeTab = AddCode(
            self.notebook, 
            on_save_success=self.registryTab.refresh_data,
            on_close=self.close_add_code
        )

        # Tab 4: Mappings (Auto-appearing)
        self._check_worker()

    def open_add_code(self):
        """Adds and switches to the Add Code tab if not present."""
        # Check if already in notebook
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == "Add Code":
                self.notebook.select(tab_id)
                return

        # Add it
        self.notebook.add(self.addCodeTab, text="Add Code")
        self.notebook.select(self.addCodeTab)

    def close_add_code(self):
        """Hides the Add Code tab."""
        self.notebook.forget(self.addCodeTab)
        self.switch_to_tab("Registry")

    def switch_to_tab(self, tab_text):
        """Switches the notebook to the tab with the given text."""
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == tab_text:
                self.notebook.select(tab_id)
                break

    def _on_tab_changed(self, event):
        """Refreshes content when tabs are switched"""
        selected_tab = self.notebook.select()
        if not selected_tab:
            return
            
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
