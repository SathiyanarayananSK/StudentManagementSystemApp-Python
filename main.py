from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, \
    QGridLayout, QLineEdit, QPushButton, QMainWindow, QTableWidget, \
    QTableWidgetItem, QDialog, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        # Create menu bar items
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add "Add Student" action to the file menu
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        # Add "About" action to the help menu
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        # Add "Search" action to the edit menu
        search_action = QAction(QIcon("icons/search.png"),"Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        # Set up the table to display student data
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create a toolbar and add actions
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Add a status bar to the main window
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Connect cell click event to a method
        self.table.cellClicked.connect(self.cell_clicked)

    def about(self):
        # Display the "About" dialog
        dialog = AboutDialog()
        dialog.exec()

    def load_data(self):
        # Load student data from the database and populate the table
        self.table.setRowCount(0)
        with sqlite3.connect("database.db") as connection:  # Use 'with' for automatic cleanup
            result = connection.execute("SELECT * FROM students")
            for row_num, row_data in enumerate(result):
                self.table.insertRow(row_num)
                for col_num, data in enumerate(row_data):
                    self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def insert(self):
        # Open the "Insert Student" dialog
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        # Open the "Search Student" dialog
        dialog = SearchDialog()
        dialog.exec()

    def cell_clicked(self):
        # Add "Edit" and "Delete" buttons to the status bar when a cell is clicked
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Remove existing buttons from the status bar
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        # Add new buttons to the status bar
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def edit(self):
        # Open the "Edit Student" dialog
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        # Open the "Delete Student" dialog
        dialog = DeleteDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """This course was created during my python programming training to upskill my GUI knowledge. Feel free to reuse it!"""
        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Set up the layout for the edit dialog
        layout = QVBoxLayout()

        # Get the selected student's data from the table
        index = management_system.table.currentRow()
        student_name = management_system.table.item(index, 1).text()

        # Add input fields for name, course, and mobile
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.stu_id = management_system.table.item(index, 0).text()

        course = management_system.table.item(index, 2).text()

        self.course_name = QComboBox()
        self.courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(self.courses)
        self.course_name.setCurrentText(course)
        layout.addWidget(self.course_name)

        mobile = management_system.table.item(index, 3).text()

        self.mobile_num = QLineEdit(mobile)
        self.mobile_num.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile_num)

        # Add an "Update" button to save changes
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        # Update the student's data in the database
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id= ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile_num.text(),
                        self.stu_id))
        connection.commit()
        cursor.close()
        connection.close()
        management_system.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        # Set up the layout for the delete confirmation dialog
        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        # Connect the "Yes" button to the delete function
        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Delete the selected student from the database
        index = management_system.table.currentRow()
        stu_id = management_system.table.item(index, 0).text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (stu_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        management_system.load_data()

        self.close()

        # Show a confirmation message after deletion
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Set up the layout for the insert dialog
        layout = QVBoxLayout()

        # Add input fields for name, course, and mobile
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.course_name = QComboBox()
        self.courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(self.courses)
        layout.addWidget(self.course_name)

        self.mobile_num = QLineEdit()
        self.mobile_num.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile_num)

        # Add a "Submit" button to save the new student
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        # Add a new student to the database
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile_num.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("Insert INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        management_system.load_data()
        self.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Set up the layout for the search dialog
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add a "Search" button to find the student
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        # Search for a student by name and highlight the result in the table
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        items = management_system.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            management_system.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


# Initialize the application and main window
app = QApplication(sys.argv)
management_system = MainWindow()
management_system.load_data()
management_system.show()
sys.exit(app.exec())
