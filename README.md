# wageo - wage organiser

## Introduction

As a person living in the UK holding Slovak citizenship, I am obliged to report tax for each calendar year (January–December).  
The salary in Slovakia is paid monthly, and this app helps me scan weekly payslips and import them into Excel.

## Usage

Create a directory called ```payslips``` and import weekly wage PDFs into this directory.  
Run the app by executing:

```bash
python app.py
```

## How it works
This tool works only with Iris and Sage formatted payslips<br>
The app will scan your payslips and, depending on the <i>date</i> formatting it will append the data into a dictionary.<br>
Calling the functions ``` calculate_monthly ``` and ``` calculate_annually ``` will calculate and return the data, which can then be exported into a ``` .txt ``` and ``` .xlsx ```(Excel) file.

## Requirements

Dependencies are listed in [requirements.txt](https://github.com/Dendop/wageo/blob/main/requirements.txt)<br>
For installation, run:
```bash
pip install -r requirements.txt
```
## Additional
The [my_test.py](https://github.com/Dendop/wageo/blob/main/my_test.py) file is used only for testing or showing the variables and data stored in the dictionaries/variables.
