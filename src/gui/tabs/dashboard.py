import ttkbootstrap as ttk

from loguru import logger

from src.gui.options import SettingsWindow

from src.core.logger import get_next_log
from src.core.settings import settings


class VisualLogger(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="Active Logger", bootstyle="primary")

        # scrollbar
        self.scrollbar = ttk.Scrollbar(self, bootstyle="primary-round")
        self.scrollbar.pack(side="right", fill="y", padx=(0, 10))

        # text box
        self.log_box = ttk.Text(
            self,
            height=1,
            width=10,
            state="disabled",
            yscrollcommand=self.scrollbar.set,
        )
        self.log_box.pack(
            side="left", expand=True, fill="both", padx=(10, 0), pady=(0, 5)
        )

        self.scrollbar.config(command=self.log_box.yview)

        # Tag configuration
        self.log_box.tag_config("INFO")
        self.log_box.tag_config("WARNING", foreground="yellow")
        self.log_box.tag_config("ERROR", foreground="red")

        self.pull_log()

    def pull_log(self):
        """Check the log for new messages"""
        while True:
            packet = get_next_log()
            
            # Queue is empty
            if packet is None:
                break

            self.append_message(packet)

        self.after(100, self.pull_log)

    def append_message(self, packet):
        """Formats and inserts the message with conditional headers."""
        timestamp = packet["time"]
        level = packet["level"]
        msg = packet["msg"]

        # Show Level only if it's not 'INFO'
        if level == "INFO":
            # Format: [09:00:00] Found new file
            log_text = f"[{timestamp}] {msg}\n"
        else:
            # Format: [09:00:00] ERROR: Worker crashed
            log_text = f"[{timestamp}] {level}: {msg}\n"

        # 1. Unlock
        self.log_box.config(state="normal")

        # 2. Insert (apply the 'level' as a tag for coloring)
        self.log_box.insert("end", log_text, level)

        # 3. Scroll & Lock
        self.log_box.see("end")
        self.log_box.config(state="disabled")


class QueueStatus(ttk.Labelframe):
    def __init__(self, parent, backend):
        super().__init__(parent, text="Queue Status", bootstyle="info")

        self.backend = backend

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Remaining orders count
        ttk.Label(
            self,
            text="Remaining",
            font=("Segoe UI", 13),
            bootstyle="info"
        ).grid(row=0, column=0, pady=(10, 10,))

        self.remaining = ttk.Label(
            self,
            text="0",
            font=("Segoe UI", 20, "bold",),
            bootstyle="info"
        )
        self.remaining.grid(row=1, column=0, pady=(0, 10))

        # Skipped orders count
        ttk.Label(
            self,
            text="Skipped",
            font=("Segoe UI", 13),
            bootstyle="info"
        ).grid(row=0, column=1, pady=(10, 10,))

        self.skipped = ttk.Label(
            self,
            text="0",
            font=("Segoe UI", 20, "bold",),
            bootstyle="info"
        )
        self.skipped.grid(row=1, column=1, pady=(0, 10))
        
        # Start the loops
        self.update_remaining()
        self.update_skipped()

    def update_remaining(self):
        """Pulls the backend queue size and updates the counter"""
        try:
            # Pull the number
            remaining_count = self.backend.file_queue.qsize()
            # Display it
            self.remaining.configure(text=str(remaining_count))

        except Exception as e:
            logger.error(f"Remaining counter: {e}")
        
        # Loop the check
        self.after(200, self.update_remaining)

    def update_skipped(self):
        pass

class ModeSwitcher(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="Operation Mode", bootstyle="primary")

        self.mode = ttk.StringVar(
            value=settings.working_mode if settings.keep_working_mode else "off"
        )

        self.off_btn = ttk.Radiobutton(
            self,
            text="OFF",
            variable=self.mode,
            value="off",
            bootstyle="danger-toolbutton",
            command=self.update_backend
        )
        self.auto_btn = ttk.Radiobutton(
            self,
            text="AUTO",
            variable=self.mode,
            value="auto",
            bootstyle="success-toolbutton",
            command=self.update_backend
        )
        self.hybrid_btn = ttk.Radiobutton(
            self,
            text="HYBRID",
            variable=self.mode,
            value="hybrid",
            bootstyle="info-toolbutton",
            command=self.update_backend
        )

        self.off_btn.grid(row=0, column=0, padx=(10, 5), pady=10)
        self.auto_btn.grid(row=0, column=1, padx=5, pady=10)
        self.hybrid_btn.grid(row=0, column=2, padx=(5, 10), pady=10)

    def update_backend(self):
        settings.working_mode = self.mode.get().lower()
        if settings.keep_working_mode:
            settings.save()
        logger.info(f"Working mode: {self.mode.get()}")


class StatusBar(ttk.Labelframe):
    def __init__(self, parent):
        super().__init__(parent, text="Active Process", bootstyle="secondary")

        self.label = ttk.Label(
            self,
            text="Ready",
            font=("Segoe UI", 12),
            bootstyle="inverse-secondary",
            anchor="w",
        )
        self.label.pack(fill="both", padx=5, pady=2)

    def set_text(self, message):
        self.label.config(text=message)


class ControlPanel(ttk.Frame):
    def __init__(self, parent, backend):
        super().__init__(parent)

        self.parent = parent
        self.backend = backend
        # Custom style for the buttons to reduce the font size
        style = ttk.Style()
        style.configure(
            "Exit.danger.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 2)
        )
        style.configure(
            "Settings.secondary.TButton", font=("Segoe UI", 10), padding=(10, 2)
        )

        # Exit Button
        self.exit_btn = ttk.Button(
            self,
            text="Exit",
            style="Exit.danger.TButton",
            command=self.exit,
            width=6
        )
        self.exit_btn.pack(side="right", padx=(5, 0))

        # Settings Button
        self.settings_btn = ttk.Button(
            self,
            text="Settings",
            style="Settings.secondary.TButton",
            command=self.open_settings,
            width=6,
        )
        self.settings_btn.pack(side="left", padx=5)

    def exit(self):
        # Stop the threads
        self.backend.exit()

        # Destroy the UI
        self.parent.after(0, self.parent.destroy())
        self.parent.quit()


    def open_settings(self):
        settings_window = SettingsWindow(self)
        # Prevent the user from clicking the main window
        settings_window.grab_set()


class Dashboard(ttk.Frame):
    def __init__(self, parent, backend):
        super().__init__(parent)
        # -- LAYER 1 The Main Workspace --
        self.main_area = ttk.Frame(self)
        self.main_area.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        # Left panel: The Logger
        self.logger = VisualLogger(self.main_area)
        self.logger.pack(side="left", fill="both", expand=True)

        # Right panel: The Widgets
        self.right_panel = ttk.Frame(self.main_area)
        self.right_panel.pack(side="left", fill="y", padx=(10, 0), anchor="n")

        # 1. Queue Status
        self.queue_status = QueueStatus(self.right_panel, backend)
        self.queue_status.pack(side="top", fill="x", pady=(0, 10))

        # 2. Mode Switcher (Stacked Top, right underneath)
        self.mode_buttons = ModeSwitcher(self.right_panel)
        self.mode_buttons.pack(side="top", fill="x")

        # -- LAYER 2: The Footer --
        self.bottom_bar = ttk.Frame(self)
        self.bottom_bar.pack(side="bottom", fill="x", padx=10, pady=(0, 2))

        for i in range(5):
            self.bottom_bar.columnconfigure(i, weight=1)
        self.bottom_bar.columnconfigure(5, weight=0)

        # -- The Status Bar --
        self.status_bar = StatusBar(self.bottom_bar)
        self.status_bar.grid(row=0, column=0, columnspan=5, sticky="sew")

        # -- Settings & Exit Buttons --
        self.controls = ControlPanel(self.bottom_bar, backend)
        self.controls.grid(row=0, column=5, sticky="se", padx=(10, 0))
