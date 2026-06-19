# file_integrity_monitor.py

import difflib
import hashlib
import json
import os
import platform
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, simpledialog

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


BASELINE_FILE = "fim_baseline.json"
NOTES_FILE = "fim_notes.json"


# =========================================================
# Hashing
# =========================================================

def sha256_hash(file_path):
    """Generate a SHA-256 hash for a file."""
    sha256 = hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    except (PermissionError, FileNotFoundError, OSError):
        return None


def read_text_snapshot(file_path):
    """
    Read file content as text so we can show what changed and possibly revert it.

    Returns:
        str if the file is readable text
        None if the file is binary, unreadable, or too large
    """

    max_size_bytes = 1_000_000

    try:
        if os.path.getsize(file_path) > max_size_bytes:
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    except (UnicodeDecodeError, PermissionError, FileNotFoundError, OSError):
        return None


def create_file_record(file_path):
    """
    Create a baseline record for one file.

    The record stores:
        - hash: integrity verification
        - snapshot: readable text content for diff output and revert support
        - size: file size in bytes
        - modified_time: last modified timestamp
    """

    file_hash = sha256_hash(file_path)

    if not file_hash:
        return None

    try:
        file_size = os.path.getsize(file_path)
        modified_time = os.path.getmtime(file_path)
    except OSError:
        file_size = None
        modified_time = None

    return {
        "hash": file_hash,
        "snapshot": read_text_snapshot(file_path),
        "size": file_size,
        "modified_time": modified_time
    }


def create_diff(old_text, new_text, file_path):
    """Create a readable line-by-line diff for modified text files."""

    if old_text is None or new_text is None:
        return "Change details unavailable. File is binary, unreadable, or too large."

    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"{file_path} - previous",
        tofile=f"{file_path} - current",
        lineterm=""
    )

    diff_text = "".join(diff)

    if not diff_text.strip():
        return "File changed, but no readable line-level difference was detected."

    return diff_text


# =========================================================
# File Monitor Event Handler
# =========================================================

class MonitorHandler(FileSystemEventHandler):
    """Handles file system events and tells the GUI to rescan."""

    def __init__(self, app):
        self.app = app

    def on_created(self, event):
        self.handle_event(event)

    def on_modified(self, event):
        self.handle_event(event)

    def on_deleted(self, event):
        self.handle_event(event)

    def on_moved(self, event):
        self.handle_event(event)

    def handle_event(self, event):
        if event.is_directory:
            return

        paths_to_check = [getattr(event, "src_path", None)]

        dest_path = getattr(event, "dest_path", None)

        if dest_path:
            paths_to_check.append(dest_path)

        ignored_internal_files = {
            os.path.abspath(BASELINE_FILE),
            os.path.abspath(NOTES_FILE)
        }

        for path in paths_to_check:
            if path and os.path.abspath(path) in ignored_internal_files:
                return

        self.app.log_message(
            "File system event detected. Scanning for changes...",
            "event_baseline"
        )

        # Immediate scan
        self.app.root.after(0, self.app.scan_for_changes)

        # Follow-up scans catch apps that save through temp files or delayed writes
        self.app.root.after(250, self.app.scan_for_changes)
        self.app.root.after(750, self.app.scan_for_changes)


# =========================================================
# GUI App
# =========================================================

class FileIntegrityMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Integrity Monitor")
        self.root.geometry("900x600")

        self.folder_to_watch = tk.StringVar(value="./watched")
        self.status_text = tk.StringVar(value="Status: Not monitoring")

        self.added_count = tk.StringVar(value="Added: 0")
        self.removed_count = tk.StringVar(value="Removed: 0")
        self.modified_count = tk.StringVar(value="Modified: 0")
        self.total_count = tk.StringVar(value="Total Changes: 0")

        self.observer = None
        self.is_monitoring = False

        self.pending_baseline = None
        self.last_scan_had_changes = False
        self.last_change_signature = None
        self.last_change_summary = None
        self.selected_file_path = None

        # Safety polling backup in case watchdog misses editor save events
        self.polling_job = None
        self.poll_interval_ms = 2000

        self.build_ui()

    # -----------------------------------------------------
    # UI Layout
    # -----------------------------------------------------

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="File Integrity Monitor",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=10)

        folder_frame = tk.Frame(self.root)
        folder_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(folder_frame, text="Folder to Watch:").pack(anchor="w")

        folder_input_frame = tk.Frame(folder_frame)
        folder_input_frame.pack(fill="x")

        self.folder_entry = tk.Entry(
            folder_input_frame,
            textvariable=self.folder_to_watch
        )
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_button = tk.Button(
            folder_input_frame,
            text="Browse",
            command=self.browse_folder,
            fg="black",
            disabledforeground="black"
        )
        browse_button.pack(side="right")

        # -------------------------------------------------
        # Button Area
        # -------------------------------------------------

        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=15, pady=10)

        button_style = {
            "width": 20,
            "fg": "black",
            "disabledforeground": "black",
            "bg": "light gray",
            "activeforeground": "black"
        }

        # Row 1: Baseline and monitoring workflow
        button_row_1 = tk.Frame(button_frame)
        button_row_1.pack(fill="x", pady=3)

        self.create_baseline_button = tk.Button(
            button_row_1,
            text="Create Baseline",
            command=self.create_baseline,
            **button_style
        )
        self.create_baseline_button.pack(side="left", padx=5)

        self.scan_button = tk.Button(
            button_row_1,
            text="Scan for Changes",
            command=self.scan_for_changes,
            **button_style
        )
        self.scan_button.pack(side="left", padx=5)

        self.start_button = tk.Button(
            button_row_1,
            text="Start Monitoring",
            command=self.start_monitoring,
            **button_style
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = tk.Button(
            button_row_1,
            text="Stop Monitoring",
            command=self.stop_monitoring,
            state="disabled",
            **button_style
        )
        self.stop_button.pack(side="left", padx=5)

        # Row 2: Analyst response workflow
        button_row_2 = tk.Frame(button_frame)
        button_row_2.pack(fill="x", pady=3)

        self.approve_button = tk.Button(
            button_row_2,
            text="Approve Changes",
            command=self.approve_changes,
            state="disabled",
            **button_style
        )
        self.approve_button.pack(side="left", padx=5)

        self.revert_button = tk.Button(
            button_row_2,
            text="Revert Changes",
            command=self.revert_changes,
            state="disabled",
            **button_style
        )
        self.revert_button.pack(side="left", padx=5)

        self.overwrite_button = tk.Button(
            button_row_2,
            text="Overwrite Data",
            command=self.overwrite_data,
            state="disabled",
            **button_style
        )
        self.overwrite_button.pack(side="left", padx=5)

        self.open_file_button = tk.Button(
            button_row_2,
            text="Open Selected File",
            command=self.open_selected_file,
            state="disabled",
            **button_style
        )
        self.open_file_button.pack(side="left", padx=5)

        # Row 3: Notes and cleanup
        button_row_3 = tk.Frame(button_frame)
        button_row_3.pack(fill="x", pady=3)

        self.note_button = tk.Button(
            button_row_3,
            text="Add Review Note",
            command=self.add_review_note,
            state="disabled",
            **button_style
        )
        self.note_button.pack(side="left", padx=5)

        clear_button = tk.Button(
            button_row_3,
            text="Clear Log",
            command=self.clear_log,
            **button_style
        )
        clear_button.pack(side="left", padx=5)

        dashboard_frame = tk.Frame(self.root, relief="groove", borderwidth=2)
        dashboard_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(
            dashboard_frame,
            textvariable=self.added_count,
            font=("Arial", 11, "bold"),
            fg="lime green"
        ).pack(side="left", padx=15, pady=8)

        tk.Label(
            dashboard_frame,
            textvariable=self.removed_count,
            font=("Arial", 11, "bold"),
            fg="DarkOrange1"
        ).pack(side="left", padx=15, pady=8)

        tk.Label(
            dashboard_frame,
            textvariable=self.modified_count,
            font=("Arial", 11, "bold"),
            fg="DeepSkyBlue"
        ).pack(side="left", padx=15, pady=8)

        tk.Label(
            dashboard_frame,
            textvariable=self.total_count,
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=15, pady=8)

        status_label = tk.Label(
            self.root,
            textvariable=self.status_text,
            font=("Arial", 11, "bold"),
            fg="lime green"
        )
        status_label.pack(anchor="w", padx=15)

        log_label = tk.Label(
            self.root,
            text="Event Log:",
            font=("Arial", 12, "bold")
        )
        log_label.pack(anchor="w", padx=15, pady=(10, 0))

        self.log_box = scrolledtext.ScrolledText(
            self.root,
            height=30,
            wrap=tk.WORD
        )
        self.log_box.pack(fill="both", expand=True, padx=15, pady=10)

        # Text color tags
        self.log_box.tag_config("event_added", foreground="lime green")
        self.log_box.tag_config("event_removed", foreground="DarkOrange1")
        self.log_box.tag_config("event_modified", foreground="DeepSkyBlue")
        self.log_box.tag_config("event_warning", foreground="red")
        self.log_box.tag_config("change_red", foreground="red")
        self.log_box.tag_config("event_baseline", foreground="gray")

    # -----------------------------------------------------
    # Folder Selection
    # -----------------------------------------------------

    def browse_folder(self):
        selected_folder = filedialog.askdirectory()

        if selected_folder:
            self.folder_to_watch.set(selected_folder)
            self.log_message(f"Selected folder: {selected_folder}")

    # -----------------------------------------------------
    # Logging
    # -----------------------------------------------------

    def log_message(self, message, tag=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"

        if tag:
            self.log_box.insert(tk.END, full_message, tag)
        else:
            self.log_box.insert(tk.END, full_message)

        self.log_box.see(tk.END)

    def log_file_event(self, event_label, file_path, tag=None):
        """
        Log a file event with a clickable file path.

        Clicking the file path selects it for opening or overwriting.
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.log_box.insert(tk.END, f"[{timestamp}] ")

        if tag:
            self.log_box.insert(tk.END, f"{event_label} ", tag)
        else:
            self.log_box.insert(tk.END, f"{event_label} ")

        link_tag = f"file_link_{abs(hash(file_path))}"

        self.log_box.insert(tk.END, file_path + "\n", link_tag)

        self.log_box.tag_config(
            link_tag,
            foreground="DeepSkyBlue",
            underline=True
        )

        self.log_box.tag_bind(
            link_tag,
            "<Button-1>",
            lambda event, path=file_path: self.select_file_from_log(path)
        )

        self.log_box.tag_bind(
            link_tag,
            "<Enter>",
            lambda event: self.log_box.config(cursor="hand2")
        )

        self.log_box.tag_bind(
            link_tag,
            "<Leave>",
            lambda event: self.log_box.config(cursor="")
        )

        self.log_box.see(tk.END)

    def select_file_from_log(self, file_path):
        """
        Select a file from the event log.

        This selected file can then be opened or used for overwrite.
        """

        self.selected_file_path = file_path
        self.open_file_button.config(state="normal")

        self.log_message(
            f"Selected file: {file_path}",
            "event_baseline"
        )

    def log_diff(self, diff_text):
        """
        Display diff output.

        Normal diff text stays the default color.
        Only the changed new values inside added lines are colored red.
        """

        lines = diff_text.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i]

            if line.startswith("-") and not line.startswith("---"):
                removed_lines = []
                added_lines = []

                while (
                    i < len(lines)
                    and lines[i].startswith("-")
                    and not lines[i].startswith("---")
                ):
                    removed_lines.append(lines[i][1:])
                    i += 1

                while (
                    i < len(lines)
                    and lines[i].startswith("+")
                    and not lines[i].startswith("+++")
                ):
                    added_lines.append(lines[i][1:])
                    i += 1

                self.log_changed_block(removed_lines, added_lines)
                continue

            self.log_box.insert(tk.END, line + "\n")
            i += 1

        self.log_box.insert(tk.END, "\n")
        self.log_box.see(tk.END)

    def log_changed_block(self, removed_lines, added_lines):
        """
        Print a changed diff block.

        Removed lines stay default color.
        Added lines stay default color except for the changed new value.
        """

        for old_line in removed_lines:
            self.log_box.insert(tk.END, "-" + old_line + "\n")

        used_old_indexes = set()

        for new_line in added_lines:
            matching_old_line = self.find_matching_old_line(
                new_line,
                removed_lines,
                used_old_indexes
            )

            self.insert_added_line_with_highlight(matching_old_line, new_line)

    def find_matching_old_line(self, new_line, removed_lines, used_old_indexes):
        """
        Try to match an added line to the correct removed line.
        """

        new_label = self.extract_label(new_line)

        for index, old_line in enumerate(removed_lines):
            if index in used_old_indexes:
                continue

            old_label = self.extract_label(old_line)

            if old_label and new_label and old_label == new_label:
                used_old_indexes.add(index)
                return old_line

        best_index = None
        best_score = 0

        for index, old_line in enumerate(removed_lines):
            if index in used_old_indexes:
                continue

            score = difflib.SequenceMatcher(None, old_line, new_line).ratio()

            if score > best_score:
                best_score = score
                best_index = index

        if best_index is not None:
            used_old_indexes.add(best_index)
            return removed_lines[best_index]

        return ""

    def extract_label(self, line):
        """
        Extract a clean label before the colon.

        Handles:
            Admin Rights: Yes
            \\cf0 Login Pswrd: password
        """

        if ":" not in line:
            return ""

        label = line.split(":", 1)[0].strip()
        return self.clean_rtf_label(label)

    def clean_rtf_label(self, label_text):
        """
        Clean a label so raw RTF control words do not break matching.

        Example:
            \\cf0 Login Pswrd

        Becomes:
            Login Pswrd
        """

        label_parts = label_text.strip().split()

        cleaned_parts = [
            part
            for part in label_parts
            if not part.startswith("\\")
        ]

        return " ".join(cleaned_parts).strip()

    def insert_added_line_with_highlight(self, old_line, new_line):
        """
        Insert an added diff line.

        The leading + stays normal.
        The label stays normal.
        Only the new changed value is red.
        """

        self.log_box.insert(tk.END, "+")

        if ":" in new_line:
            label_part, value_part = new_line.split(":", 1)

            self.log_box.insert(tk.END, label_part + ":")

            leading_spaces = len(value_part) - len(value_part.lstrip(" "))
            self.log_box.insert(tk.END, value_part[:leading_spaces])

            value = value_part[leading_spaces:]

            trailing_backslashes = ""

            while value.endswith("\\"):
                trailing_backslashes = "\\" + trailing_backslashes
                value = value[:-1]

            self.log_box.insert(tk.END, value, "change_red")
            self.log_box.insert(tk.END, trailing_backslashes)
            self.log_box.insert(tk.END, "\n")
            return

        matcher = difflib.SequenceMatcher(None, old_line, new_line)

        for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
            new_text = new_line[new_start:new_end]

            if tag == "equal":
                self.log_box.insert(tk.END, new_text)
            else:
                self.log_box.insert(tk.END, new_text, "change_red")

        self.log_box.insert(tk.END, "\n")

    def clear_log(self):
        self.log_box.delete("1.0", tk.END)

    # -----------------------------------------------------
    # Dashboard
    # -----------------------------------------------------

    def update_dashboard(self, added_total, removed_total, modified_total):
        total_changes = added_total + removed_total + modified_total

        self.added_count.set(f"Added: {added_total}")
        self.removed_count.set(f"Removed: {removed_total}")
        self.modified_count.set(f"Modified: {modified_total}")
        self.total_count.set(f"Total Changes: {total_changes}")

    # -----------------------------------------------------
    # Review Button State
    # -----------------------------------------------------

    def set_review_buttons(self, enabled):
        """Enable or disable buttons that require pending changes."""

        state = "normal" if enabled else "disabled"

        self.approve_button.config(state=state)
        self.revert_button.config(state=state)
        self.overwrite_button.config(state=state)
        self.open_file_button.config(state=state)
        self.note_button.config(state=state)

    # -----------------------------------------------------
    # Baseline Storage
    # -----------------------------------------------------

    def load_old_baseline(self):
        if not os.path.exists(BASELINE_FILE):
            return {}

        try:
            with open(BASELINE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        except (json.JSONDecodeError, OSError):
            self.log_message("Warning: Could not read existing baseline file.", "event_warning")
            return {}

    def save_baseline(self, baseline):
        with open(BASELINE_FILE, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=4)

    def build_current_baseline(self):
        folder = self.folder_to_watch.get()

        if not folder:
            messagebox.showwarning("Missing Folder", "Please select a folder to watch.")
            return None

        os.makedirs(folder, exist_ok=True)

        current_baseline = {}

        ignored_internal_files = {
            os.path.abspath(BASELINE_FILE),
            os.path.abspath(NOTES_FILE)
        }

        for root_dir, dirs, files in os.walk(folder):
            for file_name in files:
                path = os.path.join(root_dir, file_name)

                if os.path.abspath(path) in ignored_internal_files:
                    continue

                file_record = create_file_record(path)

                if file_record:
                    current_baseline[path] = file_record

        return current_baseline

    # -----------------------------------------------------
    # Review Notes
    # -----------------------------------------------------

    def load_notes(self):
        """Load review notes from disk."""

        if not os.path.exists(NOTES_FILE):
            return []

        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        except (json.JSONDecodeError, OSError):
            self.log_message("Warning: Could not read notes file.", "event_warning")
            return []

    def save_notes(self, notes):
        """Save review notes to disk."""

        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=4)

    def add_review_note(self):
        """
        Add a custom review note for the pending change set.
        """

        if not self.last_scan_had_changes or self.last_change_summary is None:
            self.log_message("No pending changes to document.")
            return

        note = simpledialog.askstring(
            "Add Review Note",
            "Enter a note for this change:"
        )

        if not note:
            self.log_message("Review note canceled.")
            return

        notes = self.load_notes()

        note_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "folder": self.folder_to_watch.get(),
            "action": "review_note",
            "note": note,
            "changes": self.last_change_summary
        }

        notes.append(note_record)
        self.save_notes(notes)

        self.log_message(f"Review note added: {note}", "event_baseline")

    # -----------------------------------------------------
    # Open Selected File
    # -----------------------------------------------------

    def open_selected_file(self):
        """
        Open the selected file using the operating system default app.

        Windows: os.startfile
        macOS: open
        Linux: xdg-open
        """

        if not self.selected_file_path:
            self.log_message(
                "No file selected. Click a file path in the output first.",
                "event_warning"
            )
            return

        file_path = self.selected_file_path

        if not os.path.exists(file_path):
            self.log_message(
                f"Selected file does not exist: {file_path}",
                "event_warning"
            )
            return

        try:
            self.open_file_cross_platform(file_path)
            self.log_message(f"Opened file: {file_path}", "event_baseline")

        except (OSError, subprocess.CalledProcessError) as error:
            self.log_message(f"Could not open file: {error}", "event_warning")

    def open_file_cross_platform(self, file_path):
        """
        Open a file with the default app on Windows, macOS, or Linux.
        """

        system_name = platform.system()

        if system_name == "Windows":
            os.startfile(file_path)

        elif system_name == "Darwin":
            subprocess.run(["open", file_path], check=True)

        elif system_name == "Linux":
            subprocess.run(["xdg-open", file_path], check=True)

        else:
            raise OSError(f"Unsupported operating system: {system_name}")

    # -----------------------------------------------------
    # Baseline Workflow
    # -----------------------------------------------------

    def create_baseline(self):
        """
        Create a trusted baseline from the current file state.
        """

        current_baseline = self.build_current_baseline()

        if current_baseline is None:
            return

        self.save_baseline(current_baseline)

        self.pending_baseline = None
        self.last_scan_had_changes = False
        self.last_change_signature = None
        self.last_change_summary = None
        self.selected_file_path = None

        self.set_review_buttons(False)
        self.update_dashboard(0, 0, 0)

        self.log_message(
            f"Trusted baseline created with {len(current_baseline)} file(s).",
            "event_baseline"
        )

    def scan_for_changes(self):
        """
        Scan current files against the trusted baseline.

        Important:
            This does NOT automatically update the trusted baseline.
            Changes must be approved manually.
        """

        if not os.path.exists(BASELINE_FILE):
            self.log_message(
                "No baseline found. Create a baseline first.",
                "event_warning"
            )
            return

        old_baseline = self.load_old_baseline()
        new_baseline = self.build_current_baseline()

        if new_baseline is None:
            return

        added = set(new_baseline) - set(old_baseline)
        removed = set(old_baseline) - set(new_baseline)

        modified = {
            file_path
            for file_path in new_baseline
            if (
                file_path in old_baseline
                and new_baseline[file_path]["hash"] != old_baseline[file_path]["hash"]
            )
        }

        added_total = len(added)
        removed_total = len(removed)
        modified_total = len(modified)

        self.update_dashboard(added_total, removed_total, modified_total)

        if not added and not removed and not modified:
            self.pending_baseline = None
            self.last_scan_had_changes = False
            self.last_change_signature = None
            self.last_change_summary = None
            self.selected_file_path = None
            self.set_review_buttons(False)

            if not self.is_monitoring:
                self.log_message("No file changes detected.")

            return

        self.last_change_summary = {
            "added": sorted(added),
            "removed": sorted(removed),
            "modified": sorted(modified)
        }

        change_signature = (
            tuple(sorted(added)),
            tuple(sorted(removed)),
            tuple(sorted(modified)),
            tuple(
                sorted(
                    new_baseline[file_path]["hash"]
                    for file_path in modified
                )
            )
        )

        self.pending_baseline = new_baseline
        self.last_scan_had_changes = True
        self.set_review_buttons(True)

        if change_signature == self.last_change_signature:
            return

        self.last_change_signature = change_signature

        self.log_message(
            "Changes detected. Review before approving baseline update.",
            "event_warning"
        )

        for file_path in sorted(added):
            self.log_file_event("[ADDED]", file_path, "event_added")

        for file_path in sorted(removed):
            self.log_file_event("[REMOVED]", file_path, "event_removed")

        for file_path in sorted(modified):
            self.log_file_event("[MODIFIED]", file_path, "event_modified")

            old_snapshot = old_baseline[file_path].get("snapshot")
            new_snapshot = new_baseline[file_path].get("snapshot")

            diff_text = create_diff(old_snapshot, new_snapshot, file_path)

            self.log_message("Change details:")
            self.log_diff(diff_text)

    def approve_changes(self):
        """
        Approve the current detected changes.

        This updates the trusted baseline to the latest scanned file state.
        """

        if not self.last_scan_had_changes or self.pending_baseline is None:
            self.log_message("No pending changes to approve.")
            return

        confirm = messagebox.askyesno(
            "Approve Changes",
            "Approve these changes and update the trusted baseline?"
        )

        if not confirm:
            self.log_message("Baseline update canceled.")
            return

        note = simpledialog.askstring(
            "Approval Note",
            "Optional note for this approved change:"
        )

        if note:
            notes = self.load_notes()

            note_record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "folder": self.folder_to_watch.get(),
                "action": "approved",
                "note": note,
                "changes": self.last_change_summary
            }

            notes.append(note_record)
            self.save_notes(notes)

            self.log_message(f"Approval note added: {note}", "event_baseline")

        self.save_baseline(self.pending_baseline)

        self.pending_baseline = None
        self.last_scan_had_changes = False
        self.last_change_signature = None
        self.last_change_summary = None
        self.selected_file_path = None

        self.set_review_buttons(False)
        self.update_dashboard(0, 0, 0)

        self.log_message(
            "Changes approved. Trusted baseline updated.",
            "event_baseline"
        )

    def revert_changes(self):
        """
        Revert pending changes back to the trusted baseline.

        Behavior:
            Added files are deleted.
            Removed text files are restored from the baseline snapshot.
            Modified text files are restored from the baseline snapshot.

        Limitation:
            Binary files cannot be restored unless a readable snapshot exists.
        """

        if not self.last_scan_had_changes or self.pending_baseline is None:
            self.log_message("No pending changes to revert.")
            return

        confirm = messagebox.askyesno(
            "Revert Changes",
            "Revert files back to the trusted baseline?\n\n"
            "Added files will be deleted.\n"
            "Modified text files will be restored.\n"
            "Removed text files will be recreated."
        )

        if not confirm:
            self.log_message("Revert canceled.")
            return

        old_baseline = self.load_old_baseline()
        new_baseline = self.pending_baseline

        added = set(new_baseline) - set(old_baseline)
        removed = set(old_baseline) - set(new_baseline)

        modified = {
            file_path
            for file_path in new_baseline
            if (
                file_path in old_baseline
                and new_baseline[file_path]["hash"] != old_baseline[file_path]["hash"]
            )
        }

        reverted_count = 0
        skipped_count = 0

        for file_path in sorted(added):
            try:
                os.remove(file_path)
                reverted_count += 1
                self.log_message(
                    f"[REVERTED ADDED FILE] Deleted {file_path}",
                    "event_removed"
                )

            except OSError:
                skipped_count += 1
                self.log_message(
                    f"[REVERT FAILED] Could not delete {file_path}",
                    "event_warning"
                )

        for file_path in sorted(removed):
            old_snapshot = old_baseline[file_path].get("snapshot")

            if old_snapshot is None:
                skipped_count += 1
                self.log_message(
                    f"[REVERT SKIPPED] No text snapshot available for removed file: {file_path}",
                    "event_warning"
                )
                continue

            try:
                folder_name = os.path.dirname(file_path)

                if folder_name:
                    os.makedirs(folder_name, exist_ok=True)

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(old_snapshot)

                reverted_count += 1
                self.log_message(
                    f"[REVERTED REMOVED FILE] Restored {file_path}",
                    "event_added"
                )

            except OSError:
                skipped_count += 1
                self.log_message(
                    f"[REVERT FAILED] Could not restore {file_path}",
                    "event_warning"
                )

        for file_path in sorted(modified):
            old_snapshot = old_baseline[file_path].get("snapshot")

            if old_snapshot is None:
                skipped_count += 1
                self.log_message(
                    f"[REVERT SKIPPED] No text snapshot available for modified file: {file_path}",
                    "event_warning"
                )
                continue

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(old_snapshot)

                reverted_count += 1
                self.log_message(
                    f"[REVERTED MODIFIED FILE] Restored {file_path}",
                    "event_modified"
                )

            except OSError:
                skipped_count += 1
                self.log_message(
                    f"[REVERT FAILED] Could not restore {file_path}",
                    "event_warning"
                )

        self.pending_baseline = None
        self.last_scan_had_changes = False
        self.last_change_signature = None
        self.last_change_summary = None
        self.selected_file_path = None

        self.set_review_buttons(False)
        self.update_dashboard(0, 0, 0)

        self.log_message(
            f"Revert complete. Reverted: {reverted_count}. Skipped: {skipped_count}.",
            "event_baseline"
        )

    def overwrite_data(self):
        """
        Overwrite a field/value pair inside a modified or added text file.

        This is useful when:
            - the old value should not be trusted
            - the changed value is suspicious
            - the analyst wants to replace the value with a known-good value

        Security note:
            The replacement value is written to the file, but not logged.
        """

        if not self.last_scan_had_changes or self.last_change_summary is None:
            self.log_message("No pending changes available for overwrite.")
            return

        candidate_files = (
            self.last_change_summary.get("modified", [])
            + self.last_change_summary.get("added", [])
        )

        if not candidate_files:
            self.log_message(
                "No modified or added files available for overwrite.",
                "event_warning"
            )
            return

        if self.selected_file_path in candidate_files:
            file_path = self.selected_file_path
        elif len(candidate_files) == 1:
            file_path = candidate_files[0]
        else:
            file_list = "\n".join(
                f"{index + 1}. {path}"
                for index, path in enumerate(candidate_files)
            )

            file_choice = simpledialog.askinteger(
                "Choose File",
                "Select the file number to overwrite:\n\n" + file_list,
                minvalue=1,
                maxvalue=len(candidate_files)
            )

            if file_choice is None:
                self.log_message("Overwrite canceled.")
                return

            file_path = candidate_files[file_choice - 1]

        field_label = simpledialog.askstring(
            "Overwrite Data",
            "Enter the field label to update.\n\nExample: Login Pswrd"
        )

        if not field_label:
            self.log_message("Overwrite canceled.")
            return

        replacement_value = simpledialog.askstring(
            "Replacement Value",
            "Enter the replacement value.\n\nThis value will NOT be written to the event log.",
            show="*"
        )

        if replacement_value is None:
            self.log_message("Overwrite canceled.")
            return

        confirm = messagebox.askyesno(
            "Confirm Overwrite",
            f"Overwrite the value for this field?\n\n"
            f"File:\n{file_path}\n\n"
            f"Field:\n{field_label}\n\n"
            "The replacement value will be written to the file but not logged."
        )

        if not confirm:
            self.log_message("Overwrite canceled.")
            return

        overwrite_result = self.replace_field_value_in_file(
            file_path,
            field_label,
            replacement_value
        )

        if not overwrite_result:
            self.log_message(
                f"Overwrite failed. Field not found or file could not be updated: {field_label}",
                "event_warning"
            )
            return

        current_baseline = self.build_current_baseline()

        if current_baseline is None:
            self.log_message(
                "Overwrite completed, but baseline could not be rebuilt.",
                "event_warning"
            )
            return

        self.save_baseline(current_baseline)

        self.pending_baseline = None
        self.last_scan_had_changes = False
        self.last_change_signature = None
        self.last_change_summary = None
        self.selected_file_path = None

        self.set_review_buttons(False)
        self.update_dashboard(0, 0, 0)

        notes = self.load_notes()

        note_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "folder": self.folder_to_watch.get(),
            "action": "overwrite_data",
            "file": file_path,
            "field": field_label,
            "note": "Field value overwritten by analyst. Replacement value was not logged.",
            "changes": "Trusted baseline updated after overwrite."
        }

        notes.append(note_record)
        self.save_notes(notes)

        self.log_message(
            f"Data overwrite completed for field: {field_label}",
            "event_baseline"
        )
        self.log_message(
            "Replacement value was not written to the event log.",
            "event_baseline"
        )
        self.log_message(
            "Trusted baseline updated after overwrite.",
            "event_baseline"
        )

    def replace_field_value_in_file(self, file_path, field_label, replacement_value):
        """
        Replace the value after a matching field label.

        Supports plain text lines:
            Login Pswrd: oldvalue

        Supports raw RTF-style lines:
            \\cf0 Login Pswrd: oldvalue\\

        The label is matched after removing simple RTF control words.
        """

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        except (UnicodeDecodeError, PermissionError, FileNotFoundError, OSError):
            return False

        updated_lines = []
        replacement_done = False

        target_label = field_label.strip()

        for line in lines:
            if ":" not in line:
                updated_lines.append(line)
                continue

            label_part, value_part = line.split(":", 1)
            clean_label = self.clean_rtf_label(label_part)

            if clean_label != target_label:
                updated_lines.append(line)
                continue

            leading_spaces = len(value_part) - len(value_part.lstrip(" "))
            spaces = value_part[:leading_spaces]

            newline_char = ""

            if value_part.endswith("\n"):
                newline_char = "\n"
                value_part = value_part[:-1]

            trailing_backslashes = ""

            while value_part.endswith("\\"):
                trailing_backslashes = "\\" + trailing_backslashes
                value_part = value_part[:-1]

            new_line = (
                label_part
                + ":"
                + spaces
                + replacement_value
                + trailing_backslashes
                + newline_char
            )

            updated_lines.append(new_line)
            replacement_done = True

        if not replacement_done:
            return False

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(updated_lines)

        except OSError:
            return False

        return True

    # -----------------------------------------------------
    # Polling Backup
    # -----------------------------------------------------

    def start_polling_backup(self):
        """
        Start a polling backup while monitoring is active.

        This catches file changes even if watchdog misses an editor save event.
        """

        if self.polling_job is not None:
            self.root.after_cancel(self.polling_job)

        self.polling_job = self.root.after(
            self.poll_interval_ms,
            self.run_polling_backup
        )

    def run_polling_backup(self):
        """
        Periodically scan for changes while monitoring is active.
        """

        self.polling_job = None

        if not self.is_monitoring:
            return

        self.scan_for_changes()

        self.polling_job = self.root.after(
            self.poll_interval_ms,
            self.run_polling_backup
        )

    def stop_polling_backup(self):
        """
        Stop the polling backup.
        """

        if self.polling_job is not None:
            self.root.after_cancel(self.polling_job)
            self.polling_job = None

    # -----------------------------------------------------
    # Monitoring Controls
    # -----------------------------------------------------

    def start_monitoring(self):
        folder = self.folder_to_watch.get()

        if not folder:
            messagebox.showwarning("Missing Folder", "Please select a folder to watch.")
            return

        os.makedirs(folder, exist_ok=True)

        if self.is_monitoring:
            return

        if not os.path.exists(BASELINE_FILE):
            messagebox.showwarning(
                "Missing Baseline",
                "Create a trusted baseline before starting monitoring."
            )
            return

        self.scan_for_changes()

        self.observer = Observer()
        self.observer.schedule(
            MonitorHandler(self),
            path=folder,
            recursive=True
        )

        self.observer.start()
        self.is_monitoring = True

        self.status_text.set(f"Status: Monitoring {folder}")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.folder_entry.config(state="disabled")
        self.create_baseline_button.config(state="disabled")

        self.start_polling_backup()

        self.log_message("Monitoring started.")
        self.log_message(
            "Polling backup enabled. The folder will also be checked every 2 seconds.",
            "event_baseline"
        )

    def stop_monitoring(self):
        self.stop_polling_backup()

        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

        self.is_monitoring = False

        self.status_text.set("Status: Not monitoring")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.folder_entry.config(state="normal")
        self.create_baseline_button.config(state="normal")

        self.log_message("Monitoring stopped.")

    def on_close(self):
        if self.is_monitoring:
            self.stop_monitoring()

        self.root.destroy()


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = FileIntegrityMonitorGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
