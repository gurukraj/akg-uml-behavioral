#!/usr/bin/env python3
"""
UML Diagram Dataset Generator for Train-Ticket Microservice Benchmark
=====================================================================
Generates UML diagram JSON files in GenMyModel-compatible format.
All data extracted directly from Train-Ticket source code analysis.

Author: Research Dataset Generator
Source: FudanSELab/train-ticket (https://github.com/FudanSELab/train-ticket)
"""

import json
import os
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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
# DATA DEFINITIONS - All from verified source code analysis
# ===========================================================================

# ---- ts-order-service ----
ORDER_SERVICE = {
    "id": "tt-class-order-service",
    "classes": {
        "Order": {
            "fields": [
                ("id", "String"), ("boughtDate", "String"), ("travelDate", "String"),
                ("travelTime", "String"), ("accountId", "String"),
                ("contactsName", "String"), ("documentType", "int"),
                ("contactsDocumentNumber", "String"), ("trainNumber", "String"),
                ("coachNumber", "int"), ("seatClass", "int"),
                ("seatNumber", "String"), ("from", "String"), ("to", "String"),
                ("status", "int"), ("price", "String")
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
        },
        "OrderAlterInfo": {
            "fields": [
                ("accountId", "String"), ("previousOrderId", "String"),
                ("loginToken", "String"), ("newOrderInfo", "Order")
            ],
            "methods": []
        },
        "OrderController": {
            "fields": [("orderService", "OrderService")],
            "methods": [
                ("getTicketListByDateAndTripId", "HttpEntity", "Seat seatRequest, HttpHeaders headers"),
                ("createNewOrder", "HttpEntity", "Order createOrder, HttpHeaders headers"),
                ("queryOrders", "HttpEntity", "OrderInfo qi, HttpHeaders headers"),
                ("queryOrdersForRefresh", "HttpEntity", "OrderInfo qi, HttpHeaders headers"),
                ("calculateSoldTicket", "HttpEntity", "String travelDate, String trainNumber, HttpHeaders headers"),
                ("getOrderPrice", "HttpEntity", "String orderId, HttpHeaders headers"),
                ("payOrder", "HttpEntity", "String orderId, HttpHeaders headers"),
                ("getOrderById", "HttpEntity", "String orderId, HttpHeaders headers"),
                ("modifyOrder", "HttpEntity", "String orderId, int status, HttpHeaders headers"),
                ("securityInfoCheck", "HttpEntity", "String checkDate, String accountId, HttpHeaders headers"),
                ("saveOrderInfo", "HttpEntity", "Order orderInfo, HttpHeaders headers"),
                ("updateOrder", "HttpEntity", "Order order, HttpHeaders headers"),
                ("deleteOrder", "HttpEntity", "String orderId, HttpHeaders headers"),
                ("findAllOrder", "HttpEntity", "HttpHeaders headers"),
                ("addcreateNewOrder", "HttpEntity", "Order order, HttpHeaders headers")
            ]
        },
        "OrderService": {
            "fields": [],
            "methods": [
                ("findOrderById", "Response", "String id, HttpHeaders headers"),
                ("create", "Response", "Order newOrder, HttpHeaders headers"),
                ("saveChanges", "Response", "Order order, HttpHeaders headers"),
                ("cancelOrder", "Response", "String accountId, String orderId, HttpHeaders headers"),
                ("queryOrders", "Response", "OrderInfo qi, String accountId, HttpHeaders headers"),
                ("queryAlreadySoldOrders", "Response", "Date travelDate, String trainNumber, HttpHeaders headers"),
                ("getAllOrders", "Response", "HttpHeaders headers"),
                ("modifyOrder", "Response", "String orderId, int status, HttpHeaders headers"),
                ("getOrderPrice", "Response", "String orderId, HttpHeaders headers"),
                ("payOrder", "Response", "String orderId, HttpHeaders headers"),
                ("getOrderById", "Response", "String orderId, HttpHeaders headers"),
                ("checkSecurityAboutOrder", "Response", "Date checkDate, String accountId, HttpHeaders headers"),
                ("deleteOrder", "Response", "String orderId, HttpHeaders headers"),
                ("getSoldTickets", "Response", "Seat seatRequest, HttpHeaders headers"),
                ("addNewOrder", "Response", "Order order, HttpHeaders headers"),
                ("updateOrder", "Response", "Order order, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "OrderServiceImpl": {
            "fields": [
                ("orderRepository", "OrderRepository"),
                ("restTemplate", "RestTemplate"),
                ("discoveryClient", "DiscoveryClient")
            ],
            "methods": [
                ("findOrderById", "Response", "String id, HttpHeaders headers"),
                ("create", "Response", "Order newOrder, HttpHeaders headers"),
                ("saveChanges", "Response", "Order order, HttpHeaders headers"),
                ("queryOrders", "Response", "OrderInfo qi, String accountId, HttpHeaders headers"),
                ("getAllOrders", "Response", "HttpHeaders headers"),
                ("modifyOrder", "Response", "String orderId, int status, HttpHeaders headers"),
                ("getSoldTickets", "Response", "Seat seatRequest, HttpHeaders headers"),
                ("queryForStationId", "Response", "List<String> ids, HttpHeaders headers")
            ],
            "implements": "OrderService"
        },
        "OrderRepository": {
            "fields": [],
            "methods": [
                ("findById", "Optional<Order>", "String id"),
                ("findAll", "ArrayList<Order>", ""),
                ("findByAccountId", "ArrayList<Order>", "String accountId"),
                ("findByTravelDateAndTrainNumber", "ArrayList<Order>", "String travelDate, String trainNumber"),
                ("deleteById", "void", "String id")
            ],
            "is_interface": True
        }
    },
    "inter_service_calls": [
        ("ts-station-service", "POST /api/v1/stationservice/stations/namelist")
    ]
}

# ---- ts-travel-service ----
TRAVEL_SERVICE = {
    "id": "tt-class-travel-service",
    "classes": {
        "Trip": {
            "fields": [
                ("id", "String"), ("tripId", "TripId"), ("trainTypeName", "String"),
                ("routeId", "String"), ("startStationName", "String"),
                ("stationsName", "String"), ("terminalStationName", "String"),
                ("startTime", "String"), ("endTime", "String")
            ],
            "methods": []
        },
        "TripId": {
            "fields": [("type", "Type"), ("number", "String")],
            "methods": [("toString", "String", "")]
        },
        "Travel": {
            "fields": [
                ("trip", "Trip"), ("startPlace", "String"),
                ("endPlace", "String"), ("departureTime", "String")
            ],
            "methods": []
        },
        "AdminTrip": {
            "fields": [
                ("trip", "Trip"), ("trainType", "TrainType"), ("route", "Route")
            ],
            "methods": []
        },
        "TripAllDetail": {
            "fields": [("tripResponse", "TripResponse"), ("trip", "Trip")],
            "methods": []
        },
        "TravelController": {
            "fields": [("travelService", "TravelService")],
            "methods": [
                ("getTrainTypeByTripId", "HttpEntity", "String tripId, HttpHeaders headers"),
                ("getRouteByTripId", "HttpEntity", "String tripId, HttpHeaders headers"),
                ("getTripsByRouteId", "HttpEntity", "ArrayList<String> routeIds, HttpHeaders headers"),
                ("createTrip", "HttpEntity", "TravelInfo routeIds, HttpHeaders headers"),
                ("retrieve", "HttpEntity", "String tripId, HttpHeaders headers"),
                ("updateTrip", "HttpEntity", "TravelInfo info, HttpHeaders headers"),
                ("deleteTrip", "HttpEntity", "String tripId, HttpHeaders headers"),
                ("queryInfo", "HttpEntity", "TripInfo info, HttpHeaders headers"),
                ("queryInfoInparallel", "HttpEntity", "TripInfo info, HttpHeaders headers"),
                ("getTripAllDetailInfo", "HttpEntity", "TripAllDetailInfo gtdi, HttpHeaders headers"),
                ("queryAll", "HttpEntity", "HttpHeaders headers"),
                ("adminQueryAll", "HttpEntity", "HttpHeaders headers")
            ]
        },
        "TravelService": {
            "fields": [],
            "methods": [
                ("create", "Response", "TravelInfo info, HttpHeaders headers"),
                ("retrieve", "Response", "String tripId, HttpHeaders headers"),
                ("update", "Response", "TravelInfo info, HttpHeaders headers"),
                ("delete", "Response", "String tripId, HttpHeaders headers"),
                ("query", "Response", "TripInfo info, HttpHeaders headers"),
                ("getTripAllDetailInfo", "Response", "TripAllDetailInfo gtdi, HttpHeaders headers"),
                ("getRouteByTripId", "Response", "String tripId, HttpHeaders headers"),
                ("getTrainTypeByTripId", "Response", "String tripId, HttpHeaders headers"),
                ("queryAll", "Response", "HttpHeaders headers"),
                ("getTripByRoute", "Response", "ArrayList<String> routeIds, HttpHeaders headers"),
                ("adminQueryAll", "Response", "HttpHeaders headers")
            ],
            "is_interface": True
        },
        "TravelServiceImpl": {
            "fields": [
                ("repository", "TripRepository"),
                ("restTemplate", "RestTemplate"),
                ("discoveryClient", "DiscoveryClient")
            ],
            "methods": [
                ("create", "Response", "TravelInfo info, HttpHeaders headers"),
                ("query", "Response", "TripInfo info, HttpHeaders headers"),
                ("getTripAllDetailInfo", "Response", "TripAllDetailInfo gtdi, HttpHeaders headers"),
                ("getTrainTypeByName", "TrainType", "String trainTypeName, HttpHeaders headers"),
                ("getRouteByRouteId", "Route", "String routeId, HttpHeaders headers"),
                ("getRestTicketNumber", "Response", "String travelDate, String trainNumber, String startStationName, String endStationName, int seatType, int totalNum, List<String> stationList, HttpHeaders headers")
            ],
            "implements": "TravelService"
        },
        "TripRepository": {
            "fields": [],
            "methods": [
                ("findByTripId", "Trip", "TripId tripId"),
                ("deleteByTripId", "void", "TripId tripId"),
                ("findAll", "ArrayList<Trip>", ""),
                ("findByRouteId", "ArrayList<Trip>", "String routeId")
            ],
            "is_interface": True
        }
    },
    "inter_service_calls": [
        ("ts-basic-service", "POST /api/v1/basicservice/basic/travel"),
        ("ts-basic-service", "POST /api/v1/basicservice/basic/travels"),
        ("ts-train-service", "GET /api/v1/trainservice/trains/byName/{trainTypeName}"),
        ("ts-route-service", "GET /api/v1/routeservice/routes/{routeId}"),
        ("ts-seat-service", "POST /api/v1/seatservice/seats/left_tickets")
    ]
}

# ---- ts-preserve-service (Main Orchestrator - 10+ inter-service calls) ----
PRESERVE_SERVICE = {
    "id": "tt-class-preserve-service",
    "classes": {
        "PreserveController": {
            "fields": [("preserveService", "PreserveService")],
            "methods": [
                ("preserve", "HttpEntity", "OrderTicketsInfo oti, HttpHeaders headers")
            ]
        },
        "PreserveService": {
            "fields": [],
            "methods": [
                ("preserve", "Response", "OrderTicketsInfo oti, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "PreserveServiceImpl": {
            "fields": [
                ("restTemplate", "RestTemplate"),
                ("sendService", "RabbitSend"),
                ("discoveryClient", "DiscoveryClient")
            ],
            "methods": [
                ("preserve", "Response", "OrderTicketsInfo oti, HttpHeaders headers"),
                ("checkSecurity", "Response", "String accountId, HttpHeaders headers"),
                ("getContactsById", "Response", "String contactsId, HttpHeaders headers"),
                ("getTripAllDetailInformation", "Response", "TripAllDetailInfo gtdi, HttpHeaders headers"),
                ("dipatchSeat", "Response", "String date, String tripId, String startStation, String endStation, int seatType, int totalNum, List<String> stationList, HttpHeaders headers"),
                ("getAccount", "Response", "String accountId, HttpHeaders headers"),
                ("addAssuranceForOrder", "Response", "int assuranceType, String orderId, HttpHeaders headers"),
                ("queryForStationId", "Response", "String stationName, HttpHeaders headers"),
                ("createOrder", "Response", "Order coi, HttpHeaders headers"),
                ("createFoodOrder", "Response", "FoodOrder afi, HttpHeaders headers"),
                ("createConsign", "Response", "Consign cr, HttpHeaders headers")
            ],
            "implements": "PreserveService"
        }
    },
    "inter_service_calls": [
        ("ts-security-service", "GET /api/v1/securityservice/securityConfigs/{accountId}"),
        ("ts-contacts-service", "GET /api/v1/contactservice/contacts/{contactsId}"),
        ("ts-travel-service", "POST /api/v1/travelservice/trip_detail"),
        ("ts-basic-service", "POST /api/v1/basicservice/basic/travel"),
        ("ts-seat-service", "POST /api/v1/seatservice/seats"),
        ("ts-user-service", "GET /api/v1/userservice/users/id/{accountId}"),
        ("ts-assurance-service", "GET /api/v1/assuranceservice/assurances/{assuranceType}/{orderId}"),
        ("ts-station-service", "GET /api/v1/stationservice/stations/id/{stationName}"),
        ("ts-order-service", "POST /api/v1/orderservice/order"),
        ("ts-food-service", "POST /api/v1/foodservice/orders"),
        ("ts-consign-service", "POST /api/v1/consignservice/consigns")
    ]
}

# ---- ts-basic-service ----
BASIC_SERVICE = {
    "id": "tt-class-basic-service",
    "classes": {
        "BasicController": {
            "fields": [("basicService", "BasicService")],
            "methods": [
                ("queryForTravel", "HttpEntity", "Travel info, HttpHeaders headers"),
                ("queryForTravels", "HttpEntity", "List<Travel> infos, HttpHeaders headers"),
                ("queryForStationId", "HttpEntity", "String stationName, HttpHeaders headers")
            ]
        },
        "BasicService": {
            "fields": [],
            "methods": [
                ("queryForTravel", "Response", "Travel info, HttpHeaders headers"),
                ("queryForTravels", "Response", "List<Travel> infos, HttpHeaders headers"),
                ("queryForStationId", "Response", "String stationName, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "BasicServiceImpl": {
            "fields": [
                ("restTemplate", "RestTemplate"),
                ("discoveryClient", "DiscoveryClient")
            ],
            "methods": [
                ("queryForTravel", "Response", "Travel info, HttpHeaders headers"),
                ("queryForTravels", "Response", "List<Travel> infos, HttpHeaders headers"),
                ("queryForStationId", "Response", "String stationName, HttpHeaders headers"),
                ("queryTrainTypeByName", "TrainType", "String trainTypeName, HttpHeaders headers"),
                ("getRouteByRouteId", "Route", "String routeId, HttpHeaders headers"),
                ("queryPriceConfigByRouteIdAndTrainType", "PriceConfig", "String routeId, String trainType, HttpHeaders headers")
            ],
            "implements": "BasicService"
        }
    },
    "inter_service_calls": [
        ("ts-station-service", "GET /api/v1/stationservice/stations/id/{stationName}"),
        ("ts-station-service", "POST /api/v1/stationservice/stations/idlist"),
        ("ts-train-service", "POST /api/v1/trainservice/trains/byNames"),
        ("ts-train-service", "GET /api/v1/trainservice/trains/byName/{trainTypeName}"),
        ("ts-route-service", "POST /api/v1/routeservice/routes/byIds"),
        ("ts-route-service", "GET /api/v1/routeservice/routes/{routeId}"),
        ("ts-price-service", "GET /api/v1/priceservice/prices/{routeId}/{trainType}"),
        ("ts-price-service", "POST /api/v1/priceservice/prices/byRouteIdsAndTrainTypes")
    ]
}

# ---- ts-seat-service ----
SEAT_SERVICE = {
    "id": "tt-class-seat-service",
    "classes": {
        "SeatController": {
            "fields": [("seatService", "SeatService")],
            "methods": [
                ("create", "HttpEntity", "Seat seatRequest, HttpHeaders headers"),
                ("getLeftTicketOfInterval", "HttpEntity", "Seat seatRequest, HttpHeaders headers")
            ]
        },
        "SeatService": {
            "fields": [],
            "methods": [
                ("distributeSeat", "Response", "Seat seatRequest, HttpHeaders headers"),
                ("getLeftTicketOfInterval", "Response", "Seat seatRequest, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "SeatServiceImpl": {
            "fields": [
                ("restTemplate", "RestTemplate"),
                ("discoveryClient", "DiscoveryClient")
            ],
            "methods": [
                ("distributeSeat", "Response", "Seat seatRequest, HttpHeaders headers"),
                ("getLeftTicketOfInterval", "Response", "Seat seatRequest, HttpHeaders headers"),
                ("getDirectProportion", "double", "HttpHeaders headers")
            ],
            "implements": "SeatService"
        }
    },
    "inter_service_calls": [
        ("ts-order-service", "POST /api/v1/orderservice/order/tickets"),
        ("ts-order-other-service", "POST /api/v1/orderOtherService/orderOther/tickets"),
        ("ts-config-service", "GET /api/v1/configservice/configs/{configName}")
    ]
}

# ---- ts-cancel-service ----
CANCEL_SERVICE = {
    "id": "tt-class-cancel-service",
    "classes": {
        "CancelController": {
            "fields": [("cancelService", "CancelService")],
            "methods": [
                ("calculate", "HttpEntity", "String orderId, HttpHeaders headers"),
                ("cancelTicket", "HttpEntity", "String orderId, String loginId, HttpHeaders headers")
            ]
        },
        "CancelService": {
            "fields": [],
            "methods": [
                ("cancelOrder", "Response", "String orderId, String loginId, HttpHeaders headers"),
                ("calculateRefund", "Response", "String orderId, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "CancelServiceImpl": {
            "fields": [
                ("restTemplate", "RestTemplate"),
                ("discoveryClient", "DiscoveryClient")
            ],
            "methods": [
                ("cancelOrder", "Response", "String orderId, String loginId, HttpHeaders headers"),
                ("calculateRefund", "Response", "String orderId, HttpHeaders headers"),
                ("sendEmail", "boolean", "NotifyInfo notifyInfo, HttpHeaders headers"),
                ("drawbackMoney", "boolean", "String money, String userId, HttpHeaders headers"),
                ("getAccount", "Response", "String orderId, HttpHeaders headers"),
                ("getOrderByIdFromOrder", "Response", "String orderId, HttpHeaders headers"),
                ("getOrderByIdFromOrderOther", "Response", "String orderId, HttpHeaders headers")
            ],
            "implements": "CancelService"
        }
    },
    "inter_service_calls": [
        ("ts-notification-service", "POST /api/v1/notifyservice/notification/order_cancel_success"),
        ("ts-order-service", "PUT /api/v1/orderservice/order"),
        ("ts-order-service", "GET /api/v1/orderservice/order/{orderId}"),
        ("ts-order-other-service", "PUT /api/v1/orderOtherService/orderOther"),
        ("ts-order-other-service", "GET /api/v1/orderOtherService/orderOther/{orderId}"),
        ("ts-inside-payment-service", "GET /api/v1/inside_pay_service/inside_payment/drawback/{userId}/{money}"),
        ("ts-user-service", "GET /api/v1/userservice/users/id/{orderId}")
    ]
}

# ---- ts-rebook-service ----
REBOOK_SERVICE = {
    "id": "tt-class-rebook-service",
    "classes": {
        "RebookInfo": {
            "fields": [
                ("loginId", "String"), ("orderId", "String"),
                ("oldTripId", "String"), ("tripId", "String"),
                ("seatType", "int"), ("date", "String")
            ],
            "methods": []
        },
        "RebookController": {
            "fields": [("rebookService", "RebookService")],
            "methods": [
                ("payDifference", "HttpEntity", "RebookInfo info, HttpHeaders headers"),
                ("rebook", "HttpEntity", "RebookInfo info, HttpHeaders headers")
            ]
        },
        "RebookService": {
            "fields": [],
            "methods": [
                ("rebook", "Response", "RebookInfo info, HttpHeaders headers"),
                ("payDifference", "Response", "RebookInfo info, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "RebookServiceImpl": {
            "fields": [
                ("restTemplate", "RestTemplate"),
                ("discoveryClient", "DiscoveryClient")
            ],
            "methods": [
                ("rebook", "Response", "RebookInfo info, HttpHeaders headers"),
                ("payDifference", "Response", "RebookInfo info, HttpHeaders headers"),
                ("dipatchSeat", "Ticket", "String date, String tripId, String startStationId, String endStationId, int seatType, int totalNum, List<String> stations, HttpHeaders headers"),
                ("getTripAllDetailInformation", "Response", "TripAllDetailInfo gtdi, String tripId, HttpHeaders headers"),
                ("createOrder", "Response", "Order order, String tripId, HttpHeaders headers"),
                ("updateOrder", "Response", "Order info, String tripId, HttpHeaders headers"),
                ("deleteOrder", "Response", "String orderId, String tripId, HttpHeaders headers"),
                ("getOrderByRebookInfo", "Response", "RebookInfo info, HttpHeaders headers"),
                ("queryTrainTypeByName", "TrainType", "String trainTypeName, HttpHeaders headers"),
                ("getRouteByRouteId", "Route", "String routeId, HttpHeaders headers"),
                ("payDifferentMoney", "boolean", "String orderId, String tripId, String userId, String money, HttpHeaders headers"),
                ("drawBackMoney", "boolean", "String userId, String money, HttpHeaders headers")
            ],
            "implements": "RebookService"
        }
    },
    "inter_service_calls": [
        ("ts-travel-service", "POST /api/v1/travelservice/trip_detail"),
        ("ts-travel2-service", "POST /api/v1/travel2service/trip_detail"),
        ("ts-seat-service", "POST /api/v1/seatservice/seats"),
        ("ts-order-service", "POST /api/v1/orderservice/order"),
        ("ts-order-service", "PUT /api/v1/orderservice/order"),
        ("ts-order-service", "GET /api/v1/orderservice/order/{orderId}"),
        ("ts-order-other-service", "POST /api/v1/orderOtherService/orderOther"),
        ("ts-order-other-service", "PUT /api/v1/orderOtherService/orderOther"),
        ("ts-order-other-service", "GET /api/v1/orderOtherService/orderOther/{orderId}"),
        ("ts-train-service", "GET /api/v1/trainservice/trains/byName/{trainTypeName}"),
        ("ts-route-service", "GET /api/v1/routeservice/routes/{routeId}"),
        ("ts-inside-payment-service", "POST /api/v1/inside_pay_service/inside_payment/difference"),
        ("ts-inside-payment-service", "GET /api/v1/inside_pay_service/inside_payment/drawback/{userId}/{money}")
    ]
}

# ---- ts-inside-payment-service ----
INSIDE_PAYMENT_SERVICE = {
    "id": "tt-class-inside-payment-service",
    "classes": {
        "Payment": {
            "fields": [
                ("id", "String"), ("orderId", "String"),
                ("userId", "String"), ("price", "String"),
                ("type", "PaymentType")
            ],
            "methods": []
        },
        "Money": {
            "fields": [
                ("id", "String"), ("userId", "String"),
                ("money", "String"), ("type", "MoneyType")
            ],
            "methods": []
        },
        "PaymentInfo": {
            "fields": [
                ("userId", "String"), ("orderId", "String"),
                ("tripId", "String"), ("price", "String")
            ],
            "methods": []
        },
        "InsidePaymentController": {
            "fields": [("insidePaymentService", "InsidePaymentService")],
            "methods": [
                ("pay", "HttpEntity", "PaymentInfo info, HttpHeaders headers"),
                ("createAccount", "HttpEntity", "AccountInfo info, HttpHeaders headers"),
                ("addMoney", "HttpEntity", "String userId, String money, HttpHeaders headers"),
                ("queryPayment", "HttpEntity", "HttpHeaders headers"),
                ("queryAccount", "HttpEntity", "HttpHeaders headers"),
                ("drawBack", "HttpEntity", "String userId, String money, HttpHeaders headers"),
                ("payDifference", "HttpEntity", "PaymentInfo info, HttpHeaders headers"),
                ("queryAddMoney", "HttpEntity", "HttpHeaders headers")
            ]
        },
        "InsidePaymentService": {
            "fields": [],
            "methods": [
                ("pay", "Response", "PaymentInfo info, HttpHeaders headers"),
                ("createAccount", "Response", "AccountInfo info, HttpHeaders headers"),
                ("addMoney", "Response", "String userId, String money, HttpHeaders headers"),
                ("queryPayment", "Response", "HttpHeaders headers"),
                ("queryAccount", "Response", "HttpHeaders headers"),
                ("drawBack", "Response", "String userId, String money, HttpHeaders headers"),
                ("payDifference", "Response", "PaymentInfo info, HttpHeaders headers"),
                ("queryAddMoney", "Response", "HttpHeaders headers")
            ],
            "is_interface": True
        },
        "InsidePaymentServiceImpl": {
            "fields": [
                ("addMoneyRepository", "AddMoneyRepository"),
                ("paymentRepository", "PaymentRepository"),
                ("restTemplate", "RestTemplate")
            ],
            "methods": [
                ("pay", "Response", "PaymentInfo info, HttpHeaders headers"),
                ("createAccount", "Response", "AccountInfo info, HttpHeaders headers"),
                ("addMoney", "Response", "String userId, String money, HttpHeaders headers"),
                ("queryPayment", "Response", "HttpHeaders headers"),
                ("drawBack", "Response", "String userId, String money, HttpHeaders headers"),
                ("payDifference", "Response", "PaymentInfo info, HttpHeaders headers"),
                ("setOrderStatus", "Response", "String tripId, String orderId, HttpHeaders headers")
            ],
            "implements": "InsidePaymentService"
        }
    },
    "inter_service_calls": [
        ("ts-order-service", "GET /api/v1/orderservice/order/{orderId}"),
        ("ts-order-service", "GET /api/v1/orderservice/order/status/{orderId}/{orderStatus}"),
        ("ts-order-other-service", "GET /api/v1/orderOtherService/orderOther/{orderId}"),
        ("ts-order-other-service", "GET /api/v1/orderOtherService/orderOther/status/{orderId}/{orderStatus}"),
        ("ts-payment-service", "POST /api/v1/paymentservice/payment")
    ]
}

# ---- Leaf services with no inter-service calls ----
STATION_SERVICE = {
    "id": "tt-class-station-service",
    "classes": {
        "Station": {
            "fields": [("id", "String"), ("name", "String"), ("stayTime", "int")],
            "methods": [("setName", "void", "String name")]
        },
        "StationController": {
            "fields": [("stationService", "StationService")],
            "methods": [
                ("query", "HttpEntity", "HttpHeaders headers"),
                ("create", "ResponseEntity", "Station station, HttpHeaders headers"),
                ("update", "HttpEntity", "Station station, HttpHeaders headers"),
                ("delete", "ResponseEntity", "String stationsId, HttpHeaders headers"),
                ("queryForStationId", "HttpEntity", "String stationName, HttpHeaders headers"),
                ("queryForIdBatch", "HttpEntity", "List<String> stationNameList, HttpHeaders headers"),
                ("queryById", "HttpEntity", "String stationId, HttpHeaders headers"),
                ("queryForNameBatch", "HttpEntity", "List<String> stationIdList, HttpHeaders headers")
            ]
        },
        "StationService": {
            "fields": [],
            "methods": [
                ("create", "Response", "Station info, HttpHeaders headers"),
                ("exist", "boolean", "String stationName, HttpHeaders headers"),
                ("update", "Response", "Station info, HttpHeaders headers"),
                ("delete", "Response", "String stationsId, HttpHeaders headers"),
                ("query", "Response", "HttpHeaders headers"),
                ("queryForId", "Response", "String stationName, HttpHeaders headers"),
                ("queryForIdBatch", "Response", "List<String> nameList, HttpHeaders headers"),
                ("queryById", "Response", "String stationId, HttpHeaders headers"),
                ("queryByIdBatch", "Response", "List<String> stationIdList, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "StationServiceImpl": {
            "fields": [("repository", "StationRepository")],
            "methods": [
                ("create", "Response", "Station station, HttpHeaders headers"),
                ("exist", "boolean", "String stationName, HttpHeaders headers"),
                ("update", "Response", "Station info, HttpHeaders headers"),
                ("delete", "Response", "String stationsId, HttpHeaders headers"),
                ("query", "Response", "HttpHeaders headers"),
                ("queryForId", "Response", "String stationName, HttpHeaders headers"),
                ("queryForIdBatch", "Response", "List<String> nameList, HttpHeaders headers"),
                ("queryById", "Response", "String stationId, HttpHeaders headers"),
                ("queryByIdBatch", "Response", "List<String> idList, HttpHeaders headers")
            ],
            "implements": "StationService"
        },
        "StationRepository": {
            "fields": [],
            "methods": [
                ("findByName", "Station", "String name"),
                ("findByNames", "List<Station>", "List<String> names"),
                ("findById", "Optional<Station>", "String id"),
                ("findAll", "List<Station>", "")
            ],
            "is_interface": True
        }
    },
    "inter_service_calls": []
}

ROUTE_SERVICE = {
    "id": "tt-class-route-service",
    "classes": {
        "Route": {
            "fields": [
                ("id", "String"), ("stations", "List<String>"),
                ("distances", "List<Integer>"),
                ("startStation", "String"), ("endStation", "String")
            ],
            "methods": []
        },
        "RouteInfo": {
            "fields": [
                ("Id", "String"), ("startStation", "String"),
                ("endStation", "String"), ("stationList", "String"),
                ("distanceList", "String")
            ],
            "methods": []
        },
        "RouteController": {
            "fields": [("routeService", "RouteService")],
            "methods": [
                ("createAndModifyRoute", "ResponseEntity", "RouteInfo createAndModifyRouteInfo, HttpHeaders headers"),
                ("deleteRoute", "HttpEntity", "String routeId, HttpHeaders headers"),
                ("queryById", "HttpEntity", "String routeId, HttpHeaders headers"),
                ("queryByIds", "HttpEntity", "List<String> routeIds, HttpHeaders headers"),
                ("queryAll", "HttpEntity", "HttpHeaders headers"),
                ("queryByStartAndTerminal", "HttpEntity", "String start, String end, HttpHeaders headers")
            ]
        },
        "RouteService": {
            "fields": [],
            "methods": [
                ("getRouteByStartAndEnd", "Response", "String startId, String terminalId, HttpHeaders headers"),
                ("getAllRoutes", "Response", "HttpHeaders headers"),
                ("getRouteById", "Response", "String routeId, HttpHeaders headers"),
                ("getRouteByIds", "Response", "List<String> routeIds, HttpHeaders headers"),
                ("deleteRoute", "Response", "String routeId, HttpHeaders headers"),
                ("createAndModify", "Response", "RouteInfo info, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "RouteServiceImpl": {
            "fields": [("routeRepository", "RouteRepository")],
            "methods": [
                ("createAndModify", "Response", "RouteInfo info, HttpHeaders headers"),
                ("deleteRoute", "Response", "String routeId, HttpHeaders headers"),
                ("getRouteById", "Response", "String routeId, HttpHeaders headers"),
                ("getRouteByIds", "Response", "List<String> routeIds, HttpHeaders headers"),
                ("getRouteByStartAndEnd", "Response", "String startId, String terminalId, HttpHeaders headers"),
                ("getAllRoutes", "Response", "HttpHeaders headers")
            ],
            "implements": "RouteService"
        },
        "RouteRepository": {
            "fields": [],
            "methods": [
                ("findById", "Optional<Route>", "String id"),
                ("findByIds", "List<Route>", "List<String> ids"),
                ("findAll", "ArrayList<Route>", ""),
                ("removeRouteById", "void", "String id"),
                ("findByStartStationAndEndStation", "ArrayList<Route>", "String startStation, String endStation")
            ],
            "is_interface": True
        }
    },
    "inter_service_calls": []
}

TRAIN_SERVICE = {
    "id": "tt-class-train-service",
    "classes": {
        "TrainType": {
            "fields": [
                ("id", "String"), ("name", "String"),
                ("economyClass", "int"), ("confortClass", "int"),
                ("averageSpeed", "int")
            ],
            "methods": []
        },
        "TrainController": {
            "fields": [("trainService", "TrainService")],
            "methods": [
                ("create", "HttpEntity", "TrainType trainType, HttpHeaders headers"),
                ("retrieve", "HttpEntity", "String id, HttpHeaders headers"),
                ("retrieveByName", "HttpEntity", "String name, HttpHeaders headers"),
                ("update", "HttpEntity", "TrainType trainType, HttpHeaders headers"),
                ("delete", "HttpEntity", "String id, HttpHeaders headers"),
                ("query", "HttpEntity", "HttpHeaders headers")
            ]
        },
        "TrainService": {
            "fields": [],
            "methods": [
                ("create", "boolean", "TrainType trainType, HttpHeaders headers"),
                ("retrieve", "TrainType", "String id, HttpHeaders headers"),
                ("retrieveByName", "TrainType", "String name, HttpHeaders headers"),
                ("retrieveByNames", "List<TrainType>", "List<String> name, HttpHeaders headers"),
                ("update", "boolean", "TrainType trainType, HttpHeaders headers"),
                ("delete", "boolean", "String id, HttpHeaders headers"),
                ("query", "List<TrainType>", "HttpHeaders headers")
            ],
            "is_interface": True
        },
        "TrainServiceImpl": {
            "fields": [("repository", "TrainTypeRepository")],
            "methods": [
                ("create", "boolean", "TrainType trainType, HttpHeaders headers"),
                ("retrieve", "TrainType", "String id, HttpHeaders headers"),
                ("retrieveByName", "TrainType", "String name, HttpHeaders headers"),
                ("update", "boolean", "TrainType trainType, HttpHeaders headers"),
                ("delete", "boolean", "String id, HttpHeaders headers"),
                ("query", "List<TrainType>", "HttpHeaders headers")
            ],
            "implements": "TrainService"
        },
        "TrainTypeRepository": {
            "fields": [],
            "methods": [
                ("findById", "Optional<TrainType>", "String id"),
                ("findAll", "List<TrainType>", ""),
                ("deleteById", "void", "String id"),
                ("findByName", "TrainType", "String name"),
                ("findByNames", "List<TrainType>", "List<String> names")
            ],
            "is_interface": True
        }
    },
    "inter_service_calls": []
}

PRICE_SERVICE = {
    "id": "tt-class-price-service",
    "classes": {
        "PriceConfig": {
            "fields": [
                ("id", "String"), ("trainType", "String"),
                ("routeId", "String"), ("basicPriceRate", "double"),
                ("firstClassPriceRate", "double")
            ],
            "methods": []
        },
        "PriceController": {
            "fields": [("priceService", "PriceService")],
            "methods": [
                ("query", "HttpEntity", "String routeId, String trainType, HttpHeaders headers"),
                ("queryAll", "HttpEntity", "HttpHeaders headers"),
                ("create", "HttpEntity", "PriceConfig info, HttpHeaders headers"),
                ("delete", "HttpEntity", "String pricesId, HttpHeaders headers"),
                ("update", "HttpEntity", "PriceConfig info, HttpHeaders headers")
            ]
        },
        "PriceService": {
            "fields": [],
            "methods": [
                ("createNewPriceConfig", "Response", "PriceConfig priceConfig, HttpHeaders headers"),
                ("findByRouteIdAndTrainType", "Response", "String routeId, String trainType, HttpHeaders headers"),
                ("findAllPriceConfig", "Response", "HttpHeaders headers"),
                ("deletePriceConfig", "Response", "String pcId, HttpHeaders headers"),
                ("updatePriceConfig", "Response", "PriceConfig c, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "PriceServiceImpl": {
            "fields": [("priceConfigRepository", "PriceConfigRepository")],
            "methods": [
                ("createNewPriceConfig", "Response", "PriceConfig createAndModifyPriceConfig, HttpHeaders headers"),
                ("findByRouteIdAndTrainType", "Response", "String routeId, String trainType, HttpHeaders headers"),
                ("findAllPriceConfig", "Response", "HttpHeaders headers"),
                ("deletePriceConfig", "Response", "String pcId, HttpHeaders headers"),
                ("updatePriceConfig", "Response", "PriceConfig c, HttpHeaders headers")
            ],
            "implements": "PriceService"
        },
        "PriceConfigRepository": {
            "fields": [],
            "methods": [
                ("findById", "Optional<PriceConfig>", "String id"),
                ("findByRouteIdAndTrainType", "PriceConfig", "String routeId, String trainType"),
                ("findAll", "List<PriceConfig>", "")
            ],
            "is_interface": True
        }
    },
    "inter_service_calls": []
}

CONTACTS_SERVICE = {
    "id": "tt-class-contacts-service",
    "classes": {
        "Contacts": {
            "fields": [
                ("id", "String"), ("accountId", "String"), ("name", "String"),
                ("documentType", "int"), ("documentNumber", "String"),
                ("phoneNumber", "String")
            ],
            "methods": []
        },
        "ContactsController": {
            "fields": [("contactsService", "ContactsService")],
            "methods": [
                ("getAllContacts", "HttpEntity", "HttpHeaders headers"),
                ("createNewContacts", "HttpEntity", "Contacts contacts, HttpHeaders headers"),
                ("deleteContacts", "HttpEntity", "String contactsId, HttpHeaders headers"),
                ("modifyContacts", "HttpEntity", "Contacts contacts, HttpHeaders headers"),
                ("findContactsByAccountId", "HttpEntity", "String accountId, HttpHeaders headers"),
                ("getContactsByContactsId", "HttpEntity", "String id, HttpHeaders headers")
            ]
        },
        "ContactsService": {
            "fields": [],
            "methods": [
                ("createContacts", "Response", "Contacts contacts, HttpHeaders headers"),
                ("create", "Response", "Contacts addContacts, HttpHeaders headers"),
                ("delete", "Response", "String contactsId, HttpHeaders headers"),
                ("modify", "Response", "Contacts contacts, HttpHeaders headers"),
                ("getAllContacts", "Response", "HttpHeaders headers"),
                ("findContactsById", "Response", "String id, HttpHeaders headers"),
                ("findContactsByAccountId", "Response", "String accountId, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "ContactsServiceImpl": {
            "fields": [("contactsRepository", "ContactsRepository")],
            "methods": [
                ("createContacts", "Response", "Contacts contacts, HttpHeaders headers"),
                ("delete", "Response", "String contactsId, HttpHeaders headers"),
                ("modify", "Response", "Contacts contacts, HttpHeaders headers"),
                ("getAllContacts", "Response", "HttpHeaders headers"),
                ("findContactsById", "Response", "String id, HttpHeaders headers"),
                ("findContactsByAccountId", "Response", "String accountId, HttpHeaders headers")
            ],
            "implements": "ContactsService"
        },
        "ContactsRepository": {
            "fields": [],
            "methods": [
                ("findById", "Optional<Contacts>", "String id"),
                ("findByAccountId", "ArrayList<Contacts>", "String accountId"),
                ("deleteById", "void", "String id"),
                ("findAll", "ArrayList<Contacts>", "")
            ],
            "is_interface": True
        }
    },
    "inter_service_calls": []
}

CONFIG_SERVICE = {
    "id": "tt-class-config-service",
    "classes": {
        "Config": {
            "fields": [("name", "String"), ("value", "String"), ("description", "String")],
            "methods": []
        },
        "ConfigController": {
            "fields": [("configService", "ConfigService")],
            "methods": [
                ("queryAll", "HttpEntity", "HttpHeaders headers"),
                ("createConfig", "HttpEntity", "Config info, HttpHeaders headers"),
                ("updateConfig", "HttpEntity", "Config info, HttpHeaders headers"),
                ("deleteConfig", "HttpEntity", "String configName, HttpHeaders headers"),
                ("retrieve", "HttpEntity", "String configName, HttpHeaders headers")
            ]
        },
        "ConfigService": {
            "fields": [],
            "methods": [
                ("create", "Response", "Config info, HttpHeaders headers"),
                ("update", "Response", "Config info, HttpHeaders headers"),
                ("query", "Response", "String name, HttpHeaders headers"),
                ("delete", "Response", "String name, HttpHeaders headers"),
                ("queryAll", "Response", "HttpHeaders headers")
            ],
            "is_interface": True
        },
        "ConfigServiceImpl": {
            "fields": [("repository", "ConfigRepository")],
            "methods": [
                ("create", "Response", "Config info, HttpHeaders headers"),
                ("update", "Response", "Config info, HttpHeaders headers"),
                ("query", "Response", "String name, HttpHeaders headers"),
                ("delete", "Response", "String name, HttpHeaders headers"),
                ("queryAll", "Response", "HttpHeaders headers")
            ],
            "implements": "ConfigService"
        },
        "ConfigRepository": {
            "fields": [],
            "methods": [
                ("findByName", "Config", "String name"),
                ("findAll", "List<Config>", ""),
                ("deleteByName", "void", "String name")
            ],
            "is_interface": True
        }
    },
    "inter_service_calls": []
}

AUTH_SERVICE = {
    "id": "tt-class-auth-service",
    "classes": {
        "User": {
            "fields": [
                ("userId", "String"), ("username", "String"),
                ("password", "String"), ("roles", "Set<String>")
            ],
            "methods": [
                ("getAuthorities", "Collection<GrantedAuthority>", ""),
                ("isAccountNonExpired", "boolean", ""),
                ("isAccountNonLocked", "boolean", ""),
                ("isCredentialsNonExpired", "boolean", ""),
                ("isEnabled", "boolean", "")
            ]
        },
        "AuthDto": {
            "fields": [("userId", "String"), ("userName", "String"), ("password", "String")],
            "methods": []
        },
        "BasicAuthDto": {
            "fields": [("username", "String"), ("password", "String"), ("verificationCode", "String")],
            "methods": []
        },
        "TokenDto": {
            "fields": [("userId", "String"), ("username", "String"), ("token", "String")],
            "methods": []
        },
        "AuthController": {
            "fields": [("userService", "UserService")],
            "methods": [
                ("createDefaultUser", "HttpEntity", "AuthDto authDto")
            ]
        },
        "UserController": {
            "fields": [("tokenService", "TokenService")],
            "methods": [
                ("getToken", "ResponseEntity", "BasicAuthDto dao, HttpHeaders headers"),
                ("getAllUser", "ResponseEntity", "HttpHeaders headers"),
                ("deleteUserById", "ResponseEntity", "String userId, HttpHeaders headers")
            ]
        },
        "TokenService": {
            "fields": [],
            "methods": [
                ("getToken", "Response", "BasicAuthDto dto, HttpHeaders headers")
            ],
            "is_interface": True
        },
        "TokenServiceImpl": {
            "fields": [
                ("jwtProvider", "JWTProvider"),
                ("userRepository", "UserRepository"),
                ("authenticationManager", "AuthenticationManager"),
                ("restTemplate", "RestTemplate")
            ],
            "methods": [
                ("getToken", "Response", "BasicAuthDto dto, HttpHeaders headers")
            ],
            "implements": "TokenService"
        },
        "UserRepository": {
            "fields": [],
            "methods": [
                ("findByUsername", "Optional<User>", "String username"),
                ("deleteByUserId", "void", "String userId")
            ],
            "is_interface": True
        }
    },
    "inter_service_calls": [
        ("ts-verification-code-service", "GET /api/v1/verifycode/verify/{verifyCode}")
    ]
}

# Collect all services
ALL_SERVICES = [
    ORDER_SERVICE, TRAVEL_SERVICE, PRESERVE_SERVICE, BASIC_SERVICE,
    SEAT_SERVICE, CANCEL_SERVICE, REBOOK_SERVICE, INSIDE_PAYMENT_SERVICE,
    STATION_SERVICE, ROUTE_SERVICE, TRAIN_SERVICE, PRICE_SERVICE,
    CONTACTS_SERVICE, CONFIG_SERVICE, AUTH_SERVICE
]


# ===========================================================================
# SEQUENCE DIAGRAM DEFINITIONS - Behavioral diagrams from actual code flows
# ===========================================================================

SEQUENCE_DIAGRAMS = [
    {
        "id": "tt-seq-ticket-reserve",
        "name": "TicketReserve",
        "description": "Ticket reservation flow through ts-preserve-service orchestrating 10+ microservices",
        "lifelines": [
            "Client", "ts-preserve-service", "ts-security-service",
            "ts-contacts-service", "ts-travel-service", "ts-basic-service",
            "ts-seat-service", "ts-user-service", "ts-assurance-service",
            "ts-station-service", "ts-order-service", "ts-food-service",
            "ts-consign-service", "ts-notification-service"
        ],
        "messages": [
            ("Client", "ts-preserve-service", "POST /preserve", "synchCall"),
            ("ts-preserve-service", "ts-security-service", "GET /securityConfigs/{accountId}", "synchCall"),
            ("ts-security-service", "ts-preserve-service", "securityCheckResult", "reply"),
            ("ts-preserve-service", "ts-contacts-service", "GET /contacts/{contactsId}", "synchCall"),
            ("ts-contacts-service", "ts-preserve-service", "contactsInfo", "reply"),
            ("ts-preserve-service", "ts-travel-service", "POST /trip_detail", "synchCall"),
            ("ts-travel-service", "ts-basic-service", "POST /basic/travel", "synchCall"),
            ("ts-basic-service", "ts-station-service", "GET /stations/id/{name}", "synchCall"),
            ("ts-station-service", "ts-basic-service", "stationId", "reply"),
            ("ts-basic-service", "ts-travel-service", "travelResult", "reply"),
            ("ts-travel-service", "ts-preserve-service", "tripAllDetail", "reply"),
            ("ts-preserve-service", "ts-seat-service", "POST /seats", "synchCall"),
            ("ts-seat-service", "ts-order-service", "POST /order/tickets", "synchCall"),
            ("ts-order-service", "ts-seat-service", "soldTickets", "reply"),
            ("ts-seat-service", "ts-preserve-service", "seatAllocation", "reply"),
            ("ts-preserve-service", "ts-user-service", "GET /users/id/{accountId}", "synchCall"),
            ("ts-user-service", "ts-preserve-service", "userAccount", "reply"),
            ("ts-preserve-service", "ts-assurance-service", "GET /assurances/{type}/{orderId}", "synchCall"),
            ("ts-assurance-service", "ts-preserve-service", "assuranceResult", "reply"),
            ("ts-preserve-service", "ts-station-service", "GET /stations/id/{name}", "synchCall"),
            ("ts-station-service", "ts-preserve-service", "stationId", "reply"),
            ("ts-preserve-service", "ts-order-service", "POST /order", "synchCall"),
            ("ts-order-service", "ts-preserve-service", "createdOrder", "reply"),
            ("ts-preserve-service", "ts-food-service", "POST /orders", "synchCall"),
            ("ts-food-service", "ts-preserve-service", "foodOrderResult", "reply"),
            ("ts-preserve-service", "ts-consign-service", "POST /consigns", "synchCall"),
            ("ts-consign-service", "ts-preserve-service", "consignResult", "reply"),
            ("ts-preserve-service", "Client", "preserveResult", "reply")
        ]
    },
    {
        "id": "tt-seq-order-pay",
        "name": "OrderPayment",
        "description": "Order payment flow through ts-inside-payment-service",
        "lifelines": [
            "Client", "ts-inside-payment-service", "ts-order-service",
            "ts-order-other-service", "ts-payment-service"
        ],
        "messages": [
            ("Client", "ts-inside-payment-service", "POST /inside_payment", "synchCall"),
            ("ts-inside-payment-service", "ts-order-service", "GET /order/{orderId}", "synchCall"),
            ("ts-order-service", "ts-inside-payment-service", "orderInfo", "reply"),
            ("ts-inside-payment-service", "ts-payment-service", "POST /payment", "synchCall"),
            ("ts-payment-service", "ts-inside-payment-service", "paymentResult", "reply"),
            ("ts-inside-payment-service", "ts-order-service", "GET /order/status/{orderId}/{status}", "synchCall"),
            ("ts-order-service", "ts-inside-payment-service", "statusUpdateResult", "reply"),
            ("ts-inside-payment-service", "Client", "paymentSuccess", "reply")
        ]
    },
    {
        "id": "tt-seq-login",
        "name": "UserLogin",
        "description": "User login and token generation flow",
        "lifelines": [
            "Client", "ts-auth-service", "ts-verification-code-service"
        ],
        "messages": [
            ("Client", "ts-auth-service", "POST /users/login", "synchCall"),
            ("ts-auth-service", "ts-verification-code-service", "GET /verifycode/verify/{code}", "synchCall"),
            ("ts-verification-code-service", "ts-auth-service", "verifyResult", "reply"),
            ("ts-auth-service", "ts-auth-service", "authenticate(username, password)", "synchCall"),
            ("ts-auth-service", "ts-auth-service", "createToken(user)", "synchCall"),
            ("ts-auth-service", "Client", "TokenDto(userId, username, token)", "reply")
        ]
    },
    {
        "id": "tt-seq-cancel-order",
        "name": "CancelOrder",
        "description": "Order cancellation flow with refund processing",
        "lifelines": [
            "Client", "ts-cancel-service", "ts-order-service",
            "ts-order-other-service", "ts-user-service",
            "ts-inside-payment-service", "ts-notification-service"
        ],
        "messages": [
            ("Client", "ts-cancel-service", "GET /cancel/{orderId}/{loginId}", "synchCall"),
            ("ts-cancel-service", "ts-order-service", "GET /order/{orderId}", "synchCall"),
            ("ts-order-service", "ts-cancel-service", "orderInfo", "reply"),
            ("ts-cancel-service", "ts-user-service", "GET /users/id/{userId}", "synchCall"),
            ("ts-user-service", "ts-cancel-service", "userAccount", "reply"),
            ("ts-cancel-service", "ts-cancel-service", "calculateRefund(order)", "synchCall"),
            ("ts-cancel-service", "ts-inside-payment-service", "GET /inside_payment/drawback/{userId}/{money}", "synchCall"),
            ("ts-inside-payment-service", "ts-cancel-service", "drawbackResult", "reply"),
            ("ts-cancel-service", "ts-order-service", "PUT /order (status=CANCEL)", "synchCall"),
            ("ts-order-service", "ts-cancel-service", "updateResult", "reply"),
            ("ts-cancel-service", "ts-notification-service", "POST /notification/order_cancel_success", "synchCall"),
            ("ts-notification-service", "ts-cancel-service", "notifyResult", "reply"),
            ("ts-cancel-service", "Client", "cancelResult", "reply")
        ]
    },
    {
        "id": "tt-seq-rebook",
        "name": "Rebook",
        "description": "Ticket rebooking flow with seat reallocation and price difference handling",
        "lifelines": [
            "Client", "ts-rebook-service", "ts-order-service",
            "ts-travel-service", "ts-seat-service",
            "ts-train-service", "ts-route-service",
            "ts-inside-payment-service"
        ],
        "messages": [
            ("Client", "ts-rebook-service", "POST /rebook", "synchCall"),
            ("ts-rebook-service", "ts-order-service", "GET /order/{orderId}", "synchCall"),
            ("ts-order-service", "ts-rebook-service", "oldOrderInfo", "reply"),
            ("ts-rebook-service", "ts-travel-service", "POST /trip_detail", "synchCall"),
            ("ts-travel-service", "ts-rebook-service", "tripDetail", "reply"),
            ("ts-rebook-service", "ts-train-service", "GET /trains/byName/{name}", "synchCall"),
            ("ts-train-service", "ts-rebook-service", "trainType", "reply"),
            ("ts-rebook-service", "ts-route-service", "GET /routes/{routeId}", "synchCall"),
            ("ts-route-service", "ts-rebook-service", "routeInfo", "reply"),
            ("ts-rebook-service", "ts-seat-service", "POST /seats", "synchCall"),
            ("ts-seat-service", "ts-rebook-service", "newSeat", "reply"),
            ("ts-rebook-service", "ts-order-service", "PUT /order", "synchCall"),
            ("ts-order-service", "ts-rebook-service", "updatedOrder", "reply"),
            ("ts-rebook-service", "ts-inside-payment-service", "POST /inside_payment/difference", "synchCall"),
            ("ts-inside-payment-service", "ts-rebook-service", "payDiffResult", "reply"),
            ("ts-rebook-service", "Client", "rebookResult", "reply")
        ]
    },
    {
        "id": "tt-seq-query-left-tickets",
        "name": "QueryLeftTickets",
        "description": "Query available tickets for a route showing the deep call chain",
        "lifelines": [
            "Client", "ts-travel-service", "ts-basic-service",
            "ts-station-service", "ts-train-service",
            "ts-route-service", "ts-price-service",
            "ts-seat-service", "ts-order-service"
        ],
        "messages": [
            ("Client", "ts-travel-service", "POST /trips/left", "synchCall"),
            ("ts-travel-service", "ts-basic-service", "POST /basic/travels", "synchCall"),
            ("ts-basic-service", "ts-station-service", "POST /stations/idlist", "synchCall"),
            ("ts-station-service", "ts-basic-service", "stationIdMap", "reply"),
            ("ts-basic-service", "ts-train-service", "POST /trains/byNames", "synchCall"),
            ("ts-train-service", "ts-basic-service", "trainTypeList", "reply"),
            ("ts-basic-service", "ts-route-service", "POST /routes/byIds", "synchCall"),
            ("ts-route-service", "ts-basic-service", "routeList", "reply"),
            ("ts-basic-service", "ts-price-service", "POST /prices/byRouteIdsAndTrainTypes", "synchCall"),
            ("ts-price-service", "ts-basic-service", "priceConfigMap", "reply"),
            ("ts-basic-service", "ts-travel-service", "travelResultList", "reply"),
            ("ts-travel-service", "ts-seat-service", "POST /seats/left_tickets", "synchCall"),
            ("ts-seat-service", "ts-order-service", "POST /order/tickets", "synchCall"),
            ("ts-order-service", "ts-seat-service", "soldTicketInfo", "reply"),
            ("ts-seat-service", "ts-travel-service", "leftTicketCount", "reply"),
            ("ts-travel-service", "Client", "availableTrips", "reply")
        ]
    },
    {
        "id": "tt-seq-consign-create",
        "name": "ConsignCreate",
        "description": "Consignment creation with price calculation",
        "lifelines": [
            "Client", "ts-consign-service", "ts-consign-price-service"
        ],
        "messages": [
            ("Client", "ts-consign-service", "POST /consigns", "synchCall"),
            ("ts-consign-service", "ts-consign-price-service", "GET /consignprice/{weight}/{isWithin}", "synchCall"),
            ("ts-consign-price-service", "ts-consign-service", "calculatedPrice", "reply"),
            ("ts-consign-service", "ts-consign-service", "saveConsignRecord()", "synchCall"),
            ("ts-consign-service", "Client", "consignResult", "reply")
        ]
    },
    {
        "id": "tt-seq-enter-station",
        "name": "EnterStation",
        "description": "Ticket execution at station entrance",
        "lifelines": [
            "Client", "ts-execute-service", "ts-order-service",
            "ts-order-other-service"
        ],
        "messages": [
            ("Client", "ts-execute-service", "GET /execute/execute/{orderId}", "synchCall"),
            ("ts-execute-service", "ts-order-service", "GET /order/{orderId}", "synchCall"),
            ("ts-order-service", "ts-execute-service", "orderInfo", "reply"),
            ("ts-execute-service", "ts-order-service", "GET /order/status/{orderId}/6", "synchCall"),
            ("ts-order-service", "ts-execute-service", "statusUpdateResult", "reply"),
            ("ts-execute-service", "Client", "executeResult", "reply")
        ]
    }
]

# ===========================================================================
# ACTIVITY DIAGRAM DEFINITIONS
# ===========================================================================

ACTIVITY_DIAGRAMS = [
    {
        "id": "tt-activity-ticket-booking",
        "name": "TicketBookingWorkflow",
        "description": "Complete ticket booking workflow from search to payment",
        "nodes": [
            {"name": "InitialNode", "type": "uml:InitialNode"},
            {"name": "SearchTrips", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_TripsFound", "type": "uml:DecisionNode"},
            {"name": "SelectTrip", "type": "uml:OpaqueAction"},
            {"name": "SelectSeat", "type": "uml:OpaqueAction"},
            {"name": "SecurityCheck", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_SecurityPass", "type": "uml:DecisionNode"},
            {"name": "GetContactInfo", "type": "uml:OpaqueAction"},
            {"name": "ForkNode_OptionalServices", "type": "uml:ForkNode"},
            {"name": "AddAssurance", "type": "uml:OpaqueAction"},
            {"name": "AddFoodOrder", "type": "uml:OpaqueAction"},
            {"name": "AddConsignment", "type": "uml:OpaqueAction"},
            {"name": "JoinNode_OptionalServices", "type": "uml:JoinNode"},
            {"name": "CreateOrder", "type": "uml:OpaqueAction"},
            {"name": "ProcessPayment", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_PaymentSuccess", "type": "uml:DecisionNode"},
            {"name": "SendNotification", "type": "uml:OpaqueAction"},
            {"name": "FinalNode_Success", "type": "uml:ActivityFinalNode"},
            {"name": "FinalNode_NoTrips", "type": "uml:ActivityFinalNode"},
            {"name": "FinalNode_SecurityFail", "type": "uml:ActivityFinalNode"},
            {"name": "FinalNode_PaymentFail", "type": "uml:ActivityFinalNode"}
        ],
        "edges": [
            ("InitialNode", "SearchTrips"),
            ("SearchTrips", "DecisionNode_TripsFound"),
            ("DecisionNode_TripsFound", "SelectTrip", "trips found"),
            ("DecisionNode_TripsFound", "FinalNode_NoTrips", "no trips"),
            ("SelectTrip", "SelectSeat"),
            ("SelectSeat", "SecurityCheck"),
            ("SecurityCheck", "DecisionNode_SecurityPass"),
            ("DecisionNode_SecurityPass", "GetContactInfo", "pass"),
            ("DecisionNode_SecurityPass", "FinalNode_SecurityFail", "fail"),
            ("GetContactInfo", "ForkNode_OptionalServices"),
            ("ForkNode_OptionalServices", "AddAssurance"),
            ("ForkNode_OptionalServices", "AddFoodOrder"),
            ("ForkNode_OptionalServices", "AddConsignment"),
            ("AddAssurance", "JoinNode_OptionalServices"),
            ("AddFoodOrder", "JoinNode_OptionalServices"),
            ("AddConsignment", "JoinNode_OptionalServices"),
            ("JoinNode_OptionalServices", "CreateOrder"),
            ("CreateOrder", "ProcessPayment"),
            ("ProcessPayment", "DecisionNode_PaymentSuccess"),
            ("DecisionNode_PaymentSuccess", "SendNotification", "success"),
            ("DecisionNode_PaymentSuccess", "FinalNode_PaymentFail", "fail"),
            ("SendNotification", "FinalNode_Success")
        ],
        "partitions": [
            {"name": "ts-preserve-service", "actions": ["SearchTrips", "SelectTrip", "SelectSeat", "SecurityCheck", "GetContactInfo", "CreateOrder"]},
            {"name": "ts-security-service", "actions": ["SecurityCheck"]},
            {"name": "ts-seat-service", "actions": ["SelectSeat"]},
            {"name": "ts-assurance-service", "actions": ["AddAssurance"]},
            {"name": "ts-food-service", "actions": ["AddFoodOrder"]},
            {"name": "ts-consign-service", "actions": ["AddConsignment"]},
            {"name": "ts-inside-payment-service", "actions": ["ProcessPayment"]},
            {"name": "ts-notification-service", "actions": ["SendNotification"]}
        ]
    },
    {
        "id": "tt-activity-cancel-refund",
        "name": "CancelAndRefundWorkflow",
        "description": "Order cancellation and refund processing workflow",
        "nodes": [
            {"name": "InitialNode", "type": "uml:InitialNode"},
            {"name": "GetOrder", "type": "uml:OpaqueAction"},
            {"name": "DecisionNode_OrderFound", "type": "uml:DecisionNode"},
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
            ("DecisionNode_OrderFound", "CheckOrderStatus", "found"),
            ("DecisionNode_OrderFound", "FinalNode_NotFound", "not found"),
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
            {"name": "ts-cancel-service", "actions": ["GetOrder", "CheckOrderStatus", "CalculateRefund"]},
            {"name": "ts-order-service", "actions": ["GetOrder", "UpdateOrderStatus"]},
            {"name": "ts-user-service", "actions": ["GetUserAccount"]},
            {"name": "ts-inside-payment-service", "actions": ["DrawbackMoney"]},
            {"name": "ts-notification-service", "actions": ["SendCancelNotification"]}
        ]
    }
]

# ===========================================================================
# COMMUNICATION DIAGRAM DEFINITIONS
# ===========================================================================

COMMUNICATION_DIAGRAMS = [
    {
        "id": "tt-comm-preserve-orchestration",
        "name": "PreserveServiceOrchestration",
        "description": "Communication topology showing ts-preserve-service as hub orchestrator",
        "objects": [
            "ts-preserve-service", "ts-security-service", "ts-contacts-service",
            "ts-travel-service", "ts-basic-service", "ts-seat-service",
            "ts-user-service", "ts-assurance-service", "ts-station-service",
            "ts-order-service", "ts-food-service", "ts-consign-service"
        ],
        "links": [
            ("ts-preserve-service", "ts-security-service", "1: checkSecurity()"),
            ("ts-preserve-service", "ts-contacts-service", "2: getContactsById()"),
            ("ts-preserve-service", "ts-travel-service", "3: getTripAllDetail()"),
            ("ts-travel-service", "ts-basic-service", "3.1: queryForTravel()"),
            ("ts-basic-service", "ts-station-service", "3.1.1: queryForStationId()"),
            ("ts-preserve-service", "ts-seat-service", "4: distributeSeat()"),
            ("ts-seat-service", "ts-order-service", "4.1: getSoldTickets()"),
            ("ts-preserve-service", "ts-user-service", "5: getAccount()"),
            ("ts-preserve-service", "ts-assurance-service", "6: addAssurance()"),
            ("ts-preserve-service", "ts-station-service", "7: queryForStationId()"),
            ("ts-preserve-service", "ts-order-service", "8: createOrder()"),
            ("ts-preserve-service", "ts-food-service", "9: createFoodOrder()"),
            ("ts-preserve-service", "ts-consign-service", "10: createConsign()")
        ]
    },
    {
        "id": "tt-comm-basic-aggregation",
        "name": "BasicServiceAggregation",
        "description": "Communication topology showing ts-basic-service aggregating data from 4 services",
        "objects": [
            "ts-basic-service", "ts-station-service", "ts-train-service",
            "ts-route-service", "ts-price-service"
        ],
        "links": [
            ("ts-basic-service", "ts-station-service", "1: queryForStationId()"),
            ("ts-basic-service", "ts-station-service", "2: checkStationsExists()"),
            ("ts-basic-service", "ts-train-service", "3: queryTrainTypeByName()"),
            ("ts-basic-service", "ts-route-service", "4: getRouteByRouteId()"),
            ("ts-basic-service", "ts-price-service", "5: queryPriceConfig()")
        ]
    },
    {
        "id": "tt-comm-payment-flow",
        "name": "PaymentServiceFlow",
        "description": "Communication topology for payment processing",
        "objects": [
            "ts-inside-payment-service", "ts-order-service",
            "ts-order-other-service", "ts-payment-service"
        ],
        "links": [
            ("ts-inside-payment-service", "ts-order-service", "1: getOrder()"),
            ("ts-inside-payment-service", "ts-order-other-service", "1: getOrder()"),
            ("ts-inside-payment-service", "ts-payment-service", "2: pay()"),
            ("ts-inside-payment-service", "ts-order-service", "3: setOrderStatus()"),
            ("ts-inside-payment-service", "ts-order-other-service", "3: setOrderStatus()")
        ]
    }
]

# ===========================================================================
# COMPONENT DIAGRAM - Overall Architecture
# ===========================================================================

COMPONENT_DIAGRAM = {
    "id": "tt-component-architecture",
    "name": "TrainTicketArchitecture",
    "description": "Overall microservice component architecture of Train-Ticket system",
    "components": [
        {"name": "ts-gateway-service", "layer": "Gateway"},
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
        {"name": "ts-assurance-service", "layer": "Ancillary"},
        {"name": "ts-food-service", "layer": "Ancillary"},
        {"name": "ts-consign-service", "layer": "Ancillary"},
        {"name": "ts-consign-price-service", "layer": "Ancillary"},
        {"name": "ts-notification-service", "layer": "Infrastructure"},
        {"name": "ts-admin-basic-info-service", "layer": "Admin"},
        {"name": "ts-admin-order-service", "layer": "Admin"},
        {"name": "ts-admin-route-service", "layer": "Admin"},
        {"name": "ts-admin-travel-service", "layer": "Admin"},
        {"name": "ts-admin-user-service", "layer": "Admin"},
        {"name": "ts-execute-service", "layer": "Operations"},
        {"name": "ts-delivery-service", "layer": "Operations"},
        {"name": "ts-route-plan-service", "layer": "Planning"},
        {"name": "ts-food-delivery-service", "layer": "Ancillary"},
        {"name": "ts-station-food-service", "layer": "Ancillary"},
        {"name": "ts-train-food-service", "layer": "Ancillary"},
        {"name": "ts-wait-order-service", "layer": "Operations"},
        {"name": "ts-voucher-service", "layer": "Operations"},
        {"name": "ts-ticket-office-service", "layer": "Operations"},
        {"name": "ts-avatar-service", "layer": "Ancillary"},
        {"name": "ts-news-service", "layer": "Ancillary"}
    ],
    "dependencies": [
        ("ts-preserve-service", "ts-security-service"),
        ("ts-preserve-service", "ts-contacts-service"),
        ("ts-preserve-service", "ts-travel-service"),
        ("ts-preserve-service", "ts-basic-service"),
        ("ts-preserve-service", "ts-seat-service"),
        ("ts-preserve-service", "ts-user-service"),
        ("ts-preserve-service", "ts-assurance-service"),
        ("ts-preserve-service", "ts-station-service"),
        ("ts-preserve-service", "ts-order-service"),
        ("ts-preserve-service", "ts-food-service"),
        ("ts-preserve-service", "ts-consign-service"),
        ("ts-cancel-service", "ts-order-service"),
        ("ts-cancel-service", "ts-order-other-service"),
        ("ts-cancel-service", "ts-inside-payment-service"),
        ("ts-cancel-service", "ts-user-service"),
        ("ts-cancel-service", "ts-notification-service"),
        ("ts-rebook-service", "ts-travel-service"),
        ("ts-rebook-service", "ts-travel2-service"),
        ("ts-rebook-service", "ts-seat-service"),
        ("ts-rebook-service", "ts-order-service"),
        ("ts-rebook-service", "ts-order-other-service"),
        ("ts-rebook-service", "ts-train-service"),
        ("ts-rebook-service", "ts-route-service"),
        ("ts-rebook-service", "ts-inside-payment-service"),
        ("ts-travel-service", "ts-basic-service"),
        ("ts-travel-service", "ts-train-service"),
        ("ts-travel-service", "ts-route-service"),
        ("ts-travel-service", "ts-seat-service"),
        ("ts-travel2-service", "ts-route-service"),
        ("ts-travel2-service", "ts-train-service"),
        ("ts-travel2-service", "ts-seat-service"),
        ("ts-basic-service", "ts-station-service"),
        ("ts-basic-service", "ts-train-service"),
        ("ts-basic-service", "ts-route-service"),
        ("ts-basic-service", "ts-price-service"),
        ("ts-seat-service", "ts-order-service"),
        ("ts-seat-service", "ts-order-other-service"),
        ("ts-seat-service", "ts-config-service"),
        ("ts-inside-payment-service", "ts-order-service"),
        ("ts-inside-payment-service", "ts-order-other-service"),
        ("ts-inside-payment-service", "ts-payment-service"),
        ("ts-security-service", "ts-order-service"),
        ("ts-security-service", "ts-order-other-service"),
        ("ts-food-service", "ts-train-food-service"),
        ("ts-food-service", "ts-travel-service"),
        ("ts-food-service", "ts-station-food-service"),
        ("ts-consign-service", "ts-consign-price-service"),
        ("ts-auth-service", "ts-verification-code-service"),
        ("ts-user-service", "ts-auth-service"),
        ("ts-travel-plan-service", "ts-route-plan-service"),
        ("ts-travel-plan-service", "ts-seat-service"),
        ("ts-travel-plan-service", "ts-travel-service"),
        ("ts-travel-plan-service", "ts-travel2-service"),
        ("ts-travel-plan-service", "ts-train-service"),
        ("ts-route-plan-service", "ts-travel-service"),
        ("ts-route-plan-service", "ts-travel2-service"),
        ("ts-route-plan-service", "ts-route-service"),
        ("ts-execute-service", "ts-order-service"),
        ("ts-execute-service", "ts-order-other-service"),
        ("ts-admin-basic-info-service", "ts-contacts-service"),
        ("ts-admin-basic-info-service", "ts-station-service"),
        ("ts-admin-basic-info-service", "ts-train-service"),
        ("ts-admin-basic-info-service", "ts-config-service"),
        ("ts-admin-basic-info-service", "ts-price-service"),
        ("ts-admin-order-service", "ts-order-service"),
        ("ts-admin-order-service", "ts-order-other-service"),
        ("ts-admin-route-service", "ts-route-service"),
        ("ts-admin-route-service", "ts-station-service"),
        ("ts-admin-travel-service", "ts-travel-service"),
        ("ts-admin-travel-service", "ts-travel2-service"),
        ("ts-admin-travel-service", "ts-station-service"),
        ("ts-admin-travel-service", "ts-train-service"),
        ("ts-admin-travel-service", "ts-route-service"),
        ("ts-admin-user-service", "ts-user-service"),
        ("ts-food-delivery-service", "ts-station-food-service"),
        ("ts-voucher-service", "ts-order-service"),
        ("ts-voucher-service", "ts-order-other-service")
    ]
}


# ===========================================================================
# GENERATION FUNCTIONS
# ===========================================================================

def generate_class_diagram(service_def):
    """Generate a Class diagram directory for a microservice."""
    diagram_id = service_def["id"]
    diagram_dir = os.path.join(BASE_DIR, diagram_id)
    os.makedirs(diagram_dir, exist_ok=True)

    classes_data = service_def["classes"]
    class_keys = {}
    dependencies = []
    associations = []

    # Generate class JSONs
    class_count = 0
    interface_count = 0
    dep_count = 0
    assoc_count = 0

    for class_name, class_def in classes_data.items():
        key = gen_key()
        class_keys[class_name] = key
        is_iface = class_def.get("is_interface", False)

        impl_keys = []
        if "implements" in class_def:
            impl_name = class_def["implements"]
            if impl_name in class_keys:
                impl_keys = [class_keys[impl_name]]

        class_json = make_class_json(
            name=class_name,
            key=key,
            fields=class_def.get("fields", []),
            methods=class_def.get("methods", []),
            implements=impl_keys,
            is_interface=is_iface
        )
        write_json(diagram_dir, f"{class_name}.json", class_json)

        if is_iface:
            interface_count += 1
        else:
            class_count += 1

    # Generate dependency JSONs for inter-service calls
    for target_service, endpoint in service_def.get("inter_service_calls", []):
        dep_key = gen_key()
        dep_name = f"calls_{target_service.replace('-', '_')}"
        dep_json = make_dependency_json(dep_name, dep_key, diagram_id, target_service)
        dep_json["endpoint"] = endpoint
        write_json(diagram_dir, f"dependency_{dep_name}_{dep_key[-8:]}.json", dep_json)
        dep_count += 1

    # Generate associations between classes (Controller->Service, ServiceImpl->Repository)
    for class_name, class_def in classes_data.items():
        for fname, ftype in class_def.get("fields", []):
            if ftype in class_keys and ftype != class_name:
                assoc_key = gen_key()
                assoc_json = make_association_json(
                    name=f"{class_name}_uses_{ftype}",
                    key=assoc_key,
                    source_key=class_keys[class_name],
                    target_key=class_keys[ftype]
                )
                write_json(diagram_dir, f"association_{class_name}_{ftype}_{assoc_key[-8:]}.json", assoc_json)
                assoc_count += 1

    # Determine classification
    has_behavioral = any(
        any(m[0] in ["preserve", "cancel", "rebook", "pay", "execute"]
            for m in cd.get("methods", []))
        for cd in classes_data.values()
    )

    detected_types = {"uml:Class": class_count}
    element_counts = {"classes": class_count}
    if interface_count > 0:
        detected_types["uml:Interface"] = interface_count
        element_counts["interfaces"] = interface_count
    if dep_count > 0:
        detected_types["uml:Dependency"] = dep_count
        element_counts["dependencies"] = dep_count
    if assoc_count > 0:
        detected_types["uml:Association"] = assoc_count
        element_counts["associations"] = assoc_count

    total = class_count + interface_count + dep_count + assoc_count

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

        # Create MessageOccurrenceSpecification fragments
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

    # Create lifeline class JSONs
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

    # Generate control flow edges
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

    # Generate activity partitions
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

    # Activity container
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

    # Collaboration container
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
        "project": "Train-Ticket Microservice Benchmark",
        "source": "https://github.com/FudanSELab/train-ticket",
        "total_diagrams": len(all_diagram_ids),
        "generation_method": "Automated extraction from source code analysis",
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
    print("Train-Ticket UML Diagram Dataset Generator")
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
    class_count = sum(1 for s in ALL_SERVICES for _ in [1])
    seq_count = len(SEQUENCE_DIAGRAMS)
    act_count = len(ACTIVITY_DIAGRAMS)
    comm_count = len(COMMUNICATION_DIAGRAMS)

    print(f"\nBreakdown:")
    print(f"  Class Diagrams (Structural):       {len(ALL_SERVICES)}")
    print(f"  Sequence Diagrams (Behavioral):     {seq_count}")
    print(f"  Activity Diagrams (Behavioral):     {act_count}")
    print(f"  Communication Diagrams (Behavioral):{comm_count}")
    print(f"  Component Diagram (Structural):     1")
    print(f"  Total:                              {len(all_ids)}")
