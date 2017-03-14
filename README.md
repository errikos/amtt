## Availability Model Translation Toolkit

[![Documentation Status](https://readthedocs.org/projects/amtt/badge/?version=latest)](http://amtt.readthedocs.io/en/latest/?badge=latest)


###Notes
This software was developed in CERN (the European Organization for Nuclear
Research) as part of my Technical Student spell.

This software is under (heavy) development.

### Input Formats
The following input formats are currently supported. You can create your own
format by implementing the `Loader` interface. For more details, please see
the documentation in the `loader` module's `__init__.py` file.

#### CSV Input Format
###### Introduction
This section outlines the specification requirements for the CSV
(Comma Separated Values) input format.

The CSV format is the simpler and most common way to import/export spreadsheet
and database data. The files are plain text files containing one row per
record. The record fields themselves are separated by a predefined delimiter
(most commonly a comma `,` but a semicolon `;` or a `TAB` are also valid
options).

Each CSV file can represent one database table or one spreadsheet sheet. This
means that you cannot have multiple tables or sheets in one file.

###### Model definition
Due to the aforementioned "limitation" of CSV files, you will need to define
(or generate) a collection of CSV files to describe the model, one file per
schema item.

The requirements of the layout are the following:
  1. Each file must be named as `{table_name}.csv`, where `{table_name}` is the
     table name that the file represents, **in lower-case** letters, with an
     underscore (`_`) between words. For example, the file that represents the
     _Components_ table must be named `components.csv`, whereas the file that
     represents the _Logic_ table must be named
     `logic.csv`.
  2. Each file must have a header with the column names in its first row. The
     column names must be **exactly** the same as in the schema specification.

After making sure that the above requirements are met, place all CSV files in
one directory (eg. `csv_input`) and provide the directory path as the input
command line argument in the `csv` option (use `-h` for help).

#### XLS/XLSX Input Format
###### Introduction
The XLS format is also known as the Microsoft Office 2003 Excel format. It is
a different and older format when compared to the Microsoft Office 2007 Excel
format (XLSX).

###### Model definition
The model definition for the XLS/XLSX format is the same as the CSV format,
with the only difference being that it is not necessary (and you should not)
put the tables in different files. Instead, tables should be defined in the
same document, but in separate sheets.

### Output Formats
The following output formats are currently supported.

#### Isograph (Availability Workbench)
Isograph Availability Workbench is an availability simulation tool developed by
Isograph LTD. For more information, please visit the software
[website](https://www.isograph.com/software/availability-workbench/).

As of version 2.1, Isograph Availability Workbench supports importing from XML,
Excel and CSV files, as well as importing from Microsoft Access, Microsoft SQL
Server and Oracle Database. The files that amtt generates are in Excel format.
More formats may be added in the future, mainly database ones. However, for the
time being, no more than Excel file inputs are necessary.
