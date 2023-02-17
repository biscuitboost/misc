import os
import mimetypes
import json

def traverse_directory(directory):
    files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            # Separate the directory name into two fields based on the pattern
            dir_parts = os.path.basename(dirpath).split('(')
            dir1 = dir_parts[0]
            dir2 = dir_parts[1][:-1]
            file_path = os.path.join(dirpath, filename)
            # Get the file size in bytes
            file_size = os.path.getsize(file_path)
            # Get the MIME content type of the file
            content_type, encoding = mimetypes.guess_type(file_path)
            files.append({
                'attributes': {
                    'Directory 1': [dir1],
                    'Directory 2': [dir2],
                    'Filename': [filename]
                },
                'content': [
                    {
                        'contentType': content_type,
                        'filename': file_path,
                        'length': file_size,
                        'offset': 0
                    }
                ]
            })
    return files

if __name__ == '__main__':
    # Set the target directory to traverse
    target_directory = '/path/to/directory'
    # Call the recursive function to traverse the directory
    files = traverse_directory(target_directory)
    # Output the file information as JSON
    output = {
        'collectionName': 'My Collection Name',
        'recordCount': len(files),
        'records': files
    }
    print(json.dumps(output))
