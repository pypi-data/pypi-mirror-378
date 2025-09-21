import asyncio
import psutil
from typing import List, Dict, Any, Optional

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, DataTable, Input, Static, Button
from textual.screen import ModalScreen
from textual.containers import Horizontal, Container, Vertical
from textual import on
from textual.events import Key

from .scaner import scan_ports,scan_changes, check_for_conflict
from pathlib import Path
import yaml
from .notifyer import alert_conflict 

async def map_table(data_list: List[Dict[str, Any]], old_data: List[Dict[str, Any]], filter_mode: str):
    from .utils import get_port_description

    table_data = []
    for item in data_list:
        pid = str(item.get("pid", "")) if item.get("pid", "") is not None else ""
        port = str(item.get("port", ""))
        process_name = item.get("process_name", "") or ""
        status = item.get("status", "") or ""
        action_label = "[red]KILL[/red]"

        note_parts = []

        # Precompute flags
        is_new = item in await scan_changes(old_data, data_list)
        is_conflict = bool(item.get("note"))

                 
        if is_conflict and is_new:
            alert_conflict(port, app_name=process_name)

        # Apply filter mode
        if filter_mode == "all":
            if is_new:
                note_parts.append("[green]NEW[/green]")
            if is_conflict:
                note_parts.append("[yellow]⚠ Conflict[/yellow]")
        elif filter_mode == "conflict":
            if not is_conflict:
                continue
            note_parts.append("[yellow]⚠ Conflict[/yellow]")
        elif filter_mode == "new":
            if not is_new:
                continue
            note_parts.append("[green]NEW[/green]")

        note = " ".join(note_parts)
        table_data.append((pid, port, process_name, status, action_label, note))

    return table_data


def apply_text_filter(data_list: List[Dict[str, Any]], text_filter: Optional[str]) -> List[Dict[str, Any]]:
    """Apply text filtering to the data list locally without re-scanning"""
    if not text_filter:
        return data_list
    
    text_filter = text_filter.lower()
    filtered_data = []
    
    for item in data_list:
        pid = str(item.get("pid", "")).lower()
        port = str(item.get("port", "")).lower()
        process_name = str(item.get("process_name", "")).lower()
        
        # Check if filter matches any field
        if (text_filter in pid or 
            text_filter in port or 
            text_filter in process_name):
            filtered_data.append(item)
    
    return filtered_data


class KillConfirmation(ModalScreen[bool]):
    def __init__(self, pid: int, process_name: str) -> None:
        super().__init__()
        self.pid = pid
        self.process_name = process_name

    def compose(self) -> ComposeResult:
        yield Container(
            Static(
                f"Do you really want to KILL\n\n[bold red]{self.process_name}[/] (PID {self.pid})?",
                classes="dialog-message",
            ),
            Horizontal(
                Button("Yes", id="yes"),
                Button("No", id="no"),
                classes="dialog-buttons",
            ),
            classes="dialog-box",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            # Note: remove heavy work from UI thread — but small terminate/kill is OK here
            try:
                proc = psutil.Process(self.pid)
                proc.terminate()
                gone, alive = psutil.wait_procs([proc], timeout=3)
                if proc in gone:
                    self.dismiss(True)
                else:
                    proc.kill()
                    gone, alive = psutil.wait_procs([proc], timeout=2)
                    self.dismiss(True)
            except psutil.NoSuchProcess:
                # already gone
                self.dismiss(True)
            except Exception:
                self.dismiss(False)
        elif event.button.id == "no":
            self.dismiss(False)


class PortWatch(App):
    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #main_content {
        padding: 1 2;
        height: 100%;
    }

    #filter_bar {
        height: auto;
        padding: 1 0;
        align: center middle;
        background: $background;
        border: tall $primary 20%;
        
        margin-bottom: 1;
         
    }

    #filter_bar .icon {
        color: $text-disabled;
        width: 4;
        content-align: center middle;
    }

    .filter_input {
        width: 50%;
        margin-right: 1;
    }

    .filter_btn {
        width: auto;
        min-width: 10;
        padding: 0 2;
        border: none;
        color: $text;
        background: transparent;
        transition: background 0.2s;
    }

    .filter_btn:hover {
        background: $primary 20%;
    }

    .filter_btn--active {
        background: $secondary;
        color: $text;
        border: tall $secondary;
        
        
    }

    .config_btn {
        margin-left: 2;
        padding: 0 2;
        height: 3;
    }

    .data_table {
        height: 1fr;
        border: tall $primary 15%;
         
    }

     
    .data_table > .datatable--header {
        background: $primary 15%;
        color: $text;
        text-style: bold;
        padding: 0 1;
    }

     
    .data_table > .datatable--cursor,
    .data_table > .datatable--even,
    .data_table > .datatable--odd {
        padding: 0 1;
    }

    Footer {
        background: $primary;
        color: $text;
    }
"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filter: Optional[str] = None
        self.conns: List[Dict[str, Any]] = []  
        self.filter_mode: str = "all"  # "all", "new", "conflict"
        self._last_refresh_data: List[Dict[str, Any]] = []  # Store last scan results
        self._refresh_in_progress = False
        
        # self.dev_ports = _get_port_config()
        

    # In PortWatch class

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main_content"):
            with Horizontal(id="filter_bar"):
                yield Static("🔍", classes="icon")
                yield Input(
                    id="input",
                    placeholder="Filter processes or ports (e.g. Chrome, 3000)",
                    classes="filter_input"
                )
                yield Button("All", id="filter_all", classes="filter_btn filter_btn--active")
                yield Button("🆕 New", id="filter_new", classes="filter_btn")
                yield Button("⚠️ Conflict", id="filter_conflict", classes="filter_btn")
                yield Button("⚙️ Config", id="open_config", variant="primary", classes="config_btn")
            yield DataTable(id="port_table", classes="data_table")
        yield Footer()
        
    
    # handle filter buttons with instant refresh
    
    @on(Button.Pressed, "#filter_all")
    def set_filter_all(self):
        self.filter_mode = "all"
        self.update_button_styles()
        # Instant refresh using cached data
        asyncio.create_task(self._refresh_display_instantly())

    @on(Button.Pressed, "#filter_new")
    def set_filter_new(self):
        self.filter_mode = "new"
        self.update_button_styles()
        # Instant refresh using cached data
        asyncio.create_task(self._refresh_display_instantly())

    @on(Button.Pressed, "#filter_conflict")
    def set_filter_conflict(self):
        self.filter_mode = "conflict"
        self.update_button_styles()
        # Instant refresh using cached data
        asyncio.create_task(self._refresh_display_instantly())
        
    def update_button_styles(self):
        """Highlight active filter button."""
        for mode in ["all", "new", "conflict"]:
            button = self.query_one(f"#filter_{mode}", Button)
            if self.filter_mode == mode:
                button.add_class("filter_btn--active")
            else:
                button.remove_class("filter_btn--active")
            
        
    # open config 

    @on(Button.Pressed, "#open_config")
    async def open_config_modal(self):
        from .portconfig_screen import PortConfigModal
        await self.push_screen(PortConfigModal())

    @on(Input.Changed)
    def input_changed(self, event: Input.Changed) -> None:
        self.filter = event.value.strip() or None
        # Instant filtering using cached data
        asyncio.create_task(self._refresh_display_instantly())

    async def on_ready(self) -> None:
        self.table = self.query_one("#port_table", DataTable)
        self.table.cursor_type = "row"
        
        # # check computer notification is enabled 
        # if not notification_is_enabled():
        #     await self.push_screen(NotificationNotEnabledAlert())  

        if not self.table.columns:
            # define columns matching map_table output
            self.table.add_columns("PID", "PORT", "PROCESS", "STATUS", "ACTION", "NOTE")

        # Initial scan and start background refresh
        await self._do_data_scan()
        asyncio.create_task(self._background_refresh_loop())

    async def _background_refresh_loop(self) -> None:
        """Background loop that only scans for new data every 2 seconds"""
        while True:
            await asyncio.sleep(2)  # Reduced from 3 to 2 seconds
            if not self._refresh_in_progress:
                await self._do_data_scan()

    async def _do_data_scan(self) -> None:
        """Scan for new data and refresh display"""
        try:
            self._refresh_in_progress = True
            
            # Always scan without text filter to get complete data
            new_conns = await scan_ports(None)
            
            # Update our data store
            old_conns = self.conns.copy()
            self.conns = new_conns
            self._last_refresh_data = new_conns
            
            # Refresh the display with current filters
            await self._refresh_display_with_data(new_conns, old_conns)
            
            self.log(f"PortWatch: scanned {len(new_conns)} connections")
        except Exception as e:
            self.log(f"PortWatch error during scan: {e}")
        finally:
            self._refresh_in_progress = False

    async def _refresh_display_instantly(self) -> None:
        """Instantly refresh display using cached data without re-scanning"""
        if not self._last_refresh_data:
            return
        
        try:
            await self._refresh_display_with_data(self._last_refresh_data, self.conns)
        except Exception as e:
            self.log(f"PortWatch error during instant refresh: {e}")

    async def _refresh_display_with_data(self, new_data: List[Dict[str, Any]], old_data: List[Dict[str, Any]]) -> None:
        """Refresh display using provided data"""
        try:
            # Apply text filter first
            filtered_data = apply_text_filter(new_data, self.filter)
            
            # Generate table rows with current filter mode
            rows = await map_table(filtered_data, old_data, self.filter_mode)

            # Preserve scroll position
            old_scroll = getattr(self.table, "scroll_offset", None)

            # Clear and add rows
            try:
                self.table.clear()
            except Exception:
                try:
                    nrows = len(self.table.rows)
                    if nrows:
                        self.table.remove_rows(0, nrows)
                except Exception:
                    pass
                    
            if rows:
                self.table.add_rows(rows)

                # Allow UI to update then restore scroll
                await asyncio.sleep(0.01)  # Very small delay
                if old_scroll:
                    try:
                        self.table.scroll_to(y=old_scroll.y, x=old_scroll.x)
                    except Exception:
                        pass

            self.log(f"PortWatch: display refreshed with {len(rows)} filtered rows")
        except Exception as e:
            self.log(f"PortWatch error during display refresh: {e}")

    @on(DataTable.RowSelected)
    async def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        # row_key object -> use directly
        row_key = event.row_key
        # get_row accepts row key; returns tuple-like values
        try:
            row = self.table.get_row(row_key)
        except Exception:
            # fallback: use cursor coordinate index
            coord = getattr(self.table, "cursor_coordinate", None)
            if coord is None:
                self.notify("No row selected", severity="error")
                return
            row = self.table.get_row(coord.row)

        if not row:
            self.notify("Row data not available", severity="error")
            return

        pid_str = str(row[0]).strip()
        process_name = str(row[2]).strip() if len(row) > 2 else ""

        try:
            pid = int(pid_str)
        except Exception:
            self.notify("Invalid PID", severity="error")
            return

        # open confirmation modal and wait
        result = await self.push_screen(KillConfirmation(pid, process_name))

        # If the modal performed the kill (returned True), refresh immediately
        if result is True:
            self.notify(f"Killed PID {pid}", severity="success")
            await self._do_data_scan()  # Force immediate scan after kill
        elif result is False:
            self.notify("Kill cancelled", severity="info")
        else:
            # None or unexpected -> treat as cancelled
            self.notify("No action taken", severity="info")
            
            

class NotificationNotEnabledAlert(ModalScreen[None]): 
    CSS = """
    NotificationNotEnabledAlert {
        align: center middle;
    }

    #alert-dialog {
        width: 60%;
        max-width: 500;
        height: auto;
        padding: 2 4;
        border: thick $error 80%;
        background: $surface;
        content-align: center middle;
    }

    #alert-dialog Static {
        text-align: center;
        width: 100%;
        padding: 1 0;
    }

    #alert-dialog Button {
        margin-top: 2;
        width: 50%;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="alert-dialog"):
            yield Static("🔔 Notifications Disabled", classes="header")
            yield Static(
                "Desktop notifications are not available or not enabled on this system.\n"
                "You may not receive alerts for port conflicts or process kills.",
                classes="message"
            )
            yield Button("OK", variant="primary", id="ok")

    @on(Button.Pressed, "#ok")
    def close_alert(self, event: Button.Pressed) -> None:
        self.dismiss()

    def on_key(self, event: Key) -> None:
        if event.key in ("enter", "escape", "space"):
            self.dismiss()
            event.stop()


def main():
    app = PortWatch()
    app.run()


if __name__ == "__main__":
    main()