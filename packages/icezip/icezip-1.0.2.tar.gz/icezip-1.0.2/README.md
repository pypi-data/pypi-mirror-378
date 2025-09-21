# Icezip
The better zip format (icezip)


### Overview

ICEZIP is a lightweight, fast, and advanced file packaging format.
It works like ZIP but with custom header, manifest management, and CLI tools. It is designed to store multiple files and folders in a single package efficiently.

### Features

Create ICEZIP archives from multiple files and folders

Add or remove files from existing archives

Extract all contents preserving folder structure

View archive contents or manifest.json

Lightweight, fast, and portable


### Installation

1. Download icezip.py from GitHub:

git clone https://github.com/username/icezip.git
cd icezip


2. Make it executable:

chmod +x icezip.py
sudo mv icezip.py /usr/local/bin/icezip


3. Now you can use the icezip command anywhere.



### Usage

icezip create archive.icezip file1.txt file2.png       # Create a new archive
icezip read archive.icezip                            # Read and display files
icezip list archive.icezip                            # List all files in archive
icezip extract archive.icezip ./output_folder        # Extract all files
icezip add archive.icezip newfile.txt                # Add files to archive
icezip remove archive.icezip file1.txt               # Remove files from archive

### Manifest

Each ICEZIP archive contains a manifest.json file internally that tracks:

List of files

Metadata (future extensions possible)



---

# FAQ 

Q1: What is ICEZIP?
A1: ICEZIP is a custom archive format based on ZIP, designed to be fast, lightweight, and easily manageable via CLI.

Q2: Can I open ICEZIP files with regular ZIP tools?
A2: Technically yes, since ICEZIP uses standard ZIP internally, but the first few bytes are custom header (ICEZIP). Normal ZIP tools may ignore or show errors on the header.

Q3: Can I add or remove files from an existing archive?
A3: Yes, use icezip add or icezip remove commands.

Q4: How do I extract all files?
A4: Use icezip extract archive.icezip ./output_folder. The folder structure is preserved.

Q5: Can I use ICEZIP on any OS?
A5: Yes, ICEZIP is Python-based, so it works on Linux, Windows, and MacOS with Python 3 installed.

Q6: Is ICEZIP faster than ZIP?
A6: ICEZIP is optimized for lightweight operations and can be faster in CLI operations due to internal manifest management, but compression is standard ZIP DEFLATE.

Q7: Can I distribute ICEZIP archives online?
A7: Yes, they are fully portable files that can be shared like ZIP archives.
