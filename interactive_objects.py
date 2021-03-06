import pygame as pg

import math
import random

SCALE = 50000/1 # (100px/1AU)

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
        """FIX LATER"""
        self.scale = SCALE

    def __repr__(self):
        return f'{self.__class__.__name__}, rect: {self.rect}'

    def __setattr__(self, attr, value):
        """Helper function to set attributes for a dictionary of variable length."""
        super().__setattr__(attr, value)

    def draw(self, color):
        pg.draw.rect(self.surface, color, self.rect)

    def meter_to_cart(self, meters):
        """Convert meters to scaled cartesian(pixel) coordinates."""
        # 1 AU = 149.6e9 m
        pixels = meters*self.scale/149.6e9
        return pixels

    def cart_to_meter(self, cart):
        """Convert scaled cartesian(pixel) coordinates to meters."""
        return cart*(1/self.scale)*149.6e9

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
        """FIX LATER"""
        self.scale = SCALE
        self.mask = self.get_mask()

    # POLAR FUNCTIONS ---------------------------------------

    def get_mask(self):
        """Return mask of the object for pixel perfect collisions."""
        w, h = self.rect.w, self.rect.h
        colorkey = (0, 0, 0)
        surface = pg.Surface((w, h))
        surface.set_colorkey(colorkey)
        # fill the surface with the spherical object
        color, center, radius = (255, 255, 255), self.rect.center, round(self.rect.w/2)
        pg.draw.circle(surface, color, center, radius)
        mask = pg.mask.from_surface(surface)
        return mask


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

    def polar_to_cartesian(self, r, theta):
        """Polar position to cartesian position where (0, 0) is the reference point."""
        # x = rcos(theta), y = rsin(theta)
        x, y = r*math.cos(theta), r*math.sin(theta)
        x, y = self.add((x, y), self.pole)
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


class Particle(PolarObject):
    """Base class for any particle. In polar to easily generate particles around circular objects."""
    def __init__(self, host_object):
        self.surface, self.pole = host_object.surface, host_object.pole
        # how fast particles "decay" and get deleted once vw becomes 0
        self.decay_rate = 2

    def generate_random_particles(self):
        self.particles = []
        self.particle_vectors = []
        # vectors in polar form
        number_of_particles = random.randint(0, 10)
        for i in range(number_of_particles):
            w = random.randint(1, 10)
            self.particles.append(pg.Rect(self.pole, (w, w)))
            vw, vr, theta =  random.randint(1, 30), random.randint(0, 10), random.uniform(0, 2*math.pi)
            vector = pg.Vector2()
            vector.from_polar((vr, theta))
            self.particle_vectors.append([vector, vw])

    def update(self, dt):
        del_set = []
        for i in range(len(self.particles)):
            vector, vw = self.particle_vectors[i][:]
            vx, vy = vector.xy[:]
            dx, dy = vx*dt, vy*dt
            p = self.particles[i]
            print(p, dx, dy)
            p = p.move(dx, dy)
            print(p)
            # update w
            p.w -= self.decay_rate
            p.h -= self.decay_rate
            # remove 0 or, negative w, h rects
            if p.w <= 0:
                # don't remove during iteration
                del_set.append(p)
                del_set.append(vector)
        if len(del_set) != 0:
            # https://stackoverflow.com/questions/36268749/remove-multiple-items-from-a-python-list-in-just-one-statement
            item_list = self.particles
            self.particles = [elm for elm in item_list if elm not in (del_set)]
            item_list = self.particle_vectors
            self.particle_vectors = [elm for elm in item_list if elm not in (del_set)]
        if len(self.particles) == 0:
            self.generate_random_particles()

    def draw(self):
        for particle in self.particles:
            pg.draw.circle(self.surface, (0, 0, 0), particle.center, particle.w)


class MassObject(PolarObject):
    """Class for any mass object; stars, planet, asteriods."""
    def __init__(self, surface, pole, x, y, mass_object_dictionary):
        # MassObject specific attributes
        # set a dictionary for the object using the object name: so self.MassObject_dictionary = dictionary
        self.__setattr__(self.__class__.__name__ + '_dictionary', mass_object_dictionary)
        self.set_attr_from_dict(mass_object_dictionary)
        self.G = 6.67408e-11 # m^3 kg^-1 s^-2
        # will use a scale in terms of AU to keep track of objects relative to the surface,
        # but SI units for computations.
        # surface is in cartesian coordinates, but computations will exist in polar coordinates
        rect_radius = self.convert_by_type()
        super().__init__(surface, pole, x, y, rect_radius)
        """FIX LATER"""
        self.scale = SCALE

    def __repr__(self):
        dictionary = getattr(self, str(self.__class__.__name__) + '_dictionary')
        string_list = []
        for key in dictionary:
            string_list.append(f'{key}: {dictionary.get(key)}')
        return string_list

    def set_attr_from_dict(self, dictionary):
        """Set attr using dict keys as attr names and values as attr values."""
        for key in dictionary:
            self.__setattr__(key, dictionary.get(key))

    def update_scale(self, new_scale):
        ratio = new_scale/self.scale
        # update all the attributes of the object
        self.scale = new_scale
        rect_radius = self.meter_to_cart(self.radius)
        # correct drifting for the star, no idea why it happens
        if isinstance(self, Star):
            self.rect.w, self.rect.h = round(rect_radius*2), round(rect_radius*2)
            self.rect.center = self.pole
        else:
            self.rect.w, self.rect.h = round(rect_radius*2), round(rect_radius*2)
        self.r = self.r*ratio
        # resize mask
        w, h = self.rect.w, self.rect.h
        self.mask = self.mask.scale((w, h))

    def draw(self, color):
        center, radius = self.rect.center, self.rect.w
        pg.draw.circle(self.surface, color, center, radius)

    def convert_by_type(self):
        """Convert dict values whether the MassObject is a Star or Planet."""
        if isinstance(self, Star):
            self.name = self.hostname
            # https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
            # returns list in alphabetical order
            star_attr_list = list(filter(lambda attr: attr.startswith('st_'), dir(self)))
            st_mass, st_rad, st_teff = star_attr_list[:]
            st_mass, st_rad, st_teff = getattr(self, st_mass), getattr(self, st_rad), getattr(self, st_teff)
            self.mass, self.radius, self.teff = *self.convert_stellar_to_si(st_mass, st_rad), st_teff
            rect_radius = self.meter_to_cart(self.radius)
            return rect_radius
        if isinstance(self, Planet):
            # https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
            # returns list in alphabetical order
            planet_attr_list = list(filter(lambda attr: attr.startswith('pl_'), dir(self)))
            pl_masse, pl_name, pl_orbper, pl_rade = planet_attr_list[:]
            pl_masse, pl_name, pl_orbper, pl_rade = getattr(self, pl_masse), getattr(self, pl_name), getattr(self, pl_orbper), getattr(self, pl_rade)
            self.name = pl_name
            self.mass, self.T, self.radius = self.convert_earth_to_si(pl_masse, pl_orbper, pl_rade)
            rect_radius = self.meter_to_cart(self.radius)
            return rect_radius

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
        pole = (x, y) # Stars will be the center of the system
        # so, the (r, theta) = self.cartesian_to_polar((x, y) - pole)
        # (r, theta) =  self.cartesian_to_polar(0, 0) = (0, 0)
        """FIX LATER"""
        self.scale = SCALE
        super().__init__(surface, pole, x, y, star_dictionary)

    def move(self, dt):
        """Group all time functions here."""
        dt = dt

    def convert_stellar_to_si(self, st_mass, st_rad):
        # convert stellar units to SI units
        # stellar mass = 1.989e30 kg.
        # stellar radius = 695700e3 m
        # stellar effective temperature = k
        mass = 1.989e30*st_mass
        radius = 6.95700e8*st_rad
        return mass, radius

    def draw(self):
        """Group star specific drawing functions."""
        self.draw_body()
        shadow_surface = self.transparent_subsurface(self.surface, self.rect)
        rect = shadow_surface.get_rect()
        # works with topleft, but doesn't seems to work with center
        center, radius = rect.topleft, int(self.rect.w/2)
        pg.draw.circle(shadow_surface, (0, 0, 0, 100), center, radius)
        self.surface.blit(shadow_surface, self.rect.topleft)

    @staticmethod
    def transparent_surface(size):
        surface = pg.Surface(size).convert_alpha()
        surface.fill((0, 0, 0, 0))
        return surface

    @staticmethod
    def transparent_subsurface(surface, rect):
        surface = surface.subsurface(rect).convert_alpha()
        surface.fill((0, 0, 0, 0))
        return surface

    def draw_body(self):
        color, center, radius = (255, 255, 0), self.rect.center, round(self.rect.w/2)
        pg.draw.circle(self.surface, color, center, radius)

class Planet(MassObject):
    """Planets are always relative to a Star."""
    def __init__(self, surface, host_star, planet_dictionary):
        # initialize the position of the planet to a given star
        self.host_star = host_star
        pole = self.host_star.pole
        """FIX LATER"""
        self.scale = SCALE
        """HACK FIX FOR NOW."""
        x, y = 0, 0
        super().__init__(surface, pole, x, y, planet_dictionary)
        """HACK FIX FOR NOW."""
        self.r = self.meter_to_cart(self.get_radial_distance_from(self.host_star))
        self.theta = random.uniform(0, 2*math.pi)
        self.rect.center = self.polar_to_cartesian(self.r, self.theta)
        self.rect.w = self.rect.w
        self.vw = self.get_angular_velocity(self.get_radial_distance_from(self.host_star), self.T)

    def __str__(self):
        return f'{self.__class__.__name__}, rect: {self.rect}'

    def get_subsurface(self):
        """Generate a subsurface bound by the instance rect."""
        w, h = self.rect.w, self.rect.h
        surface = pg.Surface((w, h))
        surface.set_colorkey((0, 0, 0))
        return pg.Surface((w, h))

    def move(self, dt):
        """Group all time functions here."""
        w_px = self.meter_to_cart(self.vw)
        # delta_theta = delta_s/r
        self.theta += self.vw*dt/self.get_radial_distance_from(self.host_star)
        self.rect.center = self.polar_to_cartesian(self.r, self.theta)

    def draw(self, color):
        self.draw_planet(color)
        self.draw_orbit()
        x1, y1, x2, y2 = *self.host_star.rect.center[:], *self.rect.center[:]
        othorg_vector = self.get_orthog_norm(x1, y1, x2, y2)
        othorg_vector.scale_to_length(self.rect.w*10)
        pos1 = self.rect.center[0]-othorg_vector.x, self.rect.center[1]-othorg_vector.y
        pos2 = self.rect.center[0]+othorg_vector.x, self.rect.center[1]+othorg_vector.y
        pg.draw.line(self.surface, (255, 0, 0), self.rect.center, pos1)
        pg.draw.line(self.surface, (255, 0, 0), self.rect.center, pos2)
        shadow_surface = self.get_subsurface()
        x1, y1, y1, y2 = *pos1[:], *pos2[:]
        r1, start_angle, r2, end_angle = *self.cartesian_to_polar(x1, y1), *self.cartesian_to_polar(x2, y2)
        pg.draw.arc(self.surface, (0, 0, 0), self.rect, start_angle, end_angle, int(self.rect.w/2))


    @staticmethod
    def get_orthog_norm(x1, y1, x2, y2):
        dx, dy = (x2-x1, y2-y1)
        vector = pg.math.Vector2((-dy, dx))
        vector.normalize()
        return vector

    @staticmethod
    def get_angular_velocity(r, T):
        """Get radial velocity relative to host star."""
        # http://www.hep.fsu.edu/~berg/teach/phy2048/0918.pdf
        # velocity = 2(pi)r/T
        return (2*math.pi*r)/T

#     def change_of_origin(self, r, theta):
#         """Change of origin position, the star, necesitates a shift of r, theta in the planet."""
#         shifted_r, shifted_theta = r+self.host_star.r, theta+self.host_star.theta
#         return shifted_r, shifted_theta

    def draw_planet(self, color):
        center, radius = self.rect.center, round(self.rect.w/2)
        pg.draw.circle(self.surface, color, center, radius)

    def draw_orbit(self):
        pg.draw.circle(self.surface, (0, 0, 255), self.pole, int(self.r), 1)

    def convert_earth_to_si(self, pl_orbper, pl_mass, pl_rad):
        """Convert earth units to SI units."""
        # 1 day = 24*60*60 s
        # 1 earth radius = 6.371e6 m
        # 1 earth mass = 5.972e24 kg
        T, radius, mass = pl_orbper*24*60*60, pl_rad*6.371e6, pl_mass*5.972e24
        return mass, T, radius

    def get_radial_distance_from(self, star):
        """Radial distance from a star using planet's orbital period."""
        # T = (4pi^2r^3/(Gm1))^1/2
        # r = ((GmT^2)/(4pi^2))^1/3
        G = 6.67408e-11
        numerator = G*star.mass*pow(self.T, 2)
        denominator = 4*pow(math.pi, 2)
        return pow(numerator/denominator, 1/3)
