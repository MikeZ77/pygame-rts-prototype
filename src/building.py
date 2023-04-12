from unit_factory import UnitFactory


class Building:
    def __init__(self):
        self.production_queue = []
        self.factory = UnitFactory()
