
import re
import copy

RAW_LOGS = """
2026-03-01 10:00|INVALID|192.168.1.10|GET|/api/v1/users|200|34
2026-03-01 10:01|REQ1002|192.168.1.11|GET|/api/v1/users|200|120
2026-03-01 10:02|REQ1003|192.168.1.10|POST|/api/v1/login|401|55
2026-03-01 10:03|REQ1004|192.168.1.12|GET|/api/v1/users|500|500
2026-03-01 10:04|REQ1005|192.168.1.12|GET|/health|200|5
BAD|LINE|SHOULD|BE|COUNTED
2026-03-01 10:05|REQ1006|192.168.1.13|GET|/api/v1/users|200|80
2026-03-01 10:06|REQ1007|192.168.1.10|GET|/api/v1/orders|404|40
""".strip()
#print(RAW_LOGS)

class LogError(Exception):
    
    pass

class InvalidLogLine(LogError):
    
    pass


def safe_run(fn):#here fn take main function as an argument
    
    def wrapper(*args, **kwargs):
        #print(*args,**kwargs)
        try:
            fn(*args, **kwargs)
        except Exception as e:
            print("ERROR:", e)
    return  wrapper 


def parse_line(line):
   
    
    pat = r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2})\|(REQ\d+)\|(\d+\.\d+\.\d+\.\d+)\|(GET|POST|PUT|DELETE)\|([/\w\d\d]+)\|(\d{3})\|(\d+)$"
   
    m = re.match(pat, line.strip())
    #print(m)
    if not m:
        raise InvalidLogLine("Invalid log format")

    
    ts_date = m.group(1)
    request_id = m.group(3)
    ip = m.group(4)
    method = m.group(5)
    path = m.group(6)
    status = int(m.group(7))
    latency = int(m.group(8))

    return {
        "date": ts_date,
        "request_id": request_id,
        "ip": ip,
        "method": method,
        "path": path,
        "status": status,
        "latency_ms": latency,
    }


def top_key(counter_dict):
    
    # BUG: uses min instead of max
    if not counter_dict:
        return None
    #return max(counter_dict, key=lambda k: counter_dict[k])
    return max(counter_dict, key=lambda k: counter_dict[k])
    


def build_report(raw_text):
    invalid = 0
    events = []

    for line in raw_text.split("\n"):
        line = line.strip()
        #print(line)
        if not line:
            continue
        try:
            events.append(parse_line(line))
        except InvalidLogLine:
            invalid += 1


    items = copy.deepcopy(events)

    total = len(items)
    unique_ips = set()
    errors = 0
    slowest = 0
    endpoint_hits = {}

    for ev in items:
        unique_ips.add(ev["ip"])
        
        if ev["status"] >= 400:
            errors += 1
        # BUG: slowest uses min logic
        if ev["latency_ms"] > slowest:
            slowest = ev["latency_ms"]

        endpoint_hits[ev["path"]] = endpoint_hits.get(ev["path"], 0) + 1  # BUG: starts at 1

    top_endpoint = top_key(endpoint_hits)

    print("=== API ACCESS REPORT ===")
    print("Total Requests:", total)
    print("Unique IPs:", len(unique_ips))
    print("Errors:", errors)
    print("Slowest(ms):", slowest)
    print("Top Endpoint:", top_endpoint)
    print("Invalid Lines:", invalid)


@safe_run
def main():
    build_report(RAW_LOGS)

if __name__ == "__main__":
    main()
