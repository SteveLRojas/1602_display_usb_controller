import time
import requests
import display_1602_platform as disp
import display_1602_regs as regs

def main():
	unique_id = disp.init(0x2EBDDBAD)
	if unique_id == 0:
		print("Could not find display")
		exit()

	disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
	disp.write_string('Lizards rule!')

	time.sleep(1.0)
	disp.write_reg(regs.R_CLEAR_DISPLAY, 0)

	try:
		url = "https://wttr.in/?format=j1"
		data = requests.get(url).json()
		if "data" in data:
			data = data["data"]

		# Case 1: normal (preferred)
		if "current_condition" in data:
			current = data["current_condition"][0]
			temp = current["temp_C"]
			condition = current["weatherDesc"][0]["value"]
		# Case 2: fallback to forecast
		elif "weather" in data:
			print("Using forecast data!")
			current = data["weather"][0]["hourly"][0]
			temp = current["tempC"]
			condition = current["weatherDesc"][0]["value"]
		else:
			print(data)
			temp = "?"
			condition = "No data"

		print(temp)
		print(condition)

		disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
		disp.write_string(f"{temp}C")

		time.sleep(1.5)

		disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
		disp.write_string(condition)

	except Exception as e:
		print(e)

if __name__ == "__main__":
	main()