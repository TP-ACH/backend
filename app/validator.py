from pydantic import BaseModel
from consts import PH_MIN, PH_MAX, TEMP_MIN, TEMP_MAX, EC_MIN, EC_MAX

class Validator(BaseModel):
    ph_min: float = PH_MIN
    ph_max: float = PH_MAX
    temp_min: float = TEMP_MIN
    temp_max: float = TEMP_MAX
    ec_min: float = EC_MIN
    ec_max: float = EC_MAX

    def set_thresholds(self, ph_min=None, ph_max=None, temp_min=None, temp_max=None, ec_min=None, ec_max=None):
        if ph_min is not None:
            self.ph_min = ph_min
        if ph_max is not None:
            self.ph_max = ph_max
        if temp_min is not None:
            self.temp_min = temp_min
        if temp_max is not None:
            self.temp_max = temp_max
        if ec_min is not None:
            self.ec_min = ec_min
        if ec_max is not None:
            self.ec_max = ec_max

    def validate(self, reading):
        if reading['ph'] < self.ph_min:
            return False, "pH value too low"
        elif reading['ph'] > self.ph_max:
            return False, "pH value too high"

        if reading['temperature'] < self.temp_min:
            return False, "Temperature value too low"
        elif reading['temperature'] > self.temp_max:
            return False, "Temperature value too high"

        if reading['ec'] < self.ec_min:
            return False, "EC value too low"
        elif reading['ec'] > self.ec_max:
            return False, "EC value too high"

        return True, "Reading is within range"
