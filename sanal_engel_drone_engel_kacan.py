import collections
if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import math

def get_distance_meters(loc1, loc2):
    dlat = loc2.lat - loc1.lat
    dlong = loc2.lon - loc1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

vehicle = connect('127.0.0.1:14550', wait_ready=True)

engeller = [
    LocationGlobalRelative(-35.3625, 149.1655, 10),
    LocationGlobalRelative(-35.3620, 149.1660, 10),
    LocationGlobalRelative(-35.3615, 149.1650, 10),
    LocationGlobalRelative(-35.3610, 149.1665, 10),
    LocationGlobalRelative(-35.3605, 149.1655, 10)
]

ana_hedef = LocationGlobalRelative(-35.3600, 149.1650, 10)

print("Kalkış yapılıyor...")
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True
vehicle.simple_takeoff(10)
time.sleep(10)

print("Gidiş başladı. Engeller taranıyor...")
vehicle.simple_goto(ana_hedef)

while True:
    current_pos = vehicle.location.global_relative_frame
    dist_to_target = get_distance_meters(current_pos, ana_hedef)
    
    for i, engel in enumerate(engeller):
        mesafe = get_distance_meters(current_pos, engel)
        
        if mesafe < 15:
            print(f"!!! UYARI: {i+1}. ENGELE ÇOK YAKINIZ ({int(mesafe)}m) !!!")
            print("Kaçış manevrası yapılıyor: Sağa kır!")
            
            # Agresif ve geniş kaçış manevrası
            kacis_noktasi = LocationGlobalRelative(current_pos.lat, current_pos.lon + 0.0008, 10)
            vehicle.simple_goto(kacis_noktasi)
            time.sleep(8)
            
            print("Tehlike geçildi, ana hedefe devam.")
            vehicle.simple_goto(ana_hedef)

    if dist_to_target < 2:
        print("Hedefe varıldı!")
        break
    time.sleep(1)

vehicle.mode = VehicleMode("RTL")
