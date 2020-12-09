import pygame as pg

import csv

import interactive_objects as io
import math


class System:
    """Class that holds star, planets, and other mass objects."""
    def __init__(self, filename, surface):
        self.surface = surface
        host_star_dict, list_of_planet_dicts = self.load_csv(filename)
        self.init_bodies(host_star_dict, list_of_planet_dicts)

    def init_bodies(self, host_star_dict, list_of_planet_dicts):
        """Initialize host star and planets of the system."""
        surface, x, y, star_dictionary = self.surface, *self.surface.get_rect().center[:], host_star_dict
        self.host_star = io.Star(surface, x, y, star_dictionary)
        self.planets = []
        for dictionary in list_of_planet_dicts:
            self.planets.append(io.Planet(self.surface, self.host_star, dictionary))

    def update(self, dt):
        for planet in self.planets:
            planet.move(dt)

    def change_scale(self, percent):
        new_scale = self.host_star.scale*(1+percent)
        self.host_star.update_scale(new_scale)
        for planet in self.planets:
            planet.update_scale(new_scale)

    def draw(self):
        self.host_star.draw()
        for planet in self.planets:
            planet.draw((255, 0, 255))
            planet.draw_orbit()

    """Book keeping."""
#         hostname:       Host Name
#         pl_name:        Planet Name
#         default_flag:   Default Parameter Set
#         sy_snum:        Number of Stars
#         sy_pnum:        Number of Planets
#         sy_mnum:        Number of Moons
#         pl_orbper:      Orbital Period [days]
#         pl_rade:        Planet Radius [Earth Radius]
#         pl_masse:       Planet Mass [Earth Mass]
#         st_teff:        Stellar Effective Temperature [K]
#         st_rad:         Stellar Radius [Solar Radius]
#         st_mass:        Stellar Mass [Solar mass]

#         Host Name
#         Planet Name
#         Default Parameter Set
#         Number of Stars
#         Number of Planets
#         Number of Moons
#         Orbital Period [days]
#         Planet Radius [Earth Radius]
#         Planet Mass [Earth Mass]
#         Stellar Effective Temperature [K]
#         Stellar Radius [Solar Radius]
#         Stellar Mass [Solar mass]

#                     "Host Name": row["hostname"],
#                     "Planet Name": row["pl_name"],
#                     "Default Parameter Set": float(row["default_flag"]),
#                     "Number of Stars": float(row["sy_snum"]),
#                     "Number of Planets": float(row["sy_pnum"]),
#                     "Number of Moons": float(row["sy_mnum"]),
#                     "Orbital Period [days]": float(row["pl_orbper"]),
#                     "Planet Radius [Earth Radius]": float(row["pl_rade"]),
#                     "Planet Mass [Earth Mass]": float(row["pl_masse"]),
#                     "Stellar Effective Temperature [K]": float(row["st_teff"]),
#                     "Stellar Radius [Solar Radius]": float(row["st_rad"]),
#                     "Stellar Mass [Solar mass]": float(row["st_mass"])

    @staticmethod
    def load_csv(filename):
        """Returns host star dictionary and list of planet dictionaries"""
        with open(f'{filename}.csv') as csvfile:
            csv_dict_reader = csv.DictReader(csvfile, delimiter=',')
            list_of_planet_dicts = []
            for row in csv_dict_reader:
                star_dict = {
                "hostname": row["hostname"],
                "st_mass": float(row["st_mass"]),
                "st_rad": float(row["st_rad"]),
                "st_teff": float(row["st_teff"])

            }
                planet_dict = {
                "pl_name": row["pl_name"],
                "pl_orbper": float(row["pl_orbper"]),
                "pl_rade": float(row["pl_rade"]),
                "pl_masse": float(row["pl_masse"])
            }
                list_of_planet_dicts.append(planet_dict)
            return star_dict, list_of_planet_dicts
