import os
import subprocess
import logging
import platform
from time import perf_counter
from collections import deque
from PyQt6.QtCore import QThread, pyqtSignal

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class ArchiveExtractor(QThread):
    finished = pyqtSignal(float, bool)  # time_taken, was_cancelled
    progress_signal = pyqtSignal(int, int, int, int,
                                 float)  # current_files, total_files, current_bytes, total_bytes, extraction_speed
    log_signal = pyqtSignal(str, str)  # message, status

    def __init__(self, source_folder, destination_folder, selected_formats):
        super().__init__()
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.selected_formats = selected_formats
        self.total_files = 0
        self.processed_files = 0
        self.total_size = 0
        self.processed_size = 0
        self._running = False

        # For ETA calculation
        self.extraction_speeds = deque(maxlen=5)  # Keep last 5 speeds for averaging
        self.last_update_time = None
        self.last_processed_size = 0
        self.current_file_start_time = None
        self.current_file_size = 0
        self.current_file_processed = 0

    def run(self):
        if not os.path.isdir(self.source_folder):
            self.log_signal.emit(f"The source folder '{self.source_folder}' does not exist.", "error")
            return

        # Normalize the source folder path to preserve exact case
        normalized_source_folder = self._get_exact_path(self.source_folder)
        self.source_folder = normalized_source_folder

        self._running = True
        self.calculate_totals()
        start_time = perf_counter()
        self.last_update_time = start_time

        self.log_signal.emit(
            f"Starting extraction of {self.total_files} files from '{self.source_folder}' to '{self.destination_folder}'",
            "info"
        )

        try:
            for root, dirs, files in os.walk(self.source_folder):
                if not self._running:
                    break
                relative_path = os.path.relpath(root, self.source_folder)
                destination_subfolder = os.path.join(self.destination_folder, relative_path)

                if not os.path.exists(destination_subfolder):
                    os.makedirs(destination_subfolder)

                for archive in files:
                    if not self._running:
                        break
                    # Use exact path matching
                    archive_path = self._get_exact_file_path(os.path.join(root, archive))
                    if self.is_supported_archive(archive_path):
                        self.extract_archive(archive_path, destination_subfolder)

            end_time = perf_counter()
            total_time = round(end_time - start_time, 2)

            if self._running:
                self.log_signal.emit(
                    f"Extraction completed successfully in {total_time} seconds.",
                    "success"
                )
                self.finished.emit(total_time, False)
            else:
                self.log_signal.emit(
                    "Extraction was cancelled by user.",
                    "info"
                )
                self.finished.emit(total_time, True)
        except Exception as e:
            self.log_signal.emit(f"Error during extraction: {str(e)}", "error")
            self.finished.emit(0, True)

    def extract_archive(self, archive_path, destination_folder):
        if not os.path.isfile(archive_path):
            self.log_signal.emit(f"The archive '{archive_path}' does not exist.", "error")
            return

        try:
            archive_name = os.path.basename(archive_path)
            archive_size = os.path.getsize(archive_path)

            # Set current file information
            self.current_file_start_time = perf_counter()
            self.current_file_size = archive_size
            self.current_file_processed = self.processed_size

            self.log_signal.emit(f"Extracting {archive_name}...", "info")

            command = self.get_extractor_command(archive_path, destination_folder)

            # Platform-specific process creation flags
            current_os = platform.system()
            if current_os == "Windows":
                window_creation_flag = subprocess.CREATE_NO_WINDOW
            else:
                window_creation_flag = 0

            # Log the exact command and paths being used
            self.log_signal.emit(f"Executing command: {' '.join(command)}", "info")
            self.log_signal.emit(f"Archive path: {archive_path}", "info")
            self.log_signal.emit(f"Destination folder: {destination_folder}", "info")

            # Start the process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=window_creation_flag
            )

            # Monitor the process while it's running
            last_progress_time = perf_counter()

            while process.poll() is None and self._running:
                current_time = perf_counter()

                if current_time - last_progress_time >= 0.05:  # 50ms
                    time_elapsed = current_time - self.current_file_start_time

                    if time_elapsed > 0:
                        # Use average speed if available, otherwise estimate based on current file
                        if self.extraction_speeds:
                            avg_speed = sum(self.extraction_speeds) / len(self.extraction_speeds)
                        else:
                            # Assume we're halfway through if no previous speed data
                            avg_speed = (archive_size / 2) / time_elapsed

                        estimated_progress = min(time_elapsed * avg_speed, archive_size)
                        estimated_total = self.processed_size + estimated_progress

                        self.progress_signal.emit(
                            self.processed_files,
                            self.total_files,
                            int(estimated_total),
                            self.total_size,
                            avg_speed
                        )

                    last_progress_time = current_time

                # Sleep briefly (10ms) to avoid excessive CPU usage
                self.msleep(10)

            stdout, stderr = process.communicate()

            if process.returncode == 0 and self._running:
                # Update progress after successful extraction
                end_time = perf_counter()
                extraction_time = end_time - self.current_file_start_time
                if extraction_time > 0:
                    speed = archive_size / extraction_time
                    self.extraction_speeds.append(speed)

                self.processed_files += 1
                self.processed_size += archive_size

                # Emit final progress for this file
                self.progress_signal.emit(
                    self.processed_files,
                    self.total_files,
                    self.processed_size,
                    self.total_size,
                    speed if extraction_time > 0 else 0
                )

                self.log_signal.emit(f"Successfully extracted {archive_name}", "success")
            else:
                self.log_signal.emit(f"Failed to extract {archive_name}: {stderr}", "error")

        except Exception as e:
            self.log_signal.emit(f"Error extracting {os.path.basename(archive_path)}: {str(e)}", "error")
        finally:
            # Reset current file tracking
            self.current_file_start_time = None
            self.current_file_size = 0
            self.current_file_processed = 0

    def calculate_totals(self):
        self.total_files = 0
        self.total_size = 0
        for root, _, files in os.walk(self.source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if self.is_supported_archive(file_path):
                    self.total_files += 1
                    self.total_size += os.path.getsize(file_path)

        self.progress_signal.emit(0, self.total_files, 0, self.total_size, 0)

    def is_supported_archive(self, archive_path):
        formats = {
            # Common archive formats
            '.zip': '7z',
            '.rar': 'unrar',
            '.7z': '7z',

            # Tar and compressed tar formats
            '.tar': '7z',
            '.tar.gz': '7z',
            '.tgz': '7z',
            '.tar.bz2': '7z',
            '.tbz2': '7z',
            '.tar.xz': '7z',
            '.txz': '7z',

            # Compression formats
            '.gz': '7z',
            '.bz2': '7z',
            '.xz': '7z',

            # Disk and system image formats
            '.wim': '7z',
            '.iso': '7z',
            '.cab': '7z',

            # Legacy formats
            '.arj': '7z',
            '.lzh': '7z'
        }

        # Normalize the archive path for extension matching, but preserve original path
        normalized_path = archive_path.lower()

        # Check if the file extension is in any of the supported formats
        matching_formats = [ext for ext in formats.keys() if normalized_path.endswith(ext)]

        # If no selected formats specified, use all supported formats
        if not self.selected_formats:
            return bool(matching_formats)

        # Convert selected formats to lowercase for case-insensitive comparison
        selected_formats_lower = [fmt.lower().strip() for fmt in self.selected_formats]

        # Check if any of the matching formats are in the selected formats
        return any(
            fmt in selected_formats_lower
            for fmt in matching_formats
        )

    def get_extractor_command(self, archive_path, destination_folder):
        # Normalize the archive path for extension matching, but preserve original path
        normalized_path = archive_path.lower()

        seven_z_cmd = '7z'
        unrar_cmd = 'unrar'

        # Use unrar for RAR files
        if normalized_path.endswith('.rar'):
            return [unrar_cmd, "x", "-y", archive_path, destination_folder]

        # Use 7z for all other formats
        return [seven_z_cmd, "x", "-y", archive_path, f"-o{destination_folder}"]

    def _get_exact_path(self, path):
        """
        Find the exact case-sensitive path for a given path
        """
        normalized_path = os.path.normpath(path)
        if os.path.exists(normalized_path):
            return normalized_path

        parts = normalized_path.split(os.sep)
        current_path = os.sep if normalized_path.startswith(os.sep) else ''

        for part in parts:
            if not part:
                continue

            # If current path is root, check the part directly
            if current_path in ['', os.sep]:
                current_path = os.path.join(current_path, part)
                continue

            # List all entries in the current directory
            try:
                entries = os.listdir(current_path)
                # Find case-insensitive match
                matching_entries = [
                    entry for entry in entries
                    if entry.lower() == part.lower()
                ]

                if matching_entries:
                    # Use the first matching entry (preserving original case)
                    current_path = os.path.join(current_path, matching_entries[0])
                else:
                    # If no match found, return the original path
                    return normalized_path
            except Exception as e:
                # If listing fails, return the original path
                return normalized_path

        return current_path

    def _get_exact_file_path(self, path):
        """
        Find the exact case-sensitive file path
        """
        directory = os.path.dirname(path)
        filename = os.path.basename(path)

        # First normalize the directory
        normalized_directory = self._get_exact_path(directory)

        # Then find the exact file in that directory
        try:
            entries = os.listdir(normalized_directory)
            matching_entries = [
                entry for entry in entries
                if entry.lower() == filename.lower()
            ]

            if matching_entries:
                return os.path.join(normalized_directory, matching_entries[0])
        except Exception:
            pass

        # If no match found, return the original path
        return path

    def cancel(self):
        self._running = False

    def is_running(self):
        return self._running
