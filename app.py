import scripts
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import sqlite3
import seaborn as sns

# The below link will show the schemas used for dev purposes
# The table names match the file names without .csv
# http://ergast.com/schemas/f1db_schema.txt


def all_time_first():
    """
    Returns heatmap of the seasons with drivers that had more than 5 wins.
    """

    conn = None

    try:
        conn = sqlite3.connect('f1.db')
        cur = conn.cursor()

        sql = "SELECT drivers.forename || ' ' || drivers.surname AS full_name, " \
              "COUNT(*) AS wins, races.year FROM results " \
              "LEFT JOIN drivers USING(driverId) " \
              "LEFT JOIN races USING(raceId) " \
              "WHERE results.position = 1 " \
              "GROUP BY full_name, year " \
              "HAVING COUNT(*) > 5 " \
              "ORDER BY year DESC;"

        data = pd.read_sql_query(sql, conn)
        # print(data)
        seasons = data['year'].unique()
        drivers = data['full_name'].unique()

        d = {i: [] for i in drivers}
        for driver in drivers:
            for season in seasons:
                value = data.query(f'full_name == "{driver}" & year == {season}')['wins'].sum()
                d[f'{driver}'].append(value)

        # print(d)

        wins = pd.DataFrame(d).to_numpy()
        # print(wins)

        fig, ax = plt.subplots(1, 1)

        im, cbar = scripts.heatmap(wins, seasons, drivers, ax=ax, cmap="turbo", cbarlabel="Wins", aspect='auto')
        texts = scripts.annotate_heatmap(im, valfmt="{x:.0f}")

        ax.set_title('Drivers with more than 5 wins in a season since 1952')

        plt.subplots_adjust(bottom=0.043, top=0.895)

        plt.get_current_fig_manager().window.state('zoomed')

        plt.show()

        cur.close()
    except (Exception, sqlite3.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def individual_circuit_lap_times(driver, circuit):
    """
    Takes driver and circuit as input and returns ridge plot of lap times by year
    for given driver and circuit as well as finishing place.

    :param driver: Any driver from the drivers table
    :param circuit: Any circuit from the circuits table
    :return: Plot showing lap times across the years
    """

    conn = None

    try:
        conn = sqlite3.connect('f1.db')
        cur = conn.cursor()

        sql = "SELECT lap, lap_times.milliseconds, drivers.forename || ' ' || drivers.surname AS full_name, " \
              "circuits.name, races.year FROM lap_times " \
              "LEFT JOIN drivers USING(driverId) " \
              "LEFT JOIN races USING(raceId) " \
              "JOIN circuits ON races.circuitId = circuits.circuitId " \
              f"WHERE full_name = '{driver}' AND circuits.name = '{circuit}'"

        data = pd.read_sql_query(sql, conn)
        # print(data)

        years = data['year']
        times = data['milliseconds'] / 1000
        title = f"{driver}'s lap time distribution at {circuit} in seconds"

        scripts.ridge_plot(years, times, title)

        cur.close()
    except Exception as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def lap_times_all_drivers_single_race(circuit, year):
    """

    :param circuit:
    :param year:
    :return:
    """

    conn = None
    try:
        conn = sqlite3.connect('f1.db')
        cur = conn.cursor()

        sql = "SELECT drivers.forename || ' ' || drivers.surname || ' - ' || results.position AS full_name, " \
              "lap_times.milliseconds, races.year, circuits.name FROM lap_times " \
              "LEFT JOIN drivers USING(driverId) " \
              "LEFT JOIN races USING(raceId) " \
              "JOIN circuits ON races.circuitId = circuits.circuitId " \
              "JOIN results USING(raceId, driverId) " \
              f"WHERE races.year = '{year}' AND circuits.name = '{circuit}' " \
              "ORDER BY results.position ASC" \

        data = pd.read_sql_query(sql, conn)
        # print(data)

        drivers = data['full_name']
        times = data['milliseconds'] / 1000
        # print(max(times))
        title = f'Lap time distributions and final position at {circuit} in {year} (seconds)'

        scripts.ridge_plot(drivers, times, title, label_x_adj=-.03, label_y_adj=.3)

        cur.close()
    except Exception as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    # all_time_first()
    # individual_circuit_lap_times('Lewis Hamilton', 'Autodromo Nazionale di Monza')
    lap_times_all_drivers_single_race('Autodromo Nazionale di Monza', 2018)