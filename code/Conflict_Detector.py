import math

MIN_DISTANCE = 10
logFile = 'logs.txt'


# The distance is checked in 2 stages in the routes_check file
# 1. Using the aabb_overlap, a faster way to avoid performing the complex processing for segments which are further away from each other
# 2. Using segment_distance, check the segments which failed in the aabb_overlap


#  Entry
def check_routes(routes, fileName):
    CONFLICTS = 0
    with open(logFile, "w") as f:
        f.write("\nStarting conflict detection program on " + fileName)
    # Sort routes by start time
    route_items = sorted(routes.values(), key=lambda r: r["startTime"])

    # print(route_items)
    activeList = []
    safeList = []

    counter = 0
    # only check for conflict with previous and active routes
    for route in route_items:
        counter = route["startTime"]

        # Move completed routes from activeList → safeList
        still_active = []
        for active in activeList:
            if counter > active["endTime"]:
                safeList.append(active)
            else:
                still_active.append(active)
        activeList = still_active

        # Check conflict with currently active routes
        for active in activeList:
            if routes_conflict(route, active):
                still_active.remove(active)
                CONFLICTS += 1
                # return "conflict detected"

        # No conflict → add to active list
        activeList.append(route)

    # All remaining active routes are safe
    safeList.extend(activeList)

    # append to logs
    with open(logFile, "a") as f:
        f.write(f"\nConflict detection complete: {CONFLICTS} conflicts found")
    return CONFLICTS



# check each waypoint segment for conflict
def segments_from_route(route):
    waypoints = route["wayPoints"]
    segments = []

    for i in range(len(waypoints) - 1):
        p1 = waypoints[i][:3]
        p2 = waypoints[i + 1][:3]
        segments.append((p1, p2))

    return segments
def routes_conflict(route_a, route_b):
    with open(logFile, "a") as f:
        f.write(f"\nChecking conflict between route{route_a['id']} and route{route_b['id']}")
        segments_a = segments_from_route(route_a)
        segments_b = segments_from_route(route_b)

        for seg_a in segments_a:
            for seg_b in segments_b:

                # Stage 1
                if not aabb_overlap(seg_a, seg_b, MIN_DISTANCE):
                    continue

                # Stage 2
                minDist = segment_distance(seg_a[0], seg_a[1], seg_b[0], seg_b[1])
                if minDist < MIN_DISTANCE:
                    f.write(f"\nConflict detected between route{route_a['id']} and route{route_b['id']}")
                    f.write(f"\nroute{route_a['id']} -> {seg_a} and route{route_b['id']} -> {seg_b}, Min Distance was = {minDist:.2f}")
                    return True

        f.write(f"\nNo conflict between route{route_a['id']} and route{route_b['id']}")
    return False





# Stage 1
# avoid segments which are further away from each other
def aabb_overlap(seg1, seg2, buffer_dist):
    for i in range(3):  # x, y, z
        min1 = min(seg1[0][i], seg1[1][i]) - buffer_dist
        max1 = max(seg1[0][i], seg1[1][i]) + buffer_dist
        min2 = min(seg2[0][i], seg2[1][i])
        max2 = max(seg2[0][i], seg2[1][i])

        if max1 < min2 or max2 < min1:
            return False

    return True



# Stage 2
# get the smallest distance between 2 segments
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def segment_distance(p1, p2, q1, q2):
    u = [p2[i] - p1[i] for i in range(3)]
    v = [q2[i] - q1[i] for i in range(3)]
    w0 = [p1[i] - q1[i] for i in range(3)]

    a = dot(u, u)
    b = dot(u, v)
    c = dot(v, v)
    d = dot(u, w0)
    e = dot(v, w0)

    denom = a * c - b * b
    sc, tc = 0.0, 0.0

    if denom != 0:
        sc = (b * e - c * d) / denom
        tc = (a * e - b * d) / denom

    sc = max(0, min(1, sc))
    tc = max(0, min(1, tc))

    closest_p = [p1[i] + sc * u[i] for i in range(3)]
    closest_q = [q1[i] + tc * v[i] for i in range(3)]

    return math.dist(closest_p, closest_q)

