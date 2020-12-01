import pygame as pg

import math

SCALE = 25000/1 # (100px/1AU)

class InteractableObject:
    """Class for mouse interactable elements on the screen."""
    def __init__(self, surface, x, y, rect_radius):
        self.surface = surface
        # Center a rect object about the given x, y
        self.rect_radius = rect_radius
        center = x-rect_radius, y-rect_radius
        self.rect = pg.Rect(center, (2*rect_radius, 2*rect_radius))
        # (x, y) = screen coordinates where (1 px, 1 px) = (1 SCALE, 1 SCALE)
        # where 100 px = 1 AU, SCALE = 100 px / 1 AU
        self.xy = self.rect.center
        self.x, self.y = self.xy[:]
        self.xy_t = x, y

        def __repr__(self):
            return f'[{self.rect}]'

    def draw(self, color):
        pg.draw.circle(self.surface, color, self.xy, self.rect_radius)

    def cart_to_meter(self, x_px, y_px):
        """Convert scaled cartesian to meters for computations."""
        #1 AU = 149.6e9 m
        x_m, y_m = x_px*(1/SCALE)*149.6e9, y_px*(1/SCALE)*149.6e9 # px*(AU/px)*(m/AU) = m
        return x_m, y_m

    def meter_to_cart(self, x_m, y_m):
        """Convert meters to scaled cartesian coordinates."""
        x_px, y_px = x_m*SCALE/149.6e9, y_m*SCALE/149.6e9
        return x_px, y_px

    def m_to_c(self, meter):
        # debug function
        return (meter*SCALE)/149.6e9

    def c_to_m(self, cart):
        return cart*(1/SCALE)*149.6e9

    def distance(self, second_object):
        """Get the euclidean distance from the first object to the second object."""
        # r = (dx^2+dy^2)^1/2
        point_1, point_2 = self.xy, second_object.xy
        delta_x, delta_y = self.sub(point_1, point_2)[:]
        squared_sum = pow(delta_x, 2) + pow(delta_y, 2)
        return math.sqrt(squared_sum)

    def add(self, iter_1, iter_2):
        """Add every element of two iterables."""
        return tuple(int(a + b) for a, b in zip(iter_1, iter_2))

    def sub(self, iter_1, iter_2):
        """Subtract every element of two iterables."""
        return tuple(int(a - b) for a, b in zip(iter_1, iter_2))


class PolarObject(InteractableObject):
    """Class for any polar coordinate object."""
    def __init__(self, surface, r, theta, rect_radius):
        self.r, self.theta = r, theta
        x, y = self.polar_to_cartesian(r, theta)
        super().__init__(surface, x, y, rect_radius)

    def __str__(self):
        return f'PolarObject @ Cart: ({self.x}, {self.y}), Polar: ({self.r}, {self.theta})'

    # POLAR FUNCTIONS ---------------------------------------
    def cartesian_to_polar(self, x, y):
        # r = (x^2+y^2)^2, theta = tan^-1(y/x)
        r = math.sqrt(pow(x, 2)+pow(y, 2))
        # set specific code for edge cases
        if x == 0 and y != 0:
            sign = lambda x: (1, -1)[x < 0]
            return r, sign(y)*math.pi/2
        if x == 0 and y == 0:
            return 0, 0
        else:
            theta = math.atan(y/x)
        return r, theta

    def polar_to_cartesian(self, r, theta):
        # x = rcos(theta), y = rsin(theta)
        x, y = r*math.cos(theta), r*math.sin(theta)
        return x, y

    def polar_distance(self, second_object):
        """Get the euclidean distance from the first object to the second object.
        Where A,B are the objects and C is the origin."""
        # (r1^2 +  r2^2 -2r1r2cos(theta2-theta1))^1/2
        r1, r2 = self.r, second_object.r
        theta1, theta2 = self.theta, second_object.theta
        return math.sqrt(pow(r1, 2)+pow(r2, 2)-(2*r1*r2*math.cos(theta1-theta2)))

    def radial_distance(self, second_object):
        return abs(self.r-second_object.r)


class MassObject(PolarObject):
    """Class for any mass object; stars, planet, asteriods."""
    def __init__(self, surface, r, theta, rect_radius, mass):
        # will use a scale in terms of AU to keep track of objects relative to the surface,
        # but SI units for computations.
        # surface is in cartesian coordinates, but computations will exist in polar coordinates
        """ r meter, theta -> r px, theta -> (x px, y px)"""
        r = self.m_to_c(r)
        x, y = self.polar_to_cartesian(r, theta)
        super().__init__(surface, x, y, rect_radius)
        # MassObject specific attributes
        self.mass = mass # kg
        self.G = 6.67408e-11 # m^3 kg^-1 s^-2
        self.velocity = 0 # m/s
        self.r, self.theta = r, theta

    def __str__(self):
        return f'MassObject @ ({self.x}, {self.y})'

    def gravity(self, second_object):
        """Returns force of gravity exerted by the mass object on the second object and vice versa."""
        # Fg = F12 = F21 = G(m1)(m2)/r^2
        m1, m2 = self.mass, second_object.mass
        r = self.radial_distance(second_object)
        return (self.G*m1*m2)/pow(r, 2)

    def volume(self):
        # V = 4/3(pi)(r^3), m^3
        return (4/3)*(math.pi)*(pow(self.radius, 3))

    def density(self):
        # D = mass / V, kg/m
        return self.mass/self.volume()


class Star(MassObject):
    """We will assume only stars exert significant enough gravity to reduce computation."""
    def __init__(self, surface, x, y, rect_radius, name, st_mass, st_rad):
        r, theta = self.cartesian_to_polar(x, y)
        r = self.c_to_m(r)
        self.name = name
        self.mass, self.radius = self.convert_stellar_to_si(st_mass, st_rad)
        super().__init__(surface, r, theta, rect_radius, self.mass)
        print((x, y), self.xy)

    def convert_stellar_to_si(self, st_mass, st_rad):
        # convert stellar units to SI units
        # stellar mass = 1.989e30 kg.
        # stellar radius = 695700e3 m
        # stellar effective temperature = k
        mass = 1.989e30*st_mass
        radius = 6.95700e8*st_rad
        return mass, radius

class Planet(MassObject):
    """Planets are always relative to a Star."""
    def __init__(self, surface, rect_radius, host_star, name, pl_orbper, pl_rad, pl_mass):
        # initialize the position of the planet to a given star
        self.host_star, self.name = host_star, name
        self.T, self.radius, self.mass = self.convert_earth_to_si(pl_orbper, pl_rad, pl_mass)
        # since the position of the host star can change and since we consider the star to be
        # the origin, we need to shift the planet position relative to the new origin
        r, theta = self.get_radial_distance_from(self.host_star), 0
        r, theta = self.change_of_origin(r, theta)
        super().__init__(surface, r, theta, rect_radius, self.mass)

    def change_of_origin(self, r, theta):
        """Change of origin position, the star, necesitates a shift of r, theta in the planet."""
        shifted_r, shifted_theta = r+self.host_star.r, theta+self.host_star.theta
        return shifted_r, shifted_theta

    def draw_orbit(self):
        distance = self.distance(self.host_star)
        pg.draw.circle(self.surface, (0, 0, 255), self.host_star.xy, int(distance), 2)

    def convert_earth_to_si(self, pl_orbper, pl_rad, pl_mass):
        """Convert earth units to SI units."""
        # 1 day = 24*60*60 s
        # 1 earth radius = 6.371e6 m
        # 1 earth mass = 5.972e24 kg
        T, radius, mass = pl_orbper*24*60*60, pl_rad*6.371e6, pl_mass*5.972e24
        return T, radius, mass

    def get_radial_distance_from(self, star):
        """Radial distance from a star using planet's orbital period."""
        # T = (4pi^2r^3/(Gm1))^1/2
        # r = ((GmT^2)/(4pi^2))^1/3
        G = 6.67408e-11
        numerator = G*star.mass*pow(self.T, 2)
        denominator = 4*pow(math.pi, 2)
        return pow(numerator/denominator, 1/3)

# s = Star('screen', 0, 0, 5, 'TRAPPIST-1', 0.12, 0.08)
# p = Planet('screen', 5, s, 'TRAPPIST-1 b', 1.51087081, 1.086, 0.85)
