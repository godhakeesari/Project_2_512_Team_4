import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.images import Image
import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import csv


class PersonalBudgetTracker(toga.App):
    def startup(self):
        # Removed unnecessary padding
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=0))

        # Input Fields
        self.date_input = toga.TextInput(value=str(
            datetime.date.today()), placeholder="YYYY-MM-DD", style=Pack(margin=5, flex=1))
        self.type_input = toga.Selection(
            items=["Income", "Expense"], style=Pack(margin=5, flex=1))
        self.category_input = toga.Selection(
            items=["Food", "Transport", "Bills", "Entertainment", "Other"], style=Pack(margin=5, flex=1))
        self.amount_input = toga.TextInput(
            placeholder="Amount", style=Pack(margin=5, flex=1))
        self.description_input = toga.TextInput(
            placeholder="Description", style=Pack(margin=5, flex=1))

        # Buttons
        self.add_button = toga.Button(
            "Add", on_press=self.add_transaction, style=Pack(padding=5))
        self.save_button = toga.Button(
            "Save CSV", on_press=self.save_to_csv, style=Pack(padding=5))
        self.load_button = toga.Button(
            "Load CSV", on_press=self.load_from_csv, style=Pack(padding=5))

        # Table
        self.table = toga.Table(
            headings=["Date", "Type", "Category", "Amount", "Description"],
            data=[],
            style=Pack(flex=1, margin=5)
        )

        # Balance Label
        self.balance_label = toga.Label("Balance: $0.00", style=Pack(
            font_size=16, padding=5, font_weight="bold"))

        # Pie Chart ImageView
        self.pie_chart = toga.ImageView(style=Pack(height=200, padding=5))

        # List to hold transactions
        self.transactions = []

        # Layout Containers
        # Removed unnecessary padding
        input_box = toga.Box(style=Pack(direction=ROW, padding=0))
        input_box.add(self.date_input)
        input_box.add(self.type_input)
        input_box.add(self.category_input)
        input_box.add(self.amount_input)
        input_box.add(self.description_input)
        input_box.add(self.add_button)

        # Removed unnecessary padding
        file_box = toga.Box(style=Pack(direction=ROW, padding=0))
        file_box.add(self.save_button)
        file_box.add(self.load_button)

        # Assemble final layout
        main_box.add(input_box)
        main_box.add(file_box)
        main_box.add(self.table)
        main_box.add(self.balance_label)
        main_box.add(self.pie_chart)

        # Main Window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def add_transaction(self, widget):
        try:
            amount = float(self.amount_input.value)
        except ValueError:
            return  # Ignore invalid amounts

        transaction = {
            "date": self.date_input.value,
            "type": self.type_input.value,
            "category": self.category_input.value,
            "amount": amount,
            "description": self.description_input.value
        }

        self.transactions.append(transaction)
        self.table.data.append((
            transaction["date"],
            transaction["type"],
            transaction["category"],
            f"{transaction['amount']:.2f}",
            transaction["description"]
        ))

        # Clear input fields
        self.amount_input.value = ""
        self.description_input.value = ""

        # Update balance and pie chart
        self.update_balance()
        self.update_pie_chart()

    def update_balance(self):
        income = sum(t["amount"]
                     for t in self.transactions if t["type"] == "Income")
        expense = sum(t["amount"]
                      for t in self.transactions if t["type"] == "Expense")
        balance = income - expense
        self.balance_label.text = f"Balance: ${balance:.2f}"

    def update_pie_chart(self):
        income = sum(t["amount"]
                     for t in self.transactions if t["type"] == "Income")
        expense = sum(t["amount"]
                      for t in self.transactions if t["type"] == "Expense")

        if income == 0 and expense == 0:
            self.pie_chart.image = None
            return

        labels = ['Income', 'Expense']
        sizes = [income, expense]
        colors = ['#66bb6a', '#ef5350']

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, colors=colors,
               autopct='%1.1f%%', startangle=90)
        # Equal aspect ratio ensures pie is drawn as a circle.
        ax.axis('equal')

        # Save the pie chart as a PNG file
        image_path = Path("pie_chart.png")
        fig.savefig(image_path, bbox_inches='tight')
        plt.close(fig)

        # Update the ImageView to display the pie chart
        self.pie_chart.image = Image(str(image_path))

    def save_to_csv(self, widget):
        path = self.main_window.save_file_dialog(
            "Save CSV", "transactions.csv")
        if path:
            with open(path, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Date", "Type", "Category", "Amount", "Description"])
                for txn in self.transactions:
                    writer.writerow([txn["date"], txn["type"], txn["category"],
                                    f"{txn['amount']:.2f}", txn["description"]])

    def load_from_csv(self, widget):
        path = self.main_window.open_file_dialog("Open CSV")
        if path:
            with open(path, mode="r") as f:
                reader = csv.DictReader(f)
                self.transactions.clear()
                self.table.data.clear()
                for row in reader:
                    row["amount"] = float(row["Amount"])
                    self.transactions.append({
                        "date": row["Date"],
                        "type": row["Type"],
                        "category": row["Category"],
                        "amount": float(row["Amount"]),
                        "description": row["Description"]
                    })
                    self.table.data.append((
                        row["Date"],
                        row["Type"],
                        row["Category"],
                        row["Amount"],
                        row["Description"]
                    ))
            self.update_balance()
            self.update_pie_chart()


def main():
    return PersonalBudgetTracker(formal_name="Personal Budget Tracker")


if __name__ == '__main__':
    main().main_loop()
