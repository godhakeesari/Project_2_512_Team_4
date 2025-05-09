import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import csv
import datetime


class BudgetTracker(toga.App):

    def startup(self):
        label = toga.Label("Hello, Toga!", style=Pack(padding=10))


# Set this label as the content for the main window
        self.main_window.content = label
        self.main_window.show()

        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Date input (using TextInput instead of DatePicker)
        self.date_input = toga.TextInput(value=str(
            datetime.date.today()), placeholder='YYYY-MM-DD', style=Pack(margin_bottom=10))

        self.type_input = toga.Selection(
            items=["Income", "Expense"], style=Pack(margin_bottom=10))
        self.category_input = toga.Selection(
            items=["Food", "Transport", "Utilities", "Entertainment", "Other"], style=Pack(margin_bottom=10))
        self.amount_input = toga.TextInput(
            placeholder='Amount', style=Pack(margin_bottom=10))
        self.description_input = toga.TextInput(
            placeholder='Description', style=Pack(margin_bottom=10))

        self.add_button = toga.Button(
            'Add Transaction', on_press=self.add_transaction, style=Pack(padding=5))

        input_box = toga.Box(children=[
            self.date_input,
            self.type_input,
            self.category_input,
            self.amount_input,
            self.description_input,
            self.add_button
        ], style=Pack(direction=COLUMN, padding=10))

        self.table = toga.Table(
            headings=["Date", "Type", "Category", "Amount", "Description"],
            data=[],
            style=Pack(flex=1, padding=10)
        )

        self.balance_label = toga.Label("Balance: $0.00", style=Pack(
            font_weight="bold", font_size=16, padding=10))

        button_box = toga.Box(style=Pack(direction=ROW, padding=10))
        self.save_button = toga.Button(
            "Save to CSV", on_press=self.save_to_csv, style=Pack(padding=5))
        self.load_button = toga.Button(
            "Load from CSV", on_press=self.load_from_csv, style=Pack(padding=5))
        button_box.add(self.save_button)
        button_box.add(self.load_button)

        main_box.add(input_box)
        main_box.add(button_box)
        main_box.add(self.table)
        main_box.add(self.balance_label)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def add_transaction(self, widget):
        date = self.date_input.value
        txn_type = self.type_input.value
        category = self.category_input.value
        amount = self.amount_input.value.strip()
        desc = self.description_input.value.strip()

        try:
            amount = float(amount)
        except ValueError:
            return

        self.table.data.append(
            (date, txn_type, category, f"{amount:.2f}", desc))

        self.amount_input.value = ''
        self.description_input.value = ''

        self.update_balance()

    def save_to_csv(self, widget):
        path = self.main_window.save_file_dialog(
            "Save CSV", "transactions.csv")
        if path:
            with open(path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(
                    ["Date", "Type", "Category", "Amount", "Description"])
                for row in self.table.data:
                    writer.writerow(row)

    def load_from_csv(self, widget):
        path = self.main_window.open_file_dialog("Open CSV")
        if path:
            with open(path, mode="r") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                self.table.data.clear()
                for row in reader:
                    self.table.data.append(tuple(row))
            self.update_balance()

    def update_balance(self):
        income = 0.0
        expense = 0.0
        for row in self.table.data:
            txn_type = row[1]
            amount = float(row[3])
            if txn_type == "Income":
                income += amount
            elif txn_type == "Expense":
                expense += amount
        balance = income - expense
        self.balance_label.text = f"Balance: ${balance:.2f}"

        label = toga.Label("Hello World", style=Pack(padding=10))

        main_box.add(label)


def main():
    return BudgetTracker(formal_name="Personal Budget Tracker", app_id="org.example.budgettracker")


def startup(self):
    # Simple Box to check if layout is showing
    main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

    # Add a single label to test UI rendering
    hello_label = toga.Label("Hello World", style=Pack(padding=10))
    main_box.add(hello_label)

    # Set the content and show the window
    self.main_window.content = main_box
    self.main_window.show()


if __name__ == '__main__':
    main().main_loop()
