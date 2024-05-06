import argparse
import hashlib
import os
import shutil
import time
from datetime import datetime


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
        is_remove_successful = self.remove_content(self.list_files(self.replica_path))
        is_update_successful = self.update_content(self.list_files(self.source_path))
        if (is_remove_successful == 0 and is_update_successful == 0):
            self.log_message("No changes were necessary.")
        elif (is_remove_successful != -1 and is_update_successful != -1):
            self.log_message("Synchronization completed successfully.")
        else:
            self.log_message("Errors occurred during synchronization.")

    def update_content(self, source_files):
        """Update or create files and directories from source to replica."""
        operations_results = []
        for entry in source_files:
            entry_replica_path = entry.replace(self.source_path, self.replica_path)
            # Handle non-existent paths in replica
            if not os.path.exists(entry_replica_path):
                if os.path.isdir(entry):
                    # Create directory if it doesn't exist
                    operations_results.append(self.create_directory(entry, entry_replica_path))
                else:
                    # Copy file if it doesn't exist
                    operations_results.append(self.create_file(entry, entry_replica_path))
            elif not os.path.isdir(entry) and not self.compare_files(entry, entry_replica_path):
                # Update file if changes detected
                operations_results.append(self.update_file(entry, entry_replica_path))
            elif os.path.isdir(entry):
                # Recursively update directory
                operations_results.append(self.update_directory(entry, entry_replica_path))
        return self.calculate_operation_result(operations_results)

    def calculate_operation_result(self, operations_results):
        """Calculates the result of the operation based on the results of internal operations"""
        if -1 in operations_results:
            return -1
        elif not 1 in operations_results:
            return 0
        else:
            return 1
    
    def update_directory(self, source_dir, replica_dir):
        """Recursively update the content of the directories."""
        try:
            # Ensure correct permissions are set
            os.chmod(replica_dir, os.stat(source_dir).st_mode)
            source_files = self.list_files(source_dir)
            return self.update_content(source_files)
        except Exception as e:
            self.log_message(f"Error updating directory {replica_dir}: {e}")
            return -1

    def update_file(self, source_file, replica_file):
        try:
            os.remove(replica_file)
            shutil.copy2(source_file, replica_file)
            self.log_message(f"Updated file: {replica_file}")
            return 1
        except Exception as e:
            self.log_message(f"Failed to update file {replica_file}: {e}")
            return -1
        
    def create_file(self, source_file, replica_file):
        """Creates file identical to source"""
        try:
            shutil.copy(source_file, replica_file)
            self.log_message(f"Created file: {source_file}")
            return 1
        except Exception as e:
            self.log_message(f"Failed to create file {replica_file}: {e}")
            return -1
        
    def create_directory(self, source_dir, replica_dir):
        """Creates directory identical to source"""
        try:
            os.mkdir(replica_dir)
            os.chmod(replica_dir, os.stat(source_dir).st_mode)
            self.log_message(f"Created directory: {replica_dir}")
            # Recursively update content
            return self.update_directory(source_dir, replica_dir)
        except Exception as e:
            self.log_message(f"Failed to create directory {replica_dir}: {e}")
            return -1

    def remove_content(self, replica_files):
        """Remove files and directories in replica that do not exist in source."""
        operands_results = []
        for entry in replica_files:
            entry_source_path = entry.replace(self.replica_path, self.source_path)
            # Check for non-existent source files and remove from replica
            if not os.path.exists(entry_source_path):
                if os.path.isdir(entry):
                    # Remove directory if it doesn't exist in source
                    operands_results.append(self.remove_directory(entry))
                else:
                    # Remove file if it doesn't exist in source
                    operands_results.append(self.remove_file(entry))
            elif os.path.isdir(entry):
                # Recursively remove content
                operands_results.append(self.remove_content(self.list_files(entry)))  
        return self.calculate_operation_result(operands_results)
    
    def remove_directory(self, directory_path):
        """Removes directory"""
        try:
            shutil.rmtree(directory_path)
            self.log_message(f"Removed directory: {directory_path}")
            return 1
        except Exception as e:
            self.log_message(f"Failed to remove directory {directory_path}: {e}")
            return -1

    def remove_file(self, file_path):
        """Removes file"""
        try:
            os.remove(file_path)
            self.log_message(f"Removed file: {file_path}")
            return 1
        except Exception as e:
            self.log_message(f"Failed to remove file {file_path}: {e}")
            return -1

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
            self.log_message(f"Error hashing file {file_path}")

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
