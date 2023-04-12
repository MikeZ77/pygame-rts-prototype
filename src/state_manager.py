from unit import Unit


class StateManager:
    _instance = None

    def __init__(self):
        self._units = []

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = StateManager()
        return cls._instance

    def add_unit(self, unit: Unit):
        self._units.append(unit)

    def remove_unit(self, unit: Unit):
        self._units.remove(unit)

    def update_game_state(self):
        """
        Determines a state transition based on the game logic and updates that objects state.
        The game object handles the state change in their update method and renders the
        corresponding action.
        """
        pass
