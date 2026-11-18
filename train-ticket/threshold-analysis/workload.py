#!/usr/bin/env python3
"""
Analysis B workload: calls a catalogue of Train-Ticket endpoints (deployed with Jaeger tracing),
records client-side latency, and then retrieves the Jaeger traces of every request to obtain the
runtime synchronous call depth (number of service hops on the longest path) and server-side latency.
"""
import json, sys, time, uuid
import requests

BASE = "http://localhost"
JAEGER = "http://localhost:16686"
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
WARMUP = 5
ACC = "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f"
DATE = "2026-10-20"

PORTS = {'ts-admin-basic-info-service': 18767, 'ts-admin-order-service': 16112, 'ts-admin-route-service': 16113, 'ts-admin-travel-service': 16114, 'ts-admin-user-service': 16115, 'ts-assurance-service': 18888, 'ts-auth-service': 12340, 'ts-basic-service': 15680, 'ts-cancel-service': 18885, 'ts-config-service': 15679, 'ts-consign-price-service': 16110, 'ts-consign-service': 16111, 'ts-contacts-service': 12347, 'ts-execute-service': 12386, 'ts-food-service': 18856, 'ts-inside-payment-service': 18673, 'ts-notification-service': 17853, 'ts-order-other-service': 12032, 'ts-order-service': 12031, 'ts-payment-service': 19001, 'ts-preserve-other-service': 14569, 'ts-preserve-service': 14568, 'ts-price-service': 16579, 'ts-rebook-service': 18886, 'ts-route-plan-service': 14578, 'ts-route-service': 11178, 'ts-seat-service': 18898, 'ts-security-service': 11188, 'ts-station-service': 12345, 'ts-train-service': 14567, 'ts-travel-plan-service': 14322, 'ts-travel-service': 12346, 'ts-travel2-service': 16346, 'ts-user-service': 12342, 'ts-verification-code-service': 15678, 'ts-ticketinfo-service': 15681, 'ts-food-map-service': 18855}

TRAVEL = {"trip": {"tripId": {"type": "G", "number": "1234"}, "trainTypeId": "GaoTieOne", "routeId": "92708982-77af-4318-be25-57ccb0ff69ad",
                   "startingStationId": "shanghai", "stationsId": "suzhou", "terminalStationId": "taiyuan"},
          "startingPlace": "Shang Hai", "endPlace": "Tai Yuan", "departureTime": DATE}

# (service, method, path, body, role)
CATALOGUE = [
    ("ts-station-service", "GET", "/api/v1/stationservice/stations", None, "user"),
    ("ts-train-service", "GET", "/api/v1/trainservice/trains", None, "user"),
    ("ts-route-service", "GET", "/api/v1/routeservice/routes", None, "user"),
    ("ts-price-service", "GET", "/api/v1/priceservice/prices", None, "user"),
    ("ts-config-service", "GET", "/api/v1/configservice/configs", None, "user"),
    ("ts-contacts-service", "GET", f"/api/v1/contactservice/contacts/account/{ACC}", None, "user"),
    ("ts-contacts-service", "GET", "/api/v1/contactservice/contacts", None, "admin"),
    ("ts-assurance-service", "GET", "/api/v1/assuranceservice/assurances/types", None, "user"),
    ("ts-assurance-service", "GET", "/api/v1/assuranceservice/assurances", None, "admin"),
    ("ts-user-service", "GET", "/api/v1/userservice/users", None, "admin"),
    ("ts-user-service", "GET", f"/api/v1/userservice/users/id/{ACC}", None, "user"),
    ("ts-auth-service", "GET", "/api/v1/users", None, "admin"),
    ("ts-travel-service", "GET", "/api/v1/travelservice/trips", None, "user"),
    ("ts-travel-service", "GET", "/api/v1/travelservice/routes/G1234", None, "user"),
    ("ts-travel-service", "GET", "/api/v1/travelservice/train_types/G1234", None, "user"),
    ("ts-travel2-service", "GET", "/api/v1/travel2service/trips", None, "user"),
    ("ts-security-service", "GET", "/api/v1/securityservice/securityConfigs", None, "admin"),
    ("ts-security-service", "GET", f"/api/v1/securityservice/securityConfigs/{ACC}", None, "user"),
    ("ts-order-service", "GET", "/api/v1/orderservice/order", None, "admin"),
    ("ts-order-service", "POST", "/api/v1/orderservice/order/refresh", {"loginId": ACC, "enableStateQuery": False, "enableTravelDateQuery": False, "enableBoughtDateQuery": False}, "user"),
    ("ts-order-other-service", "GET", "/api/v1/orderOtherService/orderOther", None, "admin"),
    ("ts-consign-price-service", "GET", "/api/v1/consignpriceservice/consignprice/5/true", None, "user"),
    ("ts-consign-price-service", "GET", "/api/v1/consignpriceservice/consignprice/price", None, "user"),
    ("ts-consign-service", "GET", f"/api/v1/consignservice/consigns/account/{ACC}", None, "user"),
    ("ts-food-map-service", "GET", "/api/v1/foodmapservice/foodstores", None, "user"),
    ("ts-food-map-service", "GET", "/api/v1/foodmapservice/trainfoods", None, "user"),
    ("ts-payment-service", "GET", "/api/v1/paymentservice/payment", None, "admin"),
    ("ts-inside-payment-service", "GET", "/api/v1/inside_pay_service/inside_payment/account", None, "admin"),
    ("ts-inside-payment-service", "GET", "/api/v1/inside_pay_service/inside_payment/payment", None, "admin"),
    ("ts-basic-service", "GET", "/api/v1/basicservice/basic/Shang Hai", None, "user"),
    ("ts-basic-service", "POST", "/api/v1/basicservice/basic/travel", TRAVEL, "user"),
    ("ts-ticketinfo-service", "GET", "/api/v1/ticketinfoservice/ticketinfo/Shang Hai", None, "user"),
    ("ts-ticketinfo-service", "POST", "/api/v1/ticketinfoservice/ticketinfo", TRAVEL, "user"),
    ("ts-admin-basic-info-service", "GET", "/api/v1/adminbasicservice/adminbasic/stations", None, "admin"),
    ("ts-admin-basic-info-service", "GET", "/api/v1/adminbasicservice/adminbasic/trains", None, "admin"),
    ("ts-admin-basic-info-service", "GET", "/api/v1/adminbasicservice/adminbasic/configs", None, "admin"),
    ("ts-admin-basic-info-service", "GET", "/api/v1/adminbasicservice/adminbasic/prices", None, "admin"),
    ("ts-admin-basic-info-service", "GET", "/api/v1/adminbasicservice/adminbasic/contacts", None, "admin"),
    ("ts-admin-route-service", "GET", "/api/v1/adminrouteservice/adminroute", None, "admin"),
    ("ts-admin-travel-service", "GET", "/api/v1/admintravelservice/admintravel", None, "admin"),
    ("ts-admin-order-service", "GET", "/api/v1/adminorderservice/adminorder", None, "admin"),
    ("ts-admin-user-service", "GET", "/api/v1/adminuserservice/users", None, "admin"),
    ("ts-food-service", "GET", f"/api/v1/foodservice/foods/{DATE}/Shang Hai/Tai Yuan/G1234", None, "user"),
    ("ts-seat-service", "POST", "/api/v1/seatservice/seats/left_tickets",
     {"travelDate": DATE, "trainNumber": "G1234", "startStation": "shanghai", "destStation": "taiyuan", "seatType": 2}, "user"),
    ("ts-travel-service", "POST", "/api/v1/travelservice/trips/left", {"startingPlace": "Shang Hai", "endPlace": "Tai Yuan", "departureTime": DATE}, "user"),
    ("ts-travel-service", "POST", "/api/v1/travelservice/trip_detail", {"tripId": "G1234", "travelDate": DATE, "from": "Shang Hai", "to": "Su Zhou"}, "user"),
    ("ts-travel2-service", "POST", "/api/v1/travel2service/trips/left", {"startingPlace": "Shang Hai", "endPlace": "Tai Yuan", "departureTime": DATE}, "user"),
    ("ts-travel-plan-service", "POST", "/api/v1/travelplanservice/travelPlan/cheapest", {"startingPlace": "Shang Hai", "endPlace": "Tai Yuan", "departureTime": DATE}, "user"),
    ("ts-travel-plan-service", "POST", "/api/v1/travelplanservice/travelPlan/quickest", {"startingPlace": "Shang Hai", "endPlace": "Tai Yuan", "departureTime": DATE}, "user"),
    ("ts-travel-plan-service", "POST", "/api/v1/travelplanservice/travelPlan/minStation", {"startingPlace": "Shang Hai", "endPlace": "Tai Yuan", "departureTime": DATE}, "user"),
    ("ts-route-plan-service", "POST", "/api/v1/routeplanservice/routePlan/cheapestRoute", {"formStationName": "Shang Hai", "toStationName": "Tai Yuan", "travelDate": DATE, "num": 5}, "user"),
    ("ts-route-plan-service", "POST", "/api/v1/routeplanservice/routePlan/quickestRoute", {"formStationName": "Shang Hai", "toStationName": "Tai Yuan", "travelDate": DATE, "num": 5}, "user"),
    ("ts-route-plan-service", "POST", "/api/v1/routeplanservice/routePlan/minStopStations", {"formStationName": "Shang Hai", "toStationName": "Tai Yuan", "travelDate": DATE, "num": 5}, "user"),
    # ts-preserve-service POST /preserve excluded: its latency is dominated by a synchronous e-mail notification
    # to an external SMTP server (smtp.163.com) that is not reachable from the test environment.
]


def login(user, pwd):
    r = requests.post(f"{BASE}:12340/api/v1/users/login", json={"username": user, "password": pwd}, timeout=60)
    return r.json()["data"]["token"]


def contacts_id(tok):
    r = requests.get(f"{BASE}:12347/api/v1/contactservice/contacts/account/{ACC}", headers={"Authorization": f"Bearer {tok}"}, timeout=60)
    d = r.json().get("data") or []
    return d[0]["id"] if d else None


def main():
    tokens = {"user": login("fdse_microservice", "111111"), "admin": login("admin", "222222")}
    cid = contacts_id(tokens["user"])
    results = []
    for svc, method, path, body, role in CATALOGUE:
        if body and "contactsId" in body:
            body = dict(body, contactsId=cid)
        url = f"{BASE}:{PORTS[svc]}{path}"
        h = {"Authorization": f"Bearer {tokens[role]}"}
        start_us = int(time.time() * 1e6)
        lat, statuses, biz = [], [], []
        for i in range(WARMUP + REPS):
            t0 = time.perf_counter()
            try:
                r = requests.request(method, url, json=body, headers=h, timeout=120)
                code = r.status_code
                try:
                    b = r.json(); bs = b.get("status") if isinstance(b, dict) else None
                except ValueError:
                    bs = None
            except requests.RequestException:
                code, bs = -1, None
            dt = (time.perf_counter() - t0) * 1000
            if i >= WARMUP:
                lat.append(dt); statuses.append(code); biz.append(bs)
        end_us = int(time.time() * 1e6)
        results.append({"service": svc, "method": method, "path": path, "start_us": start_us, "end_us": end_us,
                        "latencies_ms": lat, "http_status": statuses, "business_status": biz})
        ok = sum(1 for c in statuses if c == 200)
        print(f"{svc:30s} {method:4s} {path[:70]:70s} ok={ok}/{REPS} median={sorted(lat)[len(lat)//2]:.1f} ms", flush=True)
        json.dump(results, open("workload_results.json", "w"), indent=1)
        time.sleep(1)
    json.dump(results, open("workload_results.json", "w"), indent=1)


if __name__ == "__main__":
    main()
