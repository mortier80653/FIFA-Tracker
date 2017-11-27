from datetime import date  
from datetime import timedelta  

class PlayerAge:
    def __init__(self, birthdatedays, currdate=date(2020, 7, 16)):
        self.birthdate = date(1582, 10, 14) + timedelta(days=birthdatedays)
        self.currdate = currdate
        self.age = self._getAge()

    def _getAge(self):
        return self.currdate.year - self.birthdate.year - ((self.currdate.month, self.currdate.day) < (self.birthdate.month, self.birthdate.day))


class PlayerWage:
    # All modifiers are defined in "playerwage.ini", "PlayerWageDomesticPrestigeMods.csv" and "PlayerWageProfitabilityMods.csv"
    def __init__(self, ovr, age, posid, leagueid = 13, club_domestic_prestige = 5, club_profitability = 5):
        self.ovr = ovr
        self.age = age
        self.posid = posid
        self.leagueid = leagueid
        self.club_domestic_prestige = club_domestic_prestige
        self.club_profitability = club_profitability
        self.playerwage = self._calculate_player_wage()

    def _calculate_player_wage(self):
        league_mod = self._ovr_factor(self.ovr) * ( self._league_factor(self.leagueid) * self._domestic_presitge(self.leagueid, self.club_domestic_prestige) * self._profitability(self.leagueid, self.club_profitability))
        age_mod = (league_mod * self._age_factor(self.age)) / 100.00
        pos_mod = (league_mod * self._position_factor(self.posid)) / 100.00
        return int(self._round_to_player_wage(league_mod + age_mod + pos_mod))

    def _league_factor(self, leagueid):
        factors = {
            13: 70,     # England Premier League
            53: 43,     # Spain Primera
            31: 45,     # Italy Serie A
            19: 50,     # Germany Bundesliga 1
            16: 40,     # France Ligue 1
            10: 22,     # Netherlands
            14: 30,     # England Championship
            20: 20,     # Germany Bundesliga 2
            83: 8,      # Korea
            308: 18,    # Portugal
            54: 12,     # Spain Segunda A
            56: 8,      # Sweden
            189: 20,    # Switzerland
            39: 15,     # MLS
            17: 10,     # France Ligue 2
            341: 25,    # Mexico
            335: 6,     # Chile
            336: 4,     # Colombia
            67: 33,     # Russia
            80: 22,     # Austria
            4: 21,      # Belgium
            1: 20,      # Denmark
            41: 10,     # Norway
            68: 32,     # Turkey
            60: 8,      # England League One
            66: 13,     # Poland
            350: 25,    # Saudi Arabia
            351: 8,     # Australia
            353: 15,    # Argentina
            61: 8,      # England League Two
            50: 10,     # Scotland
            65: 3,      # Ireland
            7: 15,      # Brazil
            349: 14,    # Japan J1
        }

        try:
            return factors[leagueid]
        except KeyError:
            return 20   # Default League Modifier

    def _ovr_factor(self, ovr):
        factors = (20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 45, 45, 45, 45, 45, 45, 45, 45, 45, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 60, 60, 60, 60, 60, 60, 80, 80, 80, 120, 120, 120, 250, 250, 250, 300, 300, 300, 420, 420, 420, 500, 500, 500, 600, 600, 600, 650, 650, 850, 850, 1000, 1000, 1300, 1300, 1300, 1800, 1800, 2000, 2000, 2000, 3000, 3000, 5000, 5000, 5000)
        try:
            return factors[ovr]
        except IndexError:
            return 0

    def _age_factor(self, age):
        factors = (-60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -60, -35, -35, -35, -10, -10, 0, 0, 0, 10, 15, 15, 20, 20, 15, 15, 15, 15, 15, -15, -15, -15, -15, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20, -20)
        try:
            return factors[age]
        except IndexError:
            return 0

    def _position_factor(self, posid):
        factors = (-30, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, -10, 0, 0, 0, 0, 0, 0, 0, 0 , 10, 10, 10, 10, 10, 10, 10, 10)
        try:
            return factors[posid]
        except IndexError:
            return factors[0]

    def _domestic_presitge(self, leagueid, club_domestic_prestige):
        domestic_prestige_table = {
            0: (0,1.2,1.2,1.4,1.4,1.5,1.8,1.8,1.8,2,2,),                     
            13: (0,1,1,1.1,1.1,1.3,1.3,1.5,1.6,1.6,1.7,), 
            53: (0,0.8,0.8,0.8,0.9,0.9,0.9,1,1,1.5,3.5,), 
            31: (0,0.7,0.8,1,1,1.5,1.5,1.6,1.7,1.7,2,), 
            19: (0,1,1,1,1.1,1.1,1.1,1.4,1.2,1.6,2,), 
            16: (0,1,1,1.2,1.2,1.3,1.3,1.4,1.5,1.6,1.6,), 
            10: (0,1,1,1,1,1.1,1.1,1.2,1.2,1.5,1.5,), 
            14: (0,0.8,0.8,1,1,1.8,1.8,1.8,1.8,2.2,2.2,), 
            20: (0,1.2,1.2,1.4,1.4,1.5,1.8,1.8,1.8,2,2,), 
            32: (0,1,1,1,1.1,1.1,1.1,1.2,1.2,1.2,1.2,), 
            83: (0,1.4,1.4,1.5,1.5,1.5,1.6,1.6,1.6,2,2,), 
            308: (0,1,1,1.1,1.1,1.2,1.2,1.3,1.3,1.4,1.4,), 
            54: (0,1.1,1.1,1.2,1.2,1.3,1.3,1.4,1.4,1.5,1.5,), 
            56: (0,1,1,1.2,1.2,1.4,1.4,1.5,1.5,2,2,), 
            189: (0,1,1,1,1,1.3,1.3,1.6,1.6,1.8,1.8,), 
            39: (0,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,2.5,), 
            17: (0,1.1,1.1,1.2,1.2,1.3,1.3,1.4,1.4,1.5,1.5,), 
            341: (0,1,1,1,1,1.5,1.5,2,2,2.5,2.5,), 
            335: (0,1.5,1.5,1.5,1.5,1.5,1.6,1.8,2,2,2.3,), 
            336: (0,1.2,1.2,1.2,1.2,1.4,1.4,2,2.5,2.5,3,), 
            67: (0,1,1,1,1.2,1.2,1.2,1.4,1.4,1.6,1.8,), 
            80: (0,1.2,1.2,1.2,1.4,1.4,1.6,1.7,1.7,1.8,1.8,), 
            4: (0,1.2,1.2,1.2,1.4,1.4,1.4,1.5,1.5,2,2,), 
            1: (0,1.2,1.2,1.2,1.4,1.4,1.4,1.5,1.5,2,2,), 
            41: (0,1,1,1,1.1,1.1,1.2,1.2,1.2,1.5,1.5,), 
            68: (0,1,1,1,1,1.2,1.2,1.6,1.6,2,2,), 
            60: (0,1.8,1.8,1.8,2.1,2.1,2.1,2.3,2.3,2.5,2.5,), 
            66: (0,1,1,1.2,1.3,1.3,1.6,1.6,1.8,1.8,1.8,), 
            350: (0,1.2,1.2,1.2,1.4,1.4,1.6,1.8,2,2,2,), 
            351: (0,1,1,1,1,1.2,1.2,1.4,1.4,1.4,1.4,), 
            353: (0,2,2,2,2,2.2,2.2,2.4,2.4,2.6,2.6,), 
            61: (0,2,2,2,2.5,2.5,2.5,3,3,3,3,), 
            50: (0,1,1,1,1,1,1,1,1,5,5,), 
            65: (0,1.5,1.5,1.5,1.7,1.7,1.7,2,2,2,2,), 
            7: (0,2,2,2,2,2.2,2.6,3,3.2,3.2,3.2,), 
            349: (0,1.2,1.2,1.2,1.4,1.4,1.6,1.8,2,2,2,), 
            2076: (0,1.2,1.2,1.4,1.4,1.5,1.8,1.8,1.8,2,2,),
        }
        
        try:
            return domestic_prestige_table[leagueid][club_domestic_prestige]
        except KeyError:
            return domestic_prestige_table[0][club_domestic_prestige]

    def _profitability(self, leagueid, club_profitability):
        profitability_table = {
            0: (0,1.5,1.5,1.4,1.4,1.2,1.2,1.1,1.1,1,1,), 
            13: (0,1.6,1.6,1.5,1.5,1.3,1.3,1,1,1,1,), 
            53: (0,1.5,1.5,1.5,1.4,1.4,1.2,1.2,1,0.8,0.8,), 
            31: (0,2,1.8,1.4,1.4,1.2,1,0.9,0.8,0.8,0.7,), 
            19: (0,1.5,1.5,1.5,1.2,1.2,1,1,1,1,1,), 
            16: (0,2,1.8,1.8,1.5,1.2,1,1,1,0.8,0.8,), 
            10: (0,1.5,1.5,1.3,1.2,1.1,1,1,0.9,0.8,0.8,), 
            14: (0,1.8,1.8,1.6,1.6,1.3,1.3,1.1,1.1,0.8,0.8,), 
            20: (0,1.6,1.6,1.5,1.5,1.4,1.2,1.1,0.8,0.7,0.7,), 
            32: (0,1.1,1.1,1,1,1,0.9,0.9,0.8,0.8,0.8,), 
            83: (0,1.6,1.6,1.5,1.5,1.4,1.4,1.2,1.2,1,1,), 
            308: (0,1.5,1.5,1.3,1.3,1.1,1.1,1,1,0.8,0.8,), 
            54: (0,1.6,1.6,1.5,1.5,1.4,1.4,1.3,1.3,1.2,1.2,), 
            56: (0,1.5,1.5,1.4,1.4,1.2,1.2,1.1,1.1,1,1,), 
            189: (0,2,2,1.5,1.5,1.3,1.3,1,1,1,1,), 
            39: (0,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,), 
            17: (0,1.6,1.6,1.5,1.5,1.4,1.4,1.3,1.3,1.2,1.2,), 
            341: (0,2,1.8,1.6,1.4,1.2,1.2,1,1,0.8,0.8,), 
            335: (0,2,2,2,2,1.4,1.4,1.2,1.2,1,1,), 
            336: (0,1.1,1.1,1.1,1.1,1,1,1,0.8,0.8,0.8,), 
            67: (0,2,2,1.8,1.8,1.7,1.7,1.7,1.4,1.4,1.4,), 
            80: (0,1.8,1.8,1.6,1.4,1.2,1,1,1,0.8,0.8,), 
            4: (0,1.4,1.4,1.2,1.1,1.1,1.1,1.1,1.1,1,1,), 
            1: (0,1.4,1.4,1.2,1.1,1.1,1.1,1.1,1.1,1,1,), 
            41: (0,1.2,1.2,1.2,1.1,1.1,1.1,1,1,1,1,), 
            68: (0,1.8,1.8,1.6,1.4,1.2,1,1,1,1,1,), 
            60: (0,1.6,1.6,1.6,1.5,1.5,1.5,1.4,1.4,1,1,), 
            66: (0,1.2,1.2,1,1,1,1,0.9,0.9,0.8,0.8,), 
            350: (0,1.5,1.5,1.5,1.5,1.5,1.5,1.3,1.2,1,1,), 
            351: (0,2.5,2.5,2,2,1.5,1.5,1,1,1,1,), 
            353: (0,1.2,1.2,1.1,1.1,1,1,0.9,0.9,0.8,0.8,), 
            61: (0,1.8,1.8,1.8,1.8,1.8,1.5,1.5,1.5,1.5,1.5,), 
            50: (0,2,2,2,2,2,1.8,1.8,1.8,1.8,1.8,), 
            65: (0,1.6,1.6,1.6,1.5,1.5,1.5,1.4,1.4,1.3,1.3,), 
            7: (0,1.5,1.5,1.5,1.2,1.2,1.2,1.2,1,1,1,), 
            349: (0,1,1,1,1,0.8,0.8,0.7,0.7,0.7,0.7,), 
            2076: (0,1.6,1.6,1.5,1.5,1.4,1.2,1.1,0.8,0.7,0.7,),
        } 
    
        try:
            return profitability_table[leagueid][club_profitability]
        except KeyError:
            return profitability_table[0][club_profitability]

    def _round_to_player_wage(self, summed_wage):
        divisor = 0
        if summed_wage <= 1000.00:
            divisor = 50
        elif summed_wage <= 10000.00:
            divisor = 100
        elif summed_wage <= 50000.00:
            divisor = 500
        elif summed_wage <= 100000.00:
            divisor = 1000
        elif summed_wage <= 200000.00:
            divisor = 5000
        elif summed_wage <= 1000000.00:
            divisor = 10000
        elif summed_wage <= 5000000.00:
            divisor = 50000
        else:
            divisor = 100000
        
        reminder = summed_wage % divisor
        if reminder >= divisor / 2:
            return summed_wage + (divisor - reminder)
        else:
            return summed_wage - reminder
    

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