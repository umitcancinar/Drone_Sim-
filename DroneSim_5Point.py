import asyncio
from mavsdk import System

async def run():
    drone = System()
    print("PX4 Sistemine bağlanılıyor...")
    # PX4 SITL için port 14540
    await drone.connect(system_address="udp://:14540")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- PX4 Beynine bağlanıldı!")
            break

    print("GPS Bekleniyor...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- GPS Tamam!")
            break

    print("Konum alınıyor...")
    async for position in drone.telemetry.position():
        home_lat = position.latitude_deg
        home_lon = position.longitude_deg
        home_alt = position.absolute_altitude_m
        break

    print("-- Motorlar Çalışıyor")
    await drone.action.arm()

    print("-- Kalkış (10 Metre)")
    await drone.action.takeoff()
    await asyncio.sleep(8)

    # Kısa mesafe hedefleri (Yaklaşık 10-12 metre)
    offset = 0.0001
    hedef_irtifa = home_alt + 10

    noktalar = [
        (home_lat + offset, home_lon),           # Ön
        (home_lat + offset, home_lon + offset),  # Sağ Ön
        (home_lat, home_lon + offset),           # Sağ
        (home_lat - offset, home_lon + offset),  # Sağ Arka
        (home_lat - offset, home_lon)            # Arka
    ]

    for i, (lat, lon) in enumerate(noktalar, 1):
        print(f"-- Nokta {i}'e gidiliyor (Kısa Mesafe)...")
        await drone.action.goto_location(lat, lon, hedef_irtifa, 0)
        await asyncio.sleep(8)

    print("-- Görev bitti, başlangıca dönülüyor...")
    await drone.action.return_to_launch()

if __name__ == "__main__":
    asyncio.run(run())
