import pygame as pg

import csv

import interactive_objects as io
import math


class System:
    """Class that holds star, planets, and other mass objects."""
    def __init__(self, filename, surface):
        self.surface = surface
        self.dictionary = self.load_csv(filename)

    def draw(self):
        self.host_star.draw((255, 0, 0))
        for planet in self.planets:
            planet.draw((0, 0, 0))
            planet.draw_orbit()

    def load_csv(self, filename):
        """Load system data from csv file."""
        with open(f'{filename}.csv') as csvfile:
            csv_dict_reader = csv.DictReader(csvfile, delimiter=',')
            line_count = 0
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
            self.planets = []
            for row in csv_dict_reader:
                if line_count == 0:
                    # surface, r, theta, rect_radius, name, st_mass, st_rad
                    self.host_star = io.Star(self.surface, 640, 300, 30,
                        row["hostname"], float(row["st_mass"]), float(row["st_rad"])
                    )
                # surface, rect_radius, host_star, name, pl_orbper, pl_rad, pl_mass
                self.planets.append(io.Planet(self.surface, 5, self.host_star, row["pl_name"],
                    float(row["pl_orbper"]), float(row["pl_rade"]), float(row["pl_masse"])
                ))


# s = System('PS_2020.11.30_14.52.15 - Copy', 'screen')
