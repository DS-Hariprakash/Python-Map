import sys
import os
import tempfile
import pandas as pd
import folium

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QListWidget, QListWidgetItem, QLabel,
    QSpinBox, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


class MapApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Map Viewer")
        self.resize(1200, 800)

        self.df = None
        self.filtered_df = None
        self.map_zoom = 6

        # Layouts
        main_w = QWidget()
        main_layout = QHBoxLayout()
        main_w.setLayout(main_layout)
        self.setCentralWidget(main_w)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        left_panel.setMaximumWidth(360)

        # Controls
        self.open_btn = QPushButton("Open Excel/CSV File")
        self.open_btn.clicked.connect(self.open_file)
        left_layout.addWidget(self.open_btn)

        self.status_label = QLabel("No file loaded")
        left_layout.addWidget(self.status_label)

        left_layout.addWidget(QLabel("Select Fields to Show in Popups:"))
        self.fields_list = QListWidget()
        left_layout.addWidget(self.fields_list)

        left_layout.addWidget(QLabel("Filter by State:"))
        self.state_list = QListWidget()
        self.state_list.setSelectionMode(QListWidget.MultiSelection)
        left_layout.addWidget(self.state_list)

        left_layout.addWidget(QLabel("Filter by District:"))
        self.district_list = QListWidget()
        self.district_list.setSelectionMode(QListWidget.MultiSelection)
        left_layout.addWidget(self.district_list)

        left_layout.addWidget(QLabel("Filter by City:"))
        self.city_list = QListWidget()
        self.city_list.setSelectionMode(QListWidget.MultiSelection)
        left_layout.addWidget(self.city_list)

        controls_row = QWidget()
        controls_h = QHBoxLayout()
        controls_row.setLayout(controls_h)

        self.apply_btn = QPushButton("Apply Filters")
        self.apply_btn.clicked.connect(self.apply_filters)
        controls_h.addWidget(self.apply_btn)

        self.export_btn = QPushButton("Export Filtered to Excel")
        self.export_btn.clicked.connect(self.export_filtered)
        controls_h.addWidget(self.export_btn)

        left_layout.addWidget(controls_row)

        zoom_row = QWidget()
        zoom_h = QHBoxLayout()
        zoom_row.setLayout(zoom_h)

        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_h.addWidget(self.zoom_in_btn)

        self.zoom_out_btn = QPushButton("Zoom Out")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_h.addWidget(self.zoom_out_btn)

        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(1, 18)
        self.zoom_spin.setValue(self.map_zoom)
        self.zoom_spin.valueChanged.connect(self.set_zoom)
        zoom_h.addWidget(self.zoom_spin)

        left_layout.addWidget(zoom_row)

        left_layout.addStretch()

        # Map view
        self.map_view = QWebEngineView()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(self.map_view)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # Temp file for map
        self.temp_map_path = os.path.join(tempfile.gettempdir(), "map_view.html")
        self.create_empty_map()
        # Prompt for an input file on startup (or use command-line path)
        QTimer.singleShot(0, self.prompt_for_file)

    def create_empty_map(self):
        folium_map = folium.Map(location=[20.5937, 78.9629], zoom_start=self.map_zoom)
        folium_map.save(self.temp_map_path)
        self.map_view.load(QUrl.fromLocalFile(self.temp_map_path))

    def load_data(self, path):
        """Load dataframe from Excel or CSV and refresh UI/map."""
        try:
            if path.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)
        except Exception as e:
            self.status_label.setText(f"Failed to read file: {e}")
            return

        self.df = df
        self.filtered_df = df.copy()
        self.status_label.setText(f"Loaded {len(df)} rows from {os.path.basename(path)}")
        self.populate_fields()
        self.populate_filters()
        self.update_map()

    def prompt_for_file(self):
        """Prompt user to select a file on startup or use a command-line argument if provided."""
        # Try command-line argument first
        if len(sys.argv) > 1:
            arg_path = sys.argv[1]
            if os.path.exists(arg_path):
                self.load_data(arg_path)
                return
        # Otherwise prompt user to pick a file
        path, _ = QFileDialog.getOpenFileName(self, "Open data file", "", "Excel Files (*.xls *.xlsx);;CSV Files (*.csv)")
        if path:
            self.load_data(path)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open data file", "", "Excel Files (*.xls *.xlsx);;CSV Files (*.csv)")
        if not path:
            return
        self.load_data(path)

    def populate_fields(self):
        self.fields_list.clear()
        if self.df is None:
            return
        for col in self.df.columns:
            item = QListWidgetItem(col)
            item.setCheckState(Qt.Unchecked)
            self.fields_list.addItem(item)

    def populate_filters(self):
        # State
        self.state_list.clear()
        self.district_list.clear()
        self.city_list.clear()
        if self.df is None:
            return
        def populate_list(column, widget):
            widget.clear()
            if column in self.df.columns:
                vals = sorted(self.df[column].dropna().astype(str).unique())
                for v in vals:
                    item = QListWidgetItem(v)
                    item.setCheckState(Qt.Unchecked)
                    widget.addItem(item)
        populate_list('State', self.state_list)
        populate_list('District', self.district_list)
        populate_list('City', self.city_list)

    def get_selected_fields(self):
        fields = []
        for i in range(self.fields_list.count()):
            item = self.fields_list.item(i)
            if item.checkState() == Qt.Checked:
                fields.append(item.text())
        return fields

    def get_checked_values(self, widget):
        checked = []
        for i in range(widget.count()):
            item = widget.item(i)
            if item.checkState() == Qt.Checked:
                checked.append(item.text())
        return checked

    def apply_filters(self):
        if self.df is None:
            return
        df = self.df.copy()
        states = self.get_checked_values(self.state_list)
        districts = self.get_checked_values(self.district_list)
        cities = self.get_checked_values(self.city_list)
        if states:
            df = df[df['State'].astype(str).isin(states)]
        if districts:
            df = df[df['District'].astype(str).isin(districts)]
        if cities:
            df = df[df['City'].astype(str).isin(cities)]
        self.filtered_df = df
        self.status_label.setText(f"Filtered: {len(df)} rows")
        self.update_map()

    def find_lat_lon_columns(self):
        if self.df is None:
            return None, None
        cols = [c.lower() for c in self.filtered_df.columns]
        lat = None
        lon = None
        for c in self.filtered_df.columns:
            lc = c.lower()
            if lc in ('lat', 'latitude'):
                lat = c
            if lc in ('lon', 'lng', 'longitude'):
                lon = c
        return lat, lon

    def update_map(self):
        if self.filtered_df is None:
            self.create_empty_map()
            return
        lat_col, lon_col = self.find_lat_lon_columns()
        if not lat_col or not lon_col:
            self.status_label.setText("Missing Latitude/Longitude columns (expected names: Latitude/Longitude or lat/lon)")
            self.create_empty_map()
            return

        df = self.filtered_df.dropna(subset=[lat_col, lon_col])
        if df.empty:
            self.status_label.setText("No rows with valid coordinates")
            self.create_empty_map()
            return

        # Center map
        mean_lat = float(df[lat_col].astype(float).mean())
        mean_lon = float(df[lon_col].astype(float).mean())

        folium_map = folium.Map(location=[mean_lat, mean_lon], zoom_start=self.map_zoom)

        fields = self.get_selected_fields()
        for _, row in df.iterrows():
            try:
                lat = float(row[lat_col])
                lon = float(row[lon_col])
            except Exception:
                continue
            popup = ''
            if fields:
                popup = '<br>'.join(f"<b>{f}</b>: {row.get(f, '')}" for f in fields)
            else:
                # Default popup
                popup = '<br>'.join(f"<b>{c}</b>: {row.get(c, '')}" for c in ['City','District','State'] if c in self.filtered_df.columns)
            folium.Marker([lat, lon], popup=popup).add_to(folium_map)

        folium_map.save(self.temp_map_path)
        self.map_view.load(QUrl.fromLocalFile(self.temp_map_path))

    def export_filtered(self):
        if self.filtered_df is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save filtered data", "filtered.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return
        try:
            self.filtered_df.to_excel(path, index=False)
            self.status_label.setText(f"Exported {len(self.filtered_df)} rows to {os.path.basename(path)}")
        except Exception as e:
            self.status_label.setText(f"Export failed: {e}")

    def zoom_in(self):
        self.map_zoom = min(18, self.map_zoom + 1)
        self.zoom_spin.setValue(self.map_zoom)
        self.update_map()

    def zoom_out(self):
        self.map_zoom = max(1, self.map_zoom - 1)
        self.zoom_spin.setValue(self.map_zoom)
        self.update_map()

    def set_zoom(self, val):
        self.map_zoom = val
        self.update_map()

    def take_screenshot(self, out_path):
        """Grab the main window and save as an image then quit the app."""
        try:
            pix = self.grab()
            pix.save(out_path)
            print(f"Screenshot saved to {out_path}")
        except Exception as e:
            print(f"Screenshot failed: {e}")
        QTimer.singleShot(250, QApplication.instance().quit)


def create_map_headless(path, zoom=6, out_path='headless_map.html'):
    """Create a folium map from a file and print a short summary. Exits after saving the HTML."""
    try:
        if path.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)
    except Exception as e:
        print(f"Failed to read file: {e}")
        sys.exit(1)

    def find_lat_lon_columns_df(df):
        lat = None
        lon = None
        for c in df.columns:
            lc = c.lower()
            if lc in ('lat', 'latitude'):
                lat = c
            if lc in ('lon', 'lng', 'longitude'):
                lon = c
        return lat, lon

    lat_col, lon_col = find_lat_lon_columns_df(df)
    if not lat_col or not lon_col:
        print("Missing Latitude/Longitude columns (expected names: Latitude/Longitude or lat/lon)")
        sys.exit(1)

    df2 = df.dropna(subset=[lat_col, lon_col])
    if df2.empty:
        print("No rows with valid coordinates")
        sys.exit(1)

    mean_lat = float(df2[lat_col].astype(float).mean())
    mean_lon = float(df2[lon_col].astype(float).mean())
    folium_map = folium.Map(location=[mean_lat, mean_lon], zoom_start=zoom)

    fields = [c for c in df.columns if c not in (lat_col, lon_col)]
    count = 0
    for _, row in df2.iterrows():
        try:
            lat = float(row[lat_col])
            lon = float(row[lon_col])
        except Exception:
            continue
        popup = '<br>'.join(f"{f}: {row.get(f, '')}" for f in fields)
        folium.Marker([lat, lon], popup=popup).add_to(folium_map)
        count += 1

    folium_map.save(out_path)
    print(f"Loaded {len(df)} rows; using columns: lat={lat_col}, lon={lon_col}; markers={count}; map saved to {out_path}")


if __name__ == '__main__':
    # Support screenshot mode: python app.py --screenshot out.png [path/to/file]
    if '--screenshot' in sys.argv:
        idx = sys.argv.index('--screenshot')
        if len(sys.argv) > idx + 1:
            out = sys.argv[idx + 1]
            data_path = sys.argv[idx + 2] if len(sys.argv) > idx + 2 else None
            app = QApplication(sys.argv)
            window = MapApp()
            if data_path:
                window.load_data(data_path)
            window.show()
            # wait briefly to allow rendering, then take screenshot
            QTimer.singleShot(1500, lambda: window.take_screenshot(out))
            sys.exit(app.exec_())
        else:
            print('Usage: python app.py --screenshot out.png [path/to/file]')
            sys.exit(1)

    # Support a headless mode for CI or terminal verification: python app.py --headless path/to/file
    if '--headless' in sys.argv:
        idx = sys.argv.index('--headless')
        if len(sys.argv) > idx + 1:
            path = sys.argv[idx + 1]
            out = 'headless_map.html'
            create_map_headless(path, out_path=out)
            sys.exit(0)
        else:
            print('Usage: python app.py --headless path/to/file')
            sys.exit(1)

    app = QApplication(sys.argv)
    window = MapApp()
    window.show()
    sys.exit(app.exec_())
