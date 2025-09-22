
# Setup Python path before imports
import scripts.setup_path  # noqa: F401

import os

from batem.reno.battery.model import (
    Battery, BatteryConfig, BatterySimulationResult, NaiveStrategy)
from batem.reno.house.creation import HouseBuilder
from batem.reno.house.model import House
from batem.reno.house.services import ConsumptionAggregator, ConsumptionTrimmer
from batem.reno.indicators import (
    cost, neeg, self_consumption, self_sufficiency)
from batem.reno.plot.base import Plotter
from batem.reno.plot.battery import (
    BatteryDataProcessor, BatteryPlotConfig, BatteryRenderer,
    BatteryAxesConfigurator, BatteryFigureSaver,
    InteractiveAxesConfigurator, InteractiveFigureSaver, InteractiveRenderer)
from batem.reno.pv.creation import PVPlantBuilder, WeatherDataBuilder
from batem.reno.pv.model import PVPlant
from batem.reno.utils import FilePathBuilder, TimeSpaceHandler


def calculate_indicators(house: House, pv_plant: PVPlant,
                         battery: Battery | None = None):
    if not house.consumption.usage_hourly:
        raise ValueError("Consumption is not set")
    if not pv_plant.production.usage_hourly:
        raise ValueError("Production is not set")

    battery_power_by_time = (
        battery.get_battery_power_by_time() if battery else {})
    consumption_by_time = house.consumption.usage_hourly
    production_by_time = pv_plant.production.usage_hourly

    neeg_value = neeg(
        consumption_by_time,
        production_by_time,
        battery_power_by_time=battery_power_by_time)
    sc_value = self_consumption(
        consumption_by_time,
        production_by_time,
        battery_power_by_time=battery_power_by_time)
    ss_value = self_sufficiency(consumption_by_time,
                                production_by_time,
                                battery_power_by_time=battery_power_by_time)
    opex_cost_value = cost(consumption_by_time,
                           production_by_time,
                           battery_power_by_time=battery_power_by_time)

    return neeg_value, sc_value, ss_value, opex_cost_value


if __name__ == "__main__":

    # python scripts/battery_control.py

    time_space_handler = TimeSpaceHandler(location="Bucharest",
                                          start_date="01/02/1998",
                                          end_date="01/02/1999")

    house = HouseBuilder().build_house_by_id(2000901)

    weather_data = WeatherDataBuilder().build(
        location=time_space_handler.location,
        latitude_north_deg=time_space_handler.latitude_north_deg,
        longitude_east_deg=time_space_handler.longitude_east_deg,
        from_datetime_string=time_space_handler.start_date,
        to_datetime_string=time_space_handler.end_date)

    pv_plant = PVPlantBuilder().build(weather_data=weather_data,
                                      exposure_deg=0,
                                      slope_deg=160,
                                      number_of_panels=10,
                                      peak_power_kW=5)

    ConsumptionTrimmer(house).trim_consumption_house(time_space_handler)
    house.consumption.usage_hourly = ConsumptionAggregator(
        house).get_total_consumption_hourly()

    initial_neeg, initial_sc, initial_ss, opex_cost = calculate_indicators(
        house, pv_plant)

    print("--------------------------------")
    print(f"Initial NEEG: {initial_neeg:.3f}")
    print(f"Initial SC: {initial_sc:.3f}")
    print(f"Initial SS: {initial_ss:.3f}")
    print(f"Initial OPEX Cost: {opex_cost:.3f}")

    battery_config = BatteryConfig(
        capacity_kWh=14,
        max_discharge_power_kW=5,
        max_charge_power_kW=5,
        round_trip_efficiency=0.9)

    battery = Battery(strategy=NaiveStrategy(battery_config),
                      config=battery_config)

    for time, consumption in house.consumption.usage_hourly.items():
        production = pv_plant.production.usage_hourly[time]
        battery.step(time, consumption, production)

    final_neeg, final_sc, final_ss, final_opex_cost = calculate_indicators(
        house, pv_plant, battery)
    print("--------------------------------")
    print(f"Final NEEG: {final_neeg:.3f}")
    print(f"Final SC: {final_sc:.3f}")
    print(f"Final SS: {final_ss:.3f}")
    print(f"Final OPEX Cost: {final_opex_cost:.3f}")

    folder = FilePathBuilder().get_simulation_plots_folder()
    file_path = os.path.join(folder, "battery_plot.png")

    Plotter(
        config=BatteryPlotConfig(
            file_path=file_path,
            as_png=True,
            size=(10, 5)),
        data_processor=BatteryDataProcessor(),
        renderer=BatteryRenderer(),
        axes_configurator=BatteryAxesConfigurator(),
        figure_saver=BatteryFigureSaver()
    ).plot(BatterySimulationResult(battery=battery,
                                   house=house,
                                   pv_plant=pv_plant))

    interactive_file_path = os.path.join(
        folder, "battery_plot_interactive.html")

    Plotter(
        config=BatteryPlotConfig(
            file_path=interactive_file_path,
            as_png=True,
            size=(10, 5)),
        data_processor=BatteryDataProcessor(),
        renderer=InteractiveRenderer(),
        axes_configurator=InteractiveAxesConfigurator(),
        figure_saver=InteractiveFigureSaver()
    ).plot(BatterySimulationResult(battery=battery,
                                   house=house,
                                   pv_plant=pv_plant))
