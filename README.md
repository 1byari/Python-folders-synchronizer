# Folder Synchronization Tool

This Python script provides a simple way to synchronize two directories: a source and a replica. It ensures that the replica is an exact copy of the source by copying new files, updating changed files, and removing files from the replica that are no longer present in the source.

## Features

- **One-way synchronization**: Changes from the source folder are mirrored in the replica folder.
- **Periodic synchronization**: Synchronization occurs at user-defined intervals.
- **Logging**: All file operations are logged to both the console and a log file.

## How to Use

To use this folder synchronization tool, you'll need Python installed on your system. This script was developed with Python 3.8 or later in mind.

### Prerequisites

Before running the script, make sure you have the required dependencies:

- Python 3.8 or later
- Access to the command line or terminal of your operating system

### Setting Up

No additional libraries are required outside of Python's standard library. Simply download the script, or copy and paste it into a new Python file on your system.

### Running the Script

To run the script, open your command line or terminal and navigate to the directory where the script is located. Use the following command format to start synchronization:

```bash
python synchroniser.py <source_path> <replica_path> <time_interval> <log_path>
