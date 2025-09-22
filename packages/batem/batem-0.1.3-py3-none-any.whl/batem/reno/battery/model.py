

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import sqrt

from batem.reno.house.model import House
from batem.reno.pv.model import PVPlant


@dataclass
class BatteryConfig:
    """
    The config is the battery configuration.
    The capacity_kWh is the capacity of the battery in kWh.
    The max_discharge_power_kW is the maximum discharge power for a time step
    of the battery in kW.
    The max_charge_power_kW is the maximum charge power for a time step
    of the battery in kW.
    The round_trip_efficiency is the efficiency of the battery.
    """
    capacity_kWh: float
    max_discharge_power_kW: float
    max_charge_power_kW: float
    round_trip_efficiency: float


class Command(Enum):
    charge = 0
    discharge = 1
    do_nothing = 2


@dataclass
class BatteryState:
    """
    The state of the battery at a given time step.

    The timestamp is the current time step.
    The soc is the state of charge of the battery.
    The power is the power of the battery in kW.
    The command is the command of the battery (charge, discharge, do_nothing).
    """
    timestamp: datetime
    soc: float
    power: float
    command: Command


class Strategy(ABC):

    def __init__(self, config: BatteryConfig):
        self._config = config

    @abstractmethod
    def apply(self, consumption_kW: float, production_kW: float
              ) -> tuple[Command, float]:
        """
        Applies a strategy to determine what command and how much power to
        extract or inject into the battery.

        Args:
            consumption_kW: The consumption power in kW
            production_kW: The production power in kW

        Returns:
        tuple[Command, float]: The command and the power to
        extract or inject into the battery

        Example:
            >>> command, power = battery._apply_strategy(10, 20)
            >>> print(command, power)
            >>> Command.charge, 10
        """
        pass


class NaiveStrategy(Strategy):
    def __init__(self, config: BatteryConfig):
        super().__init__(config)

    def apply(self, consumption_kW: float, production_kW: float
              ) -> tuple[Command, float]:

        required_power = consumption_kW - production_kW

        if required_power > 0:
            # if consumption is greater than production,
            # then we need to draw positive power from the battery
            return (Command.discharge, required_power)
        elif required_power < 0:
            # if consumption is less than production,
            # then we need to charge negative power into the battery
            return (Command.charge, required_power)
        else:
            return Command.do_nothing, 0


class Battery:
    def __init__(self, strategy: Strategy, config: BatteryConfig,
                 init_soc: float = 0.8):
        """
        The config is the battery configuration.
        The init_soc is the initial state of charge of the battery.
        We initialize the soc with the initial soc
        The time step is one hour and is kept in variable k
        """
        self._state = BatteryState(
            timestamp=datetime.now(),
            soc=init_soc,
            power=0.0,
            command=Command.do_nothing)
        self._state_history: list[BatteryState] = []
        self._k = 0
        self._config = config
        self._strategy = strategy

        # We assume that the charge efficiency is equal
        # to the discharge efficiency
        self._charge_efficiency = sqrt(config.round_trip_efficiency)
        self._discharge_efficiency = sqrt(
            config.round_trip_efficiency)

    def step(self, timestamp: datetime,
             consumption_kW: float, production_kW: float):
        """
        Execute a single step of the battery, meaning that we
        apply the strategy to determine the command and the power
        to assign to the battery, and then we update the state of the battery.

        Args:
            timestamp: The timestamp of the step
            consumption_kW: The consumption power in kW
            production_kW: The production power in kW
        """

        self._k += 1

        command, power = self._strategy.apply(consumption_kW, production_kW)

        battery_power = self._get_battery_power(command, power)

        new_soc = self._state.soc - (battery_power/self._config.capacity_kWh)

        self._state = BatteryState(
            timestamp=timestamp,
            soc=new_soc,
            power=battery_power,
            command=command)

        self._state_history.append(self._state)

    def get_battery_power_by_time(self) -> dict[datetime, float]:
        """
        Get the battery power by time.
        """
        return {state.timestamp: state.power for state in self._state_history}

    def _get_battery_power(self, command: Command, assigned_power_kW: float):
        """
        Get the battery power after taking into account:
        - the efficiency
        - the max power that the battery can handle
        - the max capacity of the battery
        - the state of charge of the battery

        Args:
            command: The command to apply
            assigned_power_kW: The power to assign to the battery

        Returns:
            The battery power expressed in kW
        """

        if command == Command.charge:
            if self._state.soc >= 0.95:
                return 0

            # Determine how much power we can actually charge
            # into the battery after taking into account the efficiency
            # and consideering the total capacity of the battery
            power_after_efficiency = (assigned_power_kW *
                                      self._charge_efficiency)
            max_admissible_power = (1 - self._state.soc) * \
                self._config.capacity_kWh * self._charge_efficiency

            # Determine how much power we can actually charge
            # into the battery after considering the max power
            # that the battery can handle
            limited_power = max(power_after_efficiency,
                                -1 * max_admissible_power,
                                -1 * self._config.max_charge_power_kW)

            return limited_power
        elif command == Command.discharge:
            if self._state.soc <= 0.05:
                return 0

            # Determine how much power we can actually discharge
            # from the battery after taking into account the efficiency
            # and consideering the total capacity of the battery
            power_after_efficiency = (assigned_power_kW /
                                      self._discharge_efficiency)

            remaining_capacity = self._state.soc * \
                self._config.capacity_kWh/self._discharge_efficiency

            # Determine how much power we can actually discharge
            # from the battery after considering the max power
            # that the battery can handle
            limited_power = min(power_after_efficiency,
                                remaining_capacity,
                                self._config.max_discharge_power_kW)
            return limited_power
        else:
            return 0


@dataclass
class BatterySimulationResult:
    """
    This represents the result of the battery simulation.

    The battery is the battery model.
    The house is the house model.
    The pv_plant is the pv plant model.
    """
    battery: Battery
    house: House
    pv_plant: PVPlant
