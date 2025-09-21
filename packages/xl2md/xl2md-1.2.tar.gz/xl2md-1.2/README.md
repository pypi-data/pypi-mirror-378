# xl2md

A simple, fast, and configurable utility to convert sheets in an Excel workbook into clean Markdown tables.

Manually copying data from Excel into Markdown is tedious and error-prone. **`xl2md`** automates this process, preserving the structure of your sheets and providing a command-line tool for quick conversions and a Python library for advanced control.

## Key Features

  * **Batch Conversion**: Automatically converts every sheet in a workbook to a separate Markdown file.
  * **Simple CLI**: A straightforward command-line interface for easy use in any terminal.
  * **Flexible Library**: Import the converter into your own Python scripts for customized workflows.
  * **Smart Formatting**: Handles common Excel quirks like `Unnamed:` columns and correctly escapes special Markdown characters.
  * **Safe Filenames**: Automatically creates "slugified," web-safe filenames from sheet names (e.g., "Q3 Financial Report" becomes `Q3-Financial-Report.md`).
  * **Customizable**: Control the output directory, overwrite behavior, and more.

-----

## Installation

You can install `xl2md` directly from PyPI using pip.

```bash
pip install xl2md
```

-----

## Usage

`xl2md` can be used as a command-line tool or as a Python library.

### 1\. Command-Line Interface (CLI)

This is the quickest way to convert a file. The basic command requires only the path to your Excel workbook.

**Basic Conversion**

```bash
xl2md path/to/your/workbook.xlsx
```

By default, this command will:

1.  Read the `workbook.xlsx` file.
2.  Create a new directory named `markdown_sheets` in your current location.
3.  Save each converted sheet as a separate `.md` file inside `markdown_sheets`.

**CLI Options**

You can customize the behavior with the following options:

  * `--out-dir <directory>`: Specifies a different output directory for the Markdown files.

    ```bash
    xl2md my_data.xlsx --out-dir "converted_docs"
    ```

  * `--overwrite`: Overwrites existing Markdown files in the output directory if they have the same name. Without this flag, existing files will be skipped.

    ```bash
    xl2md my_data.xlsx --overwrite
    ```

  * `--no-safe-filenames`: Uses the original sheet names for filenames instead of converting them to a safe, URL-friendly format. **Warning:** This may cause issues if sheet names contain special characters.

    ```bash
    xl2md "My Workbook.xlsx" --no-safe-filenames
    ```

  * `-v` or `--verbose`: Enables detailed (DEBUG level) logging, which is helpful for troubleshooting.

    ```bash
    xl2md my_data.xlsx -v
    ```

**Example Combining Options**

```bash
xl2md "Financial Report Q3 2025.xlsx" --out-dir "reports/markdown" --overwrite --verbose
```

-----

### 2\. As a Python Library

For more advanced control, import `ExcelToMarkdownConverter` and `ConverterOptions` into your own Python scripts. This allows you to filter sheets, include the DataFrame index, and integrate the conversion into a larger automation workflow.

**Basic Library Usage**

```python
from xl2md import ExcelToMarkdownConverter

# Initialize with the path to your Excel file
converter = ExcelToMarkdownConverter(excel_path="path/to/my_workbook.xlsx")

# Run the conversion with default options
written_files = converter.convert()

print(f"Successfully converted files: {written_files}")
```

**Advanced Configuration**

The `ConverterOptions` class lets you fine-tune the conversion process.

```python
from xl2md import ExcelToMarkdownConverter, ConverterOptions
import logging

# 1. Configure your desired options
options = ConverterOptions(
    out_dir="./custom_output",      # Set a custom output directory
    overwrite=True,                 # Overwrite existing files
    include_index=True,             # Include the DataFrame index in the table
    index_label="Row ID",           # Set a custom label for the index column
    log_level=logging.DEBUG,        # Set the logging level
    
    # Only convert sheets whose names start with "Report_" (uses regex)
    sheet_name_allowlist=[r"Report_.+"],
    
    # Skip any sheets containing the word "Internal" (case-insensitive)
    sheet_name_blocklist=[r"Internal"]
)

# 2. Initialize the converter with the file path and custom options
try:
    converter = ExcelToMarkdownConverter(
        excel_path="financials.xlsx",
        options=options
    )

    # 3. Run the conversion
    written_files = converter.convert()

    if written_files:
        print(f"✅ Conversion complete. Files written to '{options.out_dir}':")
        for f in written_files:
            print(f"  - {f}")
    else:
        print("⚠️ No sheets were converted. Check your allow/block lists and file content.")

except Exception as e:
    print(f"❌ An error occurred: {e}")

```

-----

## Contributing

Contributions are welcome\! If you have a suggestion or find a bug, please open an issue on the GitHub repository. Pull requests are also greatly appreciated.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

-----

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.