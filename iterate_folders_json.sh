#!/bin/bash

# Set the target directory to traverse
target_dir="/example/directory"

# Output file for JSON data
output_file="output.json"

# Create the JSON header
echo '{"collectionName":"My Collection Name","recordCount":'$(
  find "${target_dir}" -type f | wc -l
)',"records":[' > "${output_file}"

# Traverse the target directory and output file information
find "${target_dir}" -type f -print0 | while IFS= read -r -d $'\0' file; do
  # Separate the directory name into two fields based on the pattern
  dir1=$(echo "$(dirname "${file}")" | sed 's/(.*)//g' | sed 's/\/$//')
  dir2=$(echo "$(dirname "${file}")" | sed 's/.*(\(.*\)).*/\1/g')
  
  # Get the file size in bytes
  file_size=$(stat -c%s "${file}")
  
  # Get the MIME content type of the file
  mime_type=$(file --mime-type -b "${file}")
  
  # Output the file information in JSON format
  printf '{"attributes":{"Directory 1":["%s"],"Directory 2":["%s"],"Filename":["%s"]},"content":[{"contentType":"%s","filename":"%s","length":%s,"offset":0}]}\n' \
    "${dir1}" "${dir2}" "$(basename "${file}")" "${mime_type}" "${file}" "${file_size}" >> "${output_file}"
done

# Create the JSON footer
echo ']}' >> "${output_file}"
