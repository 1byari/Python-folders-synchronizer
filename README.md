# Folder Synchronization Tool

This Python script provides a simple way to synchronize two directories: a source and a replica. It ensures that the replica is an exact copy of the source by copying new files, updating changed files, and removing files from the replica that are no longer present in the source.

## Features

- **One-way synchronization**: Changes from the source folder are mirrored in the replica folder.
- **Periodic synchronization**: Synchronization occurs at user-defined intervals.
- **Logging**: All file operations are logged to both the console and a log file.