import json
from Simulator import Simulator
from Conflict_Detector import *
import time

dt = 0.1              # simulation time step
speed = 5.0           # units per second
sim_time = 0.0

fileName = "schedules/schedule1.json"
drawRoute = True

# Get data from a JSON file
def getData(fName):
    try:
        with open(fName, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Json file not found")
        return {}
    except json.JSONDecodeError:
        print("could not decode json")
        return {}



data = getData(fileName)

# Run simulation only if there are no conflicts
if check_routes(data['routes'], fileName) == 0:

    # converted dict to list for ease
    drones = list(data["drones"].values())
    docks = list(data["docks"].values())
    routes = data["routes"]

    # initiated simulator
    sim = Simulator(docks)

    # for steady animation of the drone(dots)
    def lerp(p1, p2, alpha):
        return [
            p1[0] + alpha * (p2[0] - p1[0]),
            p1[1] + alpha * (p2[1] - p1[1]),
            p1[2] + alpha * (p2[2] - p1[2])
        ]


    # One route per drone (drone1 -> route1, etc.)
    routes_list = list(routes.values())
    drone_routes = dict(zip(data["drones"].keys(), routes_list))


    # Track each drone's state
    drone_state = {}
    for drone_id in data["drones"]:
        drone_state[drone_id] = {
            "wp_index": 0,
            "wait_left": 0.0
        }

    # simulation Loop
    while True:
        sim_time += dt

        for i, (drone_id, pos) in enumerate(data["drones"].items()):
            route = drone_routes.get(drone_id)
            if not route:
                continue

            if sim_time < route["startTime"] or sim_time > route["endTime"]:
                continue

            waypoints = route["wayPoints"]
            state = drone_state[drone_id]

            # Handle waiting
            if state["wait_left"] > 0:
                state["wait_left"] -= dt
                continue

            wp_idx = state["wp_index"]
            if wp_idx >= len(waypoints) - 1:
                continue  # route finished

            curr_wp = waypoints[wp_idx][:3]
            next_wp = waypoints[wp_idx + 1][:3]

            # Move drone
            dx = next_wp[0] - pos[0]
            dy = next_wp[1] - pos[1]
            dz = next_wp[2] - pos[2]
            dist = (dx**2 + dy**2 + dz**2) ** 0.5

            if dist < speed * dt:
                # Arrive at waypoint
                data["drones"][drone_id] = next_wp.copy()
                state["wait_left"] = waypoints[wp_idx + 1][3]
                state["wp_index"] += 1
            else:
                alpha = (speed * dt) / dist
                data["drones"][drone_id] = lerp(pos, next_wp, alpha)

        # Convert drones dict → 2D array
        drones_array = list(data["drones"].values())

        # print(sim_time)
        sim.redraw(drones_array, routes, drawRoute, sim_time)
        time.sleep(dt)
    # to keep the window open even after done simulating
    sim.stayOpen()

else:
    print('Resolve conflicts before running simulation')
