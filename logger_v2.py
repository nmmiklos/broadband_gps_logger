import subprocess
import time
import csv
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "gps_log.csv")

def dm_to_dd(dm, direction):
    if not dm or dm == '': return None
    try:
        if '.' not in dm: return None
        dot_index = dm.find('.')
        deg_end_index = dot_index - 2
        d = float(dm[:deg_end_index])
        m = float(dm[deg_end_index:])
        dd = d + (m / 60.0)
        if direction in ('S', 'W'): dd = -dd
        return dd
    except ValueError: return None

def get_nmea():
    try:
        result = subprocess.run(['mmcli', '-m', '0', '--location-get'],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        nmea_lines = []
        for line in result.stdout.splitlines():
            if '$GPRMC' in line:
                start = line.find('$GPRMC')
                nmea_lines.append(line[start:])
        return nmea_lines
    except Exception: return []

def parse_rmc(nmea_lines):
    for line in nmea_lines:
        if line.startswith('$GPRMC'):
            parts = line.split(',')
            if len(parts) < 10: continue
            if parts[2] != 'A': return None
            
            lat = dm_to_dd(parts[3], parts[4])
            lon = dm_to_dd(parts[5], parts[6])
            try: speed = float(parts[7]) * 1.852 if parts[7] else 0.0
            except: speed = 0.0
            try: heading = float(parts[8]) if parts[8] else 0.0
            except: heading = 0.0
            
            return {'lat': lat, 'lon': lon, 'speed_kmh': speed, 'heading_deg': heading}
    return None

print(f"Log fájl helye: {CSV_FILE}")

try:
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'lat', 'lon', 'speed_kmh', 'heading_deg'])
            writer.writeheader()
        print("CSV fájl létrehozva.")
    else:
        print("Meglévő CSV fájlhoz fűzés...")
except PermissionError:
    print("\nKRITIKUS HIBA: Nincs írási jogod a fájlhoz! Töröld a régit sudo-val vagy futtasd ezt sudo-val.")
    sys.exit(1)

print("GPS logger fut... (Ctrl+C kilépés)")

try:
    while True:
        nmea_data = get_nmea()
        gps_fix = parse_rmc(nmea_data)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        if gps_fix:
            log_msg = (f"\r{timestamp} | Fix OK! "
                       f"Lat: {gps_fix['lat']:.5f}, Lon: {gps_fix['lon']:.5f}")
            print(log_msg, end='', flush=True)
            
            try:
                with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['timestamp', 'lat', 'lon', 'speed_kmh', 'heading_deg'])
                    writer.writerow({'timestamp': timestamp, **gps_fix})
                    f.flush()
                    os.fsync(f.fileno())
                
                print(" -> MENTVE", end='', flush=True)
                
            except Exception as e:
                print(f"\n[HIBA A MENTÉSNÉL]: {e}")
        else:
            print(f"\r{timestamp} | Nincs GPS fix...", end='', flush=True)
        
        time.sleep(2)

except KeyboardInterrupt:
    print("\nLeállítás...")