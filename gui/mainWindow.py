from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QApplication
from gui.gui_interface import Ui_Main
from core.extractArchives import ArchiveExtractor
import os
import platform
import subprocess
import shutil
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.extractor = None
        self.ui = Ui_Main()
        self.ui.setupUi(self)
        self.setWindowTitle("MultiArchiveExtractor v1.0.0")

        self.check_dependencies()
        # TODO : add img to Main Window, eventually error / info window

        self.ui.btnSelectSource.clicked.connect(self.browse_source_folder)
        self.ui.btnSelectDestination.clicked.connect(self.browse_destination_folder)
        self.ui.btnStartDecompression.clicked.connect(self.start_extraction)
        self.ui.btnClearLogs.clicked.connect(self.clear_logs)
        self.ui.actionOpenLogs.triggered.connect(self.open_logs_file)
        self.ui.actionExit.triggered.connect(self.close_app)
        self.ui.btnCancelDecompression.clicked.connect(self.cancel_extraction)

    # TODO : add ETA (estimate time of arrival) below progress bar

    def browse_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select source folder")
        if folder:
            if os.path.isdir(folder):
                self.ui.txtSourceFolder.setText(folder)
            else:
                QMessageBox.critical(self, "Error", "Source folder does not exist.")
        else:
            pass

    def browse_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select destination folder")
        if folder:
            if os.path.isdir(folder):
                self.ui.txtDestinationFolder.setText(folder)
            else:
                QMessageBox.critical(self, "Error", "Destination folder does not exist.")
        else:
            pass

    def get_selected_formats(self):
        format_checkboxes = {
            ".zip": self.ui.chkZipFormat,
            ".rar": self.ui.chkRarFormat,
            ".tar.gz": self.ui.chkTarGzFormat,
            ".tar.bz2": self.ui.chkTarBz2Format,
            ".7z": self.ui.chk7zFormat,
            ".tar": self.ui.chkTarFormat
        }

        selected_formats = [format_ for format_, checkbox in format_checkboxes.items() if checkbox.isChecked()]
        return selected_formats

    def update_ui_state(self, state):
        for checkbox in [
            self.ui.chkRarFormat,
            self.ui.chkZipFormat,
            self.ui.chkTarGzFormat,
            self.ui.chkTarBz2Format,
            self.ui.chk7zFormat,
            self.ui.chkTarFormat
        ]:
            checkbox.setEnabled(state)

        for btn in [
            self.ui.btnSelectDestination,
            self.ui.btnSelectSource,
            self.ui.btnStartDecompression
        ]:
            btn.setEnabled(state)

        for txtLine in [
            self.ui.txtSourceFolder,
            self.ui.txtDestinationFolder
        ]:
            txtLine.setEnabled(state)

    def start_extraction(self):
        source_folder = self.ui.txtSourceFolder.text()
        destination_folder = self.ui.txtDestinationFolder.text()
        selected_formats = self.get_selected_formats()

        if not source_folder:
            QMessageBox.warning(self, "Warning", "Please select a source folder!")
            return

        if not destination_folder:
            QMessageBox.warning(self, "Warning", "Please select a destination folder!")
            return

        if not selected_formats:
            QMessageBox.warning(self, "Warning", "Please select at least one archive format!")
            return

        found_archive = False
        for root, dirs, files in os.walk(source_folder):
            if any(file.endswith(ext) for ext in selected_formats for file in files):
                found_archive = True

        if not found_archive:
            QMessageBox.warning(self, "Warning", "No archives of the selected format(s) found in the source folder!")
            return

        self.clear_processed_lbl()
        self.update_ui_state(False)

        self.ui.progressBarDecompression.setMaximum(100)
        self.ui.progressBarDecompression.setValue(0)
        self.ui.progressBarDecompression.setStyleSheet("")

        self.extractor = ArchiveExtractor(self.ui, source_folder, destination_folder, selected_formats)
        self.extractor.progress_updated.connect(self.update_progress_labels)
        self.extractor.finished.connect(self.on_extraction_finished)
        self.extractor.start()

    def update_progress_labels(self, processed_files, total_files, processed_size, total_size):

        def format_size(size_in_bytes):
            # format the size in KB, MB, or GB
            if size_in_bytes < 1024:
                return f"{size_in_bytes} B"
            elif size_in_bytes < 1024 ** 2:
                size_in_kb = size_in_bytes / 1024
                return f"{size_in_kb:.0f} KB"
            elif size_in_bytes < 1024 ** 3:
                size_in_mb = size_in_bytes / 1024 ** 2
                return f"{size_in_mb:.0f} MB"
            else:
                size_in_gb = size_in_bytes / 1024 ** 3
                return f"{size_in_gb:.2f} GB"

        file_progress = (processed_files / total_files) * 100
        size_progress = (processed_size / total_size) * 100
        overall_progress = ((file_progress + size_progress) / 2)

        processed_size_formatted = format_size(processed_size)
        total_size_formatted = format_size(total_size)

        self.ui.lblFilesProcessed.setText(f"Files processed: {processed_files} / {total_files}")
        self.ui.lblDataProcessed.setText(f"Data processed: {processed_size_formatted} / {total_size_formatted}")
        self.ui.progressBarDecompression.setValue(int(overall_progress))
        self.ui.lblProgressBarValue.setText(f"{self.ui.progressBarDecompression.value()}%")

    def on_extraction_finished(self, total_time):
        self.update_ui_state(True)
        QMessageBox.information(
            self,
            "Extraction Complete",
            f"Extraction finished successfully in {total_time:.2f} seconds!"
        )

    def on_extraction_cancelled(self):
        self.update_ui_state(True)
        QMessageBox.information(self, "Extraction Cancelled", "The extraction process has sucessfully been cancelled.")
        self.ui.gvDecompressionLogs.append('<font color="red">Extraction cancelled by the user.</font>')
        self.ui.progressBarDecompression.setStyleSheet("QProgressBar::chunk{background-color: #06b025;}")

    def clear_logs(self):
        self.ui.gvDecompressionLogs.clear()
        self.clear_processed_lbl()

    def clear_processed_lbl(self):
        self.ui.lblFilesProcessed.setText("Files processed: 0 / 0")
        self.ui.lblDataProcessed.setText("Data processed: 0 / 0 B")
        self.ui.progressBarDecompression.setValue(0)
        self.ui.lblProgressBarValue.setText("0%")

    def open_logs_file(self):
        # check if the program is running in a compiled (frozen) state
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            # get logs.log file path form gui/ folder
            exe_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        logs_file = os.path.join(exe_dir, "logs.log")

        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(logs_file)
            elif system == "Linux":
                subprocess.run(["xdg-open", logs_file])
            else:
                QMessageBox.warning(self, "Warning", "System not supported for opening log file.")

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error opening log file : {e}")

    def close_app(self):
        QApplication.quit()

    def cancel_extraction(self):
        if self.extractor and self.extractor.isRunning():
            self.extractor.terminate()
            self.extractor.wait()
            self.on_extraction_cancelled()
        else:
            pass  # no message box for when cancelling none existing process

    def check_dependencies(self):
        required_dependencies = {
            "7z": "7-Zip",
            "unrar": "UnRAR"
        }

        missing_dependencies = []
        for cmd_command, name in required_dependencies.items():
            if not shutil.which(cmd_command):
                missing_dependencies.append(name)

        unsupported_formats = []
        dependencies_to_formats = {
            "7-Zip": ["7z", "Zip", "TarGz", "TarBz2", "Tar"],
            "UnRAR": ["Rar"]
        }

        for dependency, formats in dependencies_to_formats.items():
            if dependency in missing_dependencies:
                unsupported_formats.extend(formats)

        unsupported_formats_str = ", ".join(unsupported_formats)

        if missing_dependencies:
            missing_str = ", ".join(missing_dependencies)
            QMessageBox.critical(self, "Missing Dependencies", (
                f"The following dependencies are missing or not accessible from the PATH: {missing_str}\n\n"
                f"As a result, the following formats will not be supported: {unsupported_formats_str}\n\n"
                "To resolve this issue, please install the required dependencies or add them to the system PATH."
            ))
            self.close()


