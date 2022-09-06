# urpautils
![workflow](https://github.com/ultimaterpa/urpautils/actions/workflows/test.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Helper module for [UltimateRPA](https://www.ultimaterpa.com) robots

Contains universal functions usable across all urpa robots

urpautils is split into two main categories:
- universal utilities including utilities for working with text or csv files, verifying BIN or personal identification numbers,
utilities for applications such as killing them or clearing cache...
- utilities used directly by urpa robot (i.e. they use methods from the urpa library)

## Universal utilities examples
### Universal utilities for working with files
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

### Universal utilities for reading and writing text files
```python
import urpautils

# Write to text file
urpautils.write_txt_file("C:\\path\\to\\file.txt", "This will be written to the file", mode="w")

# Append to text file
urpautils.write_txt_file("C:\\path\\to\\file.txt", "This will be appended to the file", mode="a")

# Read text file. Raises FileNotFoundError if the file does not exist
content = urpautils.read_txt_file("C:\\path\\to\\file.txt")

# Read json file. Raises FileNotFoundError if the file does not exist
content = urpautils.read_json_file("C:\\path\\to\\file.json")

# All functions above have optional argument 'encoding' which defaults to 'utf-8-sig'

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

### Other universal utilities for working with files
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
#   'offset': integer saying which file to copy starting from the end (0->last file, 1->second last file, ...)
newly_created_image_path = urpautils.copy_error_img("C:\\path\\to\\destination_directory")

```

### Universal utilities for working with CSV files
```python
import urpautils

# Properties such as encoding, delimiter and newline can be set via optional arguments with corresponding name

# Create csv file and write header to it
# this function also has optional kwarg "sep". If provided it writes "sep=<separator>" to first line of the file so it opens correctly in Excel
urpautils.csv_create_file("C:\\path\\to\\file.csv", header=["1st column", "2nd column"])

# Append row to an existing CSV file
urpautils.csv_append_row("C:\\path\\to\\file.csv", ["foo", "bar"])

# If we have large amount of data stored in dictionaries. We can write them directly with this class
dict_A = {"name": "ben", "surname": "dover"}
dict_B = {"name": "hugh", "surname": "jass"}
dict_C = {"surname": "mcOkiner", "name": "duncan"}
# we need to define which keys to except. "name" and "surname" in this case
dict_writer = urpautils.Csv_dict_writer("C:\\path\\to\\file.csv", ["name", "surname"])
dict_writer.write(dict_A)
dict_writer.write(dict_B)
dict_writer.write(dict_C)

# Read rows from CSV file
#   besides optional arguments such as newline or encoding this function has two more arguments:
#   'start_row_index' and `end_row_index`. All rows are read if not provided
for row in urpautils.csv_read_rows("C:\\path\\to\\file.csv"):
    print(row) # prints `["column1", "column2", "column3", "column4"]`
# by default rows are yilded as lists. Alternatively kwarg "as_dict=True" can be used.
# Rows are then yielded as <first row> : <n-th row> key-value pairs
for row in urpautils.csv_read_rows("C:\\path\\to\\file.csv", as_dict=True):
    print(row) # prints `{"header1": "column1", "header2": "column2", "header3": "column3", "header4": "column4"}`

```

### Miscellaneous universal utilities
```python
import urpautils

# Get timestamp
timestamp = urpautils.timestamp()

# Modify path to avoid win32api 260 character limit
modified_path = urpautils.add_long_path_prefix("C:\\very\long\path")

# Kill process tree
urpautils.killapp("image_name")

# Send an email
# port is an optional argument. smtplib.SMTP_PORT (=25) is used if not provided
# attachments is an optional argument
# there is one more optional arg: debug_level (defaults to 0)
urpautils.send_email_notification(
    "sender@stringdata.cz",
    ["recipient1@gmail.com", "recipient2@gmail.com"],
    ["recipient_copy1@gmail.com", "recipient_copy2@gmail.com"],
    "This is a subject",
    "This is the email body",
    "SMTP_server.com",
    smtp_port = 1234,
    attachments = ["path/to/file1.jpg", "path/to/file2.jpg"]
)

# Verify Personal Identification Number (Rodné číslo)
is_valid = urpautils.verify_rc("990512/1234")

# Verify BIN (IČO)
is_valid = urpautils.verify_ico("12345678")

# Pad BIN (IČO) with zeros to length 8
padded_bin = urpautils.justify_ico("1234") # returns 00001234
padded_bin = urpautils.justify_ico("1234", "5") # returns 55551234

# Clear Internet Explorer Cache and disable "customize" window at first run
urpautils.clear_ie_cache()

# Get PID of an application
pid_1 = urpautils.get_app_pid("chrome.exe")
# Get PID of another instance of the same application
pid_2 = urpautils.get_app_pid("chrome.exe", pids_to_exclude=[pid_1])
# Get PID of yet another instance of the same application
pid_3 = urpautils.get_app_pid("chrome.exe", pids_to_exclude=[pid_1, pid_2])

# Get previous work day date. By default it uses today as reference and Czech holidays
previous_work_day_date = get_previous_work_day_date()
# You can specify day to use as reference as well as other countries' holidays
previous_work_day_date = get_previous_work_day_date(today=datetime.date(2021, 9, 2), country="US")
```

## Utilities dependent on the urpa library examples
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

# Save file as
# by default it assumes Save As window is already opened
urpautils.save_as("file.txt")
# you can instruct the function to open the window for you
# in that case you need to provide an App element on which to open the window
urpautils.save_as("file.txt", open_save_as_window=True, app_elem=some_app_elem)
# you might need to specify the shortcut for opening Save As window aswell (defaults to CTRL+SHIT+S)
urpautils.save_as("file.txt", open_save_as_window=True, app_elem=some_app_elem, open_save_as_window_shortcut="ALT+S")
# by default it uses most common element names based on your system language (i.e. window name "Save As" for ENG and "Uložit jako" for CZE). In some cases theese can be different
urpautils.save_as("file.txt", save_as_window_name="Save file as...")
# If the file already exists you can choose to rewrite it
urpautils.save_as("file.txt", force_rewrite=True)

# Open file
# similar to Save As, this opens a file. By default it assumes Open window is already opened
urpautils.open_file("file.txt")
# you can instruct the function to open the window for you
urpautils.save_as("file.txt", open_open_file_window=True, app_elem=some_app_elem)
# specifying shortcut and element names is same as with `save_as` function

# Decorate a function to send an email with error screenshot if an Exception is raised
# Decorator function has optional arguments smtp_port (default 25), screenshot_format (default "png"), current_log_dir (default "log\name_of_main_file_RRRR-MM-DD")
@urpautils.failed_login_notification(
    "sender@stringdata.cz",
    ["receiver@stringdata.cz"],
    ["receiver_copy@stringdata.cz"],
    "subject",
    "body",
    "smtp_server.cz"
)
def my_decorated_function():
    # before SomeError is raised the email is sent
    raise SomeError
```