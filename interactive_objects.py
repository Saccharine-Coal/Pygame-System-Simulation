import pygame as pg

import math

SCALE = 25000/1 # (100px/1AU)

class InteractableObject:
    """Class for mouse interactable elements on the screen."""
    def __init__(self, surface, x, y, w, h):
        self.surface = surface
        # get topleft position with x, y being the center
        # use round because rect rounds down, so 5.9 becomes 5
        topleft = round(x-w*.5), round(y-h*.5)
        self.rect = pg.Rect(topleft, (w, h))
        # (x, y) = screen coordinates where (1 px, 1 px) = (1 SCALE, 1 SCALE)
        # where 100 px = 1 AU, SCALE = 100 px / 1 AU
        self.xy = self.rect.center

    def __repr__(self):
        return f'{self.__class__.__name__}, rect: {self.rect}'
    
    def __setattr__(self, attr, value):
        """Helper function to set attributes for a dictionary of variable length."""
        super().__setattr__(attr, value)

    def draw(self, color):
        pg.draw.rect(self.surface, color, self.xy, self.rect)
    
    @staticmethod
    def meter_to_cart(meters):
        """Convert meters to scaled cartesian(pixel) coordinates."""
        # 1 AU = 149.6e9 m
        pixels = meters*SCALE/149.6e9
        return pixels
    
    @staticmethod
    def cart_to_meter(cart):
        """Convert scaled cartesian(pixel) coordinates to meters."""
        return cart*(1/SCALE)*149.6e9

    def distance(self, second_object):
        """Get the euclidean distance from the first object to the second object."""
        # r = (dx^2+dy^2)^1/2
        point_1, point_2 = self.xy, second_object.xy
        delta_x, delta_y = self.sub(point_1, point_2)[:]
        squared_sum = pow(delta_x, 2) + pow(delta_y, 2)
        return math.sqrt(squared_sum)
    
    @staticmethod
    def add(iter_1, iter_2):
        """Add every element of two iterables."""
        return tuple(int(a + b) for a, b in zip(iter_1, iter_2))

    @staticmethod
    def sub(iter_1, iter_2):
        """Subtract every element of two iterables."""
        return tuple(int(a - b) for a, b in zip(iter_1, iter_2))


class PolarObject(InteractableObject):
    """Class for any polar coordinate object."""
    def __init__(self, surface, pole, x, y, rect_radius):
        self.pole, self.rec_radius = pole, rect_radius
        self.r, self.theta = self.cartesian_to_polar(x, y)
        super().__init__(surface, x, y, rect_radius*2, rect_radius*2)

    # POLAR FUNCTIONS ---------------------------------------
    
    def get_rel_to_pole(self, x, y):
        """Get the x, y position relative to the reference point of the polar coordinate, the pole."""
        return self.sub((x, y), self.pole)
    
    def cartesian_to_polar(self, x, y):
        """Cartesian position to polar position where (0, 0) is the reference point."""
        # r = (x^2+y^2)^2, theta = tan^-1(y/x)
        # pole is the reference point of the coordinate system
        x, y = self.get_rel_to_pole(x, y)
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
    
    @staticmethod
    def polar_to_cartesian(r, theta):
        """Polar position to cartesian position where (0, 0) is the reference point."""
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
    def __init__(self, surface, pole, x, y, rect_radius, mass_object_dictionary):
        # MassObject specific attributes
        # set a dictionary for the object using the object name: so self.MassObject_dictionary = dictionary
        self.__setattr__(self.__class__.__name__ + '_dictionary', mass_object_dictionary)
        self.set_attr_from_dict(mass_object_dictionary)
        self.G = 6.67408e-11 # m^3 kg^-1 s^-2
        # will use a scale in terms of AU to keep track of objects relative to the surface,
        # but SI units for computations.
        # surface is in cartesian coordinates, but computations will exist in polar coordinates
        super().__init__(surface, pole, x, y, rect_radius)
        self.convert_by_type()
    
    def set_attr_from_dict(self, dictionary):
        """Set attr using dict keys as attr names and values as attr values."""
        for key in dictionary:
            self.__setattr__(key, dictionary.get(key))
    
    def convert_by_type(self):
        """Convert dict values whether the MassObject is a Star or Planet."""
        if isinstance(self, Star):
            # https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
            star_attr_list = list(filter(lambda attr: attr.startswith('st_'), dir(self)))
        if isinstance(self, Planet):
            # https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
            star_attr_list = list(filter(lambda attr: attr.startswith('pl_'), dir(self)))

    def gravity(self, second_object):
        """Returns force of gravity exerted by the mass object on the second object and vice versa."""
        # Fg = F12 = F21 = G(m1)(m2)/r^2
        m1, m2 = self.mass, second_object.mass
        r = self.radial_distance(second_object)
        return (self.G*m1*m2)/pow(r, 2)

    @staticmethod
    def volume(radius):
        # V = 4/3(pi)(r^3), m^3
        return (4/3)*(math.pi)*(pow(radius, 3))

    @staticmethod
    def density(mass, volume):
        # D = mass / V, kg/m
        return mass/volume


class Star(MassObject):
    """We will assume only stars exert significant enough gravity to reduce computation."""
    def __init__(self, surface, x, y, star_dictionary):
        # stellar rad -> meters -> scaled cart(px)
        # stellar mass -> kg and so forth
        pole = (0, 0) # Stars will be the center of the system
        rect_radius = 2
        super().__init__(surface, pole, x, y, rect_radius, star_dictionary)

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


if __name__ == "__main__":
    m = Star('surface', 0, 0, {'st_mass': 5, 'test': 0})
# s = Star('screen', 0, 0, 5, 'TRAPPIST-1', 0.12, 0.08)
# p = Planet('screen', 5, s, 'TRAPPIST-1 b', 1.51087081, 1.086, 0.85)
#

