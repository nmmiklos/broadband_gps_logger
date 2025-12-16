import subprocess
import time
import csv
import os

CSV_FILE = "gps_log.csv"

def dm_to_dd(dm, direction):
    #conversion
    if not dm or dm == '':
        return None
    if '.' not in dm:
        return None
    deg_len = 2 if len(dm.split('.')[0]) <= 2 else 3
    d = float(dm[:deg_len])
    m = float(dm[deg_len:])
    dd = d + m / 60
    if direction in ('S','W'):
        dd = -dd
    return dd

def get_nmea():
    #getrawdata
    result = subprocess.run(
        ['mmcli', '-m', '0', '--location-get'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    nmea_lines = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith('$G'):
            nmea_lines.append(line)
    return nmea_lines

def parse_rmc(nmea_lines):
    #parserawdata
    for line in nmea_lines:
        if line.startswith('$GPRMC'):
            parts = line.split(',')
            status = parts[2]
            if status != 'A': # A = valid, V = void
                return None
            lat = dm_to_dd(parts[3], parts[4])
            lon = dm_to_dd(parts[5], parts[6])
            speed_knots = parts[7] or '0'
            try:
                speed_kmh = float(speed_knots) * 1.852
            except:
                speed_kmh = 0.0
            heading = float(parts[8]) if parts[8] else 0.0
            return {
                'lat': lat,
                'lon': lon,
                'speed_kmh': speed_kmh,
                'heading_deg': heading
            }
    return None

#generate csv file for easy database management
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'lat', 'lon', 'speed_kmh', 'heading_deg'])
        writer.writeheader()

print("GPS logger elindult. Várakozás fixre... (Ctrl+C a bezáráshoz)")
print("GPS logger started. Waiting for fix... (Ctrl+C to force quit)")

while True:
    nmea = get_nmea()
    data = parse_rmc(nmea)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if data:
        print(f"{timestamp} | Latitude: {data['lat']:.6f}, Longitude: {data['lon']:.6f}, "
              f"Speed: {data['speed_kmh']:.2f} km/h, Heading: {data['heading_deg']:.1f}°")
        # saveToCsv
        with open(CSV_FILE, mode='a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'lat', 'lon', 'speed_kmh', 'heading_deg'])
            writer.writerow({'timestamp': timestamp, **data})
    else:
        print(f"{timestamp} | Nincs fix még...")
        print(f"{timestamp} | No fix yet...")
    time.sleep(5)