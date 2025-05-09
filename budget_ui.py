from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QSpacerItem, QSizePolicy, QScrollArea
)
from PySide6.QtCharts import QChartView, QChart, QPieSeries
import csv


class BudgetTrackerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Budget Tracker")
        self.setMinimumWidth(600)
        self.init_ui()

    def resizeEvent(self, event):
        if self.width() < 500:
            self.switch_to_vertical()
        else:
            self.switch_to_horizontal()
        super().resizeEvent(event)

    def switch_to_vertical(self):
        if not isinstance(self.input_layout, QVBoxLayout):
            self.rebuild_input_layout(QVBoxLayout())

    def switch_to_horizontal(self):
        if not isinstance(self.input_layout, QHBoxLayout):
            self.rebuild_input_layout(QHBoxLayout())

    def rebuild_input_layout(self, new_layout):
        for i in reversed(range(self.input_layout.count())):
            widget = self.input_layout.itemAt(i).widget()
            self.input_layout.removeWidget(widget)

        old_layout = self.input_layout
        self.input_layout = new_layout

        self.input_layout.addWidget(self.date_input)
        self.input_layout.addWidget(self.type_input)
        self.input_layout.addWidget(self.category_input)
        self.input_layout.addWidget(self.amount_input)
        self.input_layout.addWidget(self.add_button)

        self.input_container.setLayout(self.input_layout)
        del old_layout

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Month Filter
        filter_layout = QHBoxLayout()
        self.month_filter = QComboBox()
        self.month_filter.addItem("All Time")
        for month in range(1, 13):
            self.month_filter.addItem(
                QDate(2025, month, 1).toString("MMMM yyyy"))
        self.month_filter.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(QLabel("Filter by Month:"))
        filter_layout.addWidget(self.month_filter)
        main_layout.addLayout(filter_layout)

        # Save/Load Buttons
        file_buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save to CSV")
        self.save_button.clicked.connect(self.save_to_csv)
        self.load_button = QPushButton("Load from CSV")
        self.load_button.clicked.connect(self.load_from_csv)
        file_buttons_layout.addWidget(self.save_button)
        file_buttons_layout.addWidget(self.load_button)
        main_layout.addLayout(file_buttons_layout)

        # Input Section
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.type_input = QComboBox()
        self.type_input.addItems(["Income", "Expense"])
        self.category_input = QComboBox()
        self.category_input.addItems(
            ["Food", "Transport", "Utilities", "Entertainment", "Other"])
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description")
        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)

        self.input_container = QWidget()
        self.input_layout = QHBoxLayout()
        self.input_container.setLayout(self.input_layout)
        self.input_layout.addWidget(self.date_input)
        self.input_layout.addWidget(self.type_input)
        self.input_layout.addWidget(self.category_input)
        self.input_layout.addWidget(self.amount_input)
        self.input_layout.addWidget(self.add_button)

        main_layout.addWidget(self.input_container)
        main_layout.addWidget(self.description_input)

        # Table Section (Scrollable)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Date", "Type", "Category", "Amount", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table_widget = QScrollArea()
        self.table_widget.setWidget(self.table)
        self.table_widget.setWidgetResizable(True)

        main_layout.addWidget(QLabel("Transaction History:"))
        main_layout.addWidget(self.table_widget)

        # Chart Section
        self.chart_view = QChartView()
        main_layout.addWidget(QLabel("Spending Breakdown (Pie Chart):"))
        main_layout.addWidget(self.chart_view)

        # Balance
        self.balance_label = QLabel("Balance: $0.00")
        self.balance_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_layout.addWidget(self.balance_label)

        self.setLayout(main_layout)

    def add_transaction(self):
        date = self.date_input.date().toString("yyyy-MM-dd")
        txn_type = self.type_input.currentText()
        category = self.category_input.currentText()
        amount = self.amount_input.text()
        desc = self.description_input.text()

        if not amount.strip().replace(".", "", 1).isdigit():
            return

        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(date))
        self.table.setItem(row_position, 1, QTableWidgetItem(txn_type))
        self.table.setItem(row_position, 2, QTableWidgetItem(category))
        self.table.setItem(row_position, 3, QTableWidgetItem(amount))
        self.table.setItem(row_position, 4, QTableWidgetItem(desc))

        self.amount_input.clear()
        self.description_input.clear()

        self.update_chart()
        self.update_balance()

    def save_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "CSV Files (*.csv)")
        if path:
            with open(path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["Date", "Type", "Category", "Amount", "Description"])
                for row in range(self.table.rowCount()):
                    data = [
                        self.table.item(row, col).text()
                        for col in range(self.table.columnCount())
                    ]
                    writer.writerow(data)

    def load_from_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "CSV Files (*.csv)")
        if path:
            with open(path, mode="r") as file:
                reader = csv.reader(file)
                next(reader)
                self.table.setRowCount(0)
                for row_data in reader:
                    row_position = self.table.rowCount()
                    self.table.insertRow(row_position)
                    for col, value in enumerate(row_data):
                        self.table.setItem(
                            row_position, col, QTableWidgetItem(value))
            self.update_chart()
            self.update_balance()

    def apply_filter(self):
        selected_month = self.month_filter.currentText()
        if selected_month == "All Time":
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
        else:
            month = QDate.fromString(selected_month, "MMMM yyyy").month()
            for row in range(self.table.rowCount()):
                row_date = QDate.fromString(
                    self.table.item(row, 0).text(), "yyyy-MM-dd")
                self.table.setRowHidden(row, row_date.month() != month)

        self.update_chart()
        self.update_balance()

    def update_chart(self):
        series = QPieSeries()
        category_totals = {}

        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            txn_type = self.table.item(row, 1).text()
            if txn_type == "Expense":
                category = self.table.item(row, 2).text()
                amount = float(self.table.item(row, 3).text())
                category_totals[category] = category_totals.get(
                    category, 0) + amount

        for category, total in category_totals.items():
            series.append(category, total)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Expenses by Category")
        self.chart_view.setChart(chart)

    def update_balance(self):
        income = 0.0
        expense = 0.0

        for row in range(self.table.rowCount()):
            if self.table.isRowHidden(row):
                continue
            txn_type = self.table.item(row, 1).text()
            amount = float(self.table.item(row, 3).text())
            if txn_type == "Income":
                income += amount
            elif txn_type == "Expense":
                expense += amount

        balance = income - expense
        self.balance_label.setText(f"Balance: ${balance:.2f}")
