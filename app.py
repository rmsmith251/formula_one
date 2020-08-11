import scripts
from matplotlib import pyplot as plt
import pandas as pd

# The below link will show the schemas used for dev purposes
# The table names match the file names without .csv
# http://ergast.com/schemas/f1db_schema.txt


def all_time_first():
    """
    Returns heatmap of the seasons with drivers that had more than 5 wins.
    """

    sql = "SELECT drivers.forename || ' ' || drivers.surname AS full_name, " \
          "COUNT(*) AS wins, races.year FROM results " \
          "LEFT JOIN drivers USING(driverId) " \
          "LEFT JOIN races USING(raceId) " \
          "WHERE results.position = 1 " \
          "GROUP BY full_name, year " \
          "HAVING COUNT(*) > 5 " \
          "ORDER BY year DESC;"

    data = scripts.db_pull(sql)
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


def individual_circuit_lap_times(driver, circuit):
    """
    Takes driver and circuit as input and returns ridge plot of lap times by year
    for given driver and circuit as well as finishing place.

    :param driver: Any driver from the drivers table
    :param circuit: Any circuit from the circuits table
    :return: Plot showing lap times across the years
    """

    sql = "SELECT lap, lap_times.milliseconds, drivers.forename || ' ' || drivers.surname AS full_name, " \
          "circuits.name, races.year FROM lap_times " \
          "LEFT JOIN drivers USING(driverId) " \
          "LEFT JOIN races USING(raceId) " \
          "JOIN circuits ON races.circuitId = circuits.circuitId " \
          f"WHERE full_name = '{driver}' AND circuits.name = '{circuit}'"

    data = scripts.db_pull(sql)
    # print(data)

    years = data['year']
    times = data['milliseconds'] / 1000
    title = f"{driver}'s lap time distribution at {circuit} in seconds"

    scripts.ridge_plot(years, times, title)


def lap_times_all_drivers_single_race(circuit, year):
    """
    Plots the distribution of lap-times for all drivers in a single race.
    :param circuit: Desired circuit to show data for
    :param year: Desired year to return the correct race
    :return: Plot of the lap-time distributions
    """

    sql = "SELECT drivers.forename || ' ' || drivers.surname || ' - ' || results.position AS full_name, " \
          "lap_times.milliseconds, races.year, circuits.name FROM lap_times " \
          "LEFT JOIN drivers USING(driverId) " \
          "LEFT JOIN races USING(raceId) " \
          "JOIN circuits ON races.circuitId = circuits.circuitId " \
          "JOIN results USING(raceId, driverId) " \
          f"WHERE races.year = '{year}' AND circuits.name = '{circuit}' " \
          "ORDER BY results.position ASC" \

    data = scripts.db_pull(sql)

    drivers = data['full_name']
    times = data['milliseconds'] / 1000
    title = f'Lap time distributions and final position at {circuit} in {year} (seconds)'

    scripts.ridge_plot(drivers, times, title, label_x_adj=-.03, label_y_adj=.3)


def driver_podium_by_circuit(driver):

    sql = "SELECT drivers.forename || ' ' || drivers.surname AS full_name, " \
          "circuits.name, results.position, COUNT(*) AS circuit_podiums FROM results " \
          "LEFT JOIN drivers USING(driverId) " \
          "LEFT JOIN races USING(raceId) " \
          "JOIN circuits USING(circuitId) " \
          f"WHERE results.position < 4 and full_name = '{driver}' " \
          "GROUP BY full_name, circuits.name " \
          "ORDER BY circuit_podiums ASC"

    data = scripts.db_pull(sql)
    circuits = data['name']
    pods = data['circuit_podiums']
    title = f'{driver} podiums by circuit - all time'

    scripts.bar(circuits, pods, title=title, x_label='Circuit', y_label='Podiums')


def constructor_podium_by_circuit(constructor):
    sql = "SELECT circuits.name AS circuit, results.position, constructors.name AS constructor, " \
          "COUNT(*) AS circuit_podiums FROM results " \
          "LEFT JOIN constructors USING(constructorId) " \
          "LEFT JOIN races USING(raceId) " \
          "JOIN circuits USING(circuitId) " \
          f"WHERE results.position < 4 AND constructor = '{constructor}' " \
          "GROUP BY constructor, circuit " \
          "ORDER BY circuit_podiums ASC"

    data = scripts.db_pull(sql)
    # print(data)
    circuits = data['circuit']
    pods = data['circuit_podiums']
    title = f'{constructor} podiums by circuit - all time'

    scripts.bar(circuits, pods, title=title, x_label='Circuit', y_label='Podiums')


def podiums_by_year(year):
    sql = "SELECT drivers.surname, COUNT(*) AS podiums, constructors.name FROM races " \
          "JOIN results USING(raceId) " \
          "JOIN drivers USING(driverId) " \
          "JOIN constructors USING(constructorId) " \
          f"WHERE races.year = {year} AND results.position < 4 " \
          "GROUP BY drivers.surname " \
          "ORDER BY constructors.name"

    data = scripts.db_pull(sql)
    con_pods = data[['name', 'podiums']].groupby('name').podiums.sum()
    con_pods = [con_pods[i] for i in range(len(con_pods))]
    con_labels = data['name'].unique()
    driver_pods = data['podiums']
    driver_labels = data['surname']
    title = f'Podium breakdown for {year}'

    scripts.nested_pie(con_pods, driver_pods,
                       labels_outer=con_labels, labels_inner=driver_labels, title=title)


if __name__ == '__main__':
    # all_time_first()
    # individual_circuit_lap_times('Lewis Hamilton', 'Autodromo Nazionale di Monza')
    # lap_times_all_drivers_single_race('Autodromo Nazionale di Monza', 2018)
    # driver_podium_by_circuit("Lewis Hamilton")
    # constructor_podium_by_circuit('McLaren')
    podiums_by_year(2019)