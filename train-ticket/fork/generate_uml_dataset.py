#!/usr/bin/env python3
"""
UML Diagram Dataset Generator for TrainTicket-Fork Microservice Application
============================================================================
Generates UML diagram JSON files in GenMyModel-compatible format.
All data extracted directly from trainticket-fork source code analysis.

This fork differs from the original Train-Ticket in several key ways:
  - ts-ticketinfo-service (NEW): intermediary between travel/preserve and basic
  - ts-food-map-service (NEW): replaces ts-station-food-service + ts-train-food-service
  - Missing services: ts-gateway-service, ts-delivery-service, ts-food-delivery-service,
    ts-station-food-service, ts-train-food-service, ts-wait-order-service
  - Hardcoded service URLs with ports (no DiscoveryClient)
  - UUID vs String ID types in entities
  - Field name differences (startingPlace vs startPlace, etc.)

Author: Research Dataset Generator
Source: trainticket-fork (forked from FudanSELab/train-ticket)
"""

import json
import os
import uuid

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))


def gen_key():
    """Generate a unique key for UML elements."""
    return "_" + uuid.uuid4().hex[:24]


def write_json(directory, filename, data):
    """Write JSON data to file."""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def make_class_json(name, key, fields, methods, implements=None, extends=None,
                    modifiers=None, is_interface=False):
    """Create a UML class/interface JSON object matching GenMyModel format."""
    field_dict = {}
    for fname, ftype in fields:
        fkey = gen_key()
        field_dict[fname] = {
            "name": fname,
            "key": fkey,
            "type": ftype,
            "visibility": "private" if not is_interface else "public",
            "isStatic": False
        }

    method_dict = {}
    for mname, mreturn, mparams in methods:
        mkey = gen_key()
        method_dict[mname] = {
            "name": mname,
            "key": mkey,
            "returnType": mreturn,
            "parameters": mparams,
            "visibility": "public",
            "isStatic": False,
            "isAbstract": is_interface
        }

    return {
        "name": name,
        "key": key,
        "type": "interface" if is_interface else "class",
        "hasTypeVariable": False,
        "position": None,
        "modifiers": modifiers or [],
        "fields": field_dict,
        "methods": method_dict,
        "file_path": f"./{name}",
        "anonymous": False,
        "auxclass": False,
        "implements_": implements or [],
        "extends_": extends or [],
        "definedInClassOrInterfaceTypeKey": None,
        "innerDefinedClasses": {},
        "innerDefinedInterfaces": {}
    }


def make_dependency_json(name, key, source_key, target_key):
    """Create a UML dependency JSON object."""
    return {
        "name": name,
        "key": key,
        "type": "dependency",
        "source": source_key,
        "target": target_key
    }


def make_association_json(name, key, source_key, target_key,
                          source_mult="1", target_mult="1"):
    """Create a UML association JSON object."""
    return {
        "name": name,
        "key": key,
        "type": "association",
        "source": source_key,
        "target": target_key,
        "sourceMultiplicity": source_mult,
        "targetMultiplicity": target_mult
    }


def make_diagram_info(diagram_id, categories, primary, is_class, is_behavioral,
                      detected_types, element_counts, total, source_file):
    """Create _diagram_info.json matching GenMyModel format."""
    return {
        "classification": {
            "categories": categories,
            "primary": primary,
            "is_class_diagram": is_class,
            "is_behavioral": is_behavioral
        },
        "detectedTypes": detected_types,
        "elementCounts": element_counts,
        "totalElements": total,
        "diagram_id": diagram_id,
        "source_file": source_file
    }


def make_interaction_json(name, key, lifelines, messages, fragments):
    """Create a UML interaction (sequence diagram) JSON object."""
    return {
        "name": name,
        "key": key,
        "type": "interaction",
        "lifelines": lifelines,
        "messages": messages,
        "fragments": fragments
    }


# ===========================================================================
# DATA DEFINITIONS - All from trainticket-fork source code analysis
# ===========================================================================

# ---- ts-auth-service (Port: 12340) ----
AUTH_SERVICE = {
    "id": "ttf-class-auth-service",
    "classes": {
        "User": {
            "fields": [
                ("userId", "UUID"), ("username", "String"),
                ("password", "String"), ("roles", "Set<String>")
            ],
            "methods": []
        },
        "AuthController": {
            "fields": [],
            "methods": [
                ("createDefaultUser", "Response", [("CreateUserInput", "HttpHeaders")])
            ]
        },
        "TokenService": {
            "fields": [],
            "methods": [
                ("createToken", "String", [("User",)]),
                ("verifyToken", "Boolean", [("String",)])
            ],
            "is_interface": True
        },
        "TokenServiceImpl": {
            "fields": [],
            "methods": [
                ("createToken", "String", [("User",)]),
                ("verifyToken", "Boolean", [("String",)])
            ],
            "implements": ["TokenService"]
        },
        "UserService": {
            "fields": [],
            "methods": [
                ("saveUser", "User", [("UserDto",)]),
                ("getAllUsers", "List<User>", []),
                ("deleteByUserId", "Response", [("UUID",)])
            ],
            "is_interface": True
        },
        "UserServiceImpl": {
            "fields": [],
            "methods": [
                ("saveUser", "User", [("UserDto",)]),
                ("getAllUsers", "List<User>", []),
                ("deleteByUserId", "Response", [("UUID",)])
            ],
            "implements": ["UserService"]
        },
        "UserRepository": {
            "fields": [],
            "methods": [
                ("findByUsername", "User", [("String",)]),
                ("deleteByUserId", "void", [("UUID",)])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("AuthController", "TokenService"),
        ("UserServiceImpl", "UserRepository"),
        ("TokenServiceImpl", "UserRepository")
    ]
}

# ---- ts-user-service (Port: 12342) ----
USER_SERVICE = {
    "id": "ttf-class-user-service",
    "classes": {
        "User": {
            "fields": [
                ("userId", "UUID"), ("userName", "String"),
                ("password", "String"), ("gender", "int"),
                ("documentType", "int"), ("documentNum", "String"),
                ("email", "String")
            ],
            "methods": []
        },
        "UserDto": {
            "fields": [
                ("userId", "UUID"), ("userName", "String"),
                ("password", "String"), ("gender", "int"),
                ("documentType", "int"), ("documentNum", "String"),
                ("email", "String")
            ],
            "methods": []
        },
        "UserController": {
            "fields": [],
            "methods": [
                ("getAllUser", "Response", [("HttpHeaders",)]),
                ("getUserByUserName", "Response", [("String", "HttpHeaders")]),
                ("getUserByUserId", "Response", [("String", "HttpHeaders")]),
                ("registerUser", "Response", [("UserDto", "HttpHeaders")]),
                ("deleteUserById", "Response", [("String", "HttpHeaders")]),
                ("updateUser", "Response", [("UserDto", "HttpHeaders")])
            ]
        },
        "UserService": {
            "fields": [],
            "methods": [
                ("saveUser", "Response", [("UserDto", "HttpHeaders")]),
                ("getAllUsers", "Response", [("HttpHeaders",)]),
                ("findByUserName", "Response", [("String", "HttpHeaders")]),
                ("findByUserId", "Response", [("String", "HttpHeaders")]),
                ("deleteUser", "Response", [("String", "HttpHeaders")]),
                ("updateUser", "Response", [("UserDto", "HttpHeaders")])
            ],
            "is_interface": True
        },
        "UserServiceImpl": {
            "fields": [],
            "methods": [
                ("saveUser", "Response", [("UserDto", "HttpHeaders")]),
                ("getAllUsers", "Response", [("HttpHeaders",)]),
                ("findByUserName", "Response", [("String", "HttpHeaders")]),
                ("findByUserId", "Response", [("String", "HttpHeaders")]),
                ("deleteUser", "Response", [("String", "HttpHeaders")]),
                ("updateUser", "Response", [("UserDto", "HttpHeaders")])
            ],
            "implements": ["UserService"],
            "calls": ["ts-auth-service"]
        },
        "UserRepository": {
            "fields": [],
            "methods": [
                ("findByUserName", "User", [("String",)]),
                ("findByUserId", "User", [("UUID",)]),
                ("deleteByUserId", "void", [("UUID",)])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("UserController", "UserService"),
        ("UserServiceImpl", "UserRepository")
    ]
}

# ---- ts-order-service (Port: 12031) ----
ORDER_SERVICE = {
    "id": "ttf-class-order-service",
    "classes": {
        "Order": {
            "fields": [
                ("id", "UUID"), ("boughtDate", "Date"), ("travelDate", "Date"),
                ("travelTime", "Date"), ("accountId", "UUID"),
                ("contactsName", "String"), ("documentType", "int"),
                ("contactsDocumentNumber", "String"), ("trainNumber", "String"),
                ("coachNumber", "int"), ("seatClass", "int"),
                ("seatNumber", "String"), ("from", "String"), ("to", "String"),
                ("status", "int"), ("price", "String")
            ],
            "methods": []
        },
        "OrderController": {
            "fields": [],
            "methods": [
                ("getTicketListByDateAndTripId", "Response", [("Seat", "HttpHeaders")]),
                ("createNewOrder", "Response", [("Order", "HttpHeaders")]),
                ("addcreateNewOrder", "Response", [("Order", "HttpHeaders")]),
                ("queryOrders", "Response", [("OrderInfo", "HttpHeaders")]),
                ("queryOrdersForRefresh", "Response", [("OrderInfo", "HttpHeaders")]),
                ("calculateSoldTicket", "Response", [("String", "String", "HttpHeaders")]),
                ("getOrderPrice", "Response", [("String", "HttpHeaders")]),
                ("payOrder", "Response", [("String", "HttpHeaders")]),
                ("getOrderById", "Response", [("String", "HttpHeaders")]),
                ("modifyOrder", "Response", [("String", "int", "HttpHeaders")]),
                ("securityInfoCheck", "Response", [("String", "String", "HttpHeaders")]),
                ("saveOrderInfo", "Response", [("Order", "HttpHeaders")]),
                ("updateOrder", "Response", [("Order", "HttpHeaders")]),
                ("deleteOrder", "Response", [("String", "HttpHeaders")]),
                ("findAllOrder", "Response", [("HttpHeaders",)])
            ]
        },
        "OrderService": {
            "fields": [],
            "methods": [
                ("findOrderById", "Response", [("UUID", "HttpHeaders")]),
                ("create", "Response", [("Order", "HttpHeaders")]),
                ("saveChanges", "Response", [("Order", "HttpHeaders")]),
                ("cancelOrder", "Response", [("UUID", "HttpHeaders")]),
                ("queryOrders", "Response", [("OrderInfo", "String", "HttpHeaders")]),
                ("queryOrdersForRefresh", "Response", [("OrderInfo", "String", "HttpHeaders")]),
                ("alterOrder", "Response", [("Order", "HttpHeaders")]),
                ("queryAlreadySoldOrders", "Response", [("Date", "String", "HttpHeaders")]),
                ("getAllOrders", "Response", [("HttpHeaders",)]),
                ("modifyOrder", "Response", [("String", "int", "HttpHeaders")]),
                ("getOrderPrice", "Response", [("String", "HttpHeaders")]),
                ("payOrder", "Response", [("String", "HttpHeaders")]),
                ("getOrderById", "Response", [("String", "HttpHeaders")]),
                ("checkSecurityAboutOrder", "Response", [("Date", "String", "HttpHeaders")]),
                ("initOrder", "Response", [("Order", "HttpHeaders")]),
                ("deleteOrder", "Response", [("String", "HttpHeaders")]),
                ("getSoldTickets", "Response", [("Seat", "HttpHeaders")]),
                ("addNewOrder", "Response", [("Order", "HttpHeaders")]),
                ("updateOrder", "Response", [("Order", "HttpHeaders")])
            ],
            "is_interface": True
        },
        "OrderServiceImpl": {
            "fields": [],
            "methods": [
                ("findOrderById", "Response", [("UUID", "HttpHeaders")]),
                ("create", "Response", [("Order", "HttpHeaders")]),
                ("saveChanges", "Response", [("Order", "HttpHeaders")]),
                ("cancelOrder", "Response", [("UUID", "HttpHeaders")]),
                ("queryOrders", "Response", [("OrderInfo", "String", "HttpHeaders")]),
                ("getAllOrders", "Response", [("HttpHeaders",)]),
                ("getSoldTickets", "Response", [("Seat", "HttpHeaders")])
            ],
            "implements": ["OrderService"],
            "calls": ["ts-station-service"]
        },
        "OrderRepository": {
            "fields": [],
            "methods": [
                ("findByAccountId", "List<Order>", [("UUID",)]),
                ("findByTravelDateAndTrainNumber", "List<Order>", [("Date", "String")]),
                ("findById", "Order", [("UUID",)]),
                ("deleteById", "void", [("UUID",)])
            ],
            "is_interface": True
        },
        "Seat": {
            "fields": [
                ("travelDate", "Date"), ("trainNumber", "String"),
                ("startStation", "String"), ("destStation", "String"),
                ("seatType", "int"), ("totalNum", "int"),
                ("stations", "List<String>")
            ],
            "methods": []
        },
        "OrderInfo": {
            "fields": [
                ("loginId", "String"), ("travelDateStart", "String"),
                ("travelDateEnd", "String"), ("boughtDateStart", "String"),
                ("boughtDateEnd", "String"), ("state", "int"),
                ("enableTravelDateQuery", "boolean"),
                ("enableBoughtDateQuery", "boolean"),
                ("enableStateQuery", "boolean")
            ],
            "methods": []
        }
    },
    "dependencies": [
        ("OrderController", "OrderService"),
        ("OrderServiceImpl", "OrderRepository")
    ]
}

# ---- ts-order-other-service (Port: 12032) ----
ORDER_OTHER_SERVICE = {
    "id": "ttf-class-order-other-service",
    "classes": {
        "Order": {
            "fields": [
                ("id", "UUID"), ("boughtDate", "Date"), ("travelDate", "Date"),
                ("travelTime", "Date"), ("accountId", "UUID"),
                ("contactsName", "String"), ("documentType", "int"),
                ("contactsDocumentNumber", "String"), ("trainNumber", "String"),
                ("coachNumber", "int"), ("seatClass", "int"),
                ("seatNumber", "String"), ("from", "String"), ("to", "String"),
                ("status", "int"), ("price", "String")
            ],
            "methods": []
        },
        "OrderOtherController": {
            "fields": [],
            "methods": [
                ("getTicketListByDateAndTripId", "Response", [("Seat", "HttpHeaders")]),
                ("createNewOrder", "Response", [("Order", "HttpHeaders")]),
                ("queryOrders", "Response", [("OrderInfo", "HttpHeaders")]),
                ("calculateSoldTicket", "Response", [("String", "String", "HttpHeaders")]),
                ("getOrderPrice", "Response", [("String", "HttpHeaders")]),
                ("payOrder", "Response", [("String", "HttpHeaders")]),
                ("getOrderById", "Response", [("String", "HttpHeaders")]),
                ("modifyOrder", "Response", [("String", "int", "HttpHeaders")]),
                ("securityInfoCheck", "Response", [("String", "String", "HttpHeaders")]),
                ("saveOrderInfo", "Response", [("Order", "HttpHeaders")]),
                ("deleteOrder", "Response", [("String", "HttpHeaders")]),
                ("findAllOrder", "Response", [("HttpHeaders",)])
            ]
        },
        "OrderOtherServiceImpl": {
            "fields": [],
            "methods": [
                ("findOrderById", "Response", [("UUID", "HttpHeaders")]),
                ("create", "Response", [("Order", "HttpHeaders")]),
                ("getAllOrders", "Response", [("HttpHeaders",)]),
                ("getSoldTickets", "Response", [("Seat", "HttpHeaders")])
            ],
            "implements": ["OrderOtherService"],
            "calls": ["ts-station-service"]
        },
        "OrderOtherRepository": {
            "fields": [],
            "methods": [
                ("findByAccountId", "List<Order>", [("UUID",)]),
                ("findByTravelDateAndTrainNumber", "List<Order>", [("Date", "String")]),
                ("findById", "Order", [("UUID",)])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("OrderOtherController", "OrderOtherServiceImpl"),
        ("OrderOtherServiceImpl", "OrderOtherRepository")
    ]
}

# ---- ts-travel-service (Port: 12346) ----
TRAVEL_SERVICE = {
    "id": "ttf-class-travel-service",
    "classes": {
        "Trip": {
            "fields": [
                ("tripId", "TripId"), ("trainTypeId", "String"),
                ("routeId", "String"), ("startingStationId", "String"),
                ("stationsId", "String"), ("terminalStationId", "String"),
                ("startingTime", "Date"), ("endTime", "Date")
            ],
            "methods": []
        },
        "TripId": {
            "fields": [("type", "Type"), ("number", "String")],
            "methods": []
        },
        "TravelResult": {
            "fields": [
                ("status", "boolean"), ("percent", "double"),
                ("trainType", "TrainType"), ("prices", "Map<String,String>"),
                ("message", "String")
            ],
            "methods": []
        },
        "TripAllDetail": {
            "fields": [
                ("tripResponse", "TripResponse"), ("trip", "Trip")
            ],
            "methods": []
        },
        "TripResponse": {
            "fields": [
                ("tripId", "TripId"), ("trainTypeId", "String"),
                ("startingStation", "String"), ("terminalStation", "String"),
                ("startingTime", "Date"), ("endTime", "Date"),
                ("economyClass", "int"), ("confortClass", "int"),
                ("priceForEconomyClass", "String"), ("priceForConfortClass", "String")
            ],
            "methods": []
        },
        "Travel": {
            "fields": [
                ("trip", "Trip"), ("startingPlace", "String"),
                ("endPlace", "String"), ("departureTime", "Date")
            ],
            "methods": []
        },
        "TravelController": {
            "fields": [],
            "methods": [
                ("getTrainTypeByTripId", "Response", [("String", "HttpHeaders")]),
                ("getRouteByTripId", "Response", [("String", "HttpHeaders")]),
                ("getTripsByRouteId", "Response", [("List<String>", "HttpHeaders")]),
                ("create", "Response", [("TravelInfo", "HttpHeaders")]),
                ("retrieve", "Response", [("String", "HttpHeaders")]),
                ("update", "Response", [("TravelInfo", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("query", "Response", [("TripInfo", "HttpHeaders")]),
                ("getTripAllDetailInfo", "Response", [("TripAllDetailInfo", "HttpHeaders")])
            ]
        },
        "TravelService": {
            "fields": [],
            "methods": [
                ("create", "Response", [("TravelInfo", "HttpHeaders")]),
                ("retrieve", "Response", [("String", "HttpHeaders")]),
                ("update", "Response", [("TravelInfo", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("query", "Response", [("TripInfo", "HttpHeaders")]),
                ("getTripAllDetailInfo", "Response", [("TripAllDetailInfo", "HttpHeaders")])
            ],
            "is_interface": True
        },
        "TravelServiceImpl": {
            "fields": [],
            "methods": [
                ("create", "Response", [("TravelInfo", "HttpHeaders")]),
                ("query", "Response", [("TripInfo", "HttpHeaders")]),
                ("getTripAllDetailInfo", "Response", [("TripAllDetailInfo", "HttpHeaders")]),
                ("queryForTravel", "TravelResult", [("Travel", "HttpHeaders")]),
                ("queryForStationId", "String", [("String", "HttpHeaders")])
            ],
            "implements": ["TravelService"],
            "calls": ["ts-ticketinfo-service", "ts-order-service", "ts-train-service",
                       "ts-route-service", "ts-seat-service"]
        },
        "TripRepository": {
            "fields": [],
            "methods": [
                ("findByTripId", "Trip", [("TripId",)]),
                ("findAll", "List<Trip>", [])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("TravelController", "TravelService"),
        ("TravelServiceImpl", "TripRepository")
    ]
}

# ---- ts-travel2-service (Port: 16346) ----
TRAVEL2_SERVICE = {
    "id": "ttf-class-travel2-service",
    "classes": {
        "Trip": {
            "fields": [
                ("tripId", "TripId"), ("trainTypeId", "String"),
                ("routeId", "String"), ("startingStationId", "String"),
                ("stationsId", "String"), ("terminalStationId", "String"),
                ("startingTime", "Date"), ("endTime", "Date")
            ],
            "methods": []
        },
        "Travel2Controller": {
            "fields": [],
            "methods": [
                ("getTrainTypeByTripId", "Response", [("String", "HttpHeaders")]),
                ("getRouteByTripId", "Response", [("String", "HttpHeaders")]),
                ("getTripsByRouteId", "Response", [("List<String>", "HttpHeaders")]),
                ("create", "Response", [("TravelInfo", "HttpHeaders")]),
                ("query", "Response", [("TripInfo", "HttpHeaders")]),
                ("getTripAllDetailInfo", "Response", [("TripAllDetailInfo", "HttpHeaders")])
            ]
        },
        "Travel2ServiceImpl": {
            "fields": [],
            "methods": [
                ("create", "Response", [("TravelInfo", "HttpHeaders")]),
                ("query", "Response", [("TripInfo", "HttpHeaders")]),
                ("getTripAllDetailInfo", "Response", [("TripAllDetailInfo", "HttpHeaders")])
            ],
            "implements": ["Travel2Service"],
            "calls": ["ts-ticketinfo-service", "ts-order-other-service",
                       "ts-train-service", "ts-route-service", "ts-seat-service"]
        }
    },
    "dependencies": [
        ("Travel2Controller", "Travel2ServiceImpl")
    ]
}

# ---- ts-ticketinfo-service (Port: 15681) - NEW in fork ----
TICKETINFO_SERVICE = {
    "id": "ttf-class-ticketinfo-service",
    "classes": {
        "Travel": {
            "fields": [
                ("trip", "Trip"), ("startingPlace", "String"),
                ("endPlace", "String"), ("departureTime", "Date")
            ],
            "methods": []
        },
        "TravelResult": {
            "fields": [
                ("status", "boolean"), ("percent", "double"),
                ("trainType", "TrainType"), ("prices", "Map<String,String>"),
                ("message", "String")
            ],
            "methods": []
        },
        "Trip": {
            "fields": [
                ("tripId", "TripId"), ("trainTypeId", "String"),
                ("routeId", "String")
            ],
            "methods": []
        },
        "TripId": {
            "fields": [("type", "Type"), ("number", "String")],
            "methods": []
        },
        "TrainType": {
            "fields": [
                ("id", "String"), ("economyClass", "int"),
                ("confortClass", "int"), ("averageSpeed", "int")
            ],
            "methods": []
        },
        "TicketInfoController": {
            "fields": [],
            "methods": [
                ("queryForTravel", "Response", [("Travel", "HttpHeaders")]),
                ("queryForStationId", "Response", [("String", "HttpHeaders")])
            ]
        },
        "TicketInfoService": {
            "fields": [],
            "methods": [
                ("queryForTravel", "Response", [("Travel", "HttpHeaders")]),
                ("queryForStationId", "Response", [("String", "HttpHeaders")])
            ],
            "is_interface": True
        },
        "TicketInfoServiceImpl": {
            "fields": [],
            "methods": [
                ("queryForTravel", "Response", [("Travel", "HttpHeaders")]),
                ("queryForStationId", "Response", [("String", "HttpHeaders")])
            ],
            "implements": ["TicketInfoService"],
            "calls": ["ts-basic-service"]
        }
    },
    "dependencies": [
        ("TicketInfoController", "TicketInfoService"),
        ("TicketInfoServiceImpl", "TicketInfoService")
    ]
}

# ---- ts-basic-service (Port: 15680) ----
BASIC_SERVICE = {
    "id": "ttf-class-basic-service",
    "classes": {
        "Travel": {
            "fields": [
                ("trip", "Trip"), ("startingPlace", "String"),
                ("endPlace", "String"), ("departureTime", "Date")
            ],
            "methods": []
        },
        "TravelResult": {
            "fields": [
                ("status", "boolean"), ("percent", "double"),
                ("trainType", "TrainType"), ("prices", "Map<String,String>")
            ],
            "methods": []
        },
        "BasicController": {
            "fields": [],
            "methods": [
                ("queryForTravel", "Response", [("Travel", "HttpHeaders")]),
                ("queryForStationId", "Response", [("String", "HttpHeaders")])
            ]
        },
        "BasicService": {
            "fields": [],
            "methods": [
                ("queryForTravel", "Response", [("Travel", "HttpHeaders")]),
                ("queryForStationId", "Response", [("String", "HttpHeaders")])
            ],
            "is_interface": True
        },
        "BasicServiceImpl": {
            "fields": [],
            "methods": [
                ("queryForTravel", "Response", [("Travel", "HttpHeaders")]),
                ("queryForStationId", "Response", [("String", "HttpHeaders")]),
                ("queryTrainType", "TrainType", [("String", "HttpHeaders")]),
                ("queryRoute", "Route", [("String", "HttpHeaders")])
            ],
            "implements": ["BasicService"],
            "calls": ["ts-train-service", "ts-route-service",
                       "ts-station-service", "ts-price-service"]
        }
    },
    "dependencies": [
        ("BasicController", "BasicService"),
        ("BasicServiceImpl", "BasicService")
    ]
}

# ---- ts-station-service (Port: 12345) ----
STATION_SERVICE = {
    "id": "ttf-class-station-service",
    "classes": {
        "Station": {
            "fields": [
                ("id", "String"), ("name", "String"), ("stayTime", "int")
            ],
            "methods": []
        },
        "StationController": {
            "fields": [],
            "methods": [
                ("create", "Response", [("Station", "HttpHeaders")]),
                ("update", "Response", [("Station", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("query", "Response", [("HttpHeaders",)]),
                ("queryById", "Response", [("String", "HttpHeaders")]),
                ("queryByName", "Response", [("String", "HttpHeaders")]),
                ("queryForIdBatch", "Response", [("List<String>", "HttpHeaders")])
            ]
        },
        "StationService": {
            "fields": [],
            "methods": [
                ("create", "Response", [("Station", "HttpHeaders")]),
                ("update", "Response", [("Station", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("query", "Response", [("HttpHeaders",)]),
                ("queryById", "Response", [("String", "HttpHeaders")]),
                ("queryByName", "Response", [("String", "HttpHeaders")])
            ],
            "is_interface": True
        },
        "StationServiceImpl": {
            "fields": [],
            "methods": [
                ("create", "Response", [("Station", "HttpHeaders")]),
                ("update", "Response", [("Station", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("query", "Response", [("HttpHeaders",)])
            ],
            "implements": ["StationService"]
        },
        "StationRepository": {
            "fields": [],
            "methods": [
                ("findByName", "Station", [("String",)]),
                ("findById", "Station", [("String",)])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("StationController", "StationService"),
        ("StationServiceImpl", "StationRepository")
    ]
}

# ---- ts-train-service (Port: 14567) ----
TRAIN_SERVICE = {
    "id": "ttf-class-train-service",
    "classes": {
        "TrainType": {
            "fields": [
                ("id", "String"), ("economyClass", "int"),
                ("confortClass", "int"), ("averageSpeed", "int")
            ],
            "methods": []
        },
        "TrainController": {
            "fields": [],
            "methods": [
                ("create", "Response", [("TrainType", "HttpHeaders")]),
                ("retrieve", "Response", [("String", "HttpHeaders")]),
                ("update", "Response", [("TrainType", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("query", "Response", [("HttpHeaders",)])
            ]
        },
        "TrainService": {
            "fields": [],
            "methods": [
                ("create", "Response", [("TrainType", "HttpHeaders")]),
                ("retrieve", "Response", [("String", "HttpHeaders")]),
                ("update", "Response", [("TrainType", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("query", "Response", [("HttpHeaders",)])
            ],
            "is_interface": True
        },
        "TrainServiceImpl": {
            "fields": [],
            "methods": [
                ("create", "Response", [("TrainType", "HttpHeaders")]),
                ("retrieve", "Response", [("String", "HttpHeaders")]),
                ("update", "Response", [("TrainType", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("query", "Response", [("HttpHeaders",)])
            ],
            "implements": ["TrainService"]
        },
        "TrainTypeRepository": {
            "fields": [],
            "methods": [
                ("findById", "TrainType", [("String",)]),
                ("findAll", "List<TrainType>", [])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("TrainController", "TrainService"),
        ("TrainServiceImpl", "TrainTypeRepository")
    ]
}

# ---- ts-route-service (Port: 11178) ----
ROUTE_SERVICE = {
    "id": "ttf-class-route-service",
    "classes": {
        "Route": {
            "fields": [
                ("id", "String"), ("stations", "List<String>"),
                ("distances", "List<Integer>"), ("startStationId", "String"),
                ("terminalStationId", "String")
            ],
            "methods": []
        },
        "RouteInfo": {
            "fields": [
                ("id", "String"), ("startStation", "String"),
                ("endStation", "String"), ("stationList", "String"),
                ("distanceList", "String")
            ],
            "methods": []
        },
        "RouteController": {
            "fields": [],
            "methods": [
                ("createAndModifyRoute", "Response", [("RouteInfo", "HttpHeaders")]),
                ("deleteRoute", "Response", [("String", "HttpHeaders")]),
                ("queryById", "Response", [("String", "HttpHeaders")]),
                ("queryAll", "Response", [("HttpHeaders",)]),
                ("queryByStartAndTerminal", "Response", [("String", "String", "HttpHeaders")])
            ]
        },
        "RouteServiceImpl": {
            "fields": [],
            "methods": [
                ("createAndModify", "Response", [("RouteInfo", "HttpHeaders")]),
                ("deleteRoute", "Response", [("String", "HttpHeaders")]),
                ("getRouteById", "Response", [("String", "HttpHeaders")]),
                ("getAllRoutes", "Response", [("HttpHeaders",)])
            ],
            "implements": ["RouteService"]
        },
        "RouteRepository": {
            "fields": [],
            "methods": [
                ("findById", "Route", [("String",)]),
                ("findAll", "List<Route>", [])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("RouteController", "RouteServiceImpl"),
        ("RouteServiceImpl", "RouteRepository")
    ]
}

# ---- ts-preserve-service (Port: 14568) ----
PRESERVE_SERVICE = {
    "id": "ttf-class-preserve-service",
    "classes": {
        "OrderTicketsInfo": {
            "fields": [
                ("accountId", "String"), ("contactsId", "String"),
                ("tripId", "String"), ("seatType", "int"),
                ("date", "Date"), ("from", "String"), ("to", "String"),
                ("assurance", "int"), ("foodType", "int"),
                ("foodName", "String"), ("foodPrice", "double"),
                ("stationName", "String"), ("storeName", "String"),
                ("handleDate", "String"), ("consigneeName", "String"),
                ("consigneePhone", "String"), ("consigneeWeight", "double"),
                ("isWithin", "boolean")
            ],
            "methods": []
        },
        "PreserveController": {
            "fields": [],
            "methods": [
                ("preserve", "Response", [("OrderTicketsInfo", "HttpHeaders")])
            ]
        },
        "PreserveService": {
            "fields": [],
            "methods": [
                ("preserve", "Response", [("OrderTicketsInfo", "HttpHeaders")])
            ],
            "is_interface": True
        },
        "PreserveServiceImpl": {
            "fields": [],
            "methods": [
                ("preserve", "Response", [("OrderTicketsInfo", "HttpHeaders")]),
                ("getTickets", "TravelResult", [("Travel", "HttpHeaders")]),
                ("distributeSeat", "Ticket", [("Seat", "HttpHeaders")]),
                ("sendEmail", "boolean", [("NotifyInfo", "HttpHeaders")]),
                ("getAccount", "User", [("String", "HttpHeaders")]),
                ("addAssurance", "Response", [("int", "String", "HttpHeaders")]),
                ("queryForStationId", "String", [("String", "HttpHeaders")]),
                ("checkSecurity", "Response", [("String", "HttpHeaders")]),
                ("getTripAllDetailInfo", "TripAllDetail", [("TripAllDetailInfo", "HttpHeaders")]),
                ("getContacts", "Contacts", [("String", "HttpHeaders")]),
                ("createOrder", "Order", [("Order", "HttpHeaders")]),
                ("createFoodOrder", "Response", [("FoodOrder", "HttpHeaders")]),
                ("createConsign", "Response", [("Consign", "HttpHeaders")])
            ],
            "implements": ["PreserveService"],
            "calls": ["ts-ticketinfo-service", "ts-seat-service",
                       "ts-notification-service", "ts-user-service",
                       "ts-assurance-service", "ts-station-service",
                       "ts-security-service", "ts-travel-service",
                       "ts-contacts-service", "ts-order-service",
                       "ts-food-service", "ts-consign-service"]
        }
    },
    "dependencies": [
        ("PreserveController", "PreserveService"),
        ("PreserveServiceImpl", "PreserveService")
    ]
}

# ---- ts-preserve-other-service (Port: 14569) ----
PRESERVE_OTHER_SERVICE = {
    "id": "ttf-class-preserve-other-service",
    "classes": {
        "OrderTicketsInfo": {
            "fields": [
                ("accountId", "String"), ("contactsId", "String"),
                ("tripId", "String"), ("seatType", "int"),
                ("date", "Date"), ("from", "String"), ("to", "String"),
                ("assurance", "int"), ("foodType", "int"),
                ("foodName", "String"), ("foodPrice", "double"),
                ("stationName", "String"), ("storeName", "String"),
                ("handleDate", "String"), ("consigneeName", "String"),
                ("consigneePhone", "String"), ("consigneeWeight", "double"),
                ("isWithin", "boolean")
            ],
            "methods": []
        },
        "PreserveOtherController": {
            "fields": [],
            "methods": [
                ("preserve", "Response", [("OrderTicketsInfo", "HttpHeaders")])
            ]
        },
        "PreserveOtherServiceImpl": {
            "fields": [],
            "methods": [
                ("preserve", "Response", [("OrderTicketsInfo", "HttpHeaders")])
            ],
            "implements": ["PreserveOtherService"],
            "calls": ["ts-ticketinfo-service", "ts-seat-service",
                       "ts-notification-service", "ts-user-service",
                       "ts-assurance-service", "ts-station-service",
                       "ts-security-service", "ts-travel2-service",
                       "ts-contacts-service", "ts-order-other-service",
                       "ts-food-service", "ts-consign-service"]
        }
    },
    "dependencies": [
        ("PreserveOtherController", "PreserveOtherServiceImpl")
    ]
}

# ---- ts-seat-service (Port: 18898) ----
SEAT_SERVICE = {
    "id": "ttf-class-seat-service",
    "classes": {
        "Seat": {
            "fields": [
                ("travelDate", "Date"), ("trainNumber", "String"),
                ("startStation", "String"), ("destStation", "String"),
                ("seatType", "int"), ("totalNum", "int"),
                ("stations", "List<String>")
            ],
            "methods": []
        },
        "LeftTicketInfo": {
            "fields": [
                ("soldTickets", "Set<Ticket>")
            ],
            "methods": []
        },
        "Ticket": {
            "fields": [
                ("seatNo", "int"), ("startStation", "String"),
                ("destStation", "String")
            ],
            "methods": []
        },
        "SeatController": {
            "fields": [],
            "methods": [
                ("distributeSeat", "Response", [("Seat", "HttpHeaders")]),
                ("getLeftTicketOfInterval", "Response", [("Seat", "HttpHeaders")])
            ]
        },
        "SeatService": {
            "fields": [],
            "methods": [
                ("distributeSeat", "Response", [("Seat", "HttpHeaders")]),
                ("getLeftTicketOfInterval", "Response", [("Seat", "HttpHeaders")])
            ],
            "is_interface": True
        },
        "SeatServiceImpl": {
            "fields": [],
            "methods": [
                ("distributeSeat", "Response", [("Seat", "HttpHeaders")]),
                ("getLeftTicketOfInterval", "Response", [("Seat", "HttpHeaders")])
            ],
            "implements": ["SeatService"],
            "calls": ["ts-travel-service", "ts-travel2-service",
                       "ts-order-service", "ts-order-other-service",
                       "ts-config-service"]
        }
    },
    "dependencies": [
        ("SeatController", "SeatService"),
        ("SeatServiceImpl", "SeatService")
    ]
}

# ---- ts-price-service (Port: 16579) ----
PRICE_SERVICE = {
    "id": "ttf-class-price-service",
    "classes": {
        "PriceConfig": {
            "fields": [
                ("id", "UUID"), ("trainType", "String"),
                ("routeId", "String"), ("basicPriceRate", "double"),
                ("firstClassPriceRate", "double")
            ],
            "methods": []
        },
        "PriceController": {
            "fields": [],
            "methods": [
                ("create", "Response", [("PriceConfig", "HttpHeaders")]),
                ("findByRouteIdAndTrainType", "Response", [("String", "String", "HttpHeaders")]),
                ("findById", "Response", [("String", "HttpHeaders")]),
                ("findAllPriceConfig", "Response", [("HttpHeaders",)]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("update", "Response", [("PriceConfig", "HttpHeaders")])
            ]
        },
        "PriceServiceImpl": {
            "fields": [],
            "methods": [
                ("createNewPriceConfig", "Response", [("PriceConfig", "HttpHeaders")]),
                ("findById", "Response", [("String", "HttpHeaders")]),
                ("findByRouteIdAndTrainType", "Response", [("String", "String", "HttpHeaders")]),
                ("findAllPriceConfig", "Response", [("HttpHeaders",)]),
                ("deletePriceConfig", "Response", [("String", "HttpHeaders")])
            ],
            "implements": ["PriceService"]
        },
        "PriceConfigRepository": {
            "fields": [],
            "methods": [
                ("findById", "PriceConfig", [("UUID",)]),
                ("findByRouteIdAndTrainType", "PriceConfig", [("String", "String")])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("PriceController", "PriceServiceImpl"),
        ("PriceServiceImpl", "PriceConfigRepository")
    ]
}

# ---- ts-contacts-service (Port: 12347) ----
CONTACTS_SERVICE = {
    "id": "ttf-class-contacts-service",
    "classes": {
        "Contacts": {
            "fields": [
                ("id", "UUID"), ("accountId", "UUID"),
                ("name", "String"), ("documentType", "int"),
                ("documentNumber", "String"), ("phoneNumber", "String")
            ],
            "methods": []
        },
        "ContactsController": {
            "fields": [],
            "methods": [
                ("create", "Response", [("Contacts", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("modify", "Response", [("Contacts", "HttpHeaders")]),
                ("findByAccountId", "Response", [("String", "HttpHeaders")]),
                ("getContactsById", "Response", [("String", "HttpHeaders")]),
                ("getAllContacts", "Response", [("HttpHeaders",)])
            ]
        },
        "ContactsServiceImpl": {
            "fields": [],
            "methods": [
                ("create", "Response", [("Contacts", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("modify", "Response", [("Contacts", "HttpHeaders")]),
                ("findContactsByAccountId", "Response", [("UUID", "HttpHeaders")]),
                ("findContactsById", "Response", [("String", "HttpHeaders")]),
                ("getAllContacts", "Response", [("HttpHeaders",)])
            ],
            "implements": ["ContactsService"]
        },
        "ContactsRepository": {
            "fields": [],
            "methods": [
                ("findByAccountId", "List<Contacts>", [("UUID",)]),
                ("findById", "Contacts", [("UUID",)])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("ContactsController", "ContactsServiceImpl"),
        ("ContactsServiceImpl", "ContactsRepository")
    ]
}

# ---- ts-config-service (Port: 15679) ----
CONFIG_SERVICE = {
    "id": "ttf-class-config-service",
    "classes": {
        "Config": {
            "fields": [
                ("name", "String"), ("value", "String"),
                ("description", "String")
            ],
            "methods": []
        },
        "ConfigController": {
            "fields": [],
            "methods": [
                ("create", "Response", [("Config", "HttpHeaders")]),
                ("update", "Response", [("Config", "HttpHeaders")]),
                ("query", "Response", [("String", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("queryAll", "Response", [("HttpHeaders",)])
            ]
        },
        "ConfigServiceImpl": {
            "fields": [],
            "methods": [
                ("create", "Response", [("Config", "HttpHeaders")]),
                ("update", "Response", [("Config", "HttpHeaders")]),
                ("query", "Response", [("String", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("queryAll", "Response", [("HttpHeaders",)])
            ],
            "implements": ["ConfigService"]
        },
        "ConfigRepository": {
            "fields": [],
            "methods": [
                ("findByName", "Config", [("String",)])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("ConfigController", "ConfigServiceImpl"),
        ("ConfigServiceImpl", "ConfigRepository")
    ]
}

# ---- ts-security-service (Port: 11188) ----
SECURITY_SERVICE = {
    "id": "ttf-class-security-service",
    "classes": {
        "SecurityConfig": {
            "fields": [
                ("id", "UUID"), ("name", "String"),
                ("value", "String"), ("description", "String")
            ],
            "methods": []
        },
        "SecurityController": {
            "fields": [],
            "methods": [
                ("create", "Response", [("SecurityConfig", "HttpHeaders")]),
                ("update", "Response", [("SecurityConfig", "HttpHeaders")]),
                ("delete", "Response", [("String", "HttpHeaders")]),
                ("findAll", "Response", [("HttpHeaders",)]),
                ("check", "Response", [("String", "HttpHeaders")])
            ]
        },
        "SecurityServiceImpl": {
            "fields": [],
            "methods": [
                ("findAllSecurityConfig", "Response", [("HttpHeaders",)]),
                ("addNewSecurityConfig", "Response", [("SecurityConfig", "HttpHeaders")]),
                ("modifySecurityConfig", "Response", [("SecurityConfig", "HttpHeaders")]),
                ("deleteSecurityConfig", "Response", [("String", "HttpHeaders")]),
                ("check", "Response", [("String", "HttpHeaders")])
            ],
            "implements": ["SecurityService"],
            "calls": ["ts-order-service", "ts-order-other-service"]
        },
        "SecurityRepository": {
            "fields": [],
            "methods": [
                ("findByName", "SecurityConfig", [("String",)])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("SecurityController", "SecurityServiceImpl"),
        ("SecurityServiceImpl", "SecurityRepository")
    ]
}

# ---- ts-inside-payment-service (Port: 18673) ----
INSIDE_PAYMENT_SERVICE = {
    "id": "ttf-class-inside-payment-service",
    "classes": {
        "Payment": {
            "fields": [
                ("id", "String"), ("orderId", "String"),
                ("userId", "String"), ("price", "String")
            ],
            "methods": []
        },
        "Balance": {
            "fields": [
                ("id", "String"), ("userId", "String"),
                ("balance", "String")
            ],
            "methods": []
        },
        "InsidePaymentController": {
            "fields": [],
            "methods": [
                ("pay", "Response", [("PaymentInfo", "HttpHeaders")]),
                ("createAccount", "Response", [("AccountInfo", "HttpHeaders")]),
                ("addMoney", "Response", [("String", "String", "HttpHeaders")]),
                ("queryPayment", "Response", [("HttpHeaders",)]),
                ("queryAccount", "Response", [("HttpHeaders",)]),
                ("drawBack", "Response", [("String", "String", "HttpHeaders")])
            ]
        },
        "InsidePaymentServiceImpl": {
            "fields": [],
            "methods": [
                ("pay", "Response", [("PaymentInfo", "HttpHeaders")]),
                ("createAccount", "Response", [("AccountInfo", "HttpHeaders")]),
                ("addMoney", "Response", [("String", "String", "HttpHeaders")]),
                ("queryPayment", "Response", [("HttpHeaders",)]),
                ("drawBack", "Response", [("String", "String", "HttpHeaders")])
            ],
            "implements": ["InsidePaymentService"],
            "calls": ["ts-order-service", "ts-order-other-service",
                       "ts-payment-service"]
        }
    },
    "dependencies": [
        ("InsidePaymentController", "InsidePaymentServiceImpl")
    ]
}

# ---- ts-payment-service (Port: 19001) ----
PAYMENT_SERVICE = {
    "id": "ttf-class-payment-service",
    "classes": {
        "Payment": {
            "fields": [
                ("id", "String"), ("orderId", "String"),
                ("userId", "String"), ("price", "String")
            ],
            "methods": []
        },
        "Money": {
            "fields": [
                ("userId", "String"), ("money", "String")
            ],
            "methods": []
        },
        "PaymentController": {
            "fields": [],
            "methods": [
                ("pay", "Response", [("Payment", "HttpHeaders")]),
                ("addMoney", "Response", [("Payment", "HttpHeaders")]),
                ("query", "Response", [("HttpHeaders",)])
            ]
        },
        "PaymentServiceImpl": {
            "fields": [],
            "methods": [
                ("pay", "Response", [("Payment", "HttpHeaders")]),
                ("addMoney", "Response", [("Payment", "HttpHeaders")]),
                ("query", "Response", [("HttpHeaders",)])
            ],
            "implements": ["PaymentService"]
        },
        "PaymentRepository": {
            "fields": [],
            "methods": [
                ("findAll", "List<Payment>", [])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("PaymentController", "PaymentServiceImpl"),
        ("PaymentServiceImpl", "PaymentRepository")
    ]
}

# ---- ts-cancel-service (Port: 18885) ----
CANCEL_SERVICE = {
    "id": "ttf-class-cancel-service",
    "classes": {
        "CancelController": {
            "fields": [],
            "methods": [
                ("calculate", "Response", [("String", "HttpHeaders")]),
                ("cancelTicket", "Response", [("String", "String", "HttpHeaders")])
            ]
        },
        "CancelServiceImpl": {
            "fields": [],
            "methods": [
                ("cancelOrder", "Response", [("String", "String", "HttpHeaders")]),
                ("calculateRefund", "Response", [("String", "HttpHeaders")]),
                ("getOrderByIdFromOrder", "Response", [("String", "HttpHeaders")]),
                ("getOrderByIdFromOrderOther", "Response", [("String", "HttpHeaders")]),
                ("cancelFromOrder", "Response", [("Order", "HttpHeaders")]),
                ("cancelFromOtherOrder", "Response", [("Order", "HttpHeaders")]),
                ("drawbackMoney", "Response", [("String", "String", "HttpHeaders")]),
                ("getAccount", "User", [("String", "HttpHeaders")]),
                ("sendEmail", "boolean", [("NotifyInfo", "HttpHeaders")])
            ],
            "implements": ["CancelService"],
            "calls": ["ts-order-service", "ts-order-other-service",
                       "ts-inside-payment-service", "ts-user-service",
                       "ts-notification-service"]
        }
    },
    "dependencies": [
        ("CancelController", "CancelServiceImpl")
    ]
}

# ---- ts-rebook-service (Port: 18886) ----
REBOOK_SERVICE = {
    "id": "ttf-class-rebook-service",
    "classes": {
        "RebookInfo": {
            "fields": [
                ("loginId", "String"), ("orderId", "String"),
                ("oldTripId", "String"), ("tripId", "String"),
                ("seatType", "int"), ("date", "Date")
            ],
            "methods": []
        },
        "RebookController": {
            "fields": [],
            "methods": [
                ("rebook", "Response", [("RebookInfo", "HttpHeaders")]),
                ("payDifference", "Response", [("RebookInfo", "HttpHeaders")])
            ]
        },
        "RebookServiceImpl": {
            "fields": [],
            "methods": [
                ("rebook", "Response", [("RebookInfo", "HttpHeaders")]),
                ("payDifference", "Response", [("RebookInfo", "HttpHeaders")]),
                ("getOrderByIdFromOrder", "Order", [("String", "HttpHeaders")]),
                ("getOrderByIdFromOrderOther", "Order", [("String", "HttpHeaders")]),
                ("queryForStationName", "String", [("String", "HttpHeaders")]),
                ("getTripAllDetailInfo", "TripAllDetail", [("TripAllDetailInfo", "HttpHeaders")]),
                ("distributeSeat", "Ticket", [("Seat", "HttpHeaders")])
            ],
            "implements": ["RebookService"],
            "calls": ["ts-order-service", "ts-order-other-service",
                       "ts-seat-service", "ts-travel-service",
                       "ts-travel2-service", "ts-station-service",
                       "ts-inside-payment-service"]
        }
    },
    "dependencies": [
        ("RebookController", "RebookServiceImpl")
    ]
}

# ---- ts-assurance-service (Port: 18888) ----
ASSURANCE_SERVICE = {
    "id": "ttf-class-assurance-service",
    "classes": {
        "Assurance": {
            "fields": [
                ("id", "UUID"), ("orderId", "UUID"),
                ("typeIndex", "int"), ("typeName", "String"),
                ("typePrice", "double")
            ],
            "methods": []
        },
        "AssuranceType": {
            "fields": [
                ("index", "int"), ("name", "String"), ("price", "double")
            ],
            "methods": []
        },
        "AssuranceController": {
            "fields": [],
            "methods": [
                ("create", "Response", [("int", "String", "HttpHeaders")]),
                ("deleteById", "Response", [("String", "HttpHeaders")]),
                ("deleteByOrderId", "Response", [("String", "HttpHeaders")]),
                ("modify", "Response", [("String", "String", "int", "HttpHeaders")]),
                ("getById", "Response", [("String", "HttpHeaders")]),
                ("findAssuranceByOrderId", "Response", [("String", "HttpHeaders")]),
                ("findAll", "Response", [("HttpHeaders",)]),
                ("getAllAssuranceType", "Response", [("HttpHeaders",)])
            ]
        },
        "AssuranceServiceImpl": {
            "fields": [],
            "methods": [
                ("create", "Response", [("int", "String", "HttpHeaders")]),
                ("deleteById", "Response", [("UUID", "HttpHeaders")]),
                ("deleteByOrderId", "Response", [("UUID", "HttpHeaders")]),
                ("modify", "Response", [("UUID", "UUID", "int", "HttpHeaders")]),
                ("getById", "Response", [("UUID", "HttpHeaders")]),
                ("findAssuranceByOrderId", "Response", [("UUID", "HttpHeaders")]),
                ("findAll", "Response", [("HttpHeaders",)]),
                ("getAllAssuranceType", "Response", [("HttpHeaders",)])
            ],
            "implements": ["AssuranceService"]
        },
        "AssuranceRepository": {
            "fields": [],
            "methods": [
                ("findById", "Assurance", [("UUID",)]),
                ("findByOrderId", "Assurance", [("UUID",)]),
                ("findAll", "List<Assurance>", [])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("AssuranceController", "AssuranceServiceImpl"),
        ("AssuranceServiceImpl", "AssuranceRepository")
    ]
}

# ---- ts-notification-service (Port: 17853) ----
NOTIFICATION_SERVICE = {
    "id": "ttf-class-notification-service",
    "classes": {
        "NotifyInfo": {
            "fields": [
                ("id", "UUID"), ("sendStatus", "boolean"),
                ("email", "String"), ("orderNumber", "String"),
                ("username", "String"), ("startingPlace", "String"),
                ("endPlace", "String"), ("startingTime", "String"),
                ("date", "String"), ("seatClass", "String"),
                ("seatNumber", "String"), ("price", "String")
            ],
            "methods": []
        },
        "NotificationController": {
            "fields": [],
            "methods": [
                ("preserve_success", "boolean", [("NotifyInfo", "HttpHeaders")]),
                ("order_cancel_success", "boolean", [("NotifyInfo", "HttpHeaders")])
            ]
        },
        "NotificationServiceImpl": {
            "fields": [],
            "methods": [
                ("preserveSuccess", "boolean", [("NotifyInfo", "HttpHeaders")]),
                ("orderCancelSuccess", "boolean", [("NotifyInfo", "HttpHeaders")])
            ],
            "implements": ["NotificationService"]
        }
    },
    "dependencies": [
        ("NotificationController", "NotificationServiceImpl")
    ]
}

# ---- ts-execute-service (Port: 12386) ----
EXECUTE_SERVICE = {
    "id": "ttf-class-execute-service",
    "classes": {
        "ExecuteController": {
            "fields": [],
            "methods": [
                ("executeTicket", "Response", [("String", "HttpHeaders")]),
                ("collectTicket", "Response", [("String", "HttpHeaders")])
            ]
        },
        "ExecuteServiceImpl": {
            "fields": [],
            "methods": [
                ("ticketExecute", "Response", [("String", "HttpHeaders")]),
                ("ticketCollect", "Response", [("String", "HttpHeaders")])
            ],
            "implements": ["ExecuteService"],
            "calls": ["ts-order-service", "ts-order-other-service"]
        }
    },
    "dependencies": [
        ("ExecuteController", "ExecuteServiceImpl")
    ]
}

# ---- ts-food-service (Port: 18856) ----
FOOD_SERVICE = {
    "id": "ttf-class-food-service",
    "classes": {
        "FoodOrder": {
            "fields": [
                ("id", "UUID"), ("orderId", "UUID"),
                ("foodType", "int"), ("foodName", "String"),
                ("price", "double"), ("stationName", "String"),
                ("storeName", "String")
            ],
            "methods": []
        },
        "AllTripFood": {
            "fields": [
                ("tripId", "String"), ("foodStoreListMap", "Map<String,List<FoodStore>>"),
                ("trainFoodList", "List<TrainFood>")
            ],
            "methods": []
        },
        "FoodController": {
            "fields": [],
            "methods": [
                ("createFoodOrder", "Response", [("FoodOrder", "HttpHeaders")]),
                ("deleteFoodOrder", "Response", [("String", "HttpHeaders")]),
                ("updateFoodOrder", "Response", [("FoodOrder", "HttpHeaders")]),
                ("findByOrderId", "Response", [("String", "HttpHeaders")]),
                ("findAllFoodOrder", "Response", [("HttpHeaders",)]),
                ("getAllFood", "Response", [("String", "String", "HttpHeaders")])
            ]
        },
        "FoodServiceImpl": {
            "fields": [],
            "methods": [
                ("createFoodOrder", "Response", [("FoodOrder", "HttpHeaders")]),
                ("deleteFoodOrder", "Response", [("String", "HttpHeaders")]),
                ("updateFoodOrder", "Response", [("FoodOrder", "HttpHeaders")]),
                ("findByOrderId", "Response", [("String", "HttpHeaders")]),
                ("findAllFoodOrder", "Response", [("HttpHeaders",)]),
                ("getAllFood", "Response", [("String", "String", "HttpHeaders")])
            ],
            "implements": ["FoodService"],
            "calls": ["ts-food-map-service", "ts-station-service",
                       "ts-travel-service"]
        },
        "FoodOrderRepository": {
            "fields": [],
            "methods": [
                ("findByOrderId", "FoodOrder", [("UUID",)]),
                ("findAll", "List<FoodOrder>", [])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("FoodController", "FoodServiceImpl"),
        ("FoodServiceImpl", "FoodOrderRepository")
    ]
}

# ---- ts-food-map-service (NEW in fork) ----
FOOD_MAP_SERVICE = {
    "id": "ttf-class-food-map-service",
    "classes": {
        "FoodStore": {
            "fields": [
                ("id", "UUID"), ("stationId", "String"),
                ("storeName", "String"), ("telephone", "String"),
                ("businessTime", "String"), ("deliveryFee", "double"),
                ("foodList", "List<Food>")
            ],
            "methods": []
        },
        "TrainFood": {
            "fields": [
                ("id", "UUID"), ("tripId", "String"),
                ("foodList", "List<Food>")
            ],
            "methods": []
        },
        "Food": {
            "fields": [
                ("foodName", "String"), ("price", "double")
            ],
            "methods": []
        },
        "FoodStoreController": {
            "fields": [],
            "methods": [
                ("getAllFoodStores", "Response", [("HttpHeaders",)]),
                ("getFoodStoresByStationId", "Response", [("String", "HttpHeaders")]),
                ("getFoodStoresByStationIds", "Response", [("List<String>", "HttpHeaders")])
            ]
        },
        "TrainFoodController": {
            "fields": [],
            "methods": [
                ("getAllTrainFood", "Response", [("HttpHeaders",)]),
                ("getTrainFoodByTripId", "Response", [("String", "HttpHeaders")])
            ]
        },
        "FoodMapServiceImpl": {
            "fields": [],
            "methods": [
                ("createFoodStore", "Response", [("FoodStore", "HttpHeaders")]),
                ("createTrainFood", "Response", [("TrainFood", "HttpHeaders")]),
                ("listFoodStores", "Response", [("HttpHeaders",)]),
                ("listTrainFood", "Response", [("HttpHeaders",)]),
                ("listFoodStoresByStationId", "Response", [("String", "HttpHeaders")]),
                ("listTrainFoodByTripId", "Response", [("String", "HttpHeaders")]),
                ("getFoodStoresByStationIds", "Response", [("List<String>", "HttpHeaders")])
            ],
            "implements": ["FoodMapService"]
        },
        "FoodStoreRepository": {
            "fields": [],
            "methods": [
                ("findByStationId", "List<FoodStore>", [("String",)]),
                ("findAll", "List<FoodStore>", [])
            ],
            "is_interface": True
        },
        "TrainFoodRepository": {
            "fields": [],
            "methods": [
                ("findByTripId", "List<TrainFood>", [("String",)]),
                ("findAll", "List<TrainFood>", [])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("FoodStoreController", "FoodMapServiceImpl"),
        ("TrainFoodController", "FoodMapServiceImpl"),
        ("FoodMapServiceImpl", "FoodStoreRepository"),
        ("FoodMapServiceImpl", "TrainFoodRepository")
    ]
}

# ---- ts-consign-service (Port: 16111) ----
CONSIGN_SERVICE = {
    "id": "ttf-class-consign-service",
    "classes": {
        "ConsignRecord": {
            "fields": [
                ("id", "UUID"), ("orderId", "UUID"),
                ("accountId", "UUID"), ("handleDate", "String"),
                ("targetDate", "String"), ("from", "String"),
                ("to", "String"), ("consignee", "String"),
                ("phone", "String"), ("weight", "double"),
                ("isWithin", "boolean")
            ],
            "methods": []
        },
        "ConsignController": {
            "fields": [],
            "methods": [
                ("insertConsignRecord", "Response", [("ConsignRecord", "HttpHeaders")]),
                ("updateConsignRecord", "Response", [("ConsignRecord", "HttpHeaders")]),
                ("queryByAccountId", "Response", [("String", "HttpHeaders")]),
                ("queryByOrderId", "Response", [("String", "HttpHeaders")])
            ]
        },
        "ConsignServiceImpl": {
            "fields": [],
            "methods": [
                ("insertConsignRecord", "Response", [("ConsignRecord", "HttpHeaders")]),
                ("updateConsignRecord", "Response", [("ConsignRecord", "HttpHeaders")]),
                ("queryByAccountId", "Response", [("UUID", "HttpHeaders")]),
                ("queryByOrderId", "Response", [("UUID", "HttpHeaders")])
            ],
            "implements": ["ConsignService"],
            "calls": ["ts-consign-price-service"]
        },
        "ConsignRepository": {
            "fields": [],
            "methods": [
                ("findByAccountId", "List<ConsignRecord>", [("UUID",)]),
                ("findByOrderId", "ConsignRecord", [("UUID",)])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("ConsignController", "ConsignServiceImpl"),
        ("ConsignServiceImpl", "ConsignRepository")
    ]
}

# ---- ts-consign-price-service ----
CONSIGN_PRICE_SERVICE = {
    "id": "ttf-class-consign-price-service",
    "classes": {
        "ConsignPrice": {
            "fields": [
                ("id", "UUID"), ("index", "int"),
                ("initialWeight", "double"), ("initialPrice", "double"),
                ("withinPrice", "double"), ("beyondPrice", "double")
            ],
            "methods": []
        },
        "ConsignPriceController": {
            "fields": [],
            "methods": [
                ("getPriceByWeightAndRegion", "Response", [("double", "boolean", "HttpHeaders")]),
                ("queryPriceInformation", "Response", [("HttpHeaders",)]),
                ("createAndModifyPrice", "Response", [("ConsignPrice", "HttpHeaders")])
            ]
        },
        "ConsignPriceServiceImpl": {
            "fields": [],
            "methods": [
                ("getPriceByWeightAndRegion", "Response", [("double", "boolean", "HttpHeaders")]),
                ("queryPriceInformation", "Response", [("HttpHeaders",)]),
                ("createAndModifyPrice", "Response", [("ConsignPrice", "HttpHeaders")])
            ],
            "implements": ["ConsignPriceService"]
        },
        "ConsignPriceConfigRepository": {
            "fields": [],
            "methods": [
                ("findByIndex", "ConsignPrice", [("int",)])
            ],
            "is_interface": True
        }
    },
    "dependencies": [
        ("ConsignPriceController", "ConsignPriceServiceImpl"),
        ("ConsignPriceServiceImpl", "ConsignPriceConfigRepository")
    ]
}

# ---- ts-route-plan-service (Port: 14578) ----
ROUTE_PLAN_SERVICE = {
    "id": "ttf-class-route-plan-service",
    "classes": {
        "RoutePlanInfo": {
            "fields": [
                ("fromStationName", "String"), ("toStationName", "String"),
                ("travelDate", "Date"), ("num", "int")
            ],
            "methods": []
        },
        "RoutePlanController": {
            "fields": [],
            "methods": [
                ("getByCheapest", "Response", [("RoutePlanInfo", "HttpHeaders")]),
                ("getByQuickest", "Response", [("RoutePlanInfo", "HttpHeaders")]),
                ("getByMinStation", "Response", [("RoutePlanInfo", "HttpHeaders")])
            ]
        },
        "RoutePlanServiceImpl": {
            "fields": [],
            "methods": [
                ("searchCheapestResult", "Response", [("RoutePlanInfo", "HttpHeaders")]),
                ("searchQuickestResult", "Response", [("RoutePlanInfo", "HttpHeaders")]),
                ("searchMinStopStations", "Response", [("RoutePlanInfo", "HttpHeaders")])
            ],
            "implements": ["RoutePlanService"],
            "calls": ["ts-route-service", "ts-travel-service",
                       "ts-travel2-service", "ts-station-service"]
        }
    },
    "dependencies": [
        ("RoutePlanController", "RoutePlanServiceImpl")
    ]
}

# ---- ts-travel-plan-service (Port: 14577) ----
TRAVEL_PLAN_SERVICE = {
    "id": "ttf-class-travel-plan-service",
    "classes": {
        "TransferTravelInfo": {
            "fields": [
                ("fromStationName", "String"), ("viaStationName", "String"),
                ("toStationName", "String"), ("travelDate", "Date"),
                ("trainType", "String")
            ],
            "methods": []
        },
        "TravelPlanController": {
            "fields": [],
            "methods": [
                ("getTransferResult", "Response", [("TransferTravelInfo", "HttpHeaders")]),
                ("getByCheapest", "Response", [("TripInfo", "HttpHeaders")]),
                ("getByQuickest", "Response", [("TripInfo", "HttpHeaders")]),
                ("getByMinStation", "Response", [("TripInfo", "HttpHeaders")])
            ]
        },
        "TravelPlanServiceImpl": {
            "fields": [],
            "methods": [
                ("getTransferSearch", "Response", [("TransferTravelInfo", "HttpHeaders")]),
                ("getCheapest", "Response", [("TripInfo", "HttpHeaders")]),
                ("getQuickest", "Response", [("TripInfo", "HttpHeaders")]),
                ("getMinStation", "Response", [("TripInfo", "HttpHeaders")])
            ],
            "implements": ["TravelPlanService"],
            "calls": ["ts-route-plan-service", "ts-travel-service",
                       "ts-travel2-service", "ts-seat-service",
                       "ts-station-service", "ts-ticketinfo-service"]
        }
    },
    "dependencies": [
        ("TravelPlanController", "TravelPlanServiceImpl")
    ]
}

# ---- ts-verification-code-service (Port: 15678) ----
VERIFICATION_CODE_SERVICE = {
    "id": "ttf-class-verification-code-service",
    "classes": {
        "VerifyController": {
            "fields": [],
            "methods": [
                ("imageCode", "void", [("HttpServletRequest", "HttpServletResponse", "HttpHeaders")]),
                ("verifyCode", "Response", [("String", "HttpServletRequest", "HttpHeaders")])
            ]
        }
    },
    "dependencies": []
}

# ---- ts-voucher-service (Python/Tornado - Port: 16101) ----
VOUCHER_SERVICE = {
    "id": "ttf-class-voucher-service",
    "classes": {
        "Voucher": {
            "fields": [
                ("voucherId", "int"), ("orderId", "String"),
                ("travelDate", "String"), ("contactName", "String"),
                ("trainNumber", "String"), ("seatClass", "int"),
                ("seatNumber", "String"), ("startStation", "String"),
                ("destStation", "String"), ("price", "float")
            ],
            "methods": []
        },
        "GetVoucherHandler": {
            "fields": [],
            "methods": [
                ("post", "void", [])
            ]
        }
    },
    "dependencies": [],
    "calls": ["ts-order-service", "ts-order-other-service"]
}

# ---- Admin services ----
ADMIN_ORDER_SERVICE = {
    "id": "ttf-class-admin-order-service",
    "classes": {
        "AdminOrderController": {
            "fields": [],
            "methods": [
                ("getAllOrders", "Response", [("HttpHeaders",)]),
                ("addOrder", "Response", [("Order", "HttpHeaders")]),
                ("updateOrder", "Response", [("Order", "HttpHeaders")]),
                ("deleteOrder", "Response", [("String", "String", "HttpHeaders")])
            ]
        },
        "AdminOrderServiceImpl": {
            "fields": [],
            "methods": [
                ("getAllOrders", "Response", [("HttpHeaders",)]),
                ("addOrder", "Response", [("Order", "HttpHeaders")]),
                ("deleteOrder", "Response", [("String", "String", "HttpHeaders")]),
                ("updateOrder", "Response", [("Order", "HttpHeaders")])
            ],
            "implements": ["AdminOrderService"],
            "calls": ["ts-order-service", "ts-order-other-service"]
        }
    },
    "dependencies": [
        ("AdminOrderController", "AdminOrderServiceImpl")
    ]
}

ADMIN_BASIC_INFO_SERVICE = {
    "id": "ttf-class-admin-basic-info-service",
    "classes": {
        "AdminBasicInfoController": {
            "fields": [],
            "methods": [
                ("getAllContacts", "Response", [("HttpHeaders",)]),
                ("getAllStations", "Response", [("HttpHeaders",)]),
                ("getAllTrains", "Response", [("HttpHeaders",)]),
                ("getAllRoutes", "Response", [("HttpHeaders",)]),
                ("getAllPrices", "Response", [("HttpHeaders",)]),
                ("addContact", "Response", [("Contacts", "HttpHeaders")]),
                ("deleteContact", "Response", [("String", "HttpHeaders")]),
                ("modifyContact", "Response", [("Contacts", "HttpHeaders")])
            ]
        },
        "AdminBasicInfoServiceImpl": {
            "fields": [],
            "methods": [
                ("getAllContacts", "Response", [("HttpHeaders",)]),
                ("getAllStations", "Response", [("HttpHeaders",)]),
                ("getAllTrains", "Response", [("HttpHeaders",)]),
                ("getAllRoutes", "Response", [("HttpHeaders",)]),
                ("getAllPrices", "Response", [("HttpHeaders",)])
            ],
            "implements": ["AdminBasicInfoService"],
            "calls": ["ts-contacts-service", "ts-station-service",
                       "ts-train-service", "ts-route-service", "ts-price-service"]
        }
    },
    "dependencies": [
        ("AdminBasicInfoController", "AdminBasicInfoServiceImpl")
    ]
}

ADMIN_ROUTE_SERVICE = {
    "id": "ttf-class-admin-route-service",
    "classes": {
        "AdminRouteController": {
            "fields": [],
            "methods": [
                ("getAllRoutes", "Response", [("HttpHeaders",)]),
                ("addRoute", "Response", [("RouteInfo", "HttpHeaders")]),
                ("deleteRoute", "Response", [("String", "HttpHeaders")])
            ]
        },
        "AdminRouteServiceImpl": {
            "fields": [],
            "methods": [
                ("getAllRoutes", "Response", [("HttpHeaders",)]),
                ("createAndModifyRoute", "Response", [("RouteInfo", "HttpHeaders")]),
                ("deleteRoute", "Response", [("String", "HttpHeaders")])
            ],
            "implements": ["AdminRouteService"],
            "calls": ["ts-route-service"]
        }
    },
    "dependencies": [
        ("AdminRouteController", "AdminRouteServiceImpl")
    ]
}

ADMIN_TRAVEL_SERVICE = {
    "id": "ttf-class-admin-travel-service",
    "classes": {
        "AdminTravelController": {
            "fields": [],
            "methods": [
                ("getAllTravels", "Response", [("HttpHeaders",)]),
                ("addTravel", "Response", [("TravelInfo", "HttpHeaders")]),
                ("updateTravel", "Response", [("TravelInfo", "HttpHeaders")]),
                ("deleteTravel", "Response", [("String", "HttpHeaders")])
            ]
        },
        "AdminTravelServiceImpl": {
            "fields": [],
            "methods": [
                ("getAllTravels", "Response", [("HttpHeaders",)]),
                ("addTravel", "Response", [("TravelInfo", "HttpHeaders")]),
                ("updateTravel", "Response", [("TravelInfo", "HttpHeaders")]),
                ("deleteTravel", "Response", [("String", "HttpHeaders")])
            ],
            "implements": ["AdminTravelService"],
            "calls": ["ts-travel-service", "ts-travel2-service"]
        }
    },
    "dependencies": [
        ("AdminTravelController", "AdminTravelServiceImpl")
    ]
}

ADMIN_USER_SERVICE = {
    "id": "ttf-class-admin-user-service",
    "classes": {
        "AdminUserController": {
            "fields": [],
            "methods": [
                ("getAllUsers", "Response", [("HttpHeaders",)]),
                ("addUser", "Response", [("UserDto", "HttpHeaders")]),
                ("updateUser", "Response", [("UserDto", "HttpHeaders")]),
                ("deleteUser", "Response", [("String", "HttpHeaders")])
            ]
        },
        "AdminUserServiceImpl": {
            "fields": [],
            "methods": [
                ("getAllUsers", "Response", [("HttpHeaders",)]),
                ("addUser", "Response", [("UserDto", "HttpHeaders")]),
                ("deleteUser", "Response", [("String", "HttpHeaders")]),
                ("updateUser", "Response", [("UserDto", "HttpHeaders")])
            ],
            "implements": ["AdminUserService"],
            "calls": ["ts-user-service"]
        }
    },
    "dependencies": [
        ("AdminUserController", "AdminUserServiceImpl")
    ]
}

# ---- ts-news-service ----
NEWS_SERVICE = {
    "id": "ttf-class-news-service",
    "classes": {
        "NewsController": {
            "fields": [],
            "methods": [
                ("queryAll", "Response", [("HttpHeaders",)])
            ]
        }
    },
    "dependencies": []
}

# ---- ts-avatar-service (Python/Flask - Port: 17001) ----
AVATAR_SERVICE = {
    "id": "ttf-class-avatar-service",
    "classes": {
        "AvatarHandler": {
            "fields": [],
            "methods": [
                ("post", "Response", [("image",)])
            ]
        }
    },
    "dependencies": []
}


# ===========================================================================
# AGGREGATE ALL SERVICES
# ===========================================================================

ALL_SERVICES = [
    AUTH_SERVICE,
    USER_SERVICE,
    ORDER_SERVICE,
    ORDER_OTHER_SERVICE,
    TRAVEL_SERVICE,
    TRAVEL2_SERVICE,
    TICKETINFO_SERVICE,       # NEW in fork
    BASIC_SERVICE,
    STATION_SERVICE,
    TRAIN_SERVICE,
    ROUTE_SERVICE,
    PRESERVE_SERVICE,
    PRESERVE_OTHER_SERVICE,
    SEAT_SERVICE,
    PRICE_SERVICE,
    CONTACTS_SERVICE,
    CONFIG_SERVICE,
    SECURITY_SERVICE,
    INSIDE_PAYMENT_SERVICE,
    PAYMENT_SERVICE,
    CANCEL_SERVICE,
    REBOOK_SERVICE,
    ASSURANCE_SERVICE,
    NOTIFICATION_SERVICE,
    EXECUTE_SERVICE,
    FOOD_SERVICE,
    FOOD_MAP_SERVICE,         # NEW in fork
    CONSIGN_SERVICE,
    CONSIGN_PRICE_SERVICE,
    ROUTE_PLAN_SERVICE,
    TRAVEL_PLAN_SERVICE,
    VERIFICATION_CODE_SERVICE,
    VOUCHER_SERVICE,
    ADMIN_ORDER_SERVICE,
    ADMIN_BASIC_INFO_SERVICE,
    ADMIN_ROUTE_SERVICE,
    ADMIN_TRAVEL_SERVICE,
    ADMIN_USER_SERVICE,
    NEWS_SERVICE,
    AVATAR_SERVICE,
]


# ===========================================================================
# SEQUENCE DIAGRAM DEFINITIONS - Based on trainticket-fork actual call chains
# ===========================================================================

SEQUENCE_DIAGRAMS = [
    {
        "id": "ttf-seq-login",
        "name": "LoginSequence",
        "lifelines": ["Client", "ts-auth-service", "ts-user-service",
                       "ts-verification-code-service"],
        "messages": [
            ("Client", "ts-verification-code-service", "getVerificationCode()", "synchCall"),
            ("ts-verification-code-service", "Client", "verificationCodeImage", "reply"),
            ("Client", "ts-auth-service", "login(username,password,verifyCode)", "synchCall"),
            ("ts-auth-service", "ts-user-service", "findByUserName(username)", "synchCall"),
            ("ts-user-service", "ts-auth-service", "userDetails", "reply"),
            ("ts-auth-service", "Client", "token", "reply")
        ]
    },
    {
        "id": "ttf-seq-preserve-booking",
        "name": "PreserveBookingSequence",
        "description": "Ticket reservation workflow through ts-preserve-service (fork version)",
        "lifelines": ["Client", "ts-preserve-service", "ts-security-service",
                       "ts-contacts-service", "ts-ticketinfo-service",
                       "ts-basic-service", "ts-travel-service",
                       "ts-seat-service", "ts-order-service",
                       "ts-user-service", "ts-assurance-service",
                       "ts-station-service", "ts-food-service",
                       "ts-consign-service", "ts-notification-service"],
        "messages": [
            ("Client", "ts-preserve-service", "preserve(orderTicketsInfo)", "synchCall"),
            ("ts-preserve-service", "ts-security-service", "check(accountId)", "synchCall"),
            ("ts-security-service", "ts-order-service", "securityInfoCheck(date,accountId)", "synchCall"),
            ("ts-order-service", "ts-security-service", "securityResult", "reply"),
            ("ts-security-service", "ts-preserve-service", "securityCheckResult", "reply"),
            ("ts-preserve-service", "ts-contacts-service", "getContactsById(contactsId)", "synchCall"),
            ("ts-contacts-service", "ts-preserve-service", "contacts", "reply"),
            ("ts-preserve-service", "ts-ticketinfo-service", "queryForTravel(travel)", "synchCall"),
            ("ts-ticketinfo-service", "ts-basic-service", "queryForTravel(travel)", "synchCall"),
            ("ts-basic-service", "ts-station-service", "queryById(stationId)", "synchCall"),
            ("ts-station-service", "ts-basic-service", "station", "reply"),
            ("ts-basic-service", "ts-ticketinfo-service", "travelResult", "reply"),
            ("ts-ticketinfo-service", "ts-preserve-service", "travelResult", "reply"),
            ("ts-preserve-service", "ts-travel-service", "getTripAllDetailInfo(tripInfo)", "synchCall"),
            ("ts-travel-service", "ts-preserve-service", "tripAllDetail", "reply"),
            ("ts-preserve-service", "ts-seat-service", "distributeSeat(seat)", "synchCall"),
            ("ts-seat-service", "ts-order-service", "getTicketsByDateAndTripId(seat)", "synchCall"),
            ("ts-order-service", "ts-seat-service", "soldTickets", "reply"),
            ("ts-seat-service", "ts-preserve-service", "ticket", "reply"),
            ("ts-preserve-service", "ts-user-service", "getUserById(accountId)", "synchCall"),
            ("ts-user-service", "ts-preserve-service", "user", "reply"),
            ("ts-preserve-service", "ts-assurance-service", "addAssurance(type,orderId)", "synchCall"),
            ("ts-assurance-service", "ts-preserve-service", "assuranceResult", "reply"),
            ("ts-preserve-service", "ts-station-service", "queryForStationId(name)", "synchCall"),
            ("ts-station-service", "ts-preserve-service", "stationId", "reply"),
            ("ts-preserve-service", "ts-order-service", "createOrder(order)", "synchCall"),
            ("ts-order-service", "ts-preserve-service", "orderResult", "reply"),
            ("ts-preserve-service", "ts-food-service", "createFoodOrder(foodOrder)", "synchCall"),
            ("ts-food-service", "ts-preserve-service", "foodResult", "reply"),
            ("ts-preserve-service", "ts-consign-service", "createConsign(consign)", "synchCall"),
            ("ts-consign-service", "ts-preserve-service", "consignResult", "reply"),
            ("ts-preserve-service", "ts-notification-service", "preserveSuccess(notifyInfo)", "synchCall"),
            ("ts-notification-service", "ts-preserve-service", "emailSent", "reply"),
            ("ts-preserve-service", "Client", "bookingResult", "reply")
        ]
    },
    {
        "id": "ttf-seq-query-tickets",
        "name": "QueryTicketsSequence",
        "description": "Query left tickets through travel service (fork version - via ticketinfo)",
        "lifelines": ["Client", "ts-travel-service", "ts-ticketinfo-service",
                       "ts-basic-service", "ts-train-service", "ts-route-service",
                       "ts-station-service", "ts-price-service",
                       "ts-seat-service", "ts-order-service"],
        "messages": [
            ("Client", "ts-travel-service", "queryLeftTickets(tripInfo)", "synchCall"),
            ("ts-travel-service", "ts-ticketinfo-service", "queryForTravel(travel)", "synchCall"),
            ("ts-ticketinfo-service", "ts-basic-service", "queryForTravel(travel)", "synchCall"),
            ("ts-basic-service", "ts-train-service", "queryTrainType(trainTypeId)", "synchCall"),
            ("ts-train-service", "ts-basic-service", "trainType", "reply"),
            ("ts-basic-service", "ts-route-service", "getRouteById(routeId)", "synchCall"),
            ("ts-route-service", "ts-basic-service", "route", "reply"),
            ("ts-basic-service", "ts-station-service", "queryById(stationId)", "synchCall"),
            ("ts-station-service", "ts-basic-service", "station", "reply"),
            ("ts-basic-service", "ts-price-service", "findByRouteIdAndTrainType()", "synchCall"),
            ("ts-price-service", "ts-basic-service", "priceConfig", "reply"),
            ("ts-basic-service", "ts-ticketinfo-service", "travelResult", "reply"),
            ("ts-ticketinfo-service", "ts-travel-service", "travelResult", "reply"),
            ("ts-travel-service", "ts-seat-service", "getLeftTicketOfInterval(seat)", "synchCall"),
            ("ts-seat-service", "ts-order-service", "getTicketsByDateAndTripId(seat)", "synchCall"),
            ("ts-order-service", "ts-seat-service", "soldTickets", "reply"),
            ("ts-seat-service", "ts-travel-service", "leftTicketInfo", "reply"),
            ("ts-travel-service", "Client", "queryResult", "reply")
        ]
    },
    {
        "id": "ttf-seq-cancel-order",
        "name": "CancelOrderSequence",
        "description": "Order cancellation and refund (fork version)",
        "lifelines": ["Client", "ts-cancel-service", "ts-order-service",
                       "ts-order-other-service", "ts-user-service",
                       "ts-inside-payment-service", "ts-notification-service"],
        "messages": [
            ("Client", "ts-cancel-service", "cancelTicket(orderId,loginId)", "synchCall"),
            ("ts-cancel-service", "ts-order-service", "getOrderById(orderId)", "synchCall"),
            ("ts-order-service", "ts-cancel-service", "order", "reply"),
            ("ts-cancel-service", "ts-cancel-service", "calculateRefund(order)", "synchCall"),
            ("ts-cancel-service", "ts-user-service", "getUserById(userId)", "synchCall"),
            ("ts-user-service", "ts-cancel-service", "user", "reply"),
            ("ts-cancel-service", "ts-inside-payment-service", "drawBack(userId,money)", "synchCall"),
            ("ts-inside-payment-service", "ts-cancel-service", "drawbackResult", "reply"),
            ("ts-cancel-service", "ts-order-service", "modifyOrder(orderId,status)", "synchCall"),
            ("ts-order-service", "ts-cancel-service", "updateResult", "reply"),
            ("ts-cancel-service", "ts-notification-service", "orderCancelSuccess(notifyInfo)", "synchCall"),
            ("ts-notification-service", "ts-cancel-service", "emailSent", "reply"),
            ("ts-cancel-service", "Client", "cancelResult", "reply")
        ]
    },
    {
        "id": "ttf-seq-rebook",
        "name": "RebookSequence",
        "description": "Ticket rebooking workflow (fork version - with station name conversion)",
        "lifelines": ["Client", "ts-rebook-service", "ts-order-service",
                       "ts-station-service", "ts-travel-service",
                       "ts-seat-service", "ts-inside-payment-service"],
        "messages": [
            ("Client", "ts-rebook-service", "rebook(rebookInfo)", "synchCall"),
            ("ts-rebook-service", "ts-order-service", "getOrderById(orderId)", "synchCall"),
            ("ts-order-service", "ts-rebook-service", "order", "reply"),
            ("ts-rebook-service", "ts-station-service", "queryForStationName(stationId)", "synchCall"),
            ("ts-station-service", "ts-rebook-service", "stationName", "reply"),
            ("ts-rebook-service", "ts-travel-service", "getTripAllDetailInfo(tripInfo)", "synchCall"),
            ("ts-travel-service", "ts-rebook-service", "tripAllDetail", "reply"),
            ("ts-rebook-service", "ts-seat-service", "distributeSeat(seat)", "synchCall"),
            ("ts-seat-service", "ts-rebook-service", "ticket", "reply"),
            ("ts-rebook-service", "ts-order-service", "saveChanges(newOrder)", "synchCall"),
            ("ts-order-service", "ts-rebook-service", "saveResult", "reply"),
            ("ts-rebook-service", "ts-inside-payment-service", "drawBack(userId,priceDiff)", "synchCall"),
            ("ts-inside-payment-service", "ts-rebook-service", "paymentResult", "reply"),
            ("ts-rebook-service", "Client", "rebookResult", "reply")
        ]
    },
    {
        "id": "ttf-seq-execute-collect",
        "name": "ExecuteAndCollectSequence",
        "description": "Ticket execution and collection at station",
        "lifelines": ["Client", "ts-execute-service", "ts-order-service",
                       "ts-order-other-service"],
        "messages": [
            ("Client", "ts-execute-service", "collectTicket(orderId)", "synchCall"),
            ("ts-execute-service", "ts-order-service", "getOrderById(orderId)", "synchCall"),
            ("ts-order-service", "ts-execute-service", "order", "reply"),
            ("ts-execute-service", "ts-order-service", "modifyOrder(orderId,collected)", "synchCall"),
            ("ts-order-service", "ts-execute-service", "updateResult", "reply"),
            ("ts-execute-service", "Client", "collectResult", "reply"),
            ("Client", "ts-execute-service", "executeTicket(orderId)", "synchCall"),
            ("ts-execute-service", "ts-order-service", "getOrderById(orderId)", "synchCall"),
            ("ts-order-service", "ts-execute-service", "order", "reply"),
            ("ts-execute-service", "ts-order-service", "modifyOrder(orderId,executed)", "synchCall"),
            ("ts-order-service", "ts-execute-service", "updateResult", "reply"),
            ("ts-execute-service", "Client", "executeResult", "reply")
        ]
    },
    {
        "id": "ttf-seq-payment",
        "name": "PaymentSequence",
        "description": "Inside payment processing workflow",
        "lifelines": ["Client", "ts-inside-payment-service",
                       "ts-order-service", "ts-payment-service"],
        "messages": [
            ("Client", "ts-inside-payment-service", "pay(paymentInfo)", "synchCall"),
            ("ts-inside-payment-service", "ts-order-service", "getOrderPrice(orderId)", "synchCall"),
            ("ts-order-service", "ts-inside-payment-service", "orderPrice", "reply"),
            ("ts-inside-payment-service", "ts-payment-service", "pay(payment)", "synchCall"),
            ("ts-payment-service", "ts-inside-payment-service", "paymentResult", "reply"),
            ("ts-inside-payment-service", "ts-order-service", "modifyOrder(orderId,paid)", "synchCall"),
            ("ts-order-service", "ts-inside-payment-service", "updateResult", "reply"),
            ("ts-inside-payment-service", "Client", "payResult", "reply")
        ]
    },
    {
        "id": "ttf-seq-voucher",
        "name": "VoucherSequence",
        "description": "Voucher printing through Python ts-voucher-service",
        "lifelines": ["Client", "ts-voucher-service", "ts-order-service",
                       "ts-order-other-service"],
        "messages": [
            ("Client", "ts-voucher-service", "getVoucher(orderId)", "synchCall"),
            ("ts-voucher-service", "ts-order-service", "getOrderById(orderId)", "synchCall"),
            ("ts-order-service", "ts-voucher-service", "order", "reply"),
            ("ts-voucher-service", "Client", "voucher", "reply")
        ]
    },
    {
        "id": "ttf-seq-food-query",
        "name": "FoodQuerySequence",
        "description": "Food query through food-service -> food-map-service (fork architecture)",
        "lifelines": ["Client", "ts-food-service", "ts-food-map-service",
                       "ts-travel-service", "ts-station-service"],
        "messages": [
            ("Client", "ts-food-service", "getAllFood(date,startStation,endStation,tripId)", "synchCall"),
            ("ts-food-service", "ts-travel-service", "getRouteByTripId(tripId)", "synchCall"),
            ("ts-travel-service", "ts-food-service", "route", "reply"),
            ("ts-food-service", "ts-food-map-service", "getFoodStoresByStationIds(stationIds)", "synchCall"),
            ("ts-food-map-service", "ts-food-service", "foodStores", "reply"),
            ("ts-food-service", "ts-food-map-service", "getTrainFoodByTripId(tripId)", "synchCall"),
            ("ts-food-map-service", "ts-food-service", "trainFoods", "reply"),
            ("ts-food-service", "Client", "allTripFood", "reply")
        ]
    },
    {
        "id": "ttf-seq-consign",
        "name": "ConsignSequence",
        "description": "Consignment creation and pricing",
        "lifelines": ["Client", "ts-consign-service", "ts-consign-price-service"],
        "messages": [
            ("Client", "ts-consign-service", "insertConsignRecord(record)", "synchCall"),
            ("ts-consign-service", "ts-consign-price-service", "getPriceByWeightAndRegion(weight,isWithin)", "synchCall"),
            ("ts-consign-price-service", "ts-consign-service", "price", "reply"),
            ("ts-consign-service", "Client", "consignResult", "reply")
        ]
    },
    {
        "id": "ttf-seq-travel-plan",
        "name": "TravelPlanSequence",
        "description": "Travel planning - cheapest/quickest/min-station routes",
        "lifelines": ["Client", "ts-travel-plan-service", "ts-route-plan-service",
                       "ts-route-service", "ts-travel-service", "ts-travel2-service",
                       "ts-station-service", "ts-seat-service",
                       "ts-ticketinfo-service"],
        "messages": [
            ("Client", "ts-travel-plan-service", "getCheapest(tripInfo)", "synchCall"),
            ("ts-travel-plan-service", "ts-route-plan-service", "searchCheapestResult(routePlanInfo)", "synchCall"),
            ("ts-route-plan-service", "ts-station-service", "queryForStationId(stationName)", "synchCall"),
            ("ts-station-service", "ts-route-plan-service", "stationId", "reply"),
            ("ts-route-plan-service", "ts-route-service", "queryByStartAndTerminal(startId,terminalId)", "synchCall"),
            ("ts-route-service", "ts-route-plan-service", "routes", "reply"),
            ("ts-route-plan-service", "ts-travel-service", "getTripsByRouteId(routeIds)", "synchCall"),
            ("ts-travel-service", "ts-route-plan-service", "trips", "reply"),
            ("ts-route-plan-service", "ts-travel2-service", "getTripsByRouteId(routeIds)", "synchCall"),
            ("ts-travel2-service", "ts-route-plan-service", "trips", "reply"),
            ("ts-route-plan-service", "ts-travel-plan-service", "cheapestResult", "reply"),
            ("ts-travel-plan-service", "ts-seat-service", "getLeftTicketOfInterval(seat)", "synchCall"),
            ("ts-seat-service", "ts-travel-plan-service", "leftTickets", "reply"),
            ("ts-travel-plan-service", "Client", "travelPlanResult", "reply")
        ]
    }
]


# ===========================================================================
# ACTIVITY DIAGRAM DEFINITIONS - Fork-specific workflows
# ===========================================================================

ACTIVITY_DIAGRAMS = [
    {
        "id": "ttf-activity-preserve-booking",
        "name": "PreserveBookingWorkflow",
        "description": "Ticket booking workflow (fork: via ts-ticketinfo-service intermediary)",
        "nodes": [
            {"name": "InitialNode", "type": "uml:InitialNode"},
            {"name": "ReceiveBookingRequest", "type": "uml:OpaqueAction"},
            {"name": "CheckSecurity", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_SecurityPass", "type": "uml:DecisionNode"},
            {"name": "GetContacts", "type": "uml:OpaqueAction"},
            {"name": "QueryTicketInfo", "type": "uml:OpaqueAction"},
            {"name": "DelegateToBasicService", "type": "uml:OpaqueAction"},
            {"name": "GetTripDetail", "type": "uml:OpaqueAction"},
            {"name": "DistributeSeat", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_SeatAvailable", "type": "uml:DecisionNode"},
            {"name": "GetUserAccount", "type": "uml:OpaqueAction"},
            {"name": "ForkNode_ParallelCreate", "type": "uml:ForkNode"},
            {"name": "CreateOrder", "type": "uml:OpaqueAction"},
            {"name": "AddAssurance", "type": "uml:OpaqueAction"},
            {"name": "CreateFoodOrder", "type": "uml:OpaqueAction"},
            {"name": "CreateConsign", "type": "uml:OpaqueAction"},
            {"name": "JoinNode_ParallelComplete", "type": "uml:JoinNode"},
            {"name": "SendNotification", "type": "uml:OpaqueAction"},
            {"name": "FinalNode_Success", "type": "uml:ActivityFinalNode"},
            {"name": "FinalNode_SecurityFail", "type": "uml:ActivityFinalNode"},
            {"name": "FinalNode_NoSeat", "type": "uml:ActivityFinalNode"}
        ],
        "edges": [
            ("InitialNode", "ReceiveBookingRequest"),
            ("ReceiveBookingRequest", "CheckSecurity"),
            ("CheckSecurity", "DecisionNode_SecurityPass"),
            ("DecisionNode_SecurityPass", "GetContacts", "pass"),
            ("DecisionNode_SecurityPass", "FinalNode_SecurityFail", "fail"),
            ("GetContacts", "QueryTicketInfo"),
            ("QueryTicketInfo", "DelegateToBasicService"),
            ("DelegateToBasicService", "GetTripDetail"),
            ("GetTripDetail", "DistributeSeat"),
            ("DistributeSeat", "DecisionNode_SeatAvailable"),
            ("DecisionNode_SeatAvailable", "GetUserAccount", "available"),
            ("DecisionNode_SeatAvailable", "FinalNode_NoSeat", "unavailable"),
            ("GetUserAccount", "ForkNode_ParallelCreate"),
            ("ForkNode_ParallelCreate", "CreateOrder"),
            ("ForkNode_ParallelCreate", "AddAssurance"),
            ("ForkNode_ParallelCreate", "CreateFoodOrder"),
            ("ForkNode_ParallelCreate", "CreateConsign"),
            ("CreateOrder", "JoinNode_ParallelComplete"),
            ("AddAssurance", "JoinNode_ParallelComplete"),
            ("CreateFoodOrder", "JoinNode_ParallelComplete"),
            ("CreateConsign", "JoinNode_ParallelComplete"),
            ("JoinNode_ParallelComplete", "SendNotification"),
            ("SendNotification", "FinalNode_Success")
        ],
        "partitions": [
            {"name": "ts-preserve-service", "actions": ["ReceiveBookingRequest", "CheckSecurity",
                                                          "GetContacts", "GetTripDetail",
                                                          "GetUserAccount", "SendNotification"]},
            {"name": "ts-ticketinfo-service", "actions": ["QueryTicketInfo"]},
            {"name": "ts-basic-service", "actions": ["DelegateToBasicService"]},
            {"name": "ts-seat-service", "actions": ["DistributeSeat"]},
            {"name": "ts-order-service", "actions": ["CreateOrder"]},
            {"name": "ts-assurance-service", "actions": ["AddAssurance"]},
            {"name": "ts-food-service", "actions": ["CreateFoodOrder"]},
            {"name": "ts-consign-service", "actions": ["CreateConsign"]},
            {"name": "ts-security-service", "actions": ["CheckSecurity"]},
            {"name": "ts-notification-service", "actions": ["SendNotification"]}
        ]
    },
    {
        "id": "ttf-activity-cancel-refund",
        "name": "CancelAndRefundWorkflow",
        "description": "Order cancellation and refund processing workflow (fork version)",
        "nodes": [
            {"name": "InitialNode", "type": "uml:InitialNode"},
            {"name": "GetOrder", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_OrderFound", "type": "uml:DecisionNode"},
            {"name": "SetCancelStatus", "type": "uml:OpaqueAction"},
            {"name": "CheckOrderStatus", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_Cancellable", "type": "uml:DecisionNode"},
            {"name": "CalculateRefund", "type": "uml:OpaqueAction"},
            {"name": "GetUserAccount", "type": "uml:OpaqueAction"},
            {"name": "DrawbackMoney", "type": "uml:OpaqueAction"},
            {"name": "UpdateOrderStatus", "type": "uml:OpaqueAction"},
            {"name": "SendCancelNotification", "type": "uml:OpaqueAction"},
            {"name": "FinalNode_Success", "type": "uml:ActivityFinalNode"},
            {"name": "FinalNode_NotFound", "type": "uml:ActivityFinalNode"},
            {"name": "FinalNode_NotCancellable", "type": "uml:ActivityFinalNode"}
        ],
        "edges": [
            ("InitialNode", "GetOrder"),
            ("GetOrder", "DecisionNode_OrderFound"),
            ("DecisionNode_OrderFound", "SetCancelStatus", "found"),
            ("DecisionNode_OrderFound", "FinalNode_NotFound", "not found"),
            ("SetCancelStatus", "CheckOrderStatus"),
            ("CheckOrderStatus", "DecisionNode_Cancellable"),
            ("DecisionNode_Cancellable", "CalculateRefund", "cancellable"),
            ("DecisionNode_Cancellable", "FinalNode_NotCancellable", "not cancellable"),
            ("CalculateRefund", "GetUserAccount"),
            ("GetUserAccount", "DrawbackMoney"),
            ("DrawbackMoney", "UpdateOrderStatus"),
            ("UpdateOrderStatus", "SendCancelNotification"),
            ("SendCancelNotification", "FinalNode_Success")
        ],
        "partitions": [
            {"name": "ts-cancel-service", "actions": ["GetOrder", "SetCancelStatus",
                                                        "CheckOrderStatus", "CalculateRefund"]},
            {"name": "ts-order-service", "actions": ["GetOrder", "UpdateOrderStatus"]},
            {"name": "ts-user-service", "actions": ["GetUserAccount"]},
            {"name": "ts-inside-payment-service", "actions": ["DrawbackMoney"]},
            {"name": "ts-notification-service", "actions": ["SendCancelNotification"]}
        ]
    },
    {
        "id": "ttf-activity-rebook",
        "name": "RebookWorkflow",
        "description": "Ticket rebooking workflow (fork: includes station name conversion fault)",
        "nodes": [
            {"name": "InitialNode", "type": "uml:InitialNode"},
            {"name": "GetOriginalOrder", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_OrderExists", "type": "uml:DecisionNode"},
            {"name": "ConvertStationNames", "type": "uml:OpaqueAction"},
            {"name": "GetTripDetail", "type": "uml:OpaqueAction"},
            {"name": "CheckPriceDifference", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_PriceCompare", "type": "uml:DecisionNode"},
            {"name": "DistributeSeat", "type": "uml:OpaqueAction"},
            {"name": "CreateNewOrder", "type": "uml:OpaqueAction"},
            {"name": "CancelOldOrder", "type": "uml:OpaqueAction"},
            {"name": "PayDifference", "type": "uml:OpaqueAction"},
            {"name": "DrawbackDifference", "type": "uml:OpaqueAction"},
            {"name": "FinalNode_Success", "type": "uml:ActivityFinalNode"},
            {"name": "FinalNode_NotFound", "type": "uml:ActivityFinalNode"}
        ],
        "edges": [
            ("InitialNode", "GetOriginalOrder"),
            ("GetOriginalOrder", "DecisionNode_OrderExists"),
            ("DecisionNode_OrderExists", "ConvertStationNames", "exists"),
            ("DecisionNode_OrderExists", "FinalNode_NotFound", "not found"),
            ("ConvertStationNames", "GetTripDetail"),
            ("GetTripDetail", "CheckPriceDifference"),
            ("CheckPriceDifference", "DecisionNode_PriceCompare"),
            ("DecisionNode_PriceCompare", "PayDifference", "new price higher"),
            ("DecisionNode_PriceCompare", "DrawbackDifference", "new price lower"),
            ("PayDifference", "DistributeSeat"),
            ("DrawbackDifference", "DistributeSeat"),
            ("DistributeSeat", "CreateNewOrder"),
            ("CreateNewOrder", "CancelOldOrder"),
            ("CancelOldOrder", "FinalNode_Success")
        ],
        "partitions": [
            {"name": "ts-rebook-service", "actions": ["GetOriginalOrder", "ConvertStationNames",
                                                        "GetTripDetail", "CheckPriceDifference"]},
            {"name": "ts-order-service", "actions": ["GetOriginalOrder", "CreateNewOrder", "CancelOldOrder"]},
            {"name": "ts-station-service", "actions": ["ConvertStationNames"]},
            {"name": "ts-travel-service", "actions": ["GetTripDetail"]},
            {"name": "ts-seat-service", "actions": ["DistributeSeat"]},
            {"name": "ts-inside-payment-service", "actions": ["PayDifference", "DrawbackDifference"]}
        ]
    },
    {
        "id": "ttf-activity-food-query",
        "name": "FoodQueryWorkflow",
        "description": "Food query workflow (fork: through ts-food-map-service)",
        "nodes": [
            {"name": "InitialNode", "type": "uml:InitialNode"},
            {"name": "GetRouteFromTravel", "type": "uml:OpaqueAction"},
            {"name": "ExtractStationIds", "type": "uml:OpaqueAction"},
            {"name": "ForkNode_FoodQuery", "type": "uml:ForkNode"},
            {"name": "QueryFoodStores", "type": "uml:OpaqueAction"},
            {"name": "QueryTrainFood", "type": "uml:OpaqueAction"},
            {"name": "JoinNode_FoodResult", "type": "uml:JoinNode"},
            {"name": "CombineResults", "type": "uml:OpaqueAction"},
            {"name": "FinalNode", "type": "uml:ActivityFinalNode"}
        ],
        "edges": [
            ("InitialNode", "GetRouteFromTravel"),
            ("GetRouteFromTravel", "ExtractStationIds"),
            ("ExtractStationIds", "ForkNode_FoodQuery"),
            ("ForkNode_FoodQuery", "QueryFoodStores"),
            ("ForkNode_FoodQuery", "QueryTrainFood"),
            ("QueryFoodStores", "JoinNode_FoodResult"),
            ("QueryTrainFood", "JoinNode_FoodResult"),
            ("JoinNode_FoodResult", "CombineResults"),
            ("CombineResults", "FinalNode")
        ],
        "partitions": [
            {"name": "ts-food-service", "actions": ["ExtractStationIds", "CombineResults"]},
            {"name": "ts-travel-service", "actions": ["GetRouteFromTravel"]},
            {"name": "ts-food-map-service", "actions": ["QueryFoodStores", "QueryTrainFood"]}
        ]
    },
    {
        "id": "ttf-activity-seat-distribution",
        "name": "SeatDistributionWorkflow",
        "description": "Seat distribution (fork: extra route/traintype queries)",
        "nodes": [
            {"name": "InitialNode", "type": "uml:InitialNode"},
            {"name": "DetermineTrainType", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_TrainType", "type": "uml:DecisionNode"},
            {"name": "QueryRouteFromTravel", "type": "uml:OpaqueAction"},
            {"name": "QueryRouteFromTravel2", "type": "uml:OpaqueAction"},
            {"name": "QueryTrainTypeInfo", "type": "uml:OpaqueAction"},
            {"name": "GetSoldTickets", "type": "uml:OpaqueAction"},
            {"name": "CalculateAvailableSeats", "type": "uml:OpaqueAction"},
            {"name": "AssignSeat", "type": "uml:OpaqueAction"},
            {"name": "FinalNode", "type": "uml:ActivityFinalNode"}
        ],
        "edges": [
            ("InitialNode", "DetermineTrainType"),
            ("DetermineTrainType", "DecisionNode_TrainType"),
            ("DecisionNode_TrainType", "QueryRouteFromTravel", "G/D train"),
            ("DecisionNode_TrainType", "QueryRouteFromTravel2", "other train"),
            ("QueryRouteFromTravel", "QueryTrainTypeInfo"),
            ("QueryRouteFromTravel2", "QueryTrainTypeInfo"),
            ("QueryTrainTypeInfo", "GetSoldTickets"),
            ("GetSoldTickets", "CalculateAvailableSeats"),
            ("CalculateAvailableSeats", "AssignSeat"),
            ("AssignSeat", "FinalNode")
        ],
        "partitions": [
            {"name": "ts-seat-service", "actions": ["DetermineTrainType", "CalculateAvailableSeats", "AssignSeat"]},
            {"name": "ts-travel-service", "actions": ["QueryRouteFromTravel", "QueryTrainTypeInfo"]},
            {"name": "ts-travel2-service", "actions": ["QueryRouteFromTravel2"]},
            {"name": "ts-order-service", "actions": ["GetSoldTickets"]}
        ]
    }
]


# ===========================================================================
# COMMUNICATION DIAGRAM DEFINITIONS - Fork-specific topology
# ===========================================================================

COMMUNICATION_DIAGRAMS = [
    {
        "id": "ttf-comm-preserve-orchestration",
        "name": "PreserveServiceOrchestration",
        "description": "Communication topology showing ts-preserve-service as hub (fork: via ticketinfo)",
        "objects": [
            "ts-preserve-service", "ts-security-service", "ts-contacts-service",
            "ts-ticketinfo-service", "ts-basic-service",
            "ts-travel-service", "ts-seat-service",
            "ts-user-service", "ts-assurance-service", "ts-station-service",
            "ts-order-service", "ts-food-service", "ts-consign-service",
            "ts-notification-service"
        ],
        "links": [
            ("ts-preserve-service", "ts-security-service", "1: check(accountId)"),
            ("ts-preserve-service", "ts-contacts-service", "2: getContactsById()"),
            ("ts-preserve-service", "ts-ticketinfo-service", "3: queryForTravel()"),
            ("ts-ticketinfo-service", "ts-basic-service", "3.1: queryForTravel()"),
            ("ts-preserve-service", "ts-travel-service", "4: getTripAllDetailInfo()"),
            ("ts-preserve-service", "ts-seat-service", "5: distributeSeat()"),
            ("ts-seat-service", "ts-order-service", "5.1: getSoldTickets()"),
            ("ts-preserve-service", "ts-user-service", "6: getAccount()"),
            ("ts-preserve-service", "ts-assurance-service", "7: addAssurance()"),
            ("ts-preserve-service", "ts-station-service", "8: queryForStationId()"),
            ("ts-preserve-service", "ts-order-service", "9: createOrder()"),
            ("ts-preserve-service", "ts-food-service", "10: createFoodOrder()"),
            ("ts-preserve-service", "ts-consign-service", "11: createConsign()"),
            ("ts-preserve-service", "ts-notification-service", "12: preserveSuccess()")
        ]
    },
    {
        "id": "ttf-comm-ticketinfo-intermediary",
        "name": "TicketInfoIntermediaryTopology",
        "description": "Communication topology showing ts-ticketinfo-service as intermediary (fork-specific)",
        "objects": [
            "ts-travel-service", "ts-travel2-service",
            "ts-preserve-service", "ts-preserve-other-service",
            "ts-travel-plan-service",
            "ts-ticketinfo-service", "ts-basic-service",
            "ts-station-service", "ts-train-service",
            "ts-route-service", "ts-price-service"
        ],
        "links": [
            ("ts-travel-service", "ts-ticketinfo-service", "1: queryForTravel()"),
            ("ts-travel-service", "ts-ticketinfo-service", "2: queryForStationId()"),
            ("ts-travel2-service", "ts-ticketinfo-service", "3: queryForTravel()"),
            ("ts-preserve-service", "ts-ticketinfo-service", "4: queryForTravel()"),
            ("ts-preserve-other-service", "ts-ticketinfo-service", "5: queryForTravel()"),
            ("ts-travel-plan-service", "ts-ticketinfo-service", "6: queryForStationId()"),
            ("ts-ticketinfo-service", "ts-basic-service", "7: queryForTravel()"),
            ("ts-ticketinfo-service", "ts-basic-service", "8: queryForStationId()"),
            ("ts-basic-service", "ts-station-service", "9: queryById()"),
            ("ts-basic-service", "ts-train-service", "10: queryTrainType()"),
            ("ts-basic-service", "ts-route-service", "11: getRouteById()"),
            ("ts-basic-service", "ts-price-service", "12: findByRouteIdAndTrainType()")
        ]
    },
    {
        "id": "ttf-comm-basic-aggregation",
        "name": "BasicServiceAggregation",
        "description": "Communication topology showing ts-basic-service aggregating data from 4 services",
        "objects": [
            "ts-basic-service", "ts-station-service", "ts-train-service",
            "ts-route-service", "ts-price-service"
        ],
        "links": [
            ("ts-basic-service", "ts-station-service", "1: queryForStationId()"),
            ("ts-basic-service", "ts-train-service", "2: queryTrainType()"),
            ("ts-basic-service", "ts-route-service", "3: getRouteByRouteId()"),
            ("ts-basic-service", "ts-price-service", "4: queryPriceConfig()")
        ]
    },
    {
        "id": "ttf-comm-payment-flow",
        "name": "PaymentServiceFlow",
        "description": "Communication topology for payment processing",
        "objects": [
            "ts-inside-payment-service", "ts-order-service",
            "ts-order-other-service", "ts-payment-service"
        ],
        "links": [
            ("ts-inside-payment-service", "ts-order-service", "1: getOrderPrice()"),
            ("ts-inside-payment-service", "ts-order-other-service", "2: getOrderPrice()"),
            ("ts-inside-payment-service", "ts-payment-service", "3: pay()"),
            ("ts-inside-payment-service", "ts-order-service", "4: modifyOrder(paid)"),
            ("ts-inside-payment-service", "ts-order-other-service", "5: modifyOrder(paid)")
        ]
    },
    {
        "id": "ttf-comm-cancel-flow",
        "name": "CancelServiceFlow",
        "description": "Communication topology for order cancellation",
        "objects": [
            "ts-cancel-service", "ts-order-service", "ts-order-other-service",
            "ts-user-service", "ts-inside-payment-service",
            "ts-notification-service"
        ],
        "links": [
            ("ts-cancel-service", "ts-order-service", "1: getOrderById()"),
            ("ts-cancel-service", "ts-order-other-service", "1: getOrderById()"),
            ("ts-cancel-service", "ts-user-service", "2: getUserById()"),
            ("ts-cancel-service", "ts-inside-payment-service", "3: drawBack()"),
            ("ts-cancel-service", "ts-order-service", "4: modifyOrder(cancelled)"),
            ("ts-cancel-service", "ts-notification-service", "5: orderCancelSuccess()")
        ]
    },
    {
        "id": "ttf-comm-food-map-flow",
        "name": "FoodMapServiceFlow",
        "description": "Communication topology for food query (fork: through food-map-service)",
        "objects": [
            "ts-food-service", "ts-food-map-service",
            "ts-travel-service", "ts-station-service"
        ],
        "links": [
            ("ts-food-service", "ts-travel-service", "1: getRouteByTripId()"),
            ("ts-food-service", "ts-food-map-service", "2: getFoodStoresByStationIds()"),
            ("ts-food-service", "ts-food-map-service", "3: getTrainFoodByTripId()"),
            ("ts-food-service", "ts-station-service", "4: queryById()")
        ]
    },
    {
        "id": "ttf-comm-system-wide",
        "name": "SystemWideCommunication",
        "description": "Full system communication topology with all 40+ services",
        "objects": [
            "ts-ui-dashboard", "ts-auth-service", "ts-user-service",
            "ts-verification-code-service",
            "ts-preserve-service", "ts-preserve-other-service",
            "ts-cancel-service", "ts-rebook-service",
            "ts-travel-plan-service", "ts-route-plan-service",
            "ts-travel-service", "ts-travel2-service",
            "ts-ticketinfo-service", "ts-basic-service",
            "ts-order-service", "ts-order-other-service",
            "ts-seat-service", "ts-security-service",
            "ts-station-service", "ts-train-service",
            "ts-route-service", "ts-price-service",
            "ts-contacts-service", "ts-config-service",
            "ts-inside-payment-service", "ts-payment-service",
            "ts-assurance-service", "ts-notification-service",
            "ts-execute-service", "ts-food-service",
            "ts-food-map-service", "ts-consign-service",
            "ts-consign-price-service", "ts-voucher-service",
            "ts-admin-order-service", "ts-admin-basic-info-service",
            "ts-admin-route-service", "ts-admin-travel-service",
            "ts-admin-user-service"
        ],
        "links": [
            # Auth flow
            ("ts-user-service", "ts-auth-service", "createDefaultAuthUser()"),
            # Preserve orchestration
            ("ts-preserve-service", "ts-ticketinfo-service", "queryForTravel()"),
            ("ts-preserve-service", "ts-security-service", "check()"),
            ("ts-preserve-service", "ts-contacts-service", "getContactsById()"),
            ("ts-preserve-service", "ts-travel-service", "getTripAllDetailInfo()"),
            ("ts-preserve-service", "ts-seat-service", "distributeSeat()"),
            ("ts-preserve-service", "ts-user-service", "getAccount()"),
            ("ts-preserve-service", "ts-assurance-service", "addAssurance()"),
            ("ts-preserve-service", "ts-station-service", "queryForStationId()"),
            ("ts-preserve-service", "ts-order-service", "createOrder()"),
            ("ts-preserve-service", "ts-food-service", "createFoodOrder()"),
            ("ts-preserve-service", "ts-consign-service", "createConsign()"),
            ("ts-preserve-service", "ts-notification-service", "preserveSuccess()"),
            # Preserve-other orchestration
            ("ts-preserve-other-service", "ts-ticketinfo-service", "queryForTravel()"),
            ("ts-preserve-other-service", "ts-travel2-service", "getTripAllDetailInfo()"),
            ("ts-preserve-other-service", "ts-seat-service", "distributeSeat()"),
            ("ts-preserve-other-service", "ts-order-other-service", "createOrder()"),
            # Ticketinfo intermediary
            ("ts-ticketinfo-service", "ts-basic-service", "queryForTravel()"),
            ("ts-ticketinfo-service", "ts-basic-service", "queryForStationId()"),
            # Basic aggregation
            ("ts-basic-service", "ts-station-service", "queryById()"),
            ("ts-basic-service", "ts-train-service", "queryTrainType()"),
            ("ts-basic-service", "ts-route-service", "getRouteById()"),
            ("ts-basic-service", "ts-price-service", "findByRouteIdAndTrainType()"),
            # Travel service
            ("ts-travel-service", "ts-ticketinfo-service", "queryForTravel()"),
            ("ts-travel-service", "ts-ticketinfo-service", "queryForStationId()"),
            ("ts-travel-service", "ts-train-service", "retrieve()"),
            ("ts-travel-service", "ts-route-service", "queryById()"),
            ("ts-travel-service", "ts-seat-service", "getLeftTicketOfInterval()"),
            ("ts-travel-service", "ts-order-service", "calculateSoldTicket()"),
            # Travel2 service
            ("ts-travel2-service", "ts-ticketinfo-service", "queryForTravel()"),
            ("ts-travel2-service", "ts-order-other-service", "calculateSoldTicket()"),
            # Seat service
            ("ts-seat-service", "ts-travel-service", "getRouteByTripId()"),
            ("ts-seat-service", "ts-travel-service", "getTrainTypeByTripId()"),
            ("ts-seat-service", "ts-travel2-service", "getRouteByTripId()"),
            ("ts-seat-service", "ts-order-service", "getTicketsByDateAndTripId()"),
            ("ts-seat-service", "ts-order-other-service", "getTicketsByDateAndTripId()"),
            ("ts-seat-service", "ts-config-service", "query()"),
            # Security
            ("ts-security-service", "ts-order-service", "securityInfoCheck()"),
            ("ts-security-service", "ts-order-other-service", "securityInfoCheck()"),
            # Cancel
            ("ts-cancel-service", "ts-order-service", "getOrderById()"),
            ("ts-cancel-service", "ts-order-other-service", "getOrderById()"),
            ("ts-cancel-service", "ts-user-service", "getUserById()"),
            ("ts-cancel-service", "ts-inside-payment-service", "drawBack()"),
            ("ts-cancel-service", "ts-notification-service", "orderCancelSuccess()"),
            # Rebook
            ("ts-rebook-service", "ts-order-service", "getOrderById()"),
            ("ts-rebook-service", "ts-order-other-service", "getOrderById()"),
            ("ts-rebook-service", "ts-station-service", "queryForStationName()"),
            ("ts-rebook-service", "ts-travel-service", "getTripAllDetailInfo()"),
            ("ts-rebook-service", "ts-travel2-service", "getTripAllDetailInfo()"),
            ("ts-rebook-service", "ts-seat-service", "distributeSeat()"),
            ("ts-rebook-service", "ts-inside-payment-service", "drawBack()"),
            # Payment
            ("ts-inside-payment-service", "ts-order-service", "getOrderPrice()"),
            ("ts-inside-payment-service", "ts-order-other-service", "getOrderPrice()"),
            ("ts-inside-payment-service", "ts-payment-service", "pay()"),
            # Execute
            ("ts-execute-service", "ts-order-service", "getOrderById()"),
            ("ts-execute-service", "ts-order-other-service", "getOrderById()"),
            # Food
            ("ts-food-service", "ts-food-map-service", "getFoodStoresByStationIds()"),
            ("ts-food-service", "ts-food-map-service", "getTrainFoodByTripId()"),
            ("ts-food-service", "ts-travel-service", "getRouteByTripId()"),
            ("ts-food-service", "ts-station-service", "queryById()"),
            # Consign
            ("ts-consign-service", "ts-consign-price-service", "getPriceByWeightAndRegion()"),
            # Route plan
            ("ts-route-plan-service", "ts-route-service", "queryByStartAndTerminal()"),
            ("ts-route-plan-service", "ts-travel-service", "getTripsByRouteId()"),
            ("ts-route-plan-service", "ts-travel2-service", "getTripsByRouteId()"),
            ("ts-route-plan-service", "ts-station-service", "queryForStationId()"),
            # Travel plan
            ("ts-travel-plan-service", "ts-route-plan-service", "searchCheapestResult()"),
            ("ts-travel-plan-service", "ts-travel-service", "query()"),
            ("ts-travel-plan-service", "ts-travel2-service", "query()"),
            ("ts-travel-plan-service", "ts-seat-service", "getLeftTicketOfInterval()"),
            ("ts-travel-plan-service", "ts-station-service", "queryById()"),
            # Voucher (Python)
            ("ts-voucher-service", "ts-order-service", "getOrderById()"),
            ("ts-voucher-service", "ts-order-other-service", "getOrderById()"),
            # Admin services
            ("ts-admin-order-service", "ts-order-service", "getAllOrders()"),
            ("ts-admin-order-service", "ts-order-other-service", "getAllOrders()"),
            ("ts-admin-basic-info-service", "ts-contacts-service", "getAllContacts()"),
            ("ts-admin-basic-info-service", "ts-station-service", "query()"),
            ("ts-admin-basic-info-service", "ts-train-service", "query()"),
            ("ts-admin-basic-info-service", "ts-route-service", "queryAll()"),
            ("ts-admin-basic-info-service", "ts-price-service", "findAllPriceConfig()"),
            ("ts-admin-route-service", "ts-route-service", "queryAll()"),
            ("ts-admin-travel-service", "ts-travel-service", "query()"),
            ("ts-admin-travel-service", "ts-travel2-service", "query()"),
            ("ts-admin-user-service", "ts-user-service", "getAllUsers()")
        ]
    }
]


# ===========================================================================
# COMPONENT DIAGRAM - Fork Architecture
# ===========================================================================

COMPONENT_DIAGRAM = {
    "id": "ttf-component-architecture",
    "name": "TrainTicketForkArchitecture",
    "description": "Overall microservice component architecture of TrainTicket-Fork",
    "components": [
        {"name": "ts-ui-dashboard", "layer": "Frontend"},
        {"name": "ts-auth-service", "layer": "Auth"},
        {"name": "ts-user-service", "layer": "Auth"},
        {"name": "ts-verification-code-service", "layer": "Auth"},
        {"name": "ts-preserve-service", "layer": "Business Orchestration"},
        {"name": "ts-preserve-other-service", "layer": "Business Orchestration"},
        {"name": "ts-cancel-service", "layer": "Business Orchestration"},
        {"name": "ts-rebook-service", "layer": "Business Orchestration"},
        {"name": "ts-travel-plan-service", "layer": "Business Orchestration"},
        {"name": "ts-travel-service", "layer": "Core Domain"},
        {"name": "ts-travel2-service", "layer": "Core Domain"},
        {"name": "ts-order-service", "layer": "Core Domain"},
        {"name": "ts-order-other-service", "layer": "Core Domain"},
        {"name": "ts-ticketinfo-service", "layer": "Core Domain"},
        {"name": "ts-basic-service", "layer": "Core Domain"},
        {"name": "ts-seat-service", "layer": "Core Domain"},
        {"name": "ts-route-service", "layer": "Data Services"},
        {"name": "ts-station-service", "layer": "Data Services"},
        {"name": "ts-train-service", "layer": "Data Services"},
        {"name": "ts-price-service", "layer": "Data Services"},
        {"name": "ts-contacts-service", "layer": "Data Services"},
        {"name": "ts-config-service", "layer": "Data Services"},
        {"name": "ts-inside-payment-service", "layer": "Payment"},
        {"name": "ts-payment-service", "layer": "Payment"},
        {"name": "ts-security-service", "layer": "Security"},
        {"name": "ts-assurance-service", "layer": "Insurance"},
        {"name": "ts-notification-service", "layer": "Notification"},
        {"name": "ts-execute-service", "layer": "Station Operations"},
        {"name": "ts-food-service", "layer": "Ancillary"},
        {"name": "ts-food-map-service", "layer": "Ancillary"},
        {"name": "ts-consign-service", "layer": "Ancillary"},
        {"name": "ts-consign-price-service", "layer": "Ancillary"},
        {"name": "ts-route-plan-service", "layer": "Planning"},
        {"name": "ts-voucher-service", "layer": "Ancillary"},
        {"name": "ts-avatar-service", "layer": "Ancillary"},
        {"name": "ts-news-service", "layer": "Ancillary"},
        {"name": "ts-admin-order-service", "layer": "Admin"},
        {"name": "ts-admin-basic-info-service", "layer": "Admin"},
        {"name": "ts-admin-route-service", "layer": "Admin"},
        {"name": "ts-admin-travel-service", "layer": "Admin"},
        {"name": "ts-admin-user-service", "layer": "Admin"}
    ],
    "dependencies": [
        # Auth layer
        ("ts-user-service", "ts-auth-service"),
        # Preserve orchestration (FORK: through ticketinfo, not basic)
        ("ts-preserve-service", "ts-ticketinfo-service"),
        ("ts-preserve-service", "ts-security-service"),
        ("ts-preserve-service", "ts-contacts-service"),
        ("ts-preserve-service", "ts-travel-service"),
        ("ts-preserve-service", "ts-seat-service"),
        ("ts-preserve-service", "ts-user-service"),
        ("ts-preserve-service", "ts-assurance-service"),
        ("ts-preserve-service", "ts-station-service"),
        ("ts-preserve-service", "ts-order-service"),
        ("ts-preserve-service", "ts-food-service"),
        ("ts-preserve-service", "ts-consign-service"),
        ("ts-preserve-service", "ts-notification-service"),
        # Preserve-other (FORK: through ticketinfo)
        ("ts-preserve-other-service", "ts-ticketinfo-service"),
        ("ts-preserve-other-service", "ts-travel2-service"),
        ("ts-preserve-other-service", "ts-seat-service"),
        ("ts-preserve-other-service", "ts-order-other-service"),
        ("ts-preserve-other-service", "ts-notification-service"),
        # Ticketinfo intermediary (FORK-SPECIFIC)
        ("ts-ticketinfo-service", "ts-basic-service"),
        # Basic aggregation
        ("ts-basic-service", "ts-station-service"),
        ("ts-basic-service", "ts-train-service"),
        ("ts-basic-service", "ts-route-service"),
        ("ts-basic-service", "ts-price-service"),
        # Travel (FORK: through ticketinfo)
        ("ts-travel-service", "ts-ticketinfo-service"),
        ("ts-travel-service", "ts-train-service"),
        ("ts-travel-service", "ts-route-service"),
        ("ts-travel-service", "ts-seat-service"),
        ("ts-travel-service", "ts-order-service"),
        # Travel2 (FORK: through ticketinfo)
        ("ts-travel2-service", "ts-ticketinfo-service"),
        ("ts-travel2-service", "ts-order-other-service"),
        # Seat
        ("ts-seat-service", "ts-travel-service"),
        ("ts-seat-service", "ts-travel2-service"),
        ("ts-seat-service", "ts-order-service"),
        ("ts-seat-service", "ts-order-other-service"),
        ("ts-seat-service", "ts-config-service"),
        # Order (calls station for ID conversion)
        ("ts-order-service", "ts-station-service"),
        ("ts-order-other-service", "ts-station-service"),
        # Security
        ("ts-security-service", "ts-order-service"),
        ("ts-security-service", "ts-order-other-service"),
        # Cancel
        ("ts-cancel-service", "ts-order-service"),
        ("ts-cancel-service", "ts-order-other-service"),
        ("ts-cancel-service", "ts-user-service"),
        ("ts-cancel-service", "ts-inside-payment-service"),
        ("ts-cancel-service", "ts-notification-service"),
        # Rebook
        ("ts-rebook-service", "ts-order-service"),
        ("ts-rebook-service", "ts-order-other-service"),
        ("ts-rebook-service", "ts-station-service"),
        ("ts-rebook-service", "ts-travel-service"),
        ("ts-rebook-service", "ts-travel2-service"),
        ("ts-rebook-service", "ts-seat-service"),
        ("ts-rebook-service", "ts-inside-payment-service"),
        # Payment
        ("ts-inside-payment-service", "ts-order-service"),
        ("ts-inside-payment-service", "ts-order-other-service"),
        ("ts-inside-payment-service", "ts-payment-service"),
        # Execute
        ("ts-execute-service", "ts-order-service"),
        ("ts-execute-service", "ts-order-other-service"),
        # Food (FORK: through food-map-service)
        ("ts-food-service", "ts-food-map-service"),
        ("ts-food-service", "ts-travel-service"),
        ("ts-food-service", "ts-station-service"),
        # Consign
        ("ts-consign-service", "ts-consign-price-service"),
        # Route plan
        ("ts-route-plan-service", "ts-route-service"),
        ("ts-route-plan-service", "ts-travel-service"),
        ("ts-route-plan-service", "ts-travel2-service"),
        ("ts-route-plan-service", "ts-station-service"),
        # Travel plan
        ("ts-travel-plan-service", "ts-route-plan-service"),
        ("ts-travel-plan-service", "ts-travel-service"),
        ("ts-travel-plan-service", "ts-travel2-service"),
        ("ts-travel-plan-service", "ts-seat-service"),
        ("ts-travel-plan-service", "ts-station-service"),
        # Voucher
        ("ts-voucher-service", "ts-order-service"),
        ("ts-voucher-service", "ts-order-other-service"),
        # Admin services
        ("ts-admin-order-service", "ts-order-service"),
        ("ts-admin-order-service", "ts-order-other-service"),
        ("ts-admin-basic-info-service", "ts-contacts-service"),
        ("ts-admin-basic-info-service", "ts-station-service"),
        ("ts-admin-basic-info-service", "ts-train-service"),
        ("ts-admin-basic-info-service", "ts-route-service"),
        ("ts-admin-basic-info-service", "ts-price-service"),
        ("ts-admin-route-service", "ts-route-service"),
        ("ts-admin-travel-service", "ts-travel-service"),
        ("ts-admin-travel-service", "ts-travel2-service"),
        ("ts-admin-user-service", "ts-user-service"),
    ]
}


# ===========================================================================
# GENERATOR FUNCTIONS
# ===========================================================================

def generate_class_diagram(svc_def):
    """Generate a Class diagram directory for a microservice."""
    diagram_id = svc_def["id"]
    diagram_dir = os.path.join(BASE_DIR, diagram_id)
    os.makedirs(diagram_dir, exist_ok=True)

    class_keys = {}
    class_count = 0
    interface_count = 0
    dep_count = 0

    for cls_name, cls_data in svc_def["classes"].items():
        cls_key = gen_key()
        class_keys[cls_name] = cls_key

        is_iface = cls_data.get("is_interface", False)
        implements = cls_data.get("implements", [])
        impl_keys = [class_keys.get(i, gen_key()) for i in implements]

        cls_json = make_class_json(
            name=cls_name,
            key=cls_key,
            fields=cls_data.get("fields", []),
            methods=cls_data.get("methods", []),
            implements=impl_keys if implements else None,
            is_interface=is_iface
        )
        write_json(diagram_dir, f"{cls_name}.json", cls_json)

        if is_iface:
            interface_count += 1
        else:
            class_count += 1

    # Generate dependency relationships
    for source, target in svc_def.get("dependencies", []):
        dep_key = gen_key()
        dep_json = make_dependency_json(
            name=f"{source}_uses_{target}",
            key=dep_key,
            source_key=class_keys.get(source, ""),
            target_key=class_keys.get(target, "")
        )
        write_json(diagram_dir, f"dependency_{dep_key[-8:]}.json", dep_json)
        dep_count += 1

    detected_types = {"uml:Class": class_count}
    element_counts = {"classes": class_count}
    total = class_count

    if interface_count > 0:
        detected_types["uml:Interface"] = interface_count
        element_counts["interfaces"] = interface_count
        total += interface_count
    if dep_count > 0:
        detected_types["uml:Dependency"] = dep_count
        element_counts["dependencies"] = dep_count
        total += dep_count

    diagram_info = make_diagram_info(
        diagram_id=diagram_id,
        categories=["Class"],
        primary="Class",
        is_class=True,
        is_behavioral=False,
        detected_types=detected_types,
        element_counts=element_counts,
        total=total,
        source_file=f"{diagram_id}.json"
    )
    write_json(diagram_dir, "_diagram_info.json", diagram_info)
    return diagram_id


def generate_sequence_diagram(seq_def):
    """Generate a Sequence diagram directory."""
    diagram_id = seq_def["id"]
    diagram_dir = os.path.join(BASE_DIR, diagram_id)
    os.makedirs(diagram_dir, exist_ok=True)

    lifeline_keys = {}
    lifelines_data = []
    for ll_name in seq_def["lifelines"]:
        ll_key = gen_key()
        lifeline_keys[ll_name] = ll_key
        lifelines_data.append({
            "name": ll_name,
            "key": ll_key,
            "represents": gen_key(),
            "coveredBy": []
        })

    messages_data = []
    fragments_data = []
    msg_count = 0
    for sender, receiver, msg_name, msg_sort in seq_def["messages"]:
        msg_key = gen_key()
        send_event_key = gen_key()
        recv_event_key = gen_key()

        messages_data.append({
            "name": msg_name,
            "key": msg_key,
            "messageSort": msg_sort,
            "sendEvent": send_event_key,
            "receiveEvent": recv_event_key,
            "connector": None,
            "signature": None
        })

        fragments_data.append({
            "key": send_event_key,
            "type": "uml:MessageOccurrenceSpecification",
            "name": None,
            "covered": lifeline_keys.get(sender, gen_key()),
            "enclosingInteraction": diagram_id,
            "message": msg_key,
            "execution": None
        })
        fragments_data.append({
            "key": recv_event_key,
            "type": "uml:MessageOccurrenceSpecification",
            "name": None,
            "covered": lifeline_keys.get(receiver, gen_key()),
            "enclosingInteraction": diagram_id,
            "message": msg_key,
            "execution": None
        })
        msg_count += 1

    interaction_key = gen_key()
    interaction_json = make_interaction_json(
        name=seq_def["name"],
        key=interaction_key,
        lifelines=lifelines_data,
        messages=messages_data,
        fragments=fragments_data
    )
    write_json(diagram_dir, f"interaction_{seq_def['name']}.json", interaction_json)

    for ll_name in seq_def["lifelines"]:
        class_json = make_class_json(
            name=ll_name,
            key=lifeline_keys[ll_name],
            fields=[],
            methods=[]
        )
        write_json(diagram_dir, f"{ll_name.replace('-', '_')}.json", class_json)

    detected_types = {
        "uml:Class": len(seq_def["lifelines"]),
        "uml:Interaction": 1,
        "uml:MessageOccurrenceSpecification": msg_count * 2
    }
    element_counts = {
        "classes": len(seq_def["lifelines"]),
        "interactions": 1
    }
    total = len(seq_def["lifelines"]) + 1

    diagram_info = make_diagram_info(
        diagram_id=diagram_id,
        categories=["Sequence"],
        primary="Sequence",
        is_class=False,
        is_behavioral=True,
        detected_types=detected_types,
        element_counts=element_counts,
        total=total,
        source_file=f"{diagram_id}.json"
    )
    write_json(diagram_dir, "_diagram_info.json", diagram_info)
    return diagram_id


def generate_activity_diagram(act_def):
    """Generate an Activity diagram directory."""
    diagram_id = act_def["id"]
    diagram_dir = os.path.join(BASE_DIR, diagram_id)
    os.makedirs(diagram_dir, exist_ok=True)

    node_keys = {}
    action_count = 0
    decision_count = 0
    fork_count = 0
    join_count = 0
    initial_count = 0
    final_count = 0

    for node in act_def["nodes"]:
        node_key = gen_key()
        node_keys[node["name"]] = node_key
        node_json = {
            "name": node["name"],
            "key": node_key,
            "type": node["type"]
        }
        write_json(diagram_dir, f"{node['name'].replace(' ', '_')}.json", node_json)

        if node["type"] == "uml:OpaqueAction":
            action_count += 1
        elif node["type"] == "uml:DecisionNode":
            decision_count += 1
        elif node["type"] == "uml:ForkNode":
            fork_count += 1
        elif node["type"] == "uml:JoinNode":
            join_count += 1
        elif node["type"] == "uml:InitialNode":
            initial_count += 1
        elif node["type"] == "uml:ActivityFinalNode":
            final_count += 1

    edge_count = 0
    for edge in act_def["edges"]:
        source_name = edge[0]
        target_name = edge[1]
        guard = edge[2] if len(edge) > 2 else None
        edge_key = gen_key()
        edge_json = {
            "name": f"{source_name}_to_{target_name}",
            "key": edge_key,
            "type": "uml:ControlFlow",
            "source": node_keys.get(source_name, ""),
            "target": node_keys.get(target_name, ""),
            "guard": guard
        }
        write_json(diagram_dir, f"controlflow_{edge_key[-8:]}.json", edge_json)
        edge_count += 1

    partition_count = 0
    for partition in act_def.get("partitions", []):
        part_key = gen_key()
        part_json = {
            "name": partition["name"],
            "key": part_key,
            "type": "uml:ActivityPartition",
            "nodes": [node_keys.get(a, "") for a in partition["actions"]]
        }
        write_json(diagram_dir, f"partition_{partition['name'].replace('-', '_')}.json", part_json)
        partition_count += 1

    activity_key = gen_key()
    activity_json = {
        "name": act_def["name"],
        "key": activity_key,
        "type": "uml:Activity",
        "description": act_def.get("description", ""),
        "nodes": list(node_keys.values()),
        "edges": edge_count
    }
    write_json(diagram_dir, f"activity_{act_def['name']}.json", activity_json)

    detected_types = {"uml:Activity": 1}
    element_counts = {"activities": 1}
    total = 1

    if action_count > 0:
        detected_types["uml:OpaqueAction"] = action_count
        element_counts["actions"] = action_count
        total += action_count
    if decision_count > 0:
        detected_types["uml:DecisionNode"] = decision_count
        element_counts["decisionNodes"] = decision_count
        total += decision_count
    if fork_count > 0:
        detected_types["uml:ForkNode"] = fork_count
        element_counts["forkNodes"] = fork_count
        total += fork_count
    if join_count > 0:
        detected_types["uml:JoinNode"] = join_count
        element_counts["joinNodes"] = join_count
        total += join_count
    if edge_count > 0:
        detected_types["uml:ControlFlow"] = edge_count
        element_counts["controlFlows"] = edge_count
        total += edge_count
    if partition_count > 0:
        detected_types["uml:ActivityPartition"] = partition_count
        element_counts["activityPartitions"] = partition_count
        total += partition_count

    diagram_info = make_diagram_info(
        diagram_id=diagram_id,
        categories=["Activity"],
        primary="Activity",
        is_class=False,
        is_behavioral=True,
        detected_types=detected_types,
        element_counts=element_counts,
        total=total,
        source_file=f"{diagram_id}.json"
    )
    write_json(diagram_dir, "_diagram_info.json", diagram_info)
    return diagram_id


def generate_communication_diagram(comm_def):
    """Generate a Communication diagram directory."""
    diagram_id = comm_def["id"]
    diagram_dir = os.path.join(BASE_DIR, diagram_id)
    os.makedirs(diagram_dir, exist_ok=True)

    object_keys = {}
    for obj_name in comm_def["objects"]:
        obj_key = gen_key()
        object_keys[obj_name] = obj_key
        obj_json = {
            "name": obj_name,
            "key": obj_key,
            "type": "uml:LifelineOrObject",
            "role": obj_name
        }
        write_json(diagram_dir, f"{obj_name.replace('-', '_')}.json", obj_json)

    link_count = 0
    for sender, receiver, msg_label in comm_def["links"]:
        link_key = gen_key()
        link_json = {
            "name": msg_label,
            "key": link_key,
            "type": "uml:Message",
            "sender": object_keys.get(sender, ""),
            "receiver": object_keys.get(receiver, ""),
            "messageLabel": msg_label
        }
        write_json(diagram_dir, f"message_{link_key[-8:]}.json", link_json)
        link_count += 1

    collab_key = gen_key()
    collab_json = {
        "name": comm_def["name"],
        "key": collab_key,
        "type": "uml:Collaboration",
        "description": comm_def.get("description", ""),
        "objects": list(object_keys.values()),
        "links": link_count
    }
    write_json(diagram_dir, f"collaboration_{comm_def['name']}.json", collab_json)

    detected_types = {
        "uml:Collaboration": 1,
        "uml:LifelineOrObject": len(comm_def["objects"]),
        "uml:Message": link_count
    }
    element_counts = {
        "collaborations": 1,
        "objects": len(comm_def["objects"]),
        "messages": link_count
    }
    total = 1 + len(comm_def["objects"]) + link_count

    diagram_info = make_diagram_info(
        diagram_id=diagram_id,
        categories=["Communication"],
        primary="Communication",
        is_class=False,
        is_behavioral=True,
        detected_types=detected_types,
        element_counts=element_counts,
        total=total,
        source_file=f"{diagram_id}.json"
    )
    write_json(diagram_dir, "_diagram_info.json", diagram_info)
    return diagram_id


def generate_component_diagram(comp_def):
    """Generate the overall Component architecture diagram."""
    diagram_id = comp_def["id"]
    diagram_dir = os.path.join(BASE_DIR, diagram_id)
    os.makedirs(diagram_dir, exist_ok=True)

    comp_keys = {}
    for comp in comp_def["components"]:
        comp_key = gen_key()
        comp_keys[comp["name"]] = comp_key
        comp_json = {
            "name": comp["name"],
            "key": comp_key,
            "type": "uml:Component",
            "layer": comp["layer"]
        }
        write_json(diagram_dir, f"component_{comp['name'].replace('-', '_')}.json", comp_json)

    dep_count = 0
    for source, target in comp_def["dependencies"]:
        dep_key = gen_key()
        dep_json = make_dependency_json(
            name=f"{source}_depends_on_{target}",
            key=dep_key,
            source_key=comp_keys.get(source, ""),
            target_key=comp_keys.get(target, "")
        )
        write_json(diagram_dir, f"dependency_{dep_key[-8:]}.json", dep_json)
        dep_count += 1

    detected_types = {
        "uml:Component": len(comp_def["components"]),
        "uml:Dependency": dep_count
    }
    element_counts = {
        "components": len(comp_def["components"]),
        "dependencies": dep_count
    }
    total = len(comp_def["components"]) + dep_count

    diagram_info = make_diagram_info(
        diagram_id=diagram_id,
        categories=["Component"],
        primary="Component",
        is_class=False,
        is_behavioral=False,
        detected_types=detected_types,
        element_counts=element_counts,
        total=total,
        source_file=f"{diagram_id}.json"
    )
    write_json(diagram_dir, "_diagram_info.json", diagram_info)
    return diagram_id


def generate_master_index(all_diagram_ids):
    """Generate a master index of all diagrams."""
    index = {
        "project": "TrainTicket-Fork Microservice Application",
        "source": "trainticket-fork (forked from FudanSELab/train-ticket)",
        "description": "UML dataset for architectural smell detection research. "
                       "This fork contains induced faults including: "
                       "ts-ticketinfo-service intermediary (extra hop), "
                       "ts-food-map-service (service decomposition change), "
                       "hardcoded service URLs (no service discovery), "
                       "UUID vs String ID type mismatches, "
                       "field name inconsistencies.",
        "total_diagrams": len(all_diagram_ids),
        "generation_method": "Automated extraction from source code analysis",
        "fork_specific_services": ["ts-ticketinfo-service", "ts-food-map-service"],
        "removed_from_original": ["ts-gateway-service", "ts-delivery-service",
                                   "ts-food-delivery-service", "ts-station-food-service",
                                   "ts-train-food-service", "ts-wait-order-service"],
        "diagrams": []
    }

    for did in all_diagram_ids:
        info_path = os.path.join(BASE_DIR, did, "_diagram_info.json")
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                info = json.load(f)
            index["diagrams"].append({
                "diagram_id": did,
                "primary_type": info["classification"]["primary"],
                "is_behavioral": info["classification"]["is_behavioral"],
                "total_elements": info["totalElements"]
            })

    write_json(BASE_DIR, "_master_index.json", index)


# ===========================================================================
# MAIN EXECUTION
# ===========================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TrainTicket-Fork UML Diagram Dataset Generator")
    print("=" * 70)

    all_ids = []

    # 1. Generate Class Diagrams for each microservice
    print("\n[1/5] Generating Class Diagrams...")
    for svc in ALL_SERVICES:
        did = generate_class_diagram(svc)
        all_ids.append(did)
        print(f"  Generated: {did}")

    # 2. Generate Sequence Diagrams
    print("\n[2/5] Generating Sequence Diagrams...")
    for seq in SEQUENCE_DIAGRAMS:
        did = generate_sequence_diagram(seq)
        all_ids.append(did)
        print(f"  Generated: {did}")

    # 3. Generate Activity Diagrams
    print("\n[3/5] Generating Activity Diagrams...")
    for act in ACTIVITY_DIAGRAMS:
        did = generate_activity_diagram(act)
        all_ids.append(did)
        print(f"  Generated: {did}")

    # 4. Generate Communication Diagrams
    print("\n[4/5] Generating Communication Diagrams...")
    for comm in COMMUNICATION_DIAGRAMS:
        did = generate_communication_diagram(comm)
        all_ids.append(did)
        print(f"  Generated: {did}")

    # 5. Generate Component Architecture Diagram
    print("\n[5/5] Generating Component Architecture Diagram...")
    did = generate_component_diagram(COMPONENT_DIAGRAM)
    all_ids.append(did)
    print(f"  Generated: {did}")

    # 6. Generate Master Index
    print("\nGenerating master index...")
    generate_master_index(all_ids)

    print(f"\n{'=' * 70}")
    print(f"COMPLETE: Generated {len(all_ids)} UML diagrams")
    print(f"Output directory: {BASE_DIR}")
    print(f"{'=' * 70}")

    # Summary stats
    seq_count = len(SEQUENCE_DIAGRAMS)
    act_count = len(ACTIVITY_DIAGRAMS)
    comm_count = len(COMMUNICATION_DIAGRAMS)

    print(f"\nBreakdown:")
    print(f"  Class Diagrams (Structural):        {len(ALL_SERVICES)}")
    print(f"  Sequence Diagrams (Behavioral):      {seq_count}")
    print(f"  Activity Diagrams (Behavioral):      {act_count}")
    print(f"  Communication Diagrams (Behavioral): {comm_count}")
    print(f"  Component Diagram (Structural):      1")
    print(f"  Total:                               {len(all_ids)}")
    print(f"\nFork-specific features captured:")
    print(f"  - ts-ticketinfo-service intermediary (extra call chain hop)")
    print(f"  - ts-food-map-service (new service decomposition)")
    print(f"  - Hardcoded URLs (no service discovery)")
    print(f"  - UUID vs String ID type mismatches")
    print(f"  - Station name conversion in rebook (potential fault)")

    # Count total JSON files
    total_files = 0
    for root, dirs, files in os.walk(BASE_DIR):
        total_files += sum(1 for f in files if f.endswith('.json'))
    print(f"\nTotal JSON files generated: {total_files}")
