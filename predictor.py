import requests
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning) # 2038 thing

API_KEY = 'xxx'
SATELLITES = {
    'NOAA-15': 25338,
    'NOAA-18': 28654,
    'NOAA-19': 33591,
    'METEOR M2-3': 57166,
    'ISS': 25544  # add as many as u want
}
observer_lat = 41.12
observer_lng = 16.85
observer_alt = 0
geolocator = Nominatim(user_agent="satellite_location")
RESET = "\033[0m"
RED = "\033[31m"
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"

world_map = [
        "\n"
        f"{YELLOW}   180   150W  120W  90W   60W   30W   000   30E   60E   90E   120E  150E  180 {RESET}",
        f"{BLUE}    |     |     |     |     |     |     |     |     |     |     |     |     | {RESET}",
        f"{YELLOW}90N{BLUE}-+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-{YELLOW}90N ",
        f"{BLUE}    |           . _..::__:  ,-\"-\"._        |7       ,     _,.__             {BLUE}|{RESET}",
        f"{BLUE}    |   _.___ _ _<_>`!(._`.`-.    /         _._     `_ ,_/  '  '-._.---.-.__{BLUE}|{RESET}",
        f"{BLUE}    |>./     \" \" `-==,',._\\|  \\  / \\)      / _ \">_,-' `                 \\-)_{BLUE}|{RESET}",
        f"{YELLOW}60N{BLUE}-+  \\_.:--.       `._ )`^-. \"'       , [_/(                       __,/-' +-{YELLOW}60N",
        f"{BLUE}    | '\"'     \\         \"    _L        oD_,--\'                )     /. (|   {BLUE}|{RESET}",
        f"{BLUE}    |          |           ,'          _)_.\\\\._<> 0              _,' /  '   {BLUE}|{RESET}",
        f"{BLUE}    |          `.         /           [_/_'\\ `\"(                <'/  )      {BLUE}|{RESET}",
        f"{YELLOW}30N{BLUE}-+           \\\\    .-. )           /   `-\"..' `:._          _)  '        +-{YELLOW}30N",
        f"{BLUE}    |    `        \\  (  `(           /         `:\\  > \\  ,-^.  /' '         {BLUE}|{RESET}",
        f"{BLUE}    |              `._,   \"\"         |           \\`'   \\|   ?_)  (\\         |",
        f"{BLUE}    |                 `=.---.        `._._       ,'     \"`  |' ,- '.        |",
        f"{YELLOW}000{BLUE}-+                   |    `-._         |     /          `:`<_|h--._      +-{YELLOW}000",
        f"{BLUE}    |                   (        >        .     | ,          `=.__.`-'\\     |",
        f"{BLUE}    |                    `.     /         |     |(|              ,-.,\\     .|",
        f"{BLUE}    |                     |   ,'           \\   / `'            ,\"     \\     |",
        f"{YELLOW}30S{BLUE}-+                     |  /              |_'                |  __  /     +-{YELLOW}30S",
        f"{BLUE}    |                     | |                                  '-'  `-'  |\\.|",
        f"{BLUE}    |                     |/                                         \"  / / |",
        f"{BLUE}    |                     \\.                                            \\'  |",
        f"{YELLOW}60S{BLUE}-+                                                                       +-{YELLOW}60S",
        f"{BLUE}    |                      ,/            ______._.--._ _..---.---------._   |",
        f"{BLUE}    |     ,-----\"-..?----_/ )      __,-'\"             \"                  (  |",
        f"{BLUE}    |-.._(                  `-----'                                       `-|",
        f"{YELLOW}90S{BLUE}-+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-{YELLOW}90S",
        f"{BLUE}    Map 1998 Matthew Thomas.|Freely usable as long as this|line is included.|",
        f"{BLUE}    |     |     |     |     |     |     |     |     |     |     |     |     |",
        f"{YELLOW}   180   150W  120W  90W   60W   30W   000   30E   60E   90E   120E  150E  180 {RESET}",
    ]


def timestamp_to_local_time(ts):
    return (datetime.utcfromtimestamp(ts) + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')


def get_country_name(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language='en')
        return location.raw["address"].get("country", "Unknown")
    except Exception:
        return "Unknown"


# api functions
def fetch_satellite_position(sat_id, observer_lat, observer_lng, observer_alt, API_KEY):
    url = f"https://api.n2yo.com/rest/v1/satellite/positions/{sat_id}/{observer_lat}/{observer_lng}/{observer_alt}/1/&apiKey={API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200 and "positions" in (data := resp.json()):
        pos = data['positions'][0]
        satellite_lat = pos['satlatitude']
        satellite_lon = pos['satlongitude']
        location = geolocator.reverse((satellite_lat, satellite_lon), language='en')
        location_name = location.address if location else "Unknown Location"

        return {
            'id': sat_id,
            'name': data['info']['satname'],
            'latitude': satellite_lat,
            'longitude': satellite_lon,
            'altitude': pos['sataltitude'],
            'location_name': location_name
        }


def fetch_visual_passes(sat_id, days=3):
    url = f"https://api.n2yo.com/rest/v1/satellite/visualpasses/{sat_id}/{observer_lat}/{observer_lng}/{observer_alt}/{days}/60/&apiKey={API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200 and "passes" in (data := resp.json()):
        return {'name': data['info']['satname'], 'passes': data['passes']}


# print functions
def print_visual_passes(data):
    if not data: return
    grouped = {}
    for p in data['passes']:
        date = timestamp_to_local_time(p['startUTC']).split()[0]
        time = timestamp_to_local_time(p['startUTC']).split()[1]
        grouped.setdefault(date, []).append((time, p['duration'] // 60))

    print(f"\n- Next passes for {data['name']}:")
    for date in sorted(grouped):
        label = {
            datetime.utcnow().date(): "Today",
            datetime.utcnow().date() + timedelta(days=1): "Tomorrow",
            datetime.utcnow().date() + timedelta(days=2): "Day After Tomorrow"
        }.get(datetime.strptime(date, "%Y-%m-%d").date(), date)
        print(f"\n  {label} ({date}):")
        for time, dur in grouped[date]:
            print(f"   • {time} ({dur} min)")


def print_map(sat_positions):
    map_width, map_height = 14, len(world_map)
    lines = [list(line) for line in world_map]  # copy of the map

    for sat in sat_positions:
        lon_index = int((sat['longitude'] + 180) / 360 * map_width)
        lat_index = int((90 - sat['latitude']) / 180 * (map_height - 1))
        lon_index = max(0, min(lon_index, map_width - 1))
        lat_index = max(0, min(lat_index, map_height - 1))
        char_x = 5 * lon_index + 3

        if char_x < len(lines[lat_index]):
            lines[lat_index][char_x] = f"{RED}x{BLUE}"

    for line in lines:
        print("".join(line))


# menu functions
def display_all():
    sats = []
    print()
    for name, sat_id in SATELLITES.items():
        pos = fetch_satellite_position(sat_id, observer_lat, observer_lng, observer_alt, API_KEY)
        if pos:
            sats.append(pos)
            print(f"{GREEN}{pos['name']}{RESET} — Lat: {pos['latitude']:.2f}, Lon: {pos['longitude']:.2f}, Alt: {pos['altitude']:.2f} km— {YELLOW}{pos['location_name']}{RESET}")
    if sats:
        print("\nSatellite positions on the map:")
        print_map(sats)
        for sat in sats:
            passes = fetch_visual_passes(sat['id'])
            if passes:
                print_visual_passes(passes)


def display_single_position():
    sat = get_satellite_choice()
    if not sat: return
    pos = fetch_satellite_position(sat['id'], observer_lat, observer_lng, observer_alt, API_KEY)
    if pos:
        country = get_country_name(pos['latitude'], pos['longitude'])
        print(f"\n{GREEN}{pos['name']}{RESET} is above {YELLOW}{country}{RESET}")
        print(f"Lat: {pos['latitude']:.2f} | Lon: {pos['longitude']:.2f} | Alt: {pos['altitude']:.2f} km\n")
        print_map([pos])


def display_single_passes():
    sat = get_satellite_choice()
    if not sat: return
    passes = fetch_visual_passes(sat['id'])
    if passes:
        print_visual_passes(passes)


def get_satellite_choice():
    print("\nAvailable Satellites:")
    for i, name in enumerate(SATELLITES):
        print(f"{i} - {name}")
    try:
        choice = int(input("Your choice: "))
        name = list(SATELLITES.keys())[choice]
        return {'id': SATELLITES[name], 'name': name}
    except (ValueError, IndexError):
        print("Invalid choice.")
        return None


def main():
    menu = {
        '0': ("Get all satellites' positions and next passes", display_all),
        '1': ("Get a single satellite's current position", display_single_position),
        '2': ("Get a single satellite's next visual passes", display_single_passes),
        '3': ("Quit", exit)
    }

    while True:
        print("\nMenu:")
        for key, (desc, _) in menu.items():
            print(f"{key} - {desc}")
        choice = input("Select an option: ")
        action = menu.get(choice)
        if action:
            action[1]()
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
