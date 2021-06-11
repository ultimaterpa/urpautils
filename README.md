# urpautils

Helper module for [UltimateRPA](https://www.ultimaterpa.com) robots

Contains universal functions usable across all urpa robots

urpautils is split into two main categories:
- universal ulitities including utilities for working with text or csv files, verifiing BIN or personal identification numbers,
utilities for applicatioins such as killing them or clearing cache...
- utilities used directly by urpa robot (i.e. they use methods from the urpa library)

# Examples
## Universal utilities for working with files
```python
import urpautils

# Remove directory
urpautils.remove_dir("C:\\path\\to\\dir")

# Remove file
urpautils.remove("C:\\path\\to\\file.txt")

# Move file
urpautils.move("C:\\path\\to\\source_file.txt", "C:\\path\\to\\destination_file.txt")

# Copy file
urpautils.copy("C:\\path\\to\\source_file.txt", "C:\\path\\to\\destination_file.txt")

# Remove all files from a directory that are older than 30 days
urpautils.remove_files_older_than("C:\\path\\to\\dir", 30)
```

## Universal utilities for reading and writing text files
```python
import urpautils

# All functions bellow have optional argument 'encoding' which defaults to 'utf-8-sig'

# Write to text file
urpautils.write_txt_file("C:\\path\\to\\file.txt", "This will be written to the file", mode="w")

# Append to text file
urpautils.write_txt_file("C:\\path\\to\\file.txt", "This will be appended to the file", mode="a")

# Read text file. Return None if the file does not exist
content = read_txt_file("C:\\path\\to\\file.txt")

## Use helper file
# Initiate. Creates the file if it does not exist and sets its value to 0
sequence = urpautils.Helper("sequence.txt")
# Get helper value
value = sequence.get()
# Write helper value
sequence.write(1)
# Increment helper value. This method has optional argument 'increment' which defaults to 1
incremented_value = sequence.increment()
# Delete the file
sequence.delete()
```

## Other universal utilities for working with files
```python
import urpautils

# Archivate file
# This function has two optional arguments:
#   'prefix_timestamp_format': adds timestamp prefix to the file name
#   'force_rewrite': if set to True the file is rewritten if already exists
urpautils.archivate_file(
    "C:\\path\\to\\source_file.txt",
    "C:\\path\\to\\destination_file.txt",
    prefix_timestamp_format="%Y-%m-%d",
    force_rewrite=True
)

# Create a directory if it doesn't exist
urpautils.prepare_dir("C:\\path\\to\\dir")

# Copy error screenshot
# This function has 4 optional arguments:
#   'output_file_name': name of the output file. Original name is used if None
#   'screenshot_format': png or bmp. Defaults to png
#   'current_log_dir': direcotry with the error screenshots. Defaults to "log\name_of_main_file_RRRR-MM-DD"
#   'offset': integer saying which file to copy startind from the end (0->last file, 1->second last file, ...)
newly_created_image_path = urpautils.copy_error_img("C:\\path\\to\\destination_directory")

```

## Universal utilities for working with CSV files
```python
import urpautils

# Properties such as encoding, delimeter and newline can be set via optional arguments with corresponding name

# Create csv file and write header to it
urpautils.csv_create_file("C:\\path\\to\\file.csv", header=["1st column", "2nd column"])

# Append row to an existing CSV file
urpautils.csv_append_row("C:\\path\\to\\file.csv", ["foo", "bar"])

# Read rows from CSV file
#   besides optional arguments such as newline or encoding this function contains two more arguments:
#   'start_row_index' and `end_row_index`. All rows are read if not provided
urpautils.csv_read_rows("C:\\path\\to\\file.csv")

```

## Miscellaneous universal utilities
```python
import urpautils

# Get timestamp
timestamp = urpautils.timestamp()

# Modify path to avoid win32api 260 character limit
modified_path = urpautils.add_long_path_prefix("C:\\very\long\path")

# Kill proccess tree
urpautils.killapp("image_name")

# Send an email
urpautils.send_email_notification(
    "sender@stringdata.cz",
    ["recipient1@gmail.com", "recipient2@gmail.com"],
    ["recipient_copy1@gmail.com", "recipient_copy2@gmail.com"],
    "This is a subject",
    "This is the email body",
    "SMTP_server.com"
)

# Verify Personal Identification Number (Rodně číslo)
is_valid = urpautils.verify_rc("990512/1234")

# Verify BIN (IČO)
is_valid = urpautils.verify_ico("12345678")

# Clear Internet Exporer Cache and disable "customize" window at first run
urpautils.clear_ie_cache()

# Get PID of an application
pid_1 = urpautils.get_app_pid("chrome.exe")
# Get PID of another instance of the same application
pid_2 = urpautils.get_app_pid("chrome.exe", pids_to_exclude=[pid_1])
# Get PID of yet another instance of the same application
pid_3 = urpautils.get_app_pid("chrome.exe", pids_to_exclude=[pid_1, pid_2])

```

## Utilities dependent on the urpa library
```python
import urpa
import urpautils

cf = urpa.condition_factory()

# Setup robot with 1920x1080 32bit resolution
urpautils.setup_robot((1920, 1080, 32))

# Search for two or more elements in parallel
index, elements = urpautils.parallel_search(urpa.App, cf.window(), cf.button())

# Find control elements
urpautils.check_elements(urpa.App, cf.window(), cf.button())

```