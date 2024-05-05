import os
import random
import string

def create_random_text_file(file_path):
    """Create a text file with random content."""
    with open(file_path, 'w') as f:
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(20, 100)))
        f.write(content)

def create_nested_folders_and_files(base_path, num_folders=3, num_files=5, depth=2):
    """Recursively create nested folders and files."""
    if depth == 0:
        return
    for _ in range(num_folders):
        folder_name = ''.join(random.choices(string.ascii_letters, k=5))
        folder_path = os.path.join(base_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        for _ in range(num_files):
            file_name = ''.join(random.choices(string.ascii_letters, k=5)) + '.txt'
            file_path = os.path.join(folder_path, file_name)
            create_random_text_file(file_path)
        create_nested_folders_and_files(folder_path, num_folders, num_files, depth - 1)

def main():
    base_path = 'source'
    if os.path.exists(base_path):
        os.rmdir(base_path)
    os.makedirs(base_path, exist_ok=True)
    create_nested_folders_and_files(base_path)

if __name__ == "__main__":
    main()
