import tkinter as tk
from tkinter import END, constants

import ttkbootstrap as ttk
from rapidfuzz import fuzz, process


class CodeSearch(ttk.Frame):
    def __init__(self, parent, code_list, descriptions_list, placeholder=""):
        super().__init__(parent, bootstyle="primary")

        # Store the data in a lists for easier searching
        self.code_list = code_list
        self.desc_list = descriptions_list

        # -- UI Setup --
        self.var = ttk.StringVar(value=placeholder)

        # The typing box
        self.entry = tk.Entry(self, textvariable=self.var, width=300)
        self.entry.pack(fill="x", expand=True)

        # The dropdown List
        self.listbox = tk.Listbox(
            self,
            height=5,
            selectmode=tk.SINGLE,
            exportselection=False,
            font=("Consolas", 9),
            activestyle="dotbox",
        )

        self.listbox_open = False

        # -- Bindings --
        # Fires every time a key is released
        self.entry.bind("<KeyRelease>", self.on_key_release)

        # Move focus to the listbox to scroll
        self.entry.bind("<Down>", self.on_arrow_down)
        self.entry.bind("<Up>", self.on_arrow_up)
        # Select the top item
        self.entry.bind("<Return>", self.on_select)

        # Close the dropdown if the user click somewhere else
        self.entry.bind("<FocusOut>", self.on_focus_out)
        # Handle clicking an item in the dropbox
        self.listbox.bind("<<ListboxSelect>>", self.on_list_click)

    def on_key_release(self, event):
        """Called whenever a key is released"""
        # 1. Skip navigation keys
        if event.keysym in ("Up", "Down", "Return", "Tab"):
            return

        # 2. Get the text
        typed = self.var.get().strip()
        if not typed:
            self.close_list()

        # 3. Fuzzy matching
        results = process.extract(
            typed,
            self.code_list,
            scorer=fuzz.token_sort_ratio,
            limit=5
        )
        if results:
            self.update_list(results)
        else:
            self.close_list()

    def update_list(self, matches):
        """Updates the suggestions in the listbox"""
        # 1. Clear old items
        self.listbox.delete(0, END)

        # 2. Insert new matches
        # Match format: (match_string, score, index)
        for match in matches:
            code = match[0]
            desc = self.desc_list[match[2]]
            text = f"{code} : {desc}"
            self.listbox.insert(END, text)

        # 3. Show the new listbox
        if not self.listbox_open:
            # Pack it under the Entry
            self.listbox.pack(fill="x", expand=True, pady=(0, 2))
            self.listbox_open = True

        # Highlight the first item automatically
        self.listbox.selection_set(0)
        self.listbox.activate(0)

    def on_arrow_down(self, event):
        """Move selection down in the suggestion box"""
        if not self.listbox_open or self.listbox.size() == 0:
            return

        # 1. Get the current index
        curr = self.listbox.curselection()
        if not curr:
            index = 0
        else:
            # 'curselection' returns a tuple with the index
            index = curr[0] + 1

        # 2. Loop at the bottom
        if index >= self.listbox.size():
            index = 0

        # 3. Update the highlight
        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)

    def on_arrow_up(self, event):
        """Move selection up in the suggestion box"""
        if not self.listbox_open or self.listbox.size() == 0:
            return

        # 1. Get the current index
        current = self.listbox.curselection()
        if not current:
            index = 0
        else:
            # 'curselection' returns a tuple with the index
            index = current[0] - 1

        # 2. Loop at the bottom
        if index < 0:
            index = self.listbox.size() - 1

        # 3. Update the highlight
        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)

    def on_select(self, event):
        """Selects the top item and puts it into the Entry"""
        if self.listbox_open and self.listbox.size() > 0:
            # Select top item
            self.listbox.selection_clear(0, END)
            self.listbox.selection_set(0)

            # Simulate a click
            self.on_list_click(None)

    def on_list_click(self, event):
        """Triggered when user clicks an item in the Listbox"""
        selection = self.listbox.curselection()
        if selection:
            # 1. Get text from listbox
            text = self.listbox.get(selection[0])
            text = text.split(" : ")[0].strip()
            # 2. Put it in the 'Entry' box
            self.var.set(text)

            # 3. Close the list and focus back on Entry
            self.close_list()
            self.entry.focus_set()
            self.entry.icursor(END)

    def on_focus_out(self, event):
        """Safely closes the list when user clicks away"""
        self.after(100, self._check_focus)

    def _check_focus(self):
        # If the new focus is not the listbox, close it
        if self.focus_get() != self.listbox:
            self.close_list()

    def close_list(self):
        """Hides the dropdown"""
        if self.listbox_open:
            self.listbox.pack_forget()
            self.listbox_open = False

    def _apply_styles(self):
        """Manually paints the standard Listbox to match the ttkbootstrap theme"""
        # 1. Get the current style object
        style = ttk.Style()

        # 2. Extract colors from the theme (using 'input' colors matches the Entry box)
        bg_color = style.colors.inputbg
        fg_color = style.colors.inputfg
        select_bg = style.colors.primary
        select_fg = style.colors.selectfg
        border_color = style.colors.border

        # 3. Configure the Listbox to blend in
        self.listbox.configure(
            bg=bg_color,
            fg=fg_color,
            selectbackground=select_bg,
            selectforeground=select_fg,
            highlightthickness=1,  # Thin border
            highlightbackground=border_color,
            highlightcolor=select_bg,  # Border turns primary color when focused
            relief="flat",  # Remove the 3D 'sunken' look
            borderwidth=0,
        )

    def get_code(self):
        """Returns the string inside the variable"""
        return self.var.get().strip()
