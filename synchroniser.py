import argparse
import os 
import shutil
import time
from datetime import datetime
import hashlib

def parse_arguments():
    """Parse command line arguments for the synchronization script."""
    parser = argparse.ArgumentParser(description="Parse arguments needed for synchronization of two folders")
    parser.add_argument("source_path", type=str, help="Path of the source folder")
    parser.add_argument("replica_path", type=str, help="Path of the replica folder")
    parser.add_argument("time_interval", type=int, help="Interval of the synchronization in seconds")
    parser.add_argument("log_path", type=str, help="Path of the log file")
    return parser.parse_args()

class Synchronizer:
    """A class to synchronize two folders."""
    
    def __init__(self, source_path, replica_path, time_interval, log_path):
        """Initialize the Synchronizer with paths and interval."""
        self.source_path = source_path
        self.replica_path = replica_path
        self.time_interval = time_interval
        self.log_path = log_path

    def synchronize_folders(self):
        """Perform folder synchronization by removing outdated content and updating necessary files."""
        self.log_message(f"Start of synchronization at {datetime.now()}: ")
        isRemoveSuccessful = self.remove_content(self.list_files(self.source_path), self.list_files(self.replica_path))
        isUpdateSuccessful = self.update_content(self.list_files(self.source_path), self.list_files(self.replica_path))
        if (isRemoveSuccessful == 0 and isUpdateSuccessful == 0):
            self.log_message("No changes were necessary.")
        elif (isRemoveSuccessful != -1 and isUpdateSuccessful != -1):
            self.log_message("Synchronization completed successfully.")
        else:
            self.log_message("Errors occurred during synchronization.")

    def update_content(self, source_files, replica_files):
        """Update or create files and directories from source to replica."""
        isSuccessful = 0
        for entry in source_files:
            entry_replica_path = entry.replace(self.source_path, self.replica_path)
            # Handle non-existent paths in replica
            if not entry_replica_path in replica_files:
                if os.path.isdir(entry):
                    # Create directory if it doesn't exist
                    try:
                        os.mkdir(entry_replica_path)
                        os.chmod(entry_replica_path, os.stat(entry).st_mode)
                        self.log_message(f"Created directory: {entry_replica_path}")
                        # Recursively update content
                        res = self.update_content(self.list_files(entry), self.list_files(entry_replica_path))
                        if res != 0 and isSuccessful != -1:
                            isSuccessful = res
                    except Exception as e:
                        self.log_message(f"Failed to create directory {entry_replica_path}: {e}")
                        isSuccessful = -1
                else:
                    # Copy file if it doesn't exist
                    try:
                        shutil.copy(entry, entry_replica_path)
                        self.log_message(f"Created file: {entry_replica_path}")
                        if isSuccessful != -1:
                            isSuccessful = 1
                    except Exception as e:
                        self.log_message(f"Failed to create file {entry_replica_path}: {e}")
                        isSuccessful = -1
            elif not os.path.isdir(entry) and not self.compare_files(entry, entry_replica_path):
                # Update file if changes detected
                try:
                    os.remove(entry_replica_path)
                    shutil.copy2(entry, entry_replica_path)
                    self.log_message(f"Updated file: {entry_replica_path}")
                    if isSuccessful != -1:
                        isSuccessful = 1
                except Exception as e:
                    self.log_message(f"Failed to update file {entry_replica_path}: {e}")
                    isSuccessful = -1
            else:
                # Ensure correct permissions are set
                os.chmod(entry_replica_path, os.stat(entry).st_mode)
                # Recursively update directories
                res = self.update_content(self.list_files(entry), self.list_files(entry_replica_path))
                if res != 0 and isSuccessful != -1:
                    isSuccessful = res
        return isSuccessful
    
    def remove_content(self, source_data, replica_data):
        """Remove files and directories in replica that do not exist in source."""
        isSuccessful = 0
        for entry in replica_data:
            entry_source_path = entry.replace(self.replica_path, self.source_path)
            # Check for non-existent source files and remove from replica
            if not entry_source_path in source_data:
                if os.path.isdir(entry):
                    # Remove directory if it doesn't exist in source
                    try:
                        shutil.rmtree(entry)
                        self.log_message(f"Removed directory: {entry}")
                        isSuccessful = 1
                    except Exception as e:
                        self.log_message(f"Failed to remove directory {entry}: {e}")
                        isSuccessful = -1
                else:
                    # Remove file if it doesn't exist in source
                    try:
                        os.remove(entry)
                        self.log_message(f"Removed file: {entry}")
                        isSuccessful = 1
                    except Exception as e:
                        self.log_message(f"Failed to remove file {entry}: {e}")
                        isSuccessful = -1
            elif os.path.isdir(entry):
                # Recursively remove content
                res = self.remove_content(self.list_files(entry), self.list_files(entry)) 
                if res != 0 and isSuccessful != -1:
                    isSuccessful = res
        return isSuccessful
        
    def list_files(self, directory_path):
        """List all files in a directory with their absolute paths."""
        abs_directory = os.path.abspath(directory_path)
        return [os.path.join(abs_directory, file) for file in os.listdir(directory_path)]

    def compare_files(self, file1, file2):
        """Compare two files based on size, content hash, and permissions."""
        if int(os.path.getsize(file1)) != int(os.path.getsize(file2)):
            return False
        if self.file_hash(file1) != self.file_hash(file2):
            return False
        if os.stat(file1).st_mode != os.stat(file2).st_mode:
            return False
        return True

    def file_hash(self, file_path):
        """Generate a SHA-256 hash of a file's content."""
        BUFFER_SIZE = 65536
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(BUFFER_SIZE)
                    if not data:
                        break
                    sha256.update(data)
            return sha256.hexdigest()
        except Exception as e:
            self.log_message(f"Error reading file {file_path}")

    def start(self):
        """Start the synchronization process and repeat at the specified time interval."""
        while True:
            self.synchronize_folders()
            time.sleep(self.time_interval)

    def log_message(self, message):
        """Log messages to both console and file."""
        print(message)
        with open(self.log_path, 'a') as f:
            f.write(message + "\n")

if __name__ == "__main__":
    arguments = parse_arguments()
    synchronizer = Synchronizer(arguments.source_path, arguments.replica_path, arguments.time_interval, arguments.log_path)
    synchronizer.start()
