"""Debug utilities for wpg-weatherchan"""

import time
from details import Details

detail = Details()

class DebugUtils:
    """Class to handle debug messages"""
    def __init__(self):
        pass

    # DEF debug messenger
    def debug_msg(self, message, priority):
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

            if debugmode > 0 and priority <= debugmode:
                print(f"{timestr}{detail.PROG}.{detail.VER}.{message}")

        except Exception as e:
            print(f"DEBUG_MSG-error: {str(e)}")
