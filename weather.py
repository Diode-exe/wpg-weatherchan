import asyncio
import datetime
import time
from debug_utils import DebugUtils

debugger = DebugUtils()

class WeatherUpdate:
    """Class to handle weather updates"""
    def __init__(self):
        pass

    def weather_update(self, group):
        """Synchronous wrapper for async weather update"""
        try:
            # Run the async function
            asyncio.run(self.weather_update_async(group))
        except Exception as e:
            debugger.debug_msg(f"WEATHER_UPDATE-wrapper error: {str(e)}", 1)
            # Set fallback values
            global real_forecast_time, real_forecast_date
            if not real_forecast_time:
                real_forecast_time = time.strftime("%I %p").lstrip("0")
            if not real_forecast_date:
                real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")
    
    # DEF update weather for all cities with improved error handling
    async def weather_update_async(self, group):
        """Async weather update with proper error handling and timeouts"""
        global real_forecast_time
        global real_forecast_date

        # used to calculate update time
        t1 = datetime.datetime.now().timestamp()
        timechk = t1 - updt_tstp[group] if group > 0 else 1801  # Force update for group 0

        if timechk > 1800 or group == 0:  # Update if more than 30 min elapsed or if group is 0 (all)
            debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-starting update for group {group}", 1)

            async def update_single_station(station, name, timeout=15):
                """Update a single weather station with timeout"""
                try:
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
                        (ec_en_wpg, "Winnipeg"),
                        (ec_en_brn, "Brandon"),
                        (ec_en_thm, "Thompson"),
                        (ec_en_tps, "The Pas"),
                        (ec_en_fln, "Flin Flon"),
                        (ec_en_chu, "Churchill"),
                        (ec_en_ken, "Kenora"),
                        (ec_en_tby, "Thunder Bay")
                    ]

                    for station, name in stations:
                        await update_single_station(station, name)
                        await asyncio.sleep(0.5)  # Small delay between requests

                    # Update time strings
                    real_forecast_time = time.strftime("%I %p").lstrip("0")
                    if real_forecast_time == "12 PM":
                        real_forecast_time = "NOON"
                    real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")

                    if group == 0:
                        for i in range(1, 4):
                            updt_tstp[i] = datetime.datetime.now().timestamp()
                    else:
                        updt_tstp[group] = datetime.datetime.now().timestamp()

                if group == 0 or group == 2:
                    debugger.debug_msg("WEATHER_UPDATE_ASYNC-updating Western Canada stations", 1)
                    stations = [
                        (ec_en_vic, "Victoria"),
                        (ec_en_van, "Vancouver"),
                        (ec_en_edm, "Edmonton"),
                        (ec_en_cal, "Calgary"),
                        (ec_en_ssk, "Saskatoon"),
                        (ec_en_reg, "Regina"),
                        (ec_en_wht, "Whitehorse")
                    ]

                    for station, name in stations:
                        await update_single_station(station, name)
                        await asyncio.sleep(0.5)

                    real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")
                    if group != 0:
                        updt_tstp[group] = datetime.datetime.now().timestamp()

                if group == 0 or group == 3:
                    debugger.debug_msg("WEATHER_UPDATE_ASYNC-updating Eastern Canada stations", 1)
                    stations = [
                        (ec_en_tor, "Toronto"),
                        (ec_en_otw, "Ottawa"),
                        (ec_en_qbc, "Quebec City"),
                        (ec_en_mtl, "Montreal"),
                        (ec_en_frd, "Fredericton"),
                        (ec_en_hal, "Halifax"),
                        (ec_en_stj, "St. John's")
                    ]

                    for station, name in stations:
                        await update_single_station(station, name)
                        await asyncio.sleep(0.5)

                    real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")
                    if group != 0:
                        updt_tstp[group] = datetime.datetime.now().timestamp()

                # calculate time it took to update
                t = datetime.datetime.now().timestamp() - t1
                debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-group {group} completed in {round(t,2)} seconds", 1)

            except Exception as e:
                debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-critical error in group {group}: {str(e)}", 1)
                # Set fallback values
                if not real_forecast_time:
                    real_forecast_time = time.strftime("%I %p").lstrip("0")

                if not real_forecast_date:
                    real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")

        else:
            debugger.debug_msg(f"WEATHER_UPDATE_ASYNC-group {group} skipped, only {round(timechk//60)} min elapsed", 1)