import ttkbootstrap as ttk

from src.core.logger import get_current_task
from src.core.settings import settings
from src.gui.options import SettingsWindow
from src.gui.tabs import AddCode, Dashboard, Registry, Review


class StatusBar(ttk.Frame):
    """Global status bar for active processes and system controls."""

    def __init__(self, parent, backend):
        super().__init__(parent, padding=(10, 2))
        self.parent = parent
        self.backend = backend

        # 0. Separator (Top)
        ttk.Separator(self, orient="horizontal").pack(side="top", fill="x", pady=(0, 5))

        # 1. Active Process Label (Left)
        self.label = ttk.Label(
            self,
            text="Active Process: Waiting for order",
            font=("Segoe UI", 10),
        )
        self.label.pack(side="left", pady=5)

        # 2. Controls (Right)
        # Style for the buttons
        style = ttk.Style()
        style.configure(
            "Exit.danger.TButton", font=("Segoe UI", 9, "bold"), padding=(10, 2)
        )
        style.configure(
            "Settings.secondary.TButton", font=("Segoe UI", 9), padding=(10, 2)
        )

        # Exit Button
        self.exit_btn = ttk.Button(
            self,
            text="Exit",
            style="Exit.danger.TButton",
            command=self.exit_app,
            width=6,
        )
        self.exit_btn.pack(side="right", padx=(5, 0))

        # Settings Button
        self.settings_btn = ttk.Button(
            self,
            text="Settings",
            style="Settings.secondary.TButton",
            command=self.open_settings,
            width=8,
        )
        self.settings_btn.pack(side="right", padx=5)

    def set_task(self, task_name):
        self.label.config(text=f"Active Process: {task_name}")

    def exit_app(self):
        self.backend.exit()
        self.parent.after(0, self.parent.destroy())
        self.parent.quit()

    def open_settings(self):
        settings_window = SettingsWindow(self.parent)
        settings_window.grab_set()


class GUI(ttk.Window):
    def __init__(self, backend):
        super().__init__(themename=settings.gui_theme)
        self.title("PO-SKU Bridge")
        self.geometry(settings.resolution)

        self.backend = backend

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=(5, 0))
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
            on_close=self.close_add_code,
        )

        # -- The Global Status Bar --
        self.status_bar = StatusBar(self, backend)
        self.status_bar.pack(side="bottom", fill="x")

        # Tab 4: Mappings (Auto-appearing)
        self._check_worker()
        self._update_status()

    def _update_status(self):
        """Pulls the current task from the logger and updates UI."""
        # Check if review tab is open
        is_reviewing = False
        for tab_id in self.notebook.tabs():
            if self.notebook.tab(tab_id, "text") == "Review mappings":
                is_reviewing = True
                break

        if is_reviewing:
            self.status_bar.set_task("Reviewing order")
        else:
            task = get_current_task()
            self.status_bar.set_task(task)

        self.after(200, self._update_status)

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
