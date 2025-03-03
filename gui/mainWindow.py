from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QApplication, QDialog, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QPalette
from PyQt6.QtCore import Qt
from gui.gui_interface import Ui_Main
from core.extractArchives import ArchiveExtractor
from gui.themes import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
import os
import platform
import subprocess
import shutil
import sys
import time
import logging
import webbrowser


class UsageInstructionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Usage Instructions")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)

        instructions = """
        MultiArchiveExtractor Usage Instructions:

        1. Select Source Folder
        - Click 'Select Source' button or go to File > Select Input Directory
        - Choose the folder containing the archives you want to extract (this folder will be scanned recursively)

        2. Select Destination Folder
        - Click 'Select Destination' button or go to File > Select Output Directory
        - Choose the folder where extracted files will be saved

        3. Select Archive Formats
        - Check the boxes for the archive formats you want to extract
        - Supported formats: ZIP, RAR, 7Z, TAR, GZIP, BZIP2, XZ, WIM, ISO, CAB, ARJ, LZH

        4. Start Extraction
        - Click 'Start Extraction' button
        - Progress will be shown in the progress bar and logs section

        5. Additional Features
        - Clear Logs: Remove logs shown in the UI (doesn't delete the content of the log file)
        - Cancel Extraction: Stop ongoing extraction process
        - Toggle Theme: Switch between light and dark modes
        - Logs are saved in the file 'logs.log' in the same directory as the executable
        """

        text_edit.setText(instructions)
        layout.addWidget(text_edit)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.extractor = None
        self.ui = Ui_Main()
        self.ui.setupUi(self)
        self.setWindowTitle("MultiArchiveExtractor v1.0.0")
        self.start_time = None

        self.check_dependencies()
        self.apply_system_theme()

        # Connect buttons
        self.ui.btnSelectSource.clicked.connect(self.browse_source_folder)
        self.ui.btnSelectDestination.clicked.connect(self.browse_destination_folder)
        self.ui.btnStartDecompression.clicked.connect(self.start_extraction)
        self.ui.btnClearLogs.clicked.connect(self.clear_logs)
        self.ui.actionOpenLogs.triggered.connect(self.open_logs_file)
        self.ui.actionExit.triggered.connect(self.close_app)
        self.ui.btnCancelDecompression.clicked.connect(self.cancel_extraction)

        # Connect menu
        self.ui.actionSelectInputDir.triggered.connect(self.browse_source_folder)
        self.ui.actionSelectOutputDir.triggered.connect(self.browse_destination_folder)
        self.ui.actionClearLogs.triggered.connect(self.clear_logs)
        self.ui.actionToggleTheme.triggered.connect(self.toggle_theme)

        # Add About menu actions
        self.ui.actionOpenGitHub.triggered.connect(self.open_github_repo)
        self.ui.actionUsageInstructions.triggered.connect(self.show_usage_instructions)
        self.ui.actionOpenLicense.triggered.connect(self.open_license)

    def apply_system_theme(self):
        """Apply theme based on system settings."""

        def is_dark_mode():
            current_os = platform.system()

            if current_os == 'Windows':
                # Check registry key for dark mode status
                try:
                    import winreg
                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
                    )
                    dark_mode, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                    return not bool(dark_mode)
                except Exception:
                    return False

            elif current_os == 'Linux':
                # Check GTK theme or environment variables
                try:
                    result = subprocess.run(
                        ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                        capture_output=True,
                        text=True
                    )
                    theme = result.stdout.strip().lower()
                    return 'dark' in theme
                except Exception:
                    # Fallback to environment variable
                    return os.environ.get('GTK_THEME', '').lower().find('dark') != -1

            return False

        # Apply theme based on detection
        if is_dark_mode():
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self):
        self.setStyleSheet(DARK_THEME_STYLESHEET)

    def apply_light_theme(self):
        self.setStyleSheet(LIGHT_THEME_STYLESHEET)

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        if self.palette().color(QPalette.ColorRole.Window).lightness() > 128:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def update_progress(self, current_files, total_files, current_bytes, total_bytes, extraction_speed):
        # Update progress bar
        percentage = int((current_bytes / total_bytes * 100) if total_bytes > 0 else 0)
        self.ui.progressBar.setValue(percentage)
        self.ui.lblProgressValue.setText(f"{percentage}%")

        # Update files processed
        self.ui.lblFilesProcessedValue.setText(f"{current_files} / {total_files}")

        # Update data processed
        processed_str = self.format_size(current_bytes)
        total_str = self.format_size(total_bytes)
        self.ui.lblDataProcessedValue.setText(f"{processed_str} / {total_str}")

        # Calculate and update ETA with speed
        if extraction_speed > 0:
            remaining_bytes = total_bytes - current_bytes
            eta_seconds = remaining_bytes / extraction_speed

            # Format speed for display
            speed_str = self.format_size(extraction_speed)
            eta_str = self.format_time(eta_seconds)

            self.ui.lblETAValue.setText(f"{eta_str} ({speed_str}/s)")
        else:
            self.ui.lblETAValue.setText("Calculating...")

        QApplication.processEvents()

    def format_time(self, seconds):
        """Format time in seconds to a human-readable string"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    def format_size(self, size_bytes):
        """Format size in bytes to a human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def get_selected_formats(self):
        formats = []

        # First row
        if self.ui.chkRar.isChecked():
            formats.append('.rar')
        if self.ui.chkZip.isChecked():
            formats.append('.zip')
        if self.ui.chk7z.isChecked():
            formats.append('.7z')
        if self.ui.chkTar.isChecked():
            formats.extend(['.tar', '.tar.gz', '.tar.bz2'])

        # Second row
        if self.ui.chkGzip.isChecked():
            formats.append('.gz')
        if self.ui.chkBzip2.isChecked():
            formats.append('.bz2')
        if self.ui.chkXz.isChecked():
            formats.append('.xz')
        if self.ui.chkWim.isChecked():
            formats.append('.wim')

        # Third row
        if self.ui.chkIso.isChecked():
            formats.append('.iso')
        if self.ui.chkCab.isChecked():
            formats.append('.cab')
        if self.ui.chkArj.isChecked():
            formats.append('.arj')
        if self.ui.chkLzh.isChecked():
            formats.append('.lzh')

        return formats

    def start_extraction(self):
        # Validate source and destination folders
        source_folder = self.ui.txtSourceFolder.text().strip()
        destination_folder = self.ui.txtDestinationFolder.text().strip()

        self.ui.txtSourceFolder.setEnabled(False)
        self.ui.txtDestinationFolder.setEnabled(False)
        self.ui.btnClearLogs.setEnabled(False)

        self.ui.actionSelectInputDir.setEnabled(False)
        self.ui.actionSelectOutputDir.setEnabled(False)
        self.ui.actionClearLogs.setEnabled(False)

        if not source_folder:
            QMessageBox.critical(self, "Error", "Please select a source folder.")
            return

        if not destination_folder:
            QMessageBox.critical(self, "Error", "Please select a destination folder.")
            return

        selected_formats = self.get_selected_formats()
        if not selected_formats:
            QMessageBox.warning(self, "Format Error", "Please select at least one archive format.")
            return

        # Disable UI elements during extraction
        self.ui.btnStartDecompression.setEnabled(False)
        self.ui.btnCancelDecompression.setEnabled(True)
        self.ui.btnSelectSource.setEnabled(False)
        self.ui.btnSelectDestination.setEnabled(False)
        self.ui.btnClearLogs.setEnabled(False)

        # Clear previous logs and reset progress
        self.ui.txtLogs.clear()
        self.ui.progressBar.setValue(0)
        self.ui.lblProgressValue.setText("0%")
        self.ui.lblFilesProcessedValue.setText("0 / 0")
        self.ui.lblDataProcessedValue.setText("0 B / 0 B")
        self.ui.lblETAValue.setText("")

        # Create and start extractor thread
        self.extractor = ArchiveExtractor(source_folder, destination_folder, selected_formats)
        self.extractor.progress_signal.connect(self.update_progress)
        self.extractor.log_signal.connect(self.update_log)
        self.extractor.finished.connect(self.on_extraction_finished)

        self.start_time = time.time()
        self.extractor.start()

    def cancel_extraction(self):
        if self.extractor and self.extractor.is_running():
            self.extractor.cancel()
            self.update_ui_state(True)
            self.ui.btnCancelDecompression.setEnabled(False)
            self.start_time = None
        else:
            pass  # no message box for when cancelling none existing process

    def check_dependencies(self):
        """ Check if required archive extraction tools are installed. """

        missing_tools = []

        tools_to_check = {
            '7z': ["7z", "(for ZIP, TAR, GZIP, BZIP2, XZ, WIM, ISO, CAB, ARJ, LZH)"],
            'unrar': ["unrar", "(for RAR)"]
        }

        for tool, (cmd, formats) in tools_to_check.items():
            if not shutil.which(cmd):
                missing_tools.append(f"{cmd} {formats}")

        if missing_tools:
            warning_message = (
                    "The following archive extraction tools are not installed:\n\n"
                    + "\n".join(missing_tools) + "\n\n"
                                                 "Some archive formats may not be extractable. "
                                                 "Please install the missing tools to ensure full functionality."
            )

            warning_box = QMessageBox()
            warning_box.setIcon(QMessageBox.Icon.Warning)
            warning_box.setWindowTitle("Missing Extraction Tools")
            warning_box.setText(warning_message)
            warning_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            warning_box.exec()

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

    def update_ui_state(self, state):
        for checkbox in [
            self.ui.chkRar,
            self.ui.chkZip,
            self.ui.chkTar,
            self.ui.chk7z,
            self.ui.chkGzip,
            self.ui.chkBzip2,
            self.ui.chkXz,
            self.ui.chkWim,
            self.ui.chkIso,
            self.ui.chkCab,
            self.ui.chkArj,
            self.ui.chkLzh
        ]:
            checkbox.setEnabled(state)

        for btn in [
            self.ui.btnSelectDestination,
            self.ui.btnSelectSource,
            self.ui.btnStartDecompression,
            self.ui.btnClearLogs
        ]:
            btn.setEnabled(state)

        for txtLine in [
            self.ui.txtSourceFolder,
            self.ui.txtDestinationFolder
        ]:
            txtLine.setEnabled(state)

        self.ui.lblSourceFolder.setEnabled(state)
        self.ui.lblDestinationFolder.setEnabled(state)

        self.ui.actionSelectInputDir.setEnabled(state)
        self.ui.actionSelectOutputDir.setEnabled(state)
        self.ui.actionClearLogs.setEnabled(state)

    def on_extraction_finished(self, time_taken, was_cancelled):
        self.update_ui_state(True)
        self.ui.btnCancelDecompression.setEnabled(False)

        if not was_cancelled:
            QMessageBox.information(
                self,
                "Success",
                f"Extraction completed successfully in {time_taken} seconds!"
            )
        else:
            QMessageBox.information(
                self,
                "Cancelled",
                "Extraction process was cancelled by user."
            )

    def on_extraction_cancelled(self):
        self.update_ui_state(True)
        QMessageBox.information(self, "Extraction Cancelled", "The extraction process has sucessfully been cancelled.")
        self.ui.txtLogs.append('<font color="red">Extraction cancelled by the user.</font>')
        self.ui.progressBar.setStyleSheet("QProgressBar::chunk{background-color: #06b025;}")

    def clear_logs(self):
        self.ui.txtLogs.clear()
        self.clear_processed_lbl()

    def clear_processed_lbl(self):
        self.ui.lblFilesProcessedValue.setText("0 / 0")
        self.ui.lblDataProcessedValue.setText("0 B / 0 B")
        self.ui.lblETAValue.setText("")
        self.ui.progressBar.setValue(0)
        self.ui.lblProgressValue.setText("0%")

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

    def update_log(self, message, status):
        """Update the log text edit with colored messages"""
        if platform.system() == "Windows":
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize'
                )
                dark_mode, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                is_dark_mode = value == 0
            except:
                is_dark_mode = False
        else:
            is_dark_mode = False

        if is_dark_mode:
            colors = {
                "success": "#4CAF50",  # Green
                "error": "#f44336",  # Red
                "info": "#2196F3"  # Blue
            }
        else:
            colors = {
                "success": "#2e7d32",  # Darker Green
                "error": "#d32f2f",  # Darker Red
                "info": "#1976d2"  # Darker Blue
            }

        color = colors.get(status, colors["info"])

        if status == "success":
            logging.info(message)
        elif status == "error":
            logging.error(message)
        else:  # info
            logging.info(message)

        formatted_message = f'<font color="{color}">{message}</font>'
        self.ui.txtLogs.append(formatted_message)
        self.ui.txtLogs.verticalScrollBar().setValue(
            self.ui.txtLogs.verticalScrollBar().maximum()
        )

    def open_github_repo(self):
        """Open the GitHub repository in the default web browser"""
        webbrowser.open("https://github.com/crowdedmovie/multi_archive_extractor")

    def show_usage_instructions(self):
        """Show usage instructions in a dialog"""
        dialog = UsageInstructionsDialog(self)
        dialog.exec()

    def open_license(self):
        """Open the license file"""
        license_path = os.path.join(os.path.dirname(__file__), '..', 'LICENSE')
        if os.path.exists(license_path):
            if platform.system() == "Windows":
                os.startfile(license_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(('open', license_path))
            else:  # linux variants
                subprocess.call(('xdg-open', license_path))
        else:
            QMessageBox.warning(self, "License Not Found", "Could not locate the LICENSE file.")
