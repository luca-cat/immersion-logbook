from datetime import datetime, timedelta

def characters_read_based_scoring(characters: int):
    character_constant = 10000
    #this constant is based on one's set difficulty 

    points_per_character_multiplier = 1/character_constant
        
    total_points = float(characters * points_per_character_multiplier)

    return total_points

def time_based_scoring(duration: int):
    points_per_minute = 1/60                     

    total_points = float(duration * points_per_minute)             

    return total_points

def uranai_multipliers():
    pass

def uranai():
    pass


