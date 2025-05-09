import sys
from PySide6.QtWidgets import QApplication
from budget_ui import BudgetTrackerUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BudgetTrackerUI()
    window.show()
    sys.exit(app.exec())
