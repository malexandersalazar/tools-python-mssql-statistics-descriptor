import argparse

parser=argparse.ArgumentParser(
    description='A lightweight tool based on sweetviz that generates high-density visualizations to kickstart Exploratory Data Analysis within Microsoft Azure SQL Database with just one line of code.',
    epilog='github.com/malexandersalazar/tools-python-mssql-statistics-descriptor')
parser.add_argument('server', type=str, help='tcp:my-db-server.database.windows.net')
parser.add_argument('database', type=str, help='sqldb-adventureworkslt-dev')
parser.add_argument('schema', type=str, help='MySchema')
parser.add_argument('-u','--user', type=str, help='database-user, server-admin@contoso.com')
parser.add_argument('-p','--password', type=str, help='specifies the user password, required only at non-interactive login')
parser.add_argument('-r','--rows', default=500000, type=int, help='specifies the number of rows to sample from the table (default: 500000)')
parser.add_argument('-l','--level', choices=['s','t'], default='s', type=str, help='specifies the database object level in which the analysis should be executed, "s" for schema and "t" for table (default: "s")')
parser.add_argument('-t','--table', type=str, help='specifies the database table name')
parser.add_argument('--associations', dest='associations', action='store_true', help='indicates that a correlation graph should be generated')
parser.set_defaults(associations=False)
parser.add_argument('--open-browser', dest='open_browser', action='store_true', help='indicates that a web browser tab should be opened while datasets are analyzed')
parser.set_defaults(open_browser=False)
parser.add_argument('--interactive', dest='interactive', action='store_true', help='indicates that program should authenticate with an Azure Active Directory identity using interactive authentication, requires Azure Active Directory admin enabled on Azure SQL server resource')
parser.set_defaults(interactive=False)
args=parser.parse_args()

SERVER = args.server
DATABASE = args.database
SCHEMA = args.schema
UID = args.user
PASSWORD = args.password
DRIVER = '{ODBC Driver 18 for SQL Server}'
ROWS = args.rows
LEVEL = args.level
TABLE = args.table
ASSOCIATIONS = args.associations
OPEN_BROWSER = args.open_browser
INTERACTIVE = args.interactive

import os
import pyodbc
import pandas as pd
import sweetviz as sv
import gc

def create_connection():
    if INTERACTIVE:
        return pyodbc.connect('DRIVER='+DRIVER+';SERVER='+SERVER+';PORT=1433;DATABASE='+DATABASE+';AUTHENTICATION=ActiveDirectoryInteractive')
    else:
        return pyodbc.connect('DRIVER='+DRIVER+';SERVER='+SERVER+';PORT=1433;DATABASE='+DATABASE+';UID='+UID+';PWD='+ PASSWORD)

tables = []

if(LEVEL=='s'):
    with create_connection() as conn1:
        with conn1.cursor() as schema_cur:
            schema_cur.execute(f"SELECT TABLE_NAME FROM [{DATABASE}].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA='{SCHEMA}'")
            schema_row = schema_cur.fetchone()
            while schema_row:
                table_name = str(schema_row[0]) 
                with create_connection() as conn2:
                    with conn2.cursor() as space_cur:
                        space_cur.execute(f"EXEC sp_spaceused N'{SCHEMA}.{table_name}'") # result columns: name rows reserved data index_size unused
                        space_row = space_cur.fetchone()
                        rows = str(space_row[1])
                        data = str(space_row[3]) 
                        index_size = str(space_row[4]) 
                        tables.append((f'{SCHEMA}.{table_name}',rows,data,index_size))
                schema_row = schema_cur.fetchone()
else:
    with create_connection() as conn2:
        with conn2.cursor() as space_cur:
            space_cur.execute(f"EXEC sp_spaceused N'{SCHEMA}.{TABLE}'") # result columns: name rows reserved data index_size unused
            space_row = space_cur.fetchone()
            rows = str(space_row[1])
            data = str(space_row[3]) 
            index_size = str(space_row[4]) 
            tables.append((f'{SCHEMA}.{TABLE}',rows,data,index_size))

if not os.path.exists('obj'):
    os.mkdir('obj')

info_arr = []

for (table_name,rows,data,index_size) in tables:
    print(f'Loading {table_name}...')

    sheet_name = table_name.split('.')[-1]

    sample_query = f'SELECT * FROM {table_name} TABLESAMPLE ({ROWS} ROWS)'
    with create_connection() as conn3:
        sample_cur = conn3.cursor().execute(sample_query)
        sample_df = pd.DataFrame.from_records(
            iter(sample_cur), columns=[x[0] for x in sample_cur.description])

        info_arr.append([table_name,rows,data,index_size, len(sample_df)])

        analysis = sv.analyze(sample_df, pairwise_analysis=("on" if ASSOCIATIONS else "off"))
        analysis.show_html(f'obj/{sheet_name}.html', open_browser=OPEN_BROWSER)

    del sample_df
    gc.collect()

# Writing summary
eda_info_df = pd.DataFrame(info_arr, columns = ['NAME','TABLE ROWS','DATA','INDEX SIZE','SAMPLE ROWS'])
excel_writer = pd.ExcelWriter(f'obj/{SCHEMA}_EDA_INFO.xlsx', engine='xlsxwriter')
eda_info_df.to_excel(excel_writer, sheet_name=SCHEMA, index=False)
worksheet = excel_writer.sheets[SCHEMA]
for idx, col in enumerate(eda_info_df):  # Loop through all columns
    series = eda_info_df[col]
    max_len = max((
        series.astype(str).str.len().max(),  # Len of largest item
        len(str(series.name))  # Len of column name/header
        )) + 9  # Adding a little extra space
    worksheet.set_column(idx, idx, max_len)  # Set column width
excel_writer.close()