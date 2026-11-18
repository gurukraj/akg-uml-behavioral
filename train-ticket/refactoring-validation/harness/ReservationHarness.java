import com.fasterxml.jackson.databind.ObjectMapper;
import edu.fudan.common.entity.*;
import edu.fudan.common.util.JsonUtils;
import edu.fudan.common.util.Response;
import org.springframework.amqp.core.AmqpTemplate;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.*;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Executes the real service classes of one Train-Ticket tree (original or refactored) with
 * Mockito stand-ins for RestTemplate (HTTP) and AmqpTemplate (RabbitMQ) and records every
 * synchronous remote call and every asynchronous message. A fixed delay per synchronous call can
 * be configured to estimate the blocking time of the reservation request.
 *
 * Usage: java ReservationHarness <label> <delayMsPerSyncCall>
 */
public class ReservationHarness {

    static final ObjectMapper M = new ObjectMapper();
    static final List<String> syncCalls = new ArrayList<>();
    static final List<String> asyncMessages = new ArrayList<>();
    static long delayMs;

    public static void main(String[] args) throws Exception {
        String label = args[0];
        delayMs = Long.parseLong(args[1]);
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("tree", label);
        out.put("delay_ms_per_sync_call", delayMs);
        out.put("preserve", runPreserve());
        out.put("basic_queryForTravel", runBasic());
        out.put("async_listeners", runListeners());
        System.out.println(M.writerWithDefaultPrettyPrinter().writeValueAsString(out));
    }

    // ------------------------------------------------------------------ preserve (reservation)
    static Map<String, Object> runPreserve() throws Exception {
        syncCalls.clear(); asyncMessages.clear();
        Object impl = Class.forName("preserve.service.PreserveServiceImpl").getDeclaredConstructor().newInstance();
        RestTemplate rt = restTemplateMock();
        AmqpTemplate amqp = amqpMock();
        inject(impl, "restTemplate", rt);
        Object rabbitSend = Class.forName("preserve.mq.RabbitSend").getDeclaredConstructor().newInstance();
        inject(rabbitSend, "rabbitTemplate", amqp);
        inject(impl, "sendService", rabbitSend);
        boolean refactored = false;
        try {
            Object publisher = Class.forName("preserve.mq.OrderEventPublisher").getDeclaredConstructor().newInstance();
            inject(publisher, "rabbitTemplate", amqp);
            inject(impl, "orderEventPublisher", publisher);
            refactored = true;
        } catch (ClassNotFoundException e) {
            // original tree: no event publisher
        }

        OrderTicketsInfo oti = M.convertValue(map(
                "accountId", "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f", "contactsId", "a3f1f9a4-27a5-4b16-9e2c-4b8a8b0f3d10",
                "tripId", "G1234", "seatType", 2, "date", "2026-10-10", "from", "shanghai", "to", "suzhou",
                "assurance", 1, "foodType", 1, "foodName", "Bone Soup", "foodPrice", 2.5,
                "consigneeName", "Alice", "consigneePhone", "123456", "consigneeWeight", 5.0, "within", false,
                "handleDate", "2026-10-09"), OrderTicketsInfo.class);
        HttpHeaders headers = new HttpHeaders();
        headers.set(HttpHeaders.AUTHORIZATION, "Bearer test-token");

        long t0 = System.nanoTime();
        Method m = impl.getClass().getMethod("preserve", OrderTicketsInfo.class, HttpHeaders.class);
        Response<?> r = (Response<?>) m.invoke(impl, oti, headers);
        long elapsed = (System.nanoTime() - t0) / 1_000_000;

        Map<String, Object> res = new LinkedHashMap<>();
        res.put("event_publisher_present", refactored);
        res.put("response_status", r.getStatus());
        res.put("response_message", r.getMsg());
        res.put("sync_calls_total", syncCalls.size());
        res.put("sync_calls", new ArrayList<>(syncCalls));
        res.put("distinct_services_called", new TreeSet<>(services(syncCalls)));
        res.put("async_messages", new ArrayList<>(asyncMessages));
        res.put("blocking_time_ms", elapsed);
        return res;
    }

    // ------------------------------------------------------------------ basic-service
    static Map<String, Object> runBasic() throws Exception {
        syncCalls.clear();
        Object impl = Class.forName("fdse.microservice.service.BasicServiceImpl").getDeclaredConstructor().newInstance();
        RestTemplate rt = restTemplateMock();
        inject(impl, "restTemplate", rt);
        Object cache = null;
        try {
            cache = Class.forName("fdse.microservice.cache.StationReferenceCache").getDeclaredConstructor().newInstance();
            inject(cache, "restTemplate", rt);
            inject(impl, "stationReferenceCache", cache);
        } catch (ClassNotFoundException e) {
            // original tree: no local station data
        }
        Travel travel = M.convertValue(map("startPlace", "shanghai", "endPlace", "suzhou", "departureTime", "2026-10-10",
                "trip", map("trainTypeName", "GaoTieOne", "routeId", "r1")), Travel.class);
        Method q = impl.getClass().getMethod("queryForTravel", Travel.class, HttpHeaders.class);

        Map<String, Object> res = new LinkedHashMap<>();
        res.put("local_station_data_present", cache != null);
        q.invoke(impl, travel, new HttpHeaders());                 // first request (cold start in refactored tree)
        res.put("first_request_calls", new ArrayList<>(syncCalls));
        syncCalls.clear();
        Response<?> r = (Response<?>) q.invoke(impl, travel, new HttpHeaders());   // steady state
        res.put("steady_state_calls", new ArrayList<>(syncCalls));
        res.put("steady_state_calls_to_station_service", syncCalls.stream().filter(c -> c.startsWith("ts-station-service")).count());
        res.put("steady_state_response_status", r.getStatus());
        res.put("steady_state_response_message", r.getMsg());

        if (cache != null) {   // event-driven update of the local copy
            Method on = cache.getClass().getMethod("onStationChanged", String.class);
            Method exists = cache.getClass().getMethod("exists", String.class);
            on.invoke(cache, "{\"operation\":\"UPSERT\",\"stationId\":\"s9\",\"stationName\":\"Nan Jing\"}");
            boolean added = (Boolean) exists.invoke(cache, "Nan Jing");
            on.invoke(cache, "{\"operation\":\"UPSERT\",\"stationId\":\"s9\",\"stationName\":\"Nanjing South\"}");
            boolean renamedOld = (Boolean) exists.invoke(cache, "Nan Jing");
            boolean renamedNew = (Boolean) exists.invoke(cache, "Nanjing South");
            on.invoke(cache, "{\"operation\":\"DELETE\",\"stationId\":\"s9\",\"stationName\":\"Nanjing South\"}");
            boolean deleted = !(Boolean) exists.invoke(cache, "Nanjing South");
            res.put("event_update_checks", map("create_visible", added, "rename_removes_old_name", !renamedOld,
                    "rename_adds_new_name", renamedNew, "delete_removes_station", deleted));
        }
        return res;
    }

    // ------------------------------------------------------------------ asynchronous consumers
    static Map<String, Object> runListeners() throws Exception {
        Map<String, Object> res = new LinkedHashMap<>();
        OrderCreatedEventHolder ev = new OrderCreatedEventHolder();
        String[][] specs = {
                {"assurance.mq.OrderCreatedListener", "assuranceService", "assurance.service.AssuranceService"},
                {"foodsearch.mq.OrderCreatedListener", "foodService", "foodsearch.service.FoodService"},
                {"consign.mq.OrderCreatedListener", "consignService", "consign.service.ConsignService"}};
        for (String[] s : specs) {
            Class<?> lc;
            try {
                lc = Class.forName(s[0]);
            } catch (ClassNotFoundException e) {
                res.put(s[0], "not present (synchronous call from ts-preserve-service)");
                continue;
            }
            Object listener = lc.getDeclaredConstructor().newInstance();
            Object svc = mock(Class.forName(s[2]));
            inject(listener, s[1], svc);
            lc.getMethod("onOrderCreated", String.class).invoke(listener, ev.json());
            List<String> invoked = new ArrayList<>();
            mockingDetails(svc).getInvocations().forEach(inv -> invoked.add(inv.getMethod().getName() + " " + Arrays.toString(argsSummary(inv.getArguments()))));
            res.put(s[0], invoked);
        }
        return res;
    }

    static class OrderCreatedEventHolder {
        String json() throws Exception {
            Class<?> c = Class.forName("edu.fudan.common.entity.OrderCreatedEvent");
            Object e = M.convertValue(map("orderId", "5ad7750b-a68b-49c0-a8c0-32776b067703", "accountId", "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f",
                    "assuranceType", 1, "authorization", "Bearer test-token",
                    "foodOrder", map("orderId", "5ad7750b-a68b-49c0-a8c0-32776b067703", "foodType", 1, "foodName", "Bone Soup", "price", 2.5),
                    "consign", map("orderId", "5ad7750b-a68b-49c0-a8c0-32776b067703", "accountId", "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f",
                            "consignee", "Alice", "phone", "123456", "weight", 5.0, "within", false)), c);
            return JsonUtils.object2Json(e);
        }
    }

    // ------------------------------------------------------------------ mocks
    @SuppressWarnings("unchecked")
    static RestTemplate restTemplateMock() {
        RestTemplate rt = mock(RestTemplate.class);
        when(rt.exchange(anyString(), any(HttpMethod.class), any(), any(ParameterizedTypeReference.class)))
                .thenAnswer(inv -> respond(inv.getArgument(0), inv.getArgument(1)));
        when(rt.exchange(anyString(), any(HttpMethod.class), any(), any(Class.class)))
                .thenAnswer(inv -> respond(inv.getArgument(0), inv.getArgument(1)));
        return rt;
    }

    static AmqpTemplate amqpMock() {
        AmqpTemplate amqp = mock(AmqpTemplate.class);
        doAnswer(inv -> { asyncMessages.add("exchange=" + inv.getArgument(0) + " routingKey='" + inv.getArgument(1) + "'"); return null; })
                .when(amqp).convertAndSend(anyString(), anyString(), any(Object.class));
        doAnswer(inv -> { asyncMessages.add("queue=" + inv.getArgument(0)); return null; })
                .when(amqp).convertAndSend(anyString(), any(Object.class));
        return amqp;
    }

    static ResponseEntity<Response<Object>> respond(String url, HttpMethod method) throws InterruptedException {
        String rest = url.replaceFirst("^http://", "");
        String svc = rest.split("/")[0].split(":")[0];
        String path = rest.substring(rest.indexOf('/'));
        syncCalls.add(svc + " " + method + " " + path);
        if (delayMs > 0) Thread.sleep(delayMs);
        Object data = null;
        if (path.contains("/contactservice/contacts/")) {
            data = M.convertValue(map("id", "a3f1f9a4-27a5-4b16-9e2c-4b8a8b0f3d10", "accountId", "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f",
                    "name", "Alice", "documentType", 1, "documentNumber", "D1", "phoneNumber", "123456"), Contacts.class);
        } else if (path.contains("/travelservice/trip_detail")) {
            data = M.convertValue(map("status", true, "tripResponse", map("economyClass", 10, "confortClass", 10, "startTime", "2026-10-10 08:00:00"),
                    "trip", map("trainTypeName", "GaoTieOne", "routeId", "r1")), TripAllDetail.class);
        } else if (path.contains("/basicservice/basic/travel")) {
            data = M.convertValue(map("status", true, "route", map("id", "r1", "stations", Arrays.asList("shanghai", "suzhou"), "distances", Arrays.asList(0, 50)),
                    "trainType", map("name", "GaoTieOne", "economyClass", 100, "confortClass", 50),
                    "prices", map("economyClass", "50.0", "confortClass", "100.0")), TravelResult.class);
        } else if (path.contains("/seatservice/seats")) {
            data = M.convertValue(map("seatNo", 5, "startStation", "shanghai", "destStation", "suzhou"), Ticket.class);
        } else if (path.endsWith("/orderservice/order")) {
            data = M.convertValue(map("id", "5ad7750b-a68b-49c0-a8c0-32776b067703", "accountId", "4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f",
                    "travelDate", "2026-10-10", "travelTime", "08:00:00", "from", "shanghai", "to", "suzhou", "seatNumber", "5", "seatClass", 2, "price", "50.0"), Order.class);
        } else if (path.contains("/userservice/users/id/")) {
            data = M.convertValue(map("userName", "alice", "email", "alice@example.com"), User.class);
        } else if (path.endsWith("/stationservice/stations")) {
            data = Arrays.asList(M.convertValue(map("id", "s1", "name", "shanghai"), Station.class),
                    M.convertValue(map("id", "s2", "name", "suzhou"), Station.class));
        } else if (path.contains("/stationservice/stations/id/")) {
            data = "s-" + path.substring(path.lastIndexOf('/') + 1);
        } else if (path.contains("/trainservice/trains/byName/")) {
            data = map("name", "GaoTieOne", "economyClass", 100, "confortClass", 50);
        } else if (path.contains("/routeservice/routes/")) {
            data = map("id", "r1", "stations", Arrays.asList("shanghai", "suzhou"), "distances", Arrays.asList(0, 50));
        } else if (path.contains("/priceservice/prices/")) {
            data = map("basicPriceRate", 1.0, "firstClassPriceRate", 2.0);
        }
        return ResponseEntity.ok(new Response<>(1, "ok", data));
    }

    // ------------------------------------------------------------------ helpers
    static Set<String> services(List<String> calls) {
        Set<String> s = new LinkedHashSet<>();
        for (String c : calls) s.add(c.split(" ")[0]);
        return s;
    }

    static Object[] argsSummary(Object[] a) {
        Object[] o = new Object[a.length];
        for (int i = 0; i < a.length; i++) o[i] = a[i] instanceof HttpHeaders ? "headers(" + ((HttpHeaders) a[i]).getFirst(HttpHeaders.AUTHORIZATION) + ")" : a[i];
        return o;
    }

    static void inject(Object target, String field, Object value) throws Exception {
        Class<?> c = target.getClass();
        while (c != null) {
            try {
                Field f = c.getDeclaredField(field);
                f.setAccessible(true);
                f.set(target, value);
                return;
            } catch (NoSuchFieldException e) {
                c = c.getSuperclass();
            }
        }
        throw new NoSuchFieldException(field);
    }

    static Map<String, Object> map(Object... kv) {
        Map<String, Object> m = new LinkedHashMap<>();
        for (int i = 0; i < kv.length; i += 2) m.put((String) kv[i], kv[i + 1]);
        return m;
    }
}
