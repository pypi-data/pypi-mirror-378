from pathlib import Path
import json
import os

from rich import print as print_rich

class StateManager:
    """Singleton class to manage the state file."""
    _instance = None
    _config_dir_name = ".ctf-orch"
    _state_file_name = "state.json"

    _default_state_structure = {
        "active_ctf": "",
        "ctfs": {}, 
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._state_file_path = Path.home() / Path(self._config_dir_name) / Path(self._state_file_name)
        self.state = None

        if not self.check_state(err=False):
            self._load_state()



    def _load_state(self):
        if not self.check_state(err=False):
            # Create new state file 
            print_rich("[blue].ctf-orch/state.json not found in home directory.[/blue]")
            self._state_file_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_file_path.touch()
            state_data = self._default_state_structure.copy()
            self._save_state(state_data)
            print_rich("[green]:heavy_check_mark:[/green] State file created")
            return state_data
        
        with open(self._state_file_path, "r", encoding="utf-8") as f:
            try:
                loaded_state = json.load(f)
                default_state = self._default_state_structure.copy()
                # Recursively merge
                current_state = self._recursive_update(default_state, loaded_state)
                return current_state
    
            except json.JSONDecodeError as exc:
                raise ValueError(f"The state file at {self._state_file_path} is corrupted or not a valid JSON.") from exc

    
    def _recursive_update(self, target, source):
        for key, value in source.items():
            # if value is a dict, and target has the same key with a dict value (assuming target has the same key)
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._recursive_update(target[key], value)
            else:
                target[key] = value
        return target
    

    def _save_state(self, state_dict: dict):
        temp_path = self._state_file_path.with_suffix('.tmp')
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(state_dict, f, indent=4)
            os.replace(temp_path, self._state_file_path)
        except Exception as e:
            raise IOError(f"Failed to save state: {e}") from e
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    # Public methods to interact with state
    def get_state(self):
        return self._load_state()
    
    def get_state_file_path(self):
        return self._state_file_path

    def get_ctf(self, ctf_name=""):
        """
        Get a CTF's dictionary (by default, gets the active CTF's dictionary.).
        """
        state_dict = self._load_state()
        if ctf_name != "":
            self.check_ctf(ctf_name)
            return state_dict["ctfs"][ctf_name]
        else:
            self.check_ctf()
            return state_dict["ctfs"].get(state_dict["active_ctf"])
        
    def get_chal(self, chal_name=""):
        """
        Get a challenge's dictionary (if chal_name is empty, get the active challenge).
        """
        state_dict = self.get_ctf()
        active_challenge = state_dict["active_challenge"]
        if chal_name == "":
            # Get active
            
            if active_challenge not in state_dict["challenges"].keys():
                raise LookupError("There is no currently active challenge.")
            else:
                return state_dict["challenges"][active_challenge]
        else:
            if chal_name not in state_dict["challenges"].keys():
                raise LookupError(f"{chal_name} is not a valid challenge")
            else:
                return state_dict["challenges"][chal_name]
    def check_state(self, err=True):
        if not self._state_file_path.exists():
            if err:
                raise FileNotFoundError(f"The state file is not found at {self._state_file_path}. \nRun[bold] ctf-orch state setup[/bold] to set necessary state first.")
            else:
                return False
        else:
            return True        
    def check_ctf(self, ctf_name="", err = True):
        """
        Check whether the ctf has been initialized. By default, checks for active ctf.
        """
        state_dict = self._load_state()
        
        if ctf_name != "":
            # CTF_name specified
            if ctf_name not in state_dict["ctfs"].keys():
                if err:
                    raise LookupError(f"{ctf_name} is not an initialized CTF.")
                else:
                    return False
        else:
            # if not specified check for active ctf
            if state_dict["active_ctf"] == "":
                if err:
                    raise LookupError("No currently active CTF.")
                else:
                    return False
            if state_dict["active_ctf"] not in state_dict["ctfs"].keys():
                if err:
                    raise LookupError(f"The active CTF '{state_dict['active_ctf']}' is not an initialized CTF. Set the active CTF to an initialized CTF.")
                    # TODO some way to initialize it
                else:
                    return False
        return True

    def set_active_ctf(self, ctf_name):
        """
        Set the active CTF.
        """
        if ctf_name != "":
            self.check_ctf(ctf_name)
        state_dict = self._load_state()
        state_dict["active_ctf"] = ctf_name
        self._save_state(state_dict)

    def set_active_chall(self, chal_name):
        """
        Set the active challenge in the active CTF.
        """
        self.check_ctf()
        state_dict = self._load_state()
        state_dict["ctfs"][state_dict["active_ctf"]]["active_challenge"] = chal_name
        self._save_state(state_dict)
    
    def add_ctf(self, ctf_directory_path, ctf_name):
        """
        Add a CTF to the CTF list.
        """
        state_dict = self._load_state()
        state_dict["ctfs"][ctf_name] = {
                "directory": ctf_directory_path.as_posix(),
                "active_challenge": "",
                "challenges": {}
            }
            
        self._save_state(state_dict)

    def add_chal(self, chal_name, category, points = 0, solved = False):
        state_dict = self._load_state()
        state_dict["ctfs"][state_dict["active_ctf"]]["challenges"][chal_name] = {
            "name": chal_name,
            "category": category,
            "points": points,
            "solved": solved
        }
        self._save_state(state_dict)
        
    def remove_ctf(self, ctf_name):
        state_dict = self._load_state()
        self.check_ctf(ctf_name)
        del state_dict["ctfs"][ctf_name]
        if state_dict["active_ctf"] == ctf_name:
            state_dict["active_ctf"] = ""
        self._save_state(state_dict)

    def remove_challenge(self, chal_name):
        state_dict = self._load_state()
        self.check_ctf()
        if chal_name not in state_dict["ctfs"][state_dict["active_ctf"]]["challenges"].keys():
            raise LookupError(f"{chal_name} is not a valid challenge")
        del state_dict["ctfs"][state_dict["active_ctf"]]["challenges"][chal_name]
        if state_dict["ctfs"][state_dict["active_ctf"]]["active_challenge"] == chal_name:
            state_dict["ctfs"][state_dict["active_ctf"]]["active_challenge"] = ""
        self._save_state(state_dict)

