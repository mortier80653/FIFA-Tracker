from datetime import date  
from datetime import timedelta  

class PlayerAge:
    def __init__(self, birthdatedays, currdate=date(2020, 7, 16)):
        self.birthdate = date(1582, 10, 14) + timedelta(days=birthdatedays)
        self.currdate = currdate
        self.age = self._getAge()

    def _getAge(self):
        return self.currdate.year - self.birthdate.year - ((self.currdate.month, self.currdate.day) < (self.birthdate.month, self.birthdate.day))


class PlayerValue:
    # All modifiers are defined in "playervalues.ini"
    def __init__(self, ovr, pot, age, posid, currency=1):
        self.ovr = ovr
        self.pot = pot
        self.age = age
        self.posid = posid
        '''
        [CONVERSION]
        USDOLLAR = 1.12
        EURO = 1.0
        POUND = 0.88
        '''
        currency_conversion = (1.12, 1.0, 0.88)
        self.currency = currency_conversion[currency]
        self.playervalue = self._calculate_player_value()

    def _calculate_player_value(self):
        basevalue = self._ovr_factor(self.ovr) * self.currency
        pos_mod = basevalue * self._position_factor(self.posid)
        pot_mod = basevalue * self._pot_factor(self.pot - self.ovr)
        age_mod = basevalue * self._age_factor(self.age, self.posid)
        return self._sum_factors(basevalue, pos_mod, pot_mod, age_mod)

    def _round_to_player_value(self, summed_value):
        divisor = 0
        if summed_value <= 5000.00:
            divisor = 50
        elif summed_value <= 10000.00:
            divisor = 1000
        elif summed_value <= 50000.00:
            divisor = 5000
        elif summed_value <= 250000.00:
            divisor = 10000
        elif summed_value <= 1000000.00:
            divisor = 25000
        elif summed_value <= 5000000.00:
            divisor = 100000
        else:
            divisor = 500000
        
        reminder = summed_value % divisor
        if reminder >= divisor / 2:
            return summed_value + (divisor - reminder)
        else:
            return summed_value - reminder

    def _ovr_factor(self, ovr):
        factors = (1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 20000, 25000, 34000, 40000, 46000, 54000, 61000, 70000, 86000, 105000, 140000, 170000, 205000, 250000, 305000, 365000, 435000, 515000, 605000, 710000, 1200000, 1600000, 2100000, 2700000, 3800000, 4500000, 5200000, 6000000, 7000000, 8500000, 10000000, 12000000, 15000000, 17500000, 21000000, 26000000, 30000000, 34000000, 40000000, 45000000, 52000000, 60000000, 68000000, 75000000, 83000000, 90000000, 11000000, 120000000, 140000000, 150000000, 200000000)
        try:
            return factors[ovr]
        except IndexError:
            return 0

    def _position_factor(self, posid):
        factors = (-40, -15, -18, -18, -15, -15, -15, -18, -18, -15, -15, -15, 15, 12, 12, 12, 15, 15, 15, 15, 18, 18, 18, 15, 18, 18, 18, 15)
        try:
            return (factors[posid] / 100)
        except IndexError:
            return (factors[0] / 100)

    def _pot_factor(self, remaining_potential):
        if remaining_potential <= 0: return 0
        factors = (0, 15, 20, 25, 30, 35, 40, 45, 55, 65, 75, 90, 100, 120, 160, 190, 235)
        if remaining_potential > len(factors):
            return (factors[-1:] / 100)

        try:
            return (factors[remaining_potential] / 100)
        except IndexError:
            return 0
    
    def _age_factor(self, age, posid):
        factors = (18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 30, 42, 50, 48, 48, 48, 48, 46, 44, 40, 35, 30, 25, 15, 0, -25, -40, -50, -65, -65, -65, -75, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000)

        if posid == 0 and age >= 28:
            age -= 2

        try:
            return (factors[age] / 100)
        except IndexError:
            return (factors[-1:] / 100)

    def _sum_factors(self, basevalue, *args):
        summed_value = basevalue
        for a in args:
            summed_value += a

        return int(self._round_to_player_value(summed_value))