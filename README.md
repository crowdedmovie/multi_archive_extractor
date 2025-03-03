# Multi Archive Extractor

A simple and efficient tool using 7z & UnRar to extract multiple archive formats, including popular formats such as zip, rar and 7z. Featuring an intuitive graphical interface built with PyQt6, it simplifies the process of managing compressed files on Windows.


## FEATURES

- Supports multiple archive formats: zip, rar, 7z, tar, tar.gz, tar.bz2, and more (XZ, WIM, ISO, CAB, ARJ, LZH).
- Intuitive graphical interface built with PyQt6 for batch extraction.
- Allows extraction from a selected folder to a user-specified destination, preserving the source folder's directory structure.
- Real-time progress tracking, including:
  - Detailed file count and total size processed
  - Extraction speed
  - Estimated Time of Arrival (ETA)
- Powered by **7z** and **unrar** for high-performance extraction.
- Logs every extraction process with a live feedback window in the UI and a persistent `logs.log` file.
- **Windows-exclusive** application with precompiled `.exe`
- **Adaptive Theme Support**:
  - Automatically detects and applies Windows system theme (light/dark mode)
  - Manual theme toggle option
- Comprehensive usage instructions built into the application

## Requirements

- **Windows 10/11** (no reason why it shouldn't work with olders versions but haven't tested it so :/ )
- Dependencies (included in the precompiled version):
  - PyQt6
  - PyQt6_sip
- External tools required for archive extraction:
  - **7z** (7-Zip command-line tool)
  - **unrar** (WinRAR command-line tool)

## Installation

### Precompiled Version

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

### Running from Source Code

1. Prerequisites:
   - **Windows 10/11**
   - **Python 3.9+** (recommended)
   - **Git** (optional, for cloning the repository)

2. Clone the repository:
   ```bash
   git clone https://github.com/crowdedmovie/multi_archive_extractor
   cd multi_archive_extractor
   ```
   
   Alternatively, download and extract the source code ZIP file from the repository.

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Install external tools:
   - Ensure **7z** and **unrar** are installed using one of the methods described in the Precompiled Version section.

6. Run the application:
   ```bash
   python main.py
   ```

**Note**: Running from source requires the same external tools (7z and unrar) as the precompiled version.

## Usage

1. Launch the program by running the downloaded `.exe` file or by executing `python main.py` if running from source.

2. The program will display the main window. Here, you can:
   - **Select the source folder** containing the archives you want to extract.
   - **Select the destination folder** where the extracted files will be saved.
   - **Choose the archive formats** you want to process.
   - **Start the extraction** by clicking the "Start Extraction" button.

3. During the extraction process:
   - A **progress bar** will show the current extraction status.
   - The **logs window** will display real-time logs for each extraction process.
   - The program tracks and displays:
     - Total files processed
     - Total data processed
     - Extraction speed
     - Estimated Time of Arrival (ETA)

4. Additional Features:
   - **Theme Toggle**: Switch between light and dark modes manually or use system default
   - **Clear Logs**: Remove logs shown in the UI (doesn't delete the log file)
   - **Cancel Extraction**: Stop ongoing extraction process
   - **Usage Instructions**: Access detailed usage guide from the Help menu

5. After the extraction is completed, a log file (`logs.log`) will store details about the operation (the logs are **not overwritten** between runs).

## Background of the project

This project originated from a practical need while managing ROM game files for retro console emulation on GBA, SNES, NGC and so on ...

Initially, I created a small command-line Python script to automate the extraction of multiple archive files, eliminating the tedious process of extracting archives one by one. Wanting to learn Qt Designer at the time, I saw an opportunity to transform this utility into a full-featured GUI app.

    
## License

This program is free software: you are allowed to redistribute and/or modify it under the terms of the **GNU General Public License** (GPL), as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed with the expectation that it will be useful, but **without any warranty**. For more information, see the **GPL**.

You should have received a copy of the **GPL** along with this program. If not, visit [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).
