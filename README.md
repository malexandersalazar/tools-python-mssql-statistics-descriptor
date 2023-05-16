# MSSQL Statistics Descriptor

![alt text](/img/viz.png "Snowflake Statistics Descriptor")

A lightweight tool based on sweetviz that generates high-density visualizations to kickstart Exploratory Data Analysis within Snowflake with just one line of code.

## Installation

Copy the `main.py` script and install the requirements located in the dist folder.

```
pip install -r requirements.txt
```

We will also need to download and install the ODBC Driver for SQL Server, this repo is using the ODBC Driver 18 for SQL Server version.

[Download ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

## Getting Started

| Positional argument | Example |
| --- | --- |
| server | tcp:my-sqldbs-dev.database.windows.net |
| database | sqldb-adventureworkslt-dev |
| schema | MySchema |

| Option | Example/Description |
| --- | --- |
| -h, --help | show this help message and exit |
| -u, --user | database-user, server-admin@contoso.com |
| -p, --password | specifies the user password, required only at non-interactive login |
| -r, --rows | specifies the number of rows to sample from the table (default: 500000) |
| -l, --level | specifies the database object level in which the analysis should be executed, "s" for schema and "t" for table (default: "s") |
| -t, --table | specifies the database table name |
| --associations | indicates that a correlation graph should be generated |
| --open-browser | indicates that a web browser tab should be opened while datasets are analyzed |
| --interactive | indicates that program should authenticate with an Azure Active Directory identity using interactive authentication, requires Azure Active Directory admin enabled on Azure SQL server resource |

The default behaviour of the script will load and analyze the specified number of rows of each table in the selected database schema.

```
python main.py tcp:my-sqldbs-dev.database.windows.net sqldb-adventureworkslt-dev SalesLT -u=database-user -p=S3cUr3P@S$w0rD -r=10000
```

The program will build and save locally high-density HTML visualizations and generate an Excel summary with table name, table rows, data size, table index size and parsed record count in a new folder called **obj**.

![alt text](/img/cmd.png "Azure SQL Database Statistics Descriptor")

If we need a correlation graph to be generated for the columns of each table, we must include the `--associations` flag.

```
python main.py tcp:my-sqldbs-dev.database.windows.net sqldb-adventureworkslt-dev SalesLT -u=database-user -p=S3cUr3P@S$w0rD -r=10000 --associations
```

We must consider that correlations and other associations may take a **quadratic time (n^2)** to complete.

![alt text](/img/associations.png "Azure SQL Database Statistics Descriptor")

If we only need the analysis for a single table we must specify "**t**" as `-l` or `--level` argument value with the corresponding **table name** in `-t` or `--table` argument.

```
python main.py tcp:my-sqldbs-dev.database.windows.net sqldb-adventureworkslt-dev SalesLT -u=database-user -p=S3cUr3P@S$w0rD -r=500000 -l=t -t=Product
```

If we need an Azure Active Directory authentication we have to set the `--interactive` flag and enable Azure Active Directory admin for our database.

```
python main.py tcp:my-sqldbs-dev.database.windows.net sqldb-adventureworkslt-dev SalesLT -l=t -t=Product -r=10000 --open-browser --interactive
```

![alt text](/img/aad.png "Azure SQL Database Statistics Descriptor")

## Prerequisites

MSSQL Statistics Descriptor was tested with:

* Python: 3.7.16
* Packages:
    * pyodbc: 4.0.39
    * pandas: 1.3.5
    * sweetviz: 2.1.4
    * XlsxWriter: 3.1.0 
* Anaconda: 2.4.0

## License

This project is licenced under the [MIT License][1].

[1]: https://opensource.org/licenses/mit-license.html "The MIT License | Open Source Initiative"