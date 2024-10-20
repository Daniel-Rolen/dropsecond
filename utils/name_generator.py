import random

def generate_space_name():
    adjectives = ["Cosmic", "Stellar", "Nebular", "Galactic", "Astral", "Celestial", "Lunar", "Solar", "Martian", "Jovian"]
    nouns = ["Voyager", "Explorer", "Pioneer", "Pathfinder", "Discoverer", "Surveyor", "Orbiter", "Lander", "Probe", "Satellite"]
    return f"{random.choice(adjectives)}_{random.choice(nouns)}_{random.randint(1000, 9999)}"
