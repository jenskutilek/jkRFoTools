class UnitizationInfo(object):
    def __init__(self):
        self.systems = {}
    
    def add_system(self, system):
        if system.upm in self.systems:
            self.systems[system.upm].append(system)
        else:
            self.systems[system.upm] = [system]
    
    def get_systems_by_upm(self, upm):
        if upm in self.systems:
            return self.systems[upm]
        else:
            return []
    
    def get_all_units(self):
        return self.systems.keys()

class UnitSystem(object):
    def __init__(self, name, units, min_units=None, max_units=None, strategy="free", unit_dict={}):
        self.name = name
        self.upm = units
        self.min_units = min_units
        self.max_units = max_units
        
        # unitization strategies
        if strategy == "alleq":
            self.set_all_equal()
        elif strategy == "fixed":
            if unit_dict:
                self.set_fixed_units(unit_dict)
            else:
                raise "Must supply unit_dict when using fixed units"
        elif strategy == "free":
            self.set_free_units()
        else:
            raise "Unknown unitization strategy."
    
    def set_fixed_units(self, unit_dict):
        self.all_equal = False
        self.fixed_units = unit_dict
        self.free_units = False
    
    def set_all_equal(self, all_equal=True):
        self.all_equal = all_equal
        self.fixed_units = {}
        self.free_units = False
    
    def set_free_units(self, free_units=True):
        self.all_equal = False
        self.fixed_units = {}
        self.free_units = free_units

# define known unit systems
# source: <http://www.quadibloc.com/comp/propint.htm>

unitization_info = UnitizationInfo()

unitization_info.add_system(UnitSystem("Monospaced", 1, 0, 1, "alleq"))
unitization_info.add_system(UnitSystem("IBM Executive", 5, 2, 5, "fixed", {
    2: ["f", "i", "j", "l", "t", "I",
        ".", ",", ":", ";", "'", "!", "(", ")", " "],
    3: ["a", "b", "c", "d", "e", "g", "h", "k", "n", "o", "p", "q", "r", "s", "u", "v", "x", "y", "z", "J", "S",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        '"', "?", "#", "+", "-", "*", "/", "="],
    4: ["w", "A", "B", "C", "D", "E", "F", "G", "H", "K", "L", "N", "O", "P", "Q", "R", "T", "U", "V", "X", "Y", "Z",
        "&"],
    5: ["m", "W", "M",
        "@", "%", "_", "½", "¼"],
}))
unitization_info.add_system(UnitSystem("Mag Card Executive", 7, 3, 7, "fixed", {
    3: ["i", "j", "l"],
    4: ["f", "t", "I", "'"],
    5: ["a", "c", "e", "h", "k", "n", "o", "r", "s", "u", "v", "x", "z", "J",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        ".", ",", ":", ";", "!", "?", '"', "@", "#", "$", "&", "¢", "(", ")", "+", "-", "*", "/", "=", "_", "½", "¼", " "],
    6: ["b", "d", "g", "p", "q", "y", "E", "F", "L", "P", "S", "Z"],
    7: ["m", "w", "A", "B", "C", "D", "G", "H", "K", "M", "N", "O", "Q", "R", "T", "U", "V", "W", "X", "Y"],
}))
unitization_info.add_system(UnitSystem("IBM Selectric Composer", 9, 3, 9, "fixed", {
    3: ["i", "j", "l",
        ".", ",", ";", "`", "'", "-", " "],
    4: ["f", "t", "r", "s", "I",
        ":", "!", "(", ")", "/"],
    5: ["a", "c", "e", "g", "z", "J", "["],
    6: ["b", "d", "h", "k", "n", "p", "q", "u", "v", "x", "y", "P", "S",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "]", "+", "*", "=", "$", "†"],
    7: ["B", "C", "E", "F", "L", "T", "Z"],
    8: ["w", "A", "D", "G", "H", "K", "N", "O", "Q", "R", "U", "V", "X", "Y",
        "&", "@", "%", "½", "¼", "¾", "—"],
    9: ["m", "W", "M"],
}))
unitization_info.add_system(UnitSystem("Monotype hot metal and early photo typesetting", 18, 0, 18, "free"))
unitization_info.add_system(UnitSystem("Linotype early photo typesetting", 18, 0, 18, "free"))
unitization_info.add_system(UnitSystem("Berthold photo typesetting", 48, 0, 48, "free"))
unitization_info.add_system(UnitSystem("Linotype later photo typesetting (3 x 18)", 54, 0, 54, "free"))
