from rubymarshal.reader import load
from rubymarshal.classes import *
import json
import re
import os
import sys
try:
    import obspython as obs
except:
    print("Not running in OBS")

def script_description():
    """Sets up the description

    This is a built-in OBS function.

    It outputs the value for the description part of the "Scripts" window for
    this script.
    """
    return "Party data extractor for Pokemon Insurgence. By Filloax"

def script_properties():
    properties = obs.obs_properties_create()
    obs.obs_properties_add_bool(properties, "run_boolean", "Run?")
    obs.obs_properties_add_int(properties, "check_interval_int", "Update Interval (seconds)", 1, 120, 1)
    obs.obs_properties_add_path(properties, "json_file", "Team JSON File", obs.OBS_PATH_FILE, "*.json", None)
    obs.obs_properties_add_path(properties, "save_file", "Pokemon Insurgence save file (Game.rxdata)", obs.OBS_PATH_FILE, "Game.rxdata", None)
    
    return properties

def script_defaults(settings):
    """Sets the default values

    This is a built-in OBS function.

    It sets all of the default values when the user presses the "Defaults"
    button on the "Scripts" screen.
    """

    # Set the run boolean as false by default, just in case
    obs.obs_data_set_default_bool(settings, "run_boolean", False)

    # Set the default update interval at 1 second
    obs.obs_data_set_default_int(settings, "check_interval_int", 1)
    
    saved_games_folder = os.path.join(os.path.expanduser('~'), 'Saved Games')
    obs.obs_data_set_default_string(settings, "save_file", os.path.join(saved_games_folder, "Pokemon Insurgence", "Game.rxdata"))

json_file = ''
save_file = ''
run_boolean = False

def script_update(settings):
    """Updates the settings values

    This is a built-in OBS function.

    This runs whenever a setting is changed or updated for the script. It also
    sets up and removes the timer.
    """
    
    global json_file
    global save_file
    global run_boolean

    # Set up the check interval
    check_interval = obs.obs_data_get_int(settings, "check_interval_int")

    # Set up the json file location
    json_file = obs.obs_data_get_string(settings, "json_file")
    save_file = obs.obs_data_get_string(settings, "save_file")

    # Set up the run bool
    run_boolean = obs.obs_data_get_bool(settings, "run_boolean")

    # Remove the timer for the update_team function, if it exists
    obs.timer_remove(run)

    if not run_boolean or not json_file or not save_file:
        return

    # So now, if everything is set up then set the timer
    # slightly offset to avoid doing on same time as the team loading
    obs.timer_add(run, check_interval * 947)

def run():
    global json_file
    global save_file
    global run_boolean
    
    if run_boolean:
        main(save_file, json_file)


def extract_pokemon_party(data):
    # Extract the player's party from the game data
    # This will depend on the structure of your game data
    # Adjust the keys as per the actual data structure
    return data.attributes["@party"]

def recursive_to_py(data):
    if type(data) is RubyString:
        return data.text
    elif isinstance(data, RubyObject):
        return {re.sub(r'^@', '', k): recursive_to_py(v) for k, v in data.attributes.items()}
    elif type(data) is list:
        return [recursive_to_py(v) for v in data]
    else:
        return data

def main(save_path, team_path):
    with open(save_path, 'rb') as save:
        party = extract_pokemon_party(load(save))
    party_data = recursive_to_py(party)

    team = {
        f'slot{i+1}': {
            'dexnumber': mon['species'],
            'shiny': False,
            'variant': None,
        }
        for i, mon in enumerate(party_data)        
    }
    with open(team_path, 'w', encoding='UTF-8') as f:
        json.dump(team, f, indent=4)
        
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

