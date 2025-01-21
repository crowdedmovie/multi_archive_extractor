# Multi Archive Extractor

A simple and efficient tool using 7z & UnRar to extract multiple archive formats, including zip, rar, 7z, tar, tar.gz, and tar.bz2. Featuring an intuitive graphical interface built with PyQt6, it simplifies the process of managing compressed files.


## Features

- Supports multiple archive formats: zip, rar, 7z, tar, tar.gz, tar.bz2.
- Intuitive graphical interface built with PyQt6 for batch extraction.
- Allows extraction from a selected folder to a user-specified destination, preserving the source folder's directory structure.
- Real-time progress tracking, including file count and total size processed.
- Powered by **7z** and **unrar** for high-performance extraction.
- Logs every extraction process with a live feedback window in the UI and a persistent `logs.log` file.
- Compatible with **Windows** (precompiled `.exe` available) and **Linux** (requires Python environment).

## Requirements

- **Python 3.x** (only required for the non-compiled version).
- Dependencies (installable via `pip`):
  - PyQt6
- External tools required for archive extraction:
  - **7z** (7-Zip command-line tool).
  - **unrar** (WinRAR command-line tool).

## Installation

### For Windows (Precompiled Version)
1. Download the latest `.exe` file from the **Releases** section on GitHub.
2. Ensure that **7z** and **unrar** are installed:

   - Using **scoop**:
     ```bash
     scoop bucket add extras
     scoop install 7zip
     scoop install winrar
     ```
   - Alternatively, download and install from their official websites:
     - [7-Zip](https://www.7-zip.org/download.html)
     - [WinRAR](https://www.win-rar.com/download.html)


3. Run the `.exe` file to launch the program. No additional setup is required.

### For Linux or Python Environments
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/multi_archive_extractor.git
   cd multi_archive_extractor
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install 7z and unrar on your system:
   - On **Debian/Ubuntu**:
   ```bash
   sudo apt install p7zip-full unrar
   ```
   
   - On **Fedora**:
   ```bash
   sudo dnf install p7zip p7zip-plugins unrar
   ```
   
   - On **Arch Linux**:
   ```bash
   sudo pacman -S p7zip unrar
   ```

4. Run the program:
   ```bash
   python main.py
   ```

## Usage

1. Launch the program.
   - For the precompiled Windows version, run the `.exe` file.
   - For the Python version, run:
     ```bash
     python main.py
     ```
     
2. The program will display the main window. Here, you can:
   - **Select the source folder** containing the archives you want to extract.
   - **Select the destination folder** where the extracted files will be saved.
   - **Choose the archive formats** you want to process.
   - **Start the extraction** by clicking the "Start Extraction" button.


3. During the extraction process:
   - A **progress bar** will show the current extraction status.
   - The **logs window** will display real-time logs for each extraction process.
   - The program will also track the total size and number of files processed.


4. After the extraction is completed, a log file (`logs.log`) will store details about the operation (the logs are **not overwritten** between runs).
   
## License

This program is free software: you are allowed to redistribute and/or modify it under the terms of the **GNU General Public License** (GPL), as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed with the expectation that it will be useful, but **without any warranty**. For more information, see the **GPL**.

You should have received a copy of the **GPL** along with this program. If not, visit [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).

