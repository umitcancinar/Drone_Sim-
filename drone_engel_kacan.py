import collections
if not hasattr(collections, 'MutableMapping'):
    import collections.abc
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import math

# Mesafe ölçer
def get_distance_meters(loc1, loc2):
    dlat = loc2.lat - loc1.lat
    dlong = loc2.lon - loc1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

# Otopilota bağlan
vehicle = connect('127.0.0.1:14550', wait_ready=True)

# Sabit Ana Hedef (Yolun sonu)
ana_hedef = LocationGlobalRelative(-35.3600, 149.1650, 10)

print("Kalkış yapılıyor...")
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True
vehicle.simple_takeoff(10)
time.sleep(10)

print("Gidiş başladı! Haritaya 'Waypoint' ekleyerek tuzakları kur...")
vehicle.simple_goto(ana_hedef)

while True:
    current_pos = vehicle.location.global_relative_frame
    dist_to_target = get_distance_meters(current_pos, ana_hedef)
    
    # --- DİNAMİK RADAR BAŞLIYOR ---
    # Haritadaki Waypointleri (Görevleri) canlı olarak indir
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    
    # Tıkladığın Waypointleri 'Engeller' listesine çevir
    dinamik_engeller = []
    for cmd in cmds:
        if cmd.x != 0.0 and cmd.y != 0.0:
            dinamik_engeller.append(LocationGlobalRelative(cmd.x, cmd.y, 10))
    # ------------------------------
    
    tehlike_var_mi = False
    
    # Her bir dinamik engele olan mesafeyi kontrol et
    for i, engel in enumerate(dinamik_engeller):
        mesafe = get_distance_meters(current_pos, engel)
        
        if mesafe < 15: # 15 metrelik sanal çember sınırı
            print(f"!!! RADAR UYARISI: Haritadan eklenen {i+1}. engele çok yakınız ({int(mesafe)}m) !!!")
            print("Kaçış manevrası yapılıyor: Sağa kır!")
            
            # Agresif kaçış manevrası
            kacis_noktasi = LocationGlobalRelative(current_pos.lat, current_pos.lon + 0.0008, 10)
            vehicle.simple_goto(kacis_noktasi)
            time.sleep(8)
            
            print("Tehlike atlatıldı, ana hedefe dönülüyor.")
            vehicle.simple_goto(ana_hedef)
            tehlike_var_mi = True
            break # Manevrayı yaptıktan sonra döngüyü kır

    if dist_to_target < 2:
        print("Hedefe varıldı!")
        break
        
    if not tehlike_var_mi:
        time.sleep(1) # Saniyede bir haritayı tara

print("Eve dönülüyor...")
vehicle.mode = VehicleMode("RTL")
