import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class Simulator:
    def __init__(self, docks):
        self.fig = plt.figure('UAV simulator')
        self.ax = self.fig.add_subplot(111, projection='3d')

        self.ax.autoscale(False)
        plt.autoscale(False)

        self.docks = docks

        self.ax.set_aspect('equal', adjustable='box')

        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)

        # To maintain axis limits
        self.cornerPoints = [
            [0, 0, 0],
            [0, 100, 0],
            [100, 0, 0],
            [100, 100, 0],
            [0, 0, 100]
        ]

        self.colors = ['green', 'orange', 'blue', 'black']

    def draw_square(self, corner, size=5, z=0, color='black', alpha=1.0):
        x, y = corner

        vertices = [
            (x, y, z),
            (x + size, y, z),
            (x + size, y + size, z),
            (x, y + size, z)
        ]

        square = Poly3DCollection([vertices], color=color, alpha=alpha)
        self.ax.add_collection3d(square)

    def draw_points(self, points, color='red', size=25):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]

        self.ax.scatter(xs, ys, zs, color=color, s=size)

    def draw_lines(self, waypoints, color='blue', lineWidth=1):
        xs = [p[0] for p in waypoints]
        ys = [p[1] for p in waypoints]
        zs = [p[2] for p in waypoints]

        self.ax.plot(xs, ys, zs, color=color, linewidth=lineWidth)

    # Draw
    def redraw(self, droneCords, routes, drawRoute, sim_time):
        self.ax.cla()

        # Draw ground planes
        self.draw_square(corner=(0, 0), size = 100, color ='lightgrey', alpha = 0.5)

        # Draw docks
        for d in self.docks:
            self.draw_square(corner=(d[0], d[1]))

        # Draw points
        self.draw_points(droneCords)
        self.draw_points(self.cornerPoints, color='grey', size=1)

        # display time
        self.ax.set_title(f"Time : {sim_time:.2f}")


        # Draw route lines
        if drawRoute:
            c = 0
            for key in routes:
                self.draw_lines(routes[key]['wayPoints'], color = self.colors[c])
                c+=1

        plt.draw()
        plt.pause(0.01)

    def stayOpen(self):
        plt.show()
