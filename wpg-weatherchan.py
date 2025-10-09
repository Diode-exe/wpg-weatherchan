# Retro Winnipeg Weather Channel
# By probnot - Fixed version with improved error handling

from tkinter import *
import time
import datetime
import asyncio # for env_canada
import textwrap # used to format forecast text
from env_canada import ECWeather
import feedparser # for RSS feed
import pygame # for background music
import random # for background music
import os # for background music
import re # for word shortener
import signal
import sys

prog = "wpg-weather"
ver = "2.2"

# Global variables for weather data
real_forecast_time = ""
real_forecast_date = ""
text_forecast = []

# DEF clock Updater
def clock():
    try:
        # Get current time in 12-hour format with leading zeros
        current = time.strftime("%I:%M:%S")  
        
        # Update the label
        timeText.config(text=current)
        
        # Schedule next update in 1 second
        root.after(1000, clock)
    except Exception as e:
        debug_msg(f"CLOCK-error: {str(e)}", 1)
        root.after(1000, clock)
    
# DEF main weather pages 
def weather_page(PageColour, PageNum):
    try:
        # pull in current seconds and minutes -- to be used to cycle the middle section every 30sec   
        linebreak = ['\n']

        PageTotal = 11

        if (PageNum == 1):
            # ===================== Screen 1 =====================
            debug_msg(("WEATHER_PAGE-display page " + str(PageNum)),2)             
            
            # get local timezone to show on screen
            local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
            
            # weather data with safe access
            try:
                temp_cur = str(safe_get_weather_value(ec_en_wpg.conditions, "temperature", "value", default="--"))
                temp_high = str(safe_get_weather_value(ec_en_wpg.conditions, "high_temp", "value", default="--"))
                temp_low = str(safe_get_weather_value(ec_en_wpg.conditions, "low_temp", "value", default="--"))
                humidity = str(safe_get_weather_value(ec_en_wpg.conditions, "humidity", "value", default="--"))
                condition = safe_get_weather_value(ec_en_wpg.conditions, "condition", "value", default="NO DATA")
                pressure = str(safe_get_weather_value(ec_en_wpg.conditions, "pressure", "value", default="--"))   
                tendency = safe_get_weather_value(ec_en_wpg.conditions, "tendency", "value", default="STEADY")
                dewpoint = str(safe_get_weather_value(ec_en_wpg.conditions, "dewpoint", "value", default="--"))
                uv_index_val = safe_get_weather_value(ec_en_wpg.conditions, "uv_index", "value", default="--")
                uv_index = str(uv_index_val) if uv_index_val is not None else "--"
                pop_val = safe_get_weather_value(ec_en_wpg.conditions, "pop", "value", default="--")
                pop = str(pop_val) if pop_val is not None else "0"

                try:
                    uv_index_val = float(uv_index_val)
                except (ValueError, TypeError):
                    uv_index_val = None

                
                # check severity of uv index
                if uv_index_val is not None:
                    if uv_index_val <= 2:
                        uv_cat = "LOW"
                    elif uv_index_val <= 5:
                        uv_cat = "MODERT"
                    elif uv_index_val <= 7:
                        uv_cat = "HIGH"
                    elif uv_index_val <= 10:
                        uv_cat = "V.HIGH"
                    else:
                        uv_cat = "EXTRM"
                else:
                    uv_cat = ""
                
                # check if windchill or humidex is present
                windchill_val = safe_get_weather_value(ec_en_wpg.conditions, "wind_chill", "value", default="--")
                humidex_val = safe_get_weather_value(ec_en_wpg.conditions, "humidex", "value", default="--")
                
                if windchill_val not in [None, "--"]:
                    windchildex = "WIND CHILL " + str(windchill_val) + " C"
                elif humidex_val not in [None, "--"]:
                    windchildex = "HUMIDEX " + str(humidex_val) + " C       "
                else:
                    windchildex = ""
                
                # check if there is wind
                wind_dir_val = safe_get_weather_value(ec_en_wpg.conditions, "wind_dir", "value", default="--")
                wind_spd_val = safe_get_weather_value(ec_en_wpg.conditions, "wind_speed", "value", default="--")
                
                if wind_dir_val is not None and wind_spd_val is not None:
                    windstr = "WIND " + str(wind_dir_val) + " " + str(wind_spd_val) + " KMH"
                else:
                    windstr = "NO WIND"
                        
                # check visibility
                visibility_val = safe_get_weather_value(ec_en_wpg.conditions, "visibility", "value", default="--")
                if visibility_val is not None:
                    visibstr = "VISBY " + str(visibility_val).rjust(5," ") + " KM         "
                else:
                    visibstr = "VISBY    -- KM         "
            
            except Exception as e:
                debug_msg(f"WEATHER_PAGE-error getting weather data: {str(e)}", 1)
                # Set default values
                temp_cur = temp_high = temp_low = humidity = dewpoint = pressure = uv_index = pop = "--"
                condition = "NO DATA AVAILABLE"
                tendency = "STEADY"
                windchildex = windstr = visibstr = ""
                uv_cat = ""
         
            # create 8 lines of text     
            s1 = ("WINNIPEG " + real_forecast_time + " " + str(local_tz) + "  " + real_forecast_date.upper()).center(35," ")
            s2 = "TEMP  " + temp_cur.rjust(5," ") + " C                "
            s2 = s2[0:24] + " HIGH " + temp_high.rjust(3," ") + " C"
            s3 = word_short(condition,24) + "                         "
            s3 = s3[0:24] + "  LOW " + temp_low.rjust(3," ") + " C"
            s4 = ("CHANCE OF PRECIP. " + pop + " %").center(35," ")
            s5 = "HUMID  " + humidity.rjust(5," ") + " %         "
            s5 = s5[0:18] + windstr.rjust(17," ")
            s6 = visibstr[0:18] + windchildex.rjust(17," ")
            s7 = "DEW   " + dewpoint.rjust(5," ") + " C         " 
            s7 = s7[0:18] + ("UV INDEX " + uv_index + " " + uv_cat).rjust(17," ")
            s8 = ("PRESSURE " + pressure + " KPA AND " + tendency.upper()).center(35," ")

        elif (PageNum == 2):
            # ===================== Screen 2 =====================
            debug_msg(("WEATHER_PAGE-display page " + str(PageNum)),2)  

            try:
                # pull text forecasts from env_canada with safe access
                current_summary = safe_get_weather_value(ec_en_wpg.conditions, "text_summary", "value", "NO FORECAST AVAILABLE")
                wsum_day1 = textwrap.wrap(current_summary.upper(), 35)
                
                wsum_day2 = wsum_day3 = wsum_day4 = wsum_day5 = wsum_day6 = []
                
                try:
                    if hasattr(ec_en_wpg, 'daily_forecasts') and len(ec_en_wpg.daily_forecasts) > 1:
                        for i, day_offset in enumerate([1,2,3,4,5], 1):
                            if len(ec_en_wpg.daily_forecasts) > day_offset:
                                period = ec_en_wpg.daily_forecasts[day_offset].get("period", "DAY " + str(i+1))
                                summary = ec_en_wpg.daily_forecasts[day_offset].get("text_summary", "NO DATA")
                                forecast_text = textwrap.wrap((period + ".." + summary).upper(), 35)
                                if i == 1: wsum_day2 = forecast_text
                                elif i == 2: wsum_day3 = forecast_text
                                elif i == 3: wsum_day4 = forecast_text
                                elif i == 4: wsum_day5 = forecast_text
                                elif i == 5: wsum_day6 = forecast_text
                except Exception as e:
                    debug_msg(f"WEATHER_PAGE-error getting daily forecasts: {str(e)}", 1)
                
                # build text_forecast string
                global text_forecast
                text_forecast = wsum_day1 + linebreak + wsum_day2 + linebreak + wsum_day3 + linebreak + wsum_day4 + linebreak + wsum_day5 + linebreak + wsum_day6
            
            except Exception as e:
                debug_msg(f"WEATHER_PAGE-error building forecasts: {str(e)}", 1)
                text_forecast = ["NO FORECAST DATA AVAILABLE"]
        
            # create 8 lines of text
            s1 = "WINNIPEG CITY FORECAST".center(35," ")
            s2 = (text_forecast[0]).center(35," ") if len(text_forecast) >= 1 else " "
            s3 = (text_forecast[1]).center(35," ") if len(text_forecast) >= 2 else " "
            s4 = (text_forecast[2]).center(35," ") if len(text_forecast) >= 3 else " "
            s5 = (text_forecast[3]).center(35," ") if len(text_forecast) >= 4 else " "
            s6 = (text_forecast[4]).center(35," ") if len(text_forecast) >= 5 else " "
            s7 = (text_forecast[5]).center(35," ") if len(text_forecast) >= 6 else " "
            s8 = (text_forecast[6]).center(35," ") if len(text_forecast) >= 7 else " "

        elif (PageNum == 3):
            # ===================== Screen 3 =====================
            debug_msg(("WEATHER_PAGE-display page " + str(PageNum)),2) 
            
            # create 8 lines of text
            s1 = "WINNIPEG CITY FORECAST CONT'D".center(35," ")
            s2 = (text_forecast[7]).center(35," ") if len(text_forecast) >= 8 else " "
            s3 = (text_forecast[8]).center(35," ") if len(text_forecast) >= 9 else " "
            s4 = (text_forecast[9]).center(35," ") if len(text_forecast) >= 10 else " "
            s5 = (text_forecast[10]).center(35," ") if len(text_forecast) >= 11 else " "
            s6 = (text_forecast[11]).center(35," ") if len(text_forecast) >= 12 else " "
            s7 = (text_forecast[12]).center(35," ") if len(text_forecast) >= 13 else " "
            s8 = (text_forecast[13]).center(35," ") if len(text_forecast) >= 14 else " " 

        elif (PageNum == 4):
            # ===================== Screen 4 =====================
            # check if this page is needed
            if len(text_forecast) <= 14:
                debug_msg(("WEATHER_PAGE-display page " + str(PageNum) + " skipped!"),2)
                PageNum = PageNum + 1 #skip this page
                if (PageColour == "#00006D"): # blue
                    PageColour = "#6D0000" # red
                else:
                    PageColour = "#00006D" # blue 
            else:
                debug_msg(("WEATHER_PAGE-display page " + str(PageNum)),2)   
            
                # create 8 lines of text       
                s1 = "WINNIPEG CITY FORECAST CONT'D".center(35," ")
                s2 = (text_forecast[14]).center(35," ") if len(text_forecast) >= 15 else " "       
                s3 = (text_forecast[15]).center(35," ") if len(text_forecast) >= 16 else " "        
                s4 = (text_forecast[16]).center(35," ") if len(text_forecast) >= 17 else " "
                s5 = (text_forecast[17]).center(35," ") if len(text_forecast) >= 18 else " "
                s6 = (text_forecast[18]).center(35," ") if len(text_forecast) >= 19 else " "
                s7 = (text_forecast[19]).center(35," ") if len(text_forecast) >= 20 else " "
                s8 = (text_forecast[20]).center(35," ") if len(text_forecast) >= 21 else " "                  
    
        elif (PageNum == 5):
            # ===================== Screen 5 =====================
            debug_msg(("WEATHER_PAGE-display page " + str(PageNum)),2)        
     
            # weather data with safe access
            # current temperature
            temp_cur = str(safe_get_weather_value(ec_en_wpg.conditions, "temperature", "value", default="--"))

            # forecast highs/lows for today
            # get today’s forecast from daily_forecasts
            if hasattr(ec_en_wpg, "daily_forecasts") and len(ec_en_wpg.daily_forecasts) > 0:
                today_forecast = ec_en_wpg.daily_forecasts[0]
                temp_high = str(safe_get_weather_value(today_forecast, "high_temp", "value", default="--"))
                temp_low  = str(safe_get_weather_value(today_forecast, "low_temp", "value", default="--"))
            else:
                temp_high = temp_low = "--"


            # yesterday’s temps
            temp_yest_high_val = safe_get_weather_value(ec_en_wpg.observations.get("yesterday", {}), "high_temp", "value", default="--")
            temp_yest_high = safe_round(temp_yest_high_val)

            temp_yest_low_val = safe_get_weather_value(ec_en_wpg.observations.get("yesterday", {}), "low_temp", "value", default="--")
            temp_yest_low = safe_round(temp_yest_low_val)

            # normal temps
            temp_norm_high = str(safe_get_weather_value(ec_en_wpg.observations.get("normals", {}), "high_temp", "value", default="--"))
            temp_norm_low  = str(safe_get_weather_value(ec_en_wpg.observations.get("normals", {}), "low_temp", "value", default="--"))


            # create 8 lines of text   
            s1 = ("TEMPERATURE STATISTICS FOR WINNIPEG").center(35," ")
            s2 = "       CURRENT " + temp_cur.rjust(5," ") + " C  "
            s3 = ""
            s4 = "                 LOW    HIGH"
            s5 = "        TODAY   " + temp_low.rjust(3," ") + " C  " + temp_high.rjust(3," ") + " C"
            s6 = "    YESTERDAY   " + temp_yest_low.rjust(3," ") + " C  " + temp_yest_high.rjust(3," ") + " C"
            s7 = "       NORMAL   " + temp_norm_low.rjust(3," ") + " C  " + temp_norm_high.rjust(3," ") + " C"
            s8 = ""
    
        elif (PageNum == 6):    
            # ===================== Screen 6 =====================
            debug_msg(("WEATHER_PAGE-display page " + str(PageNum)),2)

            # Regional temperatures with safe access
            temp_brn = str(safe_get_weather_value(ec_en_brn.conditions, "temperature", "value", default="--"))
            temp_thm = str(safe_get_weather_value(ec_en_thm.conditions, "temperature", "value", default="--"))
            temp_tps = str(safe_get_weather_value(ec_en_tps.conditions, "temperature", "value", default="--"))    
            temp_fln = str(safe_get_weather_value(ec_en_fln.conditions, "temperature", "value", default="--"))  
            temp_chu = str(safe_get_weather_value(ec_en_chu.conditions, "temperature", "value", default="--")) 
            temp_ken = str(safe_get_weather_value(ec_en_ken.conditions, "temperature", "value", default="--"))  
            temp_tby = str(safe_get_weather_value(ec_en_tby.conditions, "temperature", "value", default="--"))   

            cond_brn = safe_get_weather_value(ec_en_brn.conditions, "condition", "value", default="NO DATA")
            cond_thm = safe_get_weather_value(ec_en_thm.conditions, "condition", "value", default="NO DATA")
            cond_tps = safe_get_weather_value(ec_en_tps.conditions, "condition", "value", default="NO DATA")
            cond_fln = safe_get_weather_value(ec_en_fln.conditions, "condition", "value", default="NO DATA")
            cond_chu = safe_get_weather_value(ec_en_chu.conditions, "condition", "value", default="NO DATA")
            cond_ken = safe_get_weather_value(ec_en_ken.conditions, "condition", "value", default="NO DATA")
            cond_tby = safe_get_weather_value(ec_en_tby.conditions, "condition", "value", default="NO DATA")
            
            # create 8 lines of text   
            s1=(real_forecast_date.upper()).center(35," ")
            s2="BRANDON     " + temp_brn.rjust(5," ") + " C    "
            s2= s2[0:20] + word_short(cond_brn,13)[0:13]
            s3="THE PAS     " + temp_tps.rjust(5," ") + " C     "
            s3= s3[0:20] + word_short(cond_tps,13)[0:13]
            s4="FLIN FLON   " + temp_fln.rjust(5," ") + " C     "
            s4= s4[0:20] + word_short(cond_fln,13)[0:13]
            s5="THOMPSON    " + temp_thm.rjust(5," ") + " C     "
            s5= s5[0:20] + word_short(cond_thm,13)[0:13]
            s6="CHURCHILL   " + temp_chu.rjust(5," ") + " C     "
            s6= s6[0:20] + word_short(cond_chu,13)[0:13]
            s7="KENORA      " + temp_ken.rjust(5," ") + " C     "
            s7= s7[0:20] + word_short(cond_ken,13)[0:13]
            s8="THUNDER BAY " + temp_tby.rjust(5," ") + " C     "
            s8= s8[0:20] + word_short(cond_tby,13)[0:13]

        elif (PageNum == 7):
            # ===================== Screen 7 =====================
            debug_msg(("WEATHER_PAGE-display page " + str(PageNum)),2) 
            
            # Western Canada temperatures with safe access
            temp_vic = str(safe_get_weather_value(ec_en_vic.conditions, "temperature", "value", default="--"))
            temp_van = str(safe_get_weather_value(ec_en_van.conditions, "temperature", "value", default="--"))
            temp_edm = str(safe_get_weather_value(ec_en_edm.conditions, "temperature", "value", default="--"))    
            temp_cal = str(safe_get_weather_value(ec_en_cal.conditions, "temperature", "value", default="--"))  
            temp_ssk = str(safe_get_weather_value(ec_en_ssk.conditions, "temperature", "value", default="--"))  
            temp_reg = str(safe_get_weather_value(ec_en_reg.conditions, "temperature", "value", default="--"))   
            temp_wht = str(safe_get_weather_value(ec_en_wht.conditions, "temperature", "value", default="--")) 

            cond_vic = safe_get_weather_value(ec_en_vic.conditions, "condition", "value", default="NO DATA")
            cond_van = safe_get_weather_value(ec_en_van.conditions, "condition", "value", default="NO DATA")
            cond_edm = safe_get_weather_value(ec_en_edm.conditions, "condition", "value", default="NO DATA")
            cond_cal = safe_get_weather_value(ec_en_cal.conditions, "condition", "value", default="NO DATA")
            cond_ssk = safe_get_weather_value(ec_en_ssk.conditions, "condition", "value", default="NO DATA")
            cond_reg = safe_get_weather_value(ec_en_reg.conditions, "condition", "value", default="NO DATA")
            cond_wht = safe_get_weather_value(ec_en_wht.conditions, "condition", "value", default="NO DATA")
            
            # create 8 lines of text    
            s1=(real_forecast_date.upper()).center(35," ")
            s2="VICTORIA    " + temp_vic.rjust(5," ") + " C     "
            s2= s2[0:20] + word_short(cond_vic,13)[0:13]
            s3="VANCOUVER   " + temp_van.rjust(5," ") + " C     "
            s3= s3[0:20] + word_short(cond_van,13)[0:13]
            s4="EDMONTON    " + temp_edm.rjust(5," ") + " C     "
            s4= s4[0:20] + word_short(cond_edm,13)[0:13]
            s5="CALGARY     " + temp_cal.rjust(5," ") + " C     "
            s5= s5[0:20] + word_short(cond_cal,13)[0:13]
            s6="SASKATOON   " + temp_ssk.rjust(5," ") + " C     "
            s6= s6[0:20] + word_short(cond_ssk,13)[0:13]
            s7="REGINA      " + temp_reg.rjust(5," ") + " C     "
            s7= s7[0:20] + word_short(cond_reg,13)[0:13]
            s8="WHITEHORSE  " + temp_wht.rjust(5," ") + " C     "
            s8= s8[0:20] + word_short(cond_wht,13)[0:13]
                 
        elif (PageNum == 8):   
            # ===================== Screen 8 =====================
            debug_msg(("WEATHER_PAGE-display page " + str(PageNum)),2)
            
            # Eastern Canada temperatures with safe access
            temp_tor = str(safe_get_weather_value(ec_en_tor.conditions, "temperature", "value", default="--"))
            temp_otw = str(safe_get_weather_value(ec_en_otw.conditions, "temperature", "value", default="--"))
            temp_qbc = str(safe_get_weather_value(ec_en_qbc.conditions, "temperature", "value", default="--"))    
            temp_mtl = str(safe_get_weather_value(ec_en_mtl.conditions, "temperature", "value", default="--"))  
            temp_frd = str(safe_get_weather_value(ec_en_frd.conditions, "temperature", "value", default="--"))  
            temp_hal = str(safe_get_weather_value(ec_en_hal.conditions, "temperature", "value", default="--"))   
            temp_stj = str(safe_get_weather_value(ec_en_stj.conditions, "temperature", "value", default="--")) 

            cond_tor = safe_get_weather_value(ec_en_tor.conditions, "condition", "value", default="NO DATA")
            cond_otw = safe_get_weather_value(ec_en_otw.conditions, "condition", "value", default="NO DATA")
            cond_qbc = safe_get_weather_value(ec_en_qbc.conditions, "condition", "value", default="NO DATA")
            cond_mtl = safe_get_weather_value(ec_en_mtl.conditions, "condition", "value", default="NO DATA")
            cond_frd = safe_get_weather_value(ec_en_frd.conditions, "condition", "value", default="NO DATA")
            cond_hal = safe_get_weather_value(ec_en_hal.conditions, "condition", "value", default="NO DATA")
            cond_stj = safe_get_weather_value(ec_en_stj.conditions, "condition", "value", default="NO DATA")
            
            # create 8 lines of text    
            s1=(real_forecast_date.upper()).center(35," ")
            s2="TORONTO     " + temp_tor.rjust(5," ") + " C    "
            s2= s2[0:20] + word_short(cond_tor,13)[0:13]
            s3="OTTAWA      " + temp_otw.rjust(5," ") + " C     "
            s3= s3[0:20] + word_short(cond_otw,13)[0:13]
            s4="QUEBEC CITY " + temp_qbc.rjust(5," ") + " C     "
            s4= s4[0:20] + word_short(cond_qbc,13)[0:13]
            s5="MONTREAL    " + temp_mtl.rjust(5," ") + " C     "
            s5= s5[0:20] + word_short(cond_mtl,13)[0:13]
            s6="FREDERICTON " + temp_frd.rjust(5," ") + " C     "
            s6= s6[0:20] + word_short(cond_frd,13)[0:13]
            s7="HALIFAX     " + temp_hal.rjust(5," ") + " C     "
            s7= s7[0:20] + word_short(cond_hal,13)[0:13]
            s8="ST.JOHN'S   " + temp_stj.rjust(5," ") + " C     "
            s8= s8[0:20] + word_short(cond_stj,13)[0:13]
    
        elif (PageNum == 9):
            # ===================== Screen 9 =====================
            debug_msg(("WEATHER_PAGE-display page " + str(PageNum)), 2)

            # get local timezone to show on screen
            local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

            try:
                # convert hourly forecast data with safe access
                if hasattr(ec_en_wpg, 'hourly_forecasts') and len(ec_en_wpg.hourly_forecasts) >= 13:
                    hrly_period = []
                    hrly_temp = []
                    hrly_cond = []

                    for i in [0, 2, 4, 6, 8, 10, 12]:
                        if i < len(ec_en_wpg.hourly_forecasts):
                            forecast = ec_en_wpg.hourly_forecasts[i]

                            # Safely get period
                            period = forecast.get("period", datetime.datetime.now())
                            if not isinstance(period, datetime.datetime):
                                period = datetime.datetime.now()
                            hrly_period.append(period)

                            # Safely get temperature and normalize to string
                            temp = forecast.get("temperature", None)
                            if temp is None or temp == "--":
                                temp_str = "--"
                            else:
                                try:
                                    temp_str = str(round(float(temp)))
                                except:
                                    temp_str = "--"
                            hrly_temp.append(temp_str)

                            # Safely get condition
                            condition = forecast.get("condition", "NO DATA")
                            hrly_cond.append(str(condition))
                        else:
                            # Fill missing data
                            hrly_period.append(datetime.datetime.now())
                            hrly_temp.append("--")
                            hrly_cond.append("NO DATA")

                else:
                    # Fallback data
                    hrly_period = [datetime.datetime.now()] * 7
                    hrly_temp = ["--"] * 7
                    hrly_cond = ["NO DATA"] * 7

                # convert period to local time
                hrly_period_local = []
                for period in hrly_period:
                    try:
                        hrly_period_local.append(period.astimezone())
                    except:
                        hrly_period_local.append(datetime.datetime.now())

                # Shorten condition text
                hrly_cond = [word_short(cond, 13) for cond in hrly_cond]

            except Exception as e:
                debug_msg(f"WEATHER_PAGE-error getting hourly forecast: {str(e)}", 1)
                # Fallback data
                hrly_period_local = [datetime.datetime.now()] * 7
                hrly_temp = ["--"] * 7
                hrly_cond = ["NO DATA"] * 7

            # create 8 lines of text
            s1 = "WINNIPEG HOURLY FORECAST".center(35, " ")
            s2 = f"{hrly_period_local[0].strftime('%I:%M %p').lstrip('0').rjust(8)} {str(local_tz)}  {hrly_temp[0].rjust(3)} C  {hrly_cond[0][0:13]}"
            s3 = f"{hrly_period_local[1].strftime('%I:%M %p').lstrip('0').rjust(8)} {str(local_tz)}  {hrly_temp[1].rjust(3)} C  {hrly_cond[1][0:13]}"
            s4 = f"{hrly_period_local[2].strftime('%I:%M %p').lstrip('0').rjust(8)} {str(local_tz)}  {hrly_temp[2].rjust(3)} C  {hrly_cond[2][0:13]}"
            s5 = f"{hrly_period_local[3].strftime('%I:%M %p').lstrip('0').rjust(8)} {str(local_tz)}  {hrly_temp[3].rjust(3)} C  {hrly_cond[3][0:13]}"
            s6 = f"{hrly_period_local[4].strftime('%I:%M %p').lstrip('0').rjust(8)} {str(local_tz)}  {hrly_temp[4].rjust(3)} C  {hrly_cond[4][0:13]}"
            s7 = f"{hrly_period_local[5].strftime('%I:%M %p').lstrip('0').rjust(8)} {str(local_tz)}  {hrly_temp[5].rjust(3)} C  {hrly_cond[5][0:13]}"
            s8 = f"{hrly_period_local[6].strftime('%I:%M %p').lstrip('0').rjust(8)} {str(local_tz)}  {hrly_temp[6].rjust(3)} C  {hrly_cond[6][0:13]}"

        elif (PageNum == 10):
  # ===================== Screen 10 =====================
            debug_msg(f"WEATHER_PAGE-display page {PageNum}", 2)

            def get_daily_pop(ec_obj):
                """
                Safely get the probability of precipitation (POP) from the first daily forecast.
                Returns a string with % or '-- %' if data missing.
                """
                try:
                    if hasattr(ec_obj, "daily_forecasts") and len(ec_obj.daily_forecasts) > 0:
                        pop_val = safe_get_weather_value(ec_obj.daily_forecasts[0], "pop", "value", default="--")
                        return f"{pop_val} %" if pop_val is not None else "-- %"
                except Exception as e:
                    debug_msg(f"get_daily_pop error for {ec_obj}: {e}", 2)
                return "-- %"

            # Get today’s POP for all stations
            wpg_precip = get_daily_pop(ec_en_wpg)
            brn_precip = get_daily_pop(ec_en_brn)
            tps_precip = get_daily_pop(ec_en_tps)
            fln_precip = get_daily_pop(ec_en_fln)
            thm_precip = get_daily_pop(ec_en_thm)
            chu_precip = get_daily_pop(ec_en_chu)

            # Yesterday's precipitation — fallback, since current ECWeather version may not provide
            yest_precip_val = safe_get_weather_value(ec_en_wpg.conditions, "precip_yesterday", "value", default=None)
            yest_precip = f"{yest_precip_val} MM" if yest_precip_val is not None else "-- MM"

            # Create 8 lines of text
            s1 = "MANITOBA PRECIPITATION FORECAST".center(35, " ")
            s2 = f"    TODAY WINNIPEG  {wpg_precip.rjust(5,' ')}"
            s3 = f"          BRANDON   {brn_precip.rjust(5,' ')}"
            s4 = f"          THE PAS   {tps_precip.rjust(5,' ')}"
            s5 = f"          FLIN FLON {fln_precip.rjust(5,' ')}"
            s6 = f"          THOMPSON  {thm_precip.rjust(5,' ')}"
            s7 = f"          CHURCHILL {chu_precip.rjust(5,' ')}"
            s8 = f" PREV DAY WINNIPEG  {yest_precip.rjust(7,' ')}"


        elif (PageNum == 11):    
            # ===================== Screen 11 =====================
            debug_msg(("WEATHER_PAGE-display page " + str(PageNum)),2)         
          
            # create 8 lines of text
            s1 = "==========CHANNEL LISTING=========="
            s2 = "  2 SIMPSNS  13.1 CITY    50 SECUR"    
            s3 = "3.1 CBC FR.    14 90sTV   54 COMEDY" 
            s4 = "  6 60s/70s    16 TOONS   61 MUSIC"         
            s5 = "6.1 CBC        22 GLOBAL  64 WEATHR"
            s6 = "7.1 CTV        24 80sTV"
            s7 = "9.1 GLOBAL   35.1 FAITH"
            s8 = " 10 CBC        45 CHROMECAST" 

        else:
            # Default fallback page
            s1 = s2 = s3 = s4 = s5 = s6 = s7 = s8 = ""

        # create the canvas for middle page text
        try:
            weather = Canvas(root, height=310, width=720, bg=PageColour)
            weather.place(x=0, y=85)
            weather.config(highlightbackground=PageColour)
            
            # place the 8 lines of text
            weather.create_text(80, 17, anchor='nw', text=s1, font=('VCR OSD Mono', 21, "bold"), fill="white")
            weather.create_text(80, 60, anchor='nw', text=s2, font=('VCR OSD Mono', 21,), fill="white")
            weather.create_text(80, 95, anchor='nw', text=s3, font=('VCR OSD Mono', 21,), fill="white")
            weather.create_text(80, 130, anchor='nw', text=s4, font=('VCR OSD Mono', 21,), fill="white")
            weather.create_text(80, 165, anchor='nw', text=s5, font=('VCR OSD Mono', 21,), fill="white")
            weather.create_text(80, 200, anchor='nw', text=s6, font=('VCR OSD Mono', 21,), fill="white")
            weather.create_text(80, 235, anchor='nw', text=s7, font=('VCR OSD Mono', 21,), fill="white") 
            weather.create_text(80, 270, anchor='nw', text=s8, font=('VCR OSD Mono', 21,), fill="white") 
        except Exception as e:
            debug_msg(f"WEATHER_PAGE-error creating canvas: {str(e)}", 1)
        
        # Toggle Page Colour between Red & Blue
        if (PageColour == "#00006D"): # blue
            PageColour = "#6D0000" # red
        else:
            PageColour = "#00006D" # blue
            
        # Increment Page Number or Reset
        if (PageNum < PageTotal):
            PageNum = PageNum + 1
        elif (PageNum >= PageTotal):
            PageNum = 1
        
        root.after(20000, weather_page, PageColour, PageNum) # re-run every 20sec from program launch
        
    except Exception as e:
        debug_msg(f"WEATHER_PAGE-critical error: {str(e)}", 1)
        # Continue with next page anyway
        if (PageColour == "#00006D"):
            PageColour = "#6D0000"
        else:
            PageColour = "#00006D"
        if (PageNum < 11):
            PageNum = PageNum + 1
        else:
            PageNum = 1
        root.after(20000, weather_page, PageColour, PageNum)

# DEF safe weather data access
def safe_get_weather_value(weather_obj, *keys, default="NO DATA"):
    try:
        data = weather_obj
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default
        return data if data is not None else default
    except Exception as e:
        debug_msg(f"SAFE_GET_WEATHER_VALUE-error accessing {keys}: {str(e)}", 2)
        return default
    
#DEF Safe round so that TypeErrors don't occur in the assignments
def safe_round(value):
    try:
        return str(round(float(value)))
    except (TypeError, ValueError):
        return "--"

# DEF update weather for all cities with improved error handling
async def weather_update_async(group):
    """Async weather update with proper error handling and timeouts"""
    global real_forecast_time
    global real_forecast_date

    # used to calculate update time
    t1 = datetime.datetime.now().timestamp()
    timechk = t1 - updt_tstp[group] if group > 0 else 1801  # Force update for group 0
    
    if (timechk > 1800) or (group == 0):
        debug_msg(f"WEATHER_UPDATE_ASYNC-starting update for group {group}", 1)
        
        async def update_single_station(station, name, timeout=15):
            """Update a single weather station with timeout"""
            try:
                debug_msg(f"WEATHER_UPDATE_ASYNC-updating {name}", 2)
                await asyncio.wait_for(station.update(), timeout=timeout)
                debug_msg(f"WEATHER_UPDATE_ASYNC-{name} updated successfully", 2)
                return True
            except asyncio.TimeoutError:
                debug_msg(f"WEATHER_UPDATE_ASYNC-{name} timed out after {timeout}s", 1)
                return False
            except Exception as e:
                debug_msg(f"WEATHER_UPDATE_ASYNC-{name} error: {str(e)}", 1)
                return False

        try:
            if (group == 0 or group == 1):
                debug_msg("WEATHER_UPDATE_ASYNC-updating Manitoba/Regional stations", 1)
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
            
            if (group == 0 or group == 2):
                debug_msg("WEATHER_UPDATE_ASYNC-updating Western Canada stations", 1)
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
        
            if (group == 0 or group == 3):
                debug_msg("WEATHER_UPDATE_ASYNC-updating Eastern Canada stations", 1)
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
            debug_msg(f"WEATHER_UPDATE_ASYNC-group {group} completed in {round(t,2)} seconds", 1)
            
        except Exception as e:
            debug_msg(f"WEATHER_UPDATE_ASYNC-critical error in group {group}: {str(e)}", 1)
            # Set fallback values
            if not real_forecast_time:
                real_forecast_time = time.strftime("%I %p").lstrip("0")

            if not real_forecast_date:
                real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")
                
    else:
        debug_msg(f"WEATHER_UPDATE_ASYNC-group {group} skipped, only {round(timechk//60)} min elapsed", 1)

def weather_update(group):
    """Synchronous wrapper for async weather update"""
    try:
        # Run the async function
        asyncio.run(weather_update_async(group))
    except Exception as e:
        debug_msg(f"WEATHER_UPDATE-wrapper error: {str(e)}", 1)
        # Set fallback values
        global real_forecast_time, real_forecast_date
        if not real_forecast_time:
            real_forecast_time = time.strftime("%I %p").lstrip("0")
        if not real_forecast_date:
            real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")

# DEF bottom marquee scrolling text with improved error handling
def bottom_marquee(grouptotal, marquee):
    try:
        width = 35
        pad = " " * width

        def get_rss_feed():
            try:
                url = "https://www.cbc.ca/webfeed/rss/rss-canada-manitoba"
                wpg = feedparser.parse(url)
                if not wpg.entries:
                    return "NO NEWS DATA AVAILABLE AT THIS TIME"
                return wpg
            except Exception:
                return "RSS FEED TEMPORARILY UNAVAILABLE"

        wpg = get_rss_feed()
        if isinstance(wpg, str):
            mrq_msg = wpg.upper()
        else:
            try:
                # Ensure first entry has a valid description
                first_desc = wpg.entries[0].get("description") or ""
                wpg_desc = pad + str(first_desc)

                for n in range(1, len(wpg.entries)):
                    new_entry = wpg.entries[n].get("description") or ""
                    new_entry = str(new_entry)
                    if len(wpg_desc + pad + new_entry) * 24 < 31000:
                        wpg_desc = wpg_desc + pad + new_entry
                    else:
                        break

                mrq_msg = wpg_desc.upper()
            except Exception as e:
                debug_msg(f"RSS parsing failed: {e}", 1)
                mrq_msg = "RSS PROCESSING ERROR"

        marquee_length = len(mrq_msg)
        pixels = marquee_length * 24
        marquee.delete("all")
        text = marquee.create_text(
            1, 2, anchor='nw', text=pad + mrq_msg + pad,
            font=('VCR OSD Mono', 25,), fill="white"
        )

        def animate_marquee(pos=0):
            if pos < pixels + 730:
                marquee.move(text, -1, 0)
                marquee.update()
                root.after(2, animate_marquee, pos + 1)
            else:
                marquee.move(text, pixels + 729, 0)
                root.after(1000, lambda: bottom_marquee(grouptotal, marquee))

        animate_marquee()

    except Exception as e:
        debug_msg(f"BOTTOM_MARQUEE-critical error: {str(e)}", 1)
        try:
            root.after(30000, lambda: bottom_marquee(grouptotal, marquee))
        except:
            pass


# DEF generate playlist from folder with improved error handling
def playlist_generator(musicpath):
    """Generate music playlist with error handling"""
    try:
        debug_msg("PLAYLIST_GENERATOR-searching for music files...", 1)
        
        if not os.path.exists(musicpath):
            debug_msg(f"PLAYLIST_GENERATOR-creating music directory: {musicpath}", 1)
            os.makedirs(musicpath)
            return []
        
        filelist = os.listdir(musicpath)
        allFiles = list()
        
        for entry in filelist:
            try:
                fullPath = os.path.join(musicpath, entry)
                if os.path.isdir(fullPath):
                    allFiles = allFiles + playlist_generator(fullPath)
                elif entry.lower().endswith(('.mp3', '.wav', '.ogg')):  # Only audio files
                    allFiles.append(fullPath)
            except Exception as e:
                debug_msg(f"PLAYLIST_GENERATOR-error processing {entry}: {str(e)}", 2)
                continue
        
        debug_msg(f"PLAYLIST_GENERATOR-found {len(allFiles)} music files", 1)
        return allFiles
        
    except Exception as e:
        debug_msg(f"PLAYLIST_GENERATOR-error: {str(e)}", 1)
        return []

# DEF play background music with improved error handling
def music_player(songNumber, playlist, musicpath):
    """Play background music with error handling"""
    try:
        if not playlist:
            debug_msg("MUSIC_PLAYER-no music files found, skipping", 1)
            root.after(10000, music_player, 0, playlist, musicpath)
            return
        
        if not pygame.mixer.get_init():
            debug_msg("MUSIC_PLAYER-pygame mixer not initialized", 1)
            root.after(10000, music_player, songNumber, playlist, musicpath)
            return
        
        if ((not pygame.mixer.music.get_busy()) and (songNumber < len(playlist))):
            try:
                debug_msg(f"MUSIC_PLAYER-playing song {os.path.basename(playlist[songNumber])}", 1)
                pygame.mixer.music.load(playlist[songNumber])
                pygame.mixer.music.play(loops=0)
                songNumber = songNumber + 1
            except Exception as e:
                debug_msg(f"MUSIC_PLAYER-error playing {playlist[songNumber]}: {str(e)}", 1)
                songNumber = songNumber + 1  # Skip problematic file
                
        elif ((not pygame.mixer.music.get_busy()) and (songNumber >= len(playlist))):
            debug_msg("MUSIC_PLAYER-playlist complete, re-shuffling...", 1)
            songNumber = 0
            random.shuffle(playlist)   

        root.after(2000, music_player, songNumber, playlist, musicpath)
        
    except Exception as e:
        debug_msg(f"MUSIC_PLAYER-error: {str(e)}", 1)
        root.after(10000, music_player, songNumber, playlist, musicpath)

# DEF Word Shortener 5000 with improved error handling
def word_short(phrase, length):
    """Shorten phrases with error handling"""
    try:
        if not phrase:
            return "NO DATA"
        
        # dictionary of shortened words
        dict_short = {                    
            "BECOMING" : "BCMG",
            "SCATTERED" : "SCTD",
            "PARTLY" : "PTLY",
            "SHOWER" : "SHWR",
            "CLOUDY" : "CLDY",
            "DRIZZLE" : "DRZLE",
            "FREEZING" : "FRZG",
            "THUNDERSHOWER" : "THNDSHR",
            "THUNDERSTORM" : "THNDSTM",
            "PRECIPITATION" : "PRECIP",
            "CHANCE" : "CHNCE",
            "DEVELOPING" : "DVLPNG",
            "WITH" : "W",
            "LIGHT" : "LT",
            "HEAVY" : "HVY",
            "BLOWING" : "BLWNG"
        }
        
        phrase = str(phrase).upper()
        
        if len(phrase) > length:
            if phrase == "A MIX OF SUN AND CLOUD":
                phrase = "SUN CLOUD MIX"
            
            for key, value in dict_short.items():
                phrase = re.sub(key, value, phrase)
            
            debug_msg(f"WORD_SHORT-phrase shortened to {phrase}", 2)
        
        return phrase[:length] if len(phrase) > length else phrase
        
    except Exception as e:
        debug_msg(f"WORD_SHORT-error: {str(e)}", 2)
        return str(phrase)[:length] if phrase else "ERROR"

# DEF debug messenger
def debug_msg(message, priority):
    """Debug message handler"""
    try:
        debugmode = 2  # 0=disabled, 1=normal, 2=verbose
        timestamp = 2  # 0=none, 1=time, 2=date+time
        
        if timestamp == 1:
            timestr = time.strftime("%H:%M.")
        elif timestamp == 2:
            timestr = time.strftime("%Y%m%d-%H:%M.")
        else:
            timestr = ""
            
        if ((debugmode > 0) and (priority <= debugmode)):
            print(f"{timestr}{prog}.{ver}.{message}")
            
    except Exception as e:
        print(f"DEBUG_MSG-error: {str(e)}")

# DEF signal handler for graceful shutdown
def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    debug_msg("SIGNAL_HANDLER-received shutdown signal", 1)
    try:
        pygame.mixer.quit()
        root.quit()
        root.destroy()
    except:
        pass
    sys.exit(0)

# ROOT main setup
def main():
    """Main application setup with error handling"""
    global root, timeText, updt_tstp
    global ec_en_wpg, ec_en_brn, ec_en_thm, ec_en_tps, ec_en_chu, ec_en_fln, ec_en_ken, ec_en_tby
    global ec_en_vic, ec_en_van, ec_en_edm, ec_en_cal, ec_en_ssk, ec_en_reg, ec_en_wht
    global ec_en_tor, ec_en_otw, ec_en_qbc, ec_en_mtl, ec_en_frd, ec_en_hal, ec_en_stj
    
    try:
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # setup root
        root = Tk()
        root.attributes('-fullscreen', False)
        root.geometry("720x480")
        root.config(cursor="none", bg="green")
        root.wm_title("wpg-weatherchan")

        # Clock - Top RIGHT
        debug_msg("ROOT-placing clock", 1)
        timeText = Label(root, text="", font=("7-Segment Normal", 22), fg="white", bg="green")
        timeText.place(x=403, y=40)
        timeColon1 = Label(root, text=":", font=("VCR OSD Mono", 32), fg="white", bg="green")
        timeColon1.place(x=465, y=36)
        timeColon2 = Label(root, text=":", font=("VCR OSD Mono", 32), fg="white", bg="green")
        timeColon2.place(x=560, y=36)
        debug_msg("ROOT-launching clock updater", 1)
        clock()

        # Title - Top LEFT
        debug_msg("ROOT-placing Title Text", 1)
        Title = Label(root, text="ENVIRONMENT CANADA", font=("VCR OSD Mono", 22, "bold"), fg="white", bg="green")
        Title.place(x=80, y=40)

        # Initialize weather station objects
        debug_msg("ROOT-initializing weather stations", 1)
        try:
            # group 1 - Manitoba/Regional
            ec_en_wpg = ECWeather(station_id='MB/s0000193', language='english')
            ec_en_brn = ECWeather(station_id='MB/s0000492', language='english')
            ec_en_thm = ECWeather(station_id='MB/s0000695', language='english')
            ec_en_tps = ECWeather(station_id='MB/s0000644', language='english')
            ec_en_chu = ECWeather(station_id='MB/s0000779', language='english')
            ec_en_fln = ECWeather(station_id='MB/s0000015', language='english')
            ec_en_ken = ECWeather(station_id='ON/s0000651', language='english')
            ec_en_tby = ECWeather(station_id='ON/s0000411', language='english')

            # group 2 - Western Canada
            ec_en_vic = ECWeather(station_id='BC/s0000775', language='english')
            ec_en_van = ECWeather(station_id='BC/s0000141', language='english')
            ec_en_edm = ECWeather(station_id='AB/s0000045', language='english')
            ec_en_cal = ECWeather(station_id='AB/s0000047', language='english')
            ec_en_ssk = ECWeather(station_id='SK/s0000797', language='english')
            ec_en_reg = ECWeather(station_id='SK/s0000788', language='english')
            ec_en_wht = ECWeather(station_id='YT/s0000825', language='english')

            # group 3 - Eastern Canada
            ec_en_tor = ECWeather(station_id='ON/s0000458', language='english')
            ec_en_otw = ECWeather(station_id='ON/s0000430', language='english')
            ec_en_mtl = ECWeather(station_id='QC/s0000635', language='english')
            ec_en_qbc = ECWeather(station_id='QC/s0000620', language='english')
            ec_en_frd = ECWeather(station_id='NB/s0000250', language='english')
            ec_en_hal = ECWeather(station_id='NS/s0000318', language='english')
            ec_en_stj = ECWeather(station_id='NL/s0000280', language='english')
            
            debug_msg("ROOT-weather stations initialized successfully", 1)
            
        except Exception as e:
            debug_msg(f"ROOT-error initializing weather stations: {str(e)}", 1)
            # Continue anyway - the safe_get_weather_value function will handle missing data

        # Initialize update timestamps
        updt_tstp = [0, 0, 0, 0]
        grouptotal = 3

        # Set initial fallback values
        global real_forecast_time, real_forecast_date
        real_forecast_time = time.strftime("%I %p").lstrip("0")
        if real_forecast_time == "12 PM":
            real_forecast_time = "NOON"
        real_forecast_date = datetime.datetime.now().strftime("%a %b %d/%Y")

        # Update Weather Information
        debug_msg("ROOT-launching initial weather update", 1)
        try:
            weather_update(0)  # update all cities
            debug_msg("ROOT-initial weather update completed", 1)
        except Exception as e:
            debug_msg(f"ROOT-initial weather update failed: {str(e)}", 1)
            debug_msg("ROOT-continuing with fallback data", 1)

        # Middle Section (Cycling weather pages)
        debug_msg("ROOT-launching weather_page", 1)
        PageColour = "#00006D"  # blue
        PageNum = 1
        try:
            weather_page(PageColour, PageNum)
        except Exception as e:
            debug_msg(f"ROOT-error starting weather pages: {str(e)}", 1)

        # Generate background music playlist
        debug_msg("ROOT-launching playlist generator", 1)
        musicpath = os.path.expanduser("~/WeatherPi/music")
        try:
            playlist = playlist_generator(musicpath)
            random.shuffle(playlist) if playlist else None
            debug_msg(f"ROOT-playlist generated with {len(playlist)} songs", 1)
        except Exception as e:
            debug_msg(f"ROOT-playlist generation error: {str(e)}", 1)
            playlist = []

        # Play background music
        debug_msg("ROOT-launching background music", 1)
        songNumber = 0
        try:
            pygame.mixer.init()
            music_player(songNumber, playlist, musicpath)
            debug_msg("ROOT-background music system started", 1)
        except Exception as e:
            debug_msg(f"ROOT-background music error: {str(e)}", 1)

        # Bottom Scrolling Text (RSS Feed)
        debug_msg("ROOT-launching bottom_marquee", 1)
        try:
            # Use root.after to start the marquee after a short delay
            root.after(2000, lambda: bottom_marquee(grouptotal, marquee))
        except Exception as e:
            debug_msg(f"ROOT-bottom marquee error: {str(e)}", 1)

        # Start the main loop
        debug_msg("ROOT-starting main application loop", 1)
        try:
            root.mainloop()
        except KeyboardInterrupt:
            debug_msg("ROOT-keyboard interrupt received", 1)
            signal_handler(None, None)
        except Exception as e:
            debug_msg(f"ROOT-main loop error: {str(e)}", 1)
        debug_msg("ROOT-launching bottom_marquee", 1)
        try:
            marquee = Canvas(root, height=120, width=580, bg="green")
            marquee.config(highlightbackground="green")
            marquee.place(x=80, y=400)
            root.after(2000, lambda: bottom_marquee(grouptotal, marquee))
        except Exception as e:
            debug_msg(f"ROOT-bottom marquee error: {str(e)}", 1)
            
    except Exception as e:
        debug_msg(f"ROOT-critical startup error: {str(e)}", 1)
        sys.exit(1)
    finally:
        # Cleanup
        try:
            if 'pygame' in globals():
                pygame.mixer.quit()
        except:
            pass

if __name__ == "__main__":
    main()