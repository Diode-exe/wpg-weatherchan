import asyncio
import datetime
import time
from debug_utils import DebugUtils

debugger = DebugUtils()

class WeatherUpdate:
    """Class to handle weather updates"""
    def __init__(self, stations=None):
        self.stations = stations or {}
        self.real_forecast_time = ""
        self.real_forecast_date = ""

    def set_stations(self, stations):
        """Replace the station map used by update routines."""
        self.stations = stations or {}

    def _station(self, key):
        """Return a configured station object by key."""
        return self.stations.get(key)

    def weather_update(self, group, updt_tstp_ref):
        """Synchronous wrapper for async weather update"""
        try:
            # Run the async function
            asyncio.run(self.weather_update_async(group, updt_tstp_ref))
        except Exception as e:
            debugger.debug_msg(f"WEATHER_UPDATE-wrapper error: {str(e)}", 1)
            # Set fallback values
            if not self.real_forecast_time:
                self.real_forecast_time = time.strftime("%I %p").lstrip("0")
            if not self.real_forecast_date:
                self.real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")
    
    # DEF update weather for all cities with improved error handling
    async def weather_update_async(self, group, updt_tstp_ref):
        """Async weather update with proper error handling and timeouts"""
        # used to calculate update time
        t1 = datetime.datetime.now().timestamp()
        timechk = t1 - updt_tstp_ref[group] if group > 0 else 1801  # Force update for group 0

        if timechk > 1800 or group == 0:  # Update if more than 30 min elapsed or if group is 0 (all)
            debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-starting update for group {group}", 1)

            async def update_single_station(station, name, timeout=15):
                """Update a single weather station with timeout"""
                try:
                    if station is None:
                        debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-{name} missing station reference", 1)
                        return False
                    debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-updating {name}", 2)
                    await asyncio.wait_for(station.update(), timeout=timeout)
                    debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-{name} updated successfully", 2)
                    return True
                except asyncio.TimeoutError:
                    debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-{name} timed out after {timeout}s", 1)
                    return False
                except Exception as e:
                    debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-{name} error: {str(e)}", 1)
                    return False

            try:
                if group == 0 or group == 1:
                    debugger.debug_msg("WEATHER_UPDATE_ASYNC-updating Manitoba/Regional stations", 1)
                    stations = [
                        (self._station("wpg"), "Winnipeg"),
                        (self._station("brn"), "Brandon"),
                        (self._station("thm"), "Thompson"),
                        (self._station("tps"), "The Pas"),
                        (self._station("fln"), "Flin Flon"),
                        (self._station("chu"), "Churchill"),
                        (self._station("ken"), "Kenora"),
                        (self._station("tby"), "Thunder Bay")
                    ]

                    for station, name in stations:
                        await update_single_station(station, name)
                        await asyncio.sleep(0.5)  # Small delay between requests

                    # Update time strings
                    self.real_forecast_time = time.strftime("%I %p").lstrip("0")
                    if self.real_forecast_time == "12 PM":
                        self.real_forecast_time = "NOON"
                    self.real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")

                    if group == 0:
                        for i in range(1, 4):
                            updt_tstp_ref[i] = datetime.datetime.now().timestamp()
                    else:
                        updt_tstp_ref[group] = datetime.datetime.now().timestamp()

                if group == 0 or group == 2:
                    debugger.debug_msg("WEATHER_UPDATE_ASYNC-updating Western Canada stations", 1)
                    stations = [
                        (self._station("vic"), "Victoria"),
                        (self._station("van"), "Vancouver"),
                        (self._station("edm"), "Edmonton"),
                        (self._station("cal"), "Calgary"),
                        (self._station("ssk"), "Saskatoon"),
                        (self._station("reg"), "Regina"),
                        (self._station("wht"), "Whitehorse")
                    ]

                    for station, name in stations:
                        await update_single_station(station, name)
                        await asyncio.sleep(0.5)

                    self.real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")
                    if group != 0:
                        updt_tstp_ref[group] = datetime.datetime.now().timestamp()

                if group == 0 or group == 3:
                    debugger.debug_msg("WEATHER_UPDATE_ASYNC-updating Eastern Canada stations", 1)
                    stations = [
                        (self._station("tor"), "Toronto"),
                        (self._station("otw"), "Ottawa"),
                        (self._station("qbc"), "Quebec City"),
                        (self._station("mtl"), "Montreal"),
                        (self._station("frd"), "Fredericton"),
                        (self._station("hal"), "Halifax"),
                        (self._station("stj"), "St. John's")
                    ]

                    for station, name in stations:
                        await update_single_station(station, name)
                        await asyncio.sleep(0.5)

                    self.real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")
                    if group != 0:
                        updt_tstp_ref[group] = datetime.datetime.now().timestamp()

                # calculate time it took to update
                t = datetime.datetime.now().timestamp() - t1
                debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-group {group} completed in {round(t,2)} seconds", 1)

            except Exception as e:
                debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-critical error in group {group}: {str(e)}", 1)
                # Set fallback values
                if not self.real_forecast_time:
                    self.real_forecast_time = time.strftime("%I %p").lstrip("0")

                if not self.real_forecast_date:
                    self.real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")

        else:
            debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-group {group} skipped, only {round(timechk//60)} min elapsed", 1)
        return updt_tstp_ref[group] if group > 0 else None  # Return updated timestamp for the group if applicable