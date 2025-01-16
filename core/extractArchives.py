import os
import subprocess
import logging
import platform
from time import perf_counter
from PyQt6.QtCore import QThread, pyqtSignal

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ArchiveExtractor(QThread):
    finished = pyqtSignal(float)
    progress_updated = pyqtSignal(int, int, float, float)

    def __init__(self, ui, source_folder, destination_folder, selected_formats):
        super().__init__()
        self.ui = ui
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.selected_formats = selected_formats
        self.total_files = 0
        self.processed_files = 0
        self.total_size = 0
        self.processed_size = 0

    def run(self):
        if not os.path.isdir(self.source_folder):
            self.update_log(f"The source folder '{self.source_folder}' does not exist.", "error")
            return

        self.calculate_totals()
        start_time = perf_counter()

        for root, dirs, files in os.walk(self.source_folder):
            if self.isInterruptionRequested():
                break
            relative_path = os.path.relpath(root, self.source_folder)
            destination_subfolder = os.path.join(self.destination_folder, relative_path)

            if not os.path.exists(destination_subfolder):
                os.makedirs(destination_subfolder)

            for archive in files:
                if self.isInterruptionRequested():
                    break
                archive_path = os.path.join(root, archive)
                if self.is_supported_archive(archive_path):
                    self.extract_archive(archive_path, destination_subfolder)

        end_time = perf_counter()
        total_time = round(end_time - start_time, 2)
        # noinspection PyUnresolvedReferences
        self.finished.emit(total_time)

    def calculate_totals(self):
        for root, _, files in os.walk(self.source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if self.is_supported_archive(file_path):
                    self.total_files += 1
                    self.total_size += os.path.getsize(file_path)

        # bytes to gigabytes
        print(self.total_size)
        # noinspection PyUnresolvedReferences
        self.progress_updated.emit(self.processed_files, self.total_files, self.processed_size, self.total_size)

    def is_supported_archive(self, archive_path):
        return any(archive_path.endswith(extension) for extension in self.selected_formats)

    def extract_archive(self, archive_path, destination_folder):
        if not os.path.isfile(archive_path):
            self.update_log(f"The archive '{archive_path}' does not exist.", "error")
            return

        start_time = perf_counter()

        try:
            if archive_path.endswith(".rar"):
                command = ["unrar", "x", "-y", archive_path, destination_folder]
            else:
                command = ["7z", "x", "-y", archive_path, f"-o{destination_folder}"]

            window_creation_flag = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0

            result = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=window_creation_flag
            )

            if result.returncode == 0:
                end_time = perf_counter()
                duration = round(end_time - start_time, 2)
                self.update_log(
                    f"Extraction successful: {archive_path} -> {destination_folder} (in {duration}s)", "success"
                )
                self.processed_files += 1
                self.processed_size += os.path.getsize(archive_path)
                # noinspection PyUnresolvedReferences
                self.progress_updated.emit(
                    self.processed_files, self.total_files, self.processed_size, self.total_size
                )

            else:
                self.update_log(f"Extraction failed for {archive_path}. Command output: {result.stderr.strip()}", "error")

        except subprocess.CalledProcessError as e:
            self.update_log(f"Error: {str(e)} during extraction of {archive_path}", "error")

    def update_log(self, message, status):
        if status == "success":
            logging.info(message)
            text_color = "green"
        else:
            logging.error(message)
            text_color = "red"

        gv_message = f'<font color="{text_color}">{message}</font>'
        self.ui.gvDecompressionLogs.append(gv_message)
        self.ui.gvDecompressionLogs.verticalScrollBar().setValue(
            self.ui.gvDecompressionLogs.verticalScrollBar().maximum()
        )

        # TODO: Modify log file formats for decompression events:
        #  Decompression started: decompression of [source_folder] to [destination_folder] started, [y] files will be processed
        #  Decompression finished: decompression of [source_folder] to [destination_folder] finished, [x/y] files processed
        #  Decompression canceled: decompression of [source_folder] to [destination_folder] canceled, [x/y] files processed


