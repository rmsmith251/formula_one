import requests
from zipfile import ZipFile
import os
import sqlite3
import csv


def setup():
    """
    Downloads the package, unzips the file, creates the DB if necessary,
    and loads the data into the DB for easier access.
    Optionally, one can also import the CSV files into sqlite using the CLI and .import function.
    """
    print('Initiating data setup...')

    wd = os.getcwd()
    path = os.path.join(wd, 'files')

    # Call download and load into local environment
    if 'f1db_csv.zip' not in os.scandir(wd):
        link = 'http://ergast.com/downloads/f1db_csv.zip'
        r = requests.get(link, allow_redirects=True)
        open('f1db_csv.zip', 'wb').write(r.content)
    else:
        print('Zip file already exists.')

    if not path:
        os.mkdir(path)
    with ZipFile('f1db_csv.zip', 'r') as z:
        z.extractall(path)

    # Checks if all tables have been made in the required database
    # creates the DB and tables if they don't exist
    create_tables_db()
    insert_from_csv()

    try:
        os.remove('f1db_csv.zip')
    except Exception as error:
        print(error)

    print('Setup complete.')


def create_tables_db():
    """
    Creates new tables in an sqlite DB to avoid the slow access time and
    difficult handling of data in multiple CSV files.
    Throws an exception if the table exists.
    """

    con = sqlite3.connect('f1.db')
    cur = con.cursor()

    sql = (
        """
        CREATE TABLE circuits (
        circuitId INTEGER NOT NULL,
        circuitRef VARCHAR(255) DEFAULT "" NOT NULL,
        name VARCHAR(255) DEFAULT "" NOT NULL,
        location VARCHAR(255),
        country VARCHAR(255),
        lat REAL,
        lng REAL,
        alt INTEGER,
        url VARCHAR(255) DEFAULT "" NOT NULL,
        UNIQUE(url),
        PRIMARY KEY(circuitId)
        )
        """,
        """
        CREATE TABLE constructor_results (
        constructorResultsId INTEGER NOT NULL,
        raceId INTEGER DEFAULT 0 NOT NULL,
        constructorId INTEGER DEFAULT 0 NOT NULL,
        points REAL,
        status VARCHAR(255),
        PRIMARY KEY(constructorResultsId)
        )
        """,
        """
        CREATE TABLE constructor_standings (
        constructorStandingsId INTEGER NOT NULL,
        raceId INTEGER DEFAULT 0 NOT NULL,
        constructorId INTEGER DEFAULT 0 NOT NULL,
        points REAL DEFAULT 0 NOT NULL,
        position INTEGER,
        positionText VARCHAR(255),
        wins INTEGER DEFAULT 0 NOT NULL,
        PRIMARY KEY(constructorStandingsId)
        )
        """,
        """
        CREATE TABLE constructors (
        constructorId INTEGER NOT NULL,
        constructorRef VARCHAR(255) DEFAULT "" NOT NULL,
        name VARCHAR(255) DEFAULT "" NOT NULL,
        nationality VARCHAR(255),
        url VARCHAR(255) DEFAULT "" NOT NULL,
        UNIQUE(name),
        PRIMARY KEY(constructorId)
        )
        """,
        """
        CREATE TABLE driver_standings (
        driverStandingsId INTEGER NOT NULL,
        raceId INTEGER DEFAULT 0 NOT NULL,
        driverId INTEGER DEFAULT 0 NOT NULL,
        points REAL DEFAULT 0 NOT NULL,
        position INTEGER,
        positionText VARCHAR(255),
        wins INTEGER DEFAULT 0 NOT NULL,
        PRIMARY KEY(driverStandingsId)
        )
        """,
        """
        CREATE TABLE drivers (
        driverId INTEGER NOT NULL,
        driverRef VARCHAR(255) DEFAULT "" NOT NULL,
        number INTEGER,
        code VARCHAR(255),
        forename VARCHAR(255) DEFAULT "" NOT NULL,
        surname VARCHAR(255) DEFAULT "" NOT NULL,
        dob DATE,
        nationality VARCHAR(255),
        url VARCHAR(255) DEFAULT "" NOT NULL,
        UNIQUE(url),
        PRIMARY KEY(driverId)
        )
        """,
        """
        CREATE TABLE lap_times (
        raceId INTEGER NOT NULL,
        driverId INTEGER NOT NULL,
        lap INTEGER NOT NULL,
        position INTEGER,
        time VARCHAR(255),
        milliseconds INTEGER,
        PRIMARY KEY(raceId, driverId, lap)
        )
        """,
        """
        CREATE TABLE pit_stops (
        raceId INTEGER NOT NULL,
        driverId INTEGER NOT NULL,
        stop INTEGER NOT NULL,
        lap INTEGER NOT NULL,
        time NUMERIC NOT NULL,
        duration VARCHAR(255),
        milliseconds INTEGER,
        PRIMARY KEY(raceId, driverId, stop)
        )
        """,
        """
        CREATE TABLE qualifying (
        qualifyId INTEGER NOT NULL,
        raceId INTEGER DEFAULT 0 NOT NULL,
        driverId INTEGER DEFAULT 0 NOT NULL,
        constructorId INTEGER DEFAULT 0 NOT NULL,
        number INTEGER DEFAULT 0 NOT NULL,
        position INTEGER,
        q1 VARCHAR(255),
        q2 VARCHAR(255),
        q3 VARCHAR(255),
        PRIMARY KEY(qualifyId)
        )
        """,
        """
        CREATE TABLE races (
        raceId INTEGER NOT NULL,
        year INTEGER DEFAULT 0 NOT NULL,
        round INTEGER DEFAULT 0 NOT NULL,
        circuitId INTEGER DEFAULT 0 NOT NULL,
        name VARCHAR(255) DEFAULT "" NOT NULL,
        date DATE DEFAULT "0000-00-00" NOT NULL,
        time NUMERIC,
        url VARCHAR(255),
        UNIQUE(url)
        PRIMARY KEY(raceId)
        )
        """,
        """
        CREATE TABLE results (
        resultId INTEGER NOT NULL,
        raceId INTEGER DEFAULT 0 NOT NULL,
        driverId INTEGER DEFAULT 0 NOT NULL,
        constructorId INTEGER DEFAULT 0 NOT NULL,
        number INTEGER,
        grid INTEGER DEFAULT 0 NOT NULL,
        position INTEGER,
        positionText VARCHAR(255) DEFAULT "" NOT NULL,
        positionOrder INTEGER DEFAULT 0 NOT NULL,
        points REAL DEFAULT 0 NOT NULL,
        laps INTEGER DEFAULT 0 NOT NULL,
        time VARCHAR(255),
        milliseconds INTEGER,
        fastestLap INTEGER,
        rank INTEGER DEFAULT 0,
        fastestLapTime VARCHAR(255),
        fastestLapSpeed VARCHAR(255),
        statusId INTEGER DEFAULT 0 NOT NULL,
        PRIMARY KEY(resultId)
        )
        """,
        """
        CREATE TABLE seasons (
        year INTEGER DEFAULT 0 NOT NULL,
        url VARCHAR(255) DEFAULT "" NOT NULL,
        UNIQUE(url)
        PRIMARY KEY(year)
        )
        """,
        """
        CREATE TABLE status (
        statusId INTEGER NOT NULL,
        status VARCHAR(255) DEFAULT "" NOT NULL,
        PRIMARY KEY(statusId)
        )
        """
    )

    for i in sql:
        try:
            cur.execute(i)
        except Exception as error:
            print(error)


def insert_from_csv():
    """
    Inserts the data into the DB.
    """
    conn = sqlite3.connect('f1.db')

    cur = conn.cursor()

    wd = os.getcwd()
    path = os.path.join(wd, 'files')
    for file in os.listdir(path=path):
        file_path = os.path.join(path, file)
        data_to_insert = read_data_from_csv(file_path)

        if len(data_to_insert) > 0:
            table = ''.join(file.split())[:-4]

            col_names, col_nums = get_columns_from_db(cur, table)
            values_str = '?, ' * col_nums
            values_str = values_str[:-2]

            sql = f'INSERT INTO {table}({col_names}) VALUES ({values_str})'

            cur.executemany(sql, data_to_insert)
            conn.commit()

            l = len(data_to_insert)

            print(f'{l} rows inserted.')
        else:
            print('Nothing to insert.')

    conn.close()


def read_data_from_csv(file_path):
    """
    Opens the required CSV and pulls the data
    :param file_path: path of the CSV file to process
    :return: list with CSV content
    """
    with open(file_path, 'r', encoding='utf8') as csv_file:
        r = csv.reader(csv_file)
        next(r)

        data = list()
        for row in r:
            data.append(row)

    return data


def get_columns_from_db(sql_cursor, table_name):
    """
    Takes in the cursor and table name and returns the columns from the DB
    :param sql_cursor: Cursor for the DB
    :param table_name: Table to look up in DB
    :return: Column names in comma separated form from given table in the DB
    """
    column_names = f'PRAGMA table_info({table_name});'
    sql_cursor.execute(column_names)
    column_names = sql_cursor.fetchall()

    col_count = len(column_names)
    col_names = list()

    for name in column_names:
        col_names.append(name[1])

    return ', '.join(col_names), col_count


if __name__ == '__main__':
    setup()

