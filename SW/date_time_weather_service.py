import signal
import time
from datetime import datetime
import requests
import configparser
import logging
import display_1602_platform as disp
import display_1602_regs as regs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


def stop(signum=None, frame=None):
    log.info("Stopping display")
    disp.stop()
    raise SystemExit


# Open-Meteo uses WMO weather interpretation codes.
WMO_DESCRIPTIONS = {
    0: "Clear",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Freezing drizzle",
    57: "Heavy frz drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy frz rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Snow showers",
    86: "Heavy snow shwr",
    95: "Thunderstorm",
    96: "Storm with hail",
    99: "Heavy storm/hail",
}


def fetch_open_meteo(latitude, longitude):
    """Return (temperature_C, description), or None if Open-Meteo fails."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        current = response.json()["current"]

        temperature = current["temperature_2m"]
        weather_code = int(current["weather_code"])
        description = WMO_DESCRIPTIONS.get(
            weather_code, f"Weather code {weather_code}"
        )

        log.info("Weather received from Open-Meteo")
        return temperature, description
    except (requests.RequestException, KeyError, TypeError, ValueError):
        log.exception("Open-Meteo request failed")
        return None


def fetch_wttr():
    """Return (temperature_C, description), or None if wttr.in fails."""
    try:
        response = requests.get("https://wttr.in/?format=j1", timeout=5)
        response.raise_for_status()
        data = response.json()

        # Some wrappers put the wttr.in response below a top-level 'data' key.
        if isinstance(data, dict) and "data" in data:
            data = data["data"]

        current = data["current_condition"][0]
        temperature = current["temp_C"]
        description = current["weatherDesc"][0]["value"]

        log.info("Weather received from wttr.in")
        return temperature, description
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        log.exception("wttr.in request failed")
        return None


def fetch_weather(latitude, longitude):
    """Try Open-Meteo first, then fall back to wttr.in."""
    weather = fetch_open_meteo(latitude, longitude)
    if weather is not None:
        return weather

    log.warning("Falling back to wttr.in")
    return fetch_wttr()


def main():
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    config = configparser.ConfigParser()
    config.read("config.ini")

    conf_interval = config.getint("settings", "update_interval", fallback=60)
    conf_unique_id = config.get("settings", "unique_id", fallback="0")
    conf_unique_id = int(conf_unique_id, 16)
    conf_contrast = config.getint("settings", "contrast", fallback=45)
    conf_brightness_r = config.getint("settings", "brightness_r", fallback=127)
    conf_brightness_g = config.getint("settings", "brightness_g", fallback=127)
    conf_brightness_b = config.getint("settings", "brightness_b", fallback=127)

    # Munich defaults. Override these in config.ini for the display's location.
    conf_latitude = config.getfloat("settings", "latitude", fallback=48.1374)
    conf_longitude = config.getfloat("settings", "longitude", fallback=11.5755)

    while True:
        log.info("Connecting to display")
        unique_id = disp.init(conf_unique_id)
        while unique_id == 0:
            time.sleep(1.0)
            unique_id = disp.init(conf_unique_id)

        disp.write_reg(regs.R_CONTRAST, conf_contrast)
        disp.write_reg(regs.R_BRIGHTNESS_R, conf_brightness_r)
        disp.write_reg(regs.R_BRIGHTNESS_G, conf_brightness_g)
        disp.write_reg(regs.R_BRIGHTNESS_B, conf_brightness_b)

        log.info("Device ID: %08X", disp.get_device_id())
        log.info("Unique ID: %08X", disp.get_unique_id())
        log.info("Num rows: %d", disp.num_rows)
        log.info("Num columns: %d", disp.num_columns)
        log.info("Reset type: %02X", disp.read_reg(regs.R_RESET_TYP))

        disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
        disp.write_string("Lizards rule!")

        time.sleep(1.0)
        disp.write_reg(regs.R_CLEAR_DISPLAY, 0)

        try:
            # Here we assume that none of the strings take more lines.
            num_strings = 4
            lines_per_string = 1
            if disp.num_columns < 16:
                lines_per_string = 2
            disp.bouncy_init(num_strings)

            time_count = 0
            line = 0

            while True:
                now = datetime.now()
                date_str = now.strftime("%d.%m.%y")
                time_str = now.strftime("%H:%M")
                disp.bouncy_set_string("Date: " + date_str, 0, lines_per_string)
                disp.bouncy_set_string("Time: " + time_str, 1, lines_per_string)

                if time_count == 0:
                    weather = fetch_weather(conf_latitude, conf_longitude)
                    if weather is not None:
                        temp, condition = weather
                        try:
                            temp = f"{float(temp):.1f}"
                        except (TypeError, ValueError):
                            temp = "?"
                    else:
                        temp = "?"
                        condition = "No data"

                    max_line_length = disp.num_columns * lines_per_string - 1
                    condition = str(condition)[:max_line_length]
                    disp.bouncy_set_string(f"Temp: {temp}C", 2, lines_per_string)
                    disp.bouncy_set_string(condition, 3, lines_per_string)

                for row in range(disp.num_rows // lines_per_string):
                    disp.bouncy_update((line + row) % num_strings, row * lines_per_string,)
                line = (line + 1) % num_strings

                time_count = (time_count + 1) % conf_interval
                time.sleep(1.0)

        except Exception as error:
            log.exception("Something is fishy: %s", error)
            disp.stop()
            time.sleep(10.0)
            continue


if __name__ == "__main__":
    main()
