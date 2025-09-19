# BSD 3-Clause License
#
# Copyright (c) 2025, Arm Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
InputDialog:

This module defines a modal dialog window using the PySide6 library for selecting input data
required for CMN mesh processing. The dialog is titled "Select input CMN mesh information" and
provides two horizontally arranged input fields:

1. A file selector for choosing a `.json` file that contains mesh configuration or metadata.
2. A directory selector for specifying the location where related CSV output or resources are stored.

The dialog includes "OK" and "Cancel" buttons:
- Pressing "OK" returns the selected file and directory paths via `output_json_file` and `output_csv_dir`.
- Pressing "Cancel" closes the dialog gracefully without returning any values.
"""

#
# Example usage
#
#   if __name__ == "__main__":
#       app = QApplication(sys.argv)
#       dialog = InputDialog()
#       output_json_file = ""
#       output_csv_dir = ""
#
#       if dialog.exec() == QDialog.Accepted:
#           output_json_file, output_csv_dir = dialog.get_inputs()
#           print("Selected JSON file:", output_json_file)
#           print("Selected directory:", output_csv_dir)
#       else:
#           print("Dialog cancelled.")


from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QFileDialog, QSizePolicy
)

class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select input CMN mesh information")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.adjustSize()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # JSON file input
        json_layout = QHBoxLayout()
        self.json_input = QLineEdit()
        self.json_input.setPlaceholderText("Select CMN topology JSON file")
        json_button = QPushButton("Browse...")
        json_button.clicked.connect(self.select_json_file)
        json_layout.addWidget(self.json_input)
        json_layout.addWidget(json_button)
        main_layout.addLayout(json_layout)

        # Directory input
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Select directory with `topdown_tool` CSV file(s)")
        dir_button = QPushButton("Browse...")
        dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        main_layout.addLayout(dir_layout)

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def select_json_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", "JSON Files (*.json)")
        if file_path:
            self.json_input.setText(file_path)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.dir_input.setText(dir_path)

    def get_inputs(self):
        return self.json_input.text(), self.dir_input.text()
