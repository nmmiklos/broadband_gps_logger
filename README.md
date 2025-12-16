Broadband GPS logger, using NMEA format (MBIM compatible). Logs to a csv file, which you can upload to sites like gpsvisualizer.com
Logger2 is only hungarian for now, logger is a previous semi-working attempt at gps based tracking, which is available in english and hungarian.

made and tested on:

/org/freedesktop/ModemManager1/Modem/0 [Sierra Wireless Inc] HP un2430 Mobile Broadband Module

Arch linux 6.17.9 HP EliteBook 2170p.

Useage:
enable nmea location service in mmcli

$ sudo mmcli -m 0 --location-enable-gps-nmea

run python3

$ python3 [location]/logger_v2.py
