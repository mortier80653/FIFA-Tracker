from datetime import date, timedelta

def get_team_name(all_teams, teamid):
    for t in all_teams:
        if int(t['teamid']) == int(teamid):
            return t['teamname']
            
class FifaDate():

    def convert_days_to_py_date(self, days):
        """Convert birthdate or playerjointeamdate into python datetime.date format."""

        return date(year=1582, month=10, day=14) + timedelta(days=int(days))

    def convert_to_py_date(self, fifa_date):
        """Convert FIFA Date format into python datetime.date format."""
        fifa_date = str(fifa_date)
        if len(fifa_date) == 4:
            # Date contains only year 
            return date(year=int(fifa_date), month=7, day=1)
        elif len(fifa_date) == 8:
            return date(int(fifa_date[:4]), int(fifa_date[4:6]), int(fifa_date[6:]))  
        else:
            return date(year=2017, month=7, day=1)

    def convert_age_to_birthdate(self, current_date, age):
        """Convert Player Age to birthdate for futher database query"""

        start_date = date(year=1582, month=10, day=14)
        current_date = self.convert_to_py_date(fifa_date=current_date)

        birthdate = date(year=current_date.year - int(age), month=current_date.month, day=current_date.day) 
        return (birthdate - start_date).days

    def convert_to_fifa_date(self, current_date):
        """Return days since 14.10.1582 to current date"""
        start_date = date(year=1582, month=10, day=14)
        current_date = self.convert_to_py_date(fifa_date=current_date)
        return (current_date - start_date).days

class PlayerAge():
    def __init__(self, birth_date=141279, current_date=20170701):
        self.birth_date = FifaDate().convert_days_to_py_date(days=birth_date)
        self.current_date = FifaDate().convert_to_py_date(fifa_date=current_date)
        self.age = self.get_age()

    def get_age(self):
        """returns age of your player"""
        return self.current_date.year - self.birth_date.year - ((self.current_date.month, self.current_date.day) < (self.birth_date.month, self.birth_date.day))


class PlayerWage:
    # All modifiers are defined in "playerwage.ini", "PlayerWageDomesticPrestigeMods.csv" and "PlayerWageProfitabilityMods.csv"
    def __init__(self, ovr = 0, age = 0, posid = 0, player_team = None, currency=1):
        if player_team:
            self.ovr = ovr
            self.age = age
            self.posid = posid
            self.leagueid = player_team['league']['leagueid']
            self.club_domestic_prestige = player_team['team']['domesticprestige']
            self.club_profitability = player_team['team']['profitability']
            '''
            print('----------class PlayerWage--------------')
            print(self.leagueid)
            print(self.club_domestic_prestige )
            print(self.club_profitability)
            '''

            '''
            [CONVERSION]
            USDOLLAR = 1.12
            EURO = 1.0
            POUND = 0.88
            '''
            currency_conversion = (1.12, 1.0, 0.88)
            try:
                self.currency = currency_conversion[currency]
            except IndexError:
                self.currency = currency_conversion[1] # Euro

            self.wage = self._calculate_player_wage()
        else:
            self.wage = 500
        self.formated_wage = "{:,}".format(self.wage)

    def _calculate_player_wage(self):
        league_mod = self._ovr_factor(self.ovr) * self.currency * ( self._league_factor(self.leagueid) * self._domestic_presitge(self.leagueid, self.club_domestic_prestige) * self._profitability(self.leagueid, self.club_profitability))
        age_mod = (league_mod * self._age_factor(self.age)) / 100.00
        pos_mod = (league_mod * self._position_factor(self.posid)) / 100.00

        player_wage = int(self._round_to_player_wage(league_mod + age_mod + pos_mod))

        if player_wage < 500:
            player_wage = 500
        return player_wage

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
            return domestic_prestige_table[0][0]

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
            return profitability_table[0][0]

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
    def __init__(self, ovr=0, pot=0, age=0, posid=0, currency=1, value=None):
        if value:
            self.value = value
            self.formated_value = "{:,}".format(self.value)
        else:
            self.ovr = int(ovr)
            self.pot = int(pot)
            self.age = int(age)
            self.posid = int(posid)
            '''
            [CONVERSION]
            USDOLLAR = 1.12
            EURO = 1.0
            POUND = 0.88
            '''
            currency_conversion = (1.12, 1.0, 0.88)
            try:
                self.currency = currency_conversion[int(currency)]
            except IndexError:
                self.currency = currency_conversion[1] # Euro

            self.value = self._calculate_player_value()
            self.formated_value = "{:,}".format(self.value)

    def _calculate_player_value(self):
        basevalue = self._ovr_factor(self.ovr) * self.currency
        pos_mod = basevalue * self._position_factor(self.posid)
        pot_mod = basevalue * self._pot_factor(self.pot - self.ovr)
        age_mod = basevalue * self._age_factor(self.age, self.posid)
        player_value = self._sum_factors(basevalue, pos_mod, pot_mod, age_mod)

        if player_value < 0:
            player_value = basevalue/10

        if player_value < 1000:
            player_value = 10000 # Player value can't be lower than 10 000    

        return int(player_value)

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
        if reminder > divisor / 2:
            return summed_value + (divisor - reminder)
        else:
            return summed_value - reminder

    def _ovr_factor(self, ovr):
        factors = (1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 15000, 20000, 25000, 34000, 40000, 46000, 54000, 61000, 70000, 86000, 105000, 140000, 170000, 205000, 250000, 305000, 365000, 435000, 515000, 605000, 710000, 1200000, 1600000, 2100000, 2700000, 3800000, 4500000, 5200000, 6000000, 7000000, 8500000, 10000000, 12000000, 15000000, 17500000, 21000000, 26000000, 30000000, 34000000, 40000000, 45000000, 52000000, 60000000, 68000000, 75000000, 83000000, 90000000, 110000000, 120000000, 140000000, 150000000, 200000000)
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
        
        factors = (0, 15, 20, 25, 30, 35, 40, 45, 55, 65, 75, 90, 100, 120, 160, 160, 160, 160, 160, 160, 160, 190, 190, 190, 190, 190, 190, 190, 190, 190, 190, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235, 235)
        
        if remaining_potential > len(factors):
            return (factors[-1] / 100)

        try:
            return (factors[remaining_potential] / 100)
        except IndexError:
            return 0
    
    def _age_factor(self, age, posid):
        factors = (18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 30, 42, 50, 48, 48, 48, 48, 46, 44, 40, 35, 30, 25, 15, 0, -25, -40, -50, -65, -65, -65, -75, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000)

        if age > len(factors):
            return (factors[-1] / 100)

        if posid == 0 and age >= 28:
            age -= 2

        try:
            return (factors[age] / 100)
        except IndexError:
            return (factors[-1] / 100)

    def _sum_factors(self, basevalue, *args):
        summed_value = basevalue
        for a in args:
            summed_value += a

        return int(self._round_to_player_value(summed_value))

class PlayerName():
    def __init__(self, player, dict_cached_queries, fifa_edition=18):
        self.fifa_edition = int(fifa_edition)
        self.player = player
        try:
            self.dc_player_names = dict_cached_queries['q_dcplayernames']
        except KeyError:
            self.dc_player_names = None

        try:    
            self.edited_player_names = dict_cached_queries['q_edited_player_names']
        except KeyError:
            self.edited_player_names = None

        self.playername = self.set_player_name()


    def set_player_name(self):
        if self.fifa_edition == 18:
            dcplayernames_start_index = 34000
        else:
            dcplayernames_start_index = 30000

        name = {
            'firstname': int(self.player.firstname_id or 0),
            'lastname': int(self.player.lastname_id or 0),
            'commonname': int(self.player.commonname_id or 0),
            'playerjerseyname': int(self.player.playerjerseyname_id or 0),
        }
      
        if name['firstname'] == 0 and name['lastname'] == 0 and self.edited_player_names is not None:
            for i in range(len(self.edited_player_names)):
                if self.edited_player_names[i].playerid == self.player.playerid:
                    name['firstname'] = self.edited_player_names[i].firstname
                    name['lastname'] = self.edited_player_names[i].surname
                    name['commonname'] = self.edited_player_names[i].commonname 
                    name['playerjerseyname'] = self.edited_player_names[i].playerjerseyname
                    break
        elif self.dc_player_names is not None:
            for key in name:
                if name[key] >= dcplayernames_start_index:
                    # Get playername from dcplayernames
                    name[key] = self.get_dcplayername(name[key])
                else:
                    # Get playername from playernames
                    get_attr = getattr(self.player, key, None)
                    if get_attr is not None and get_attr.name is not None:
                        name[key] = get_attr.name
                    else:
                        name[key] = ""


        # This name will be displayed on website
        if name['commonname']:
            name['knownas'] = name['commonname']
        else:
            name['knownas'] = " ".join((str(name['firstname']), str(name['lastname'])))

        return name

    def get_dcplayername(self, nameid):
        if self.dc_player_names is None:
            return 0
            
        for i in range(len(self.dc_player_names)):
            if self.dc_player_names[i].nameid == nameid:
                return self.dc_player_names[i].name
        
        return nameid

class FifaTeam():
    def __init__(self, teamid, dict_cached_queries):
        pass

class FifaPlayer():

    def __init__(self, player, username, current_date, dict_cached_queries, currency, fifa_edition):
        self.player = player
        self.username = username
        self.dict_cached_queries = dict_cached_queries
        self.team_player_links = dict_cached_queries['q_team_player_links']
        self.q_teams = dict_cached_queries['q_teams']
        self.league_team_links = dict_cached_queries['q_league_team_links']
        self.leagues = dict_cached_queries['q_leagues']
        self.release_clauses = dict_cached_queries['q_release_clauses']
        self.players_stats = dict_cached_queries['q_players_stats']

        # FIFA 18/FIFA 17
        self.fifa_edition = fifa_edition

        # Current Date
        self.current_date = current_date
        self.current_date_py = FifaDate().convert_to_py_date(fifa_date=self.current_date)

        try:
            self.query_player_loans = dict_cached_queries['q_player_loans']
        except KeyError:
            self.query_player_loans = None

        # Currency
        try:
            self.currency = int(currency)
        except KeyError:
            self.currency = 1 # Set Euro as default currency

        self.player_teams = self.set_teams()

        # q_dcplayernames & q_edited_player_names
        self.player_name = PlayerName(self.player, self.dict_cached_queries, self.fifa_edition).playername

        # Player Age
        self.player_age = PlayerAge(self.player.birthdate, current_date)

        # Player Value
        if self.currency == 0:
            # USD
            self.player_value = PlayerValue(self.player.overallrating, self.player.potential, self.player_age.age, self.player.preferredposition1, self.currency, self.player.value_usd)
        elif self.currency == 2:
            # GBP
            self.player_value = PlayerValue(self.player.overallrating, self.player.potential, self.player_age.age, self.player.preferredposition1, self.currency, self.player.value_gbp)
        else:
            # EURO by default
            self.player_value = PlayerValue(self.player.overallrating, self.player.potential, self.player_age.age, self.player.preferredposition1, self.currency, self.player.value_eur)
            
        # Player Wage (slow)
        try:
            self.player_wage = PlayerWage(self.player.overallrating, self.player_age.age, self.player.preferredposition1, self.player_teams['club_team'], int(self.currency))
        except KeyError:
            #print('KeyError: {}'.format(e))
            self.player_teams['club_team'] = {
                'team': {'teamid': 0, 'teamname': "Not Found"},
                'league': {'leagueid': 0, 'leaguename': "Not Found"}, 
            }
            self.player_wage = PlayerWage()

        self.player_stats = self.get_player_stats()
        self.release_clause = self.get_release_clause()
        self.player_contract = self.set_contract()
        self.traits = self.set_traits()
        self.headshot = self.set_headshot()
        self.bodytype = self.get_bodytype()
        self.boots = self.get_boots_name()
        self.haircolor = self.get_hair_color()
    
    def get_player_stats(self):
        stats = {
            "total":    {
                "avg":          0,
                "app":          0,
                "goals":        0,
                "assists":      0,
                "yellowcards":  0,
                "redcards":     0,
                "cleansheets":  0,
            }
        }
        num_of_comps = 0
        for i in range(len(self.players_stats)):
            if self.players_stats[i].playerid == self.player.playerid:
                num_of_comps += 1
                stats["total"]["avg"] += self.players_stats[i].avg      # Avg. Rating
                stats["total"]["app"] += self.players_stats[i].app      # Appearances
                stats["total"]["goals"] += self.players_stats[i].goals
                stats["total"]["assists"] += self.players_stats[i].assists
                stats["total"]["yellowcards"] += self.players_stats[i].yellowcards
                stats["total"]["redcards"] += self.players_stats[i].redcards
                stats["total"]["cleansheets"] += self.players_stats[i].cleansheets
                '''
                stats[self.players_stats[i].tournamentid] = {
                    "avg":          self.players_stats[i].avg,
                    "app":          self.players_stats[i].app,
                    "goals":        self.players_stats[i].goals,
                    "assists":      self.players_stats[i].assists,
                    "yellowcards":  self.players_stats[i].yellowcards,
                    "redcards":     self.players_stats[i].redcards,
                    "cleansheets":  self.players_stats[i].cleansheets,
                    "date1":        self.players_stats[i].date1,
                    "date2":        self.players_stats[i].date2,
                    "date3":        self.players_stats[i].date3,
                }
                '''
                

        if num_of_comps > 0:
            if num_of_comps >= 2:
                stats["total"]["avg"] = int(stats["total"]["avg"] / num_of_comps)
            return stats

        return None

    def get_hair_color(self):
        haircolors = (
            'Blonde',
            'Black',
            'Ash Blonde',
            'Dark Brown',
            'Platinum Blonde',
            'Light Brown',
            'Brown',
            'Red',
            'White',
            'Gray',
            'Green',
            'Violet', 
        )

        try:
            return haircolors[int(self.player.haircolorcode)]
        except Exception:
            return  "{}. Unknown".format(self.player.haircolorcode)

    def get_bodytype(self):
        bodytypes = (
            '0. Invalid',
            '1. Lean',
            '2. Normal',
            '3. Stocky',
            '4. Lean',
            '5. Normal',
            '6. Stocky',
            '7. Lean',
            '8. Normal',
            '9. Stocky',
            '10. Messi',
            '11. Very Tall and Lean',
            '12. Akinfenwa',
            '13. Courtois',
            '14. Neymar',
            '15. Shaqiri',
            '16. Cristiano Ronaldo',
            '17. Leroux (Only Women)',
        )

        try:
            return bodytypes[int(self.player.bodytypecode)]
        except Exception:
            return  "{}. Unknown".format(self.player.bodytypecode)

    def get_boots_name(self):
        boots_names = (
            '0. Invalid',
            '1. EA Black/White',
            '2. EA Black/White',
            '3. EA Black/White',
            '4. EA Black/White',
            '5. EA Black/White',
            '6. EA Black/White',
            '7. EA Black/White',
            '8. EA Black/White',
            '9. EA Black/White',
            '10. EA Black/White',
            '11. EA Black/White',
            '12. EA Black/White',
            '13. EA Black/White',
            '14. EA Black/White',
            '15. EA Black/White',
            '16. adidas F50 TUNiT - Black',
            '17. EA Black/White',
            '18. EA Black/White',
            '19. EA Black/White',
            '20. EA Black/White',
            '21. adidas ACE 17+ PURECONTROL Magnetic Storm',
            '22. adidas ACE 17+ PURECONTROL Ocean Storm',
            '22. EA Black/White',
            '23. adidas ACE 17+ PURECONTROL Thunder Storm',
            '24. adidas ACE 17+ PURECONTROL Pyro Storm',
            '24. EA Black/White',
            '25. adidas ACE 17+ PURECONTROL Earth Storm',
            '26. adidas ACE 17.1 - Mystery Ink/Easy Coral/Core Black - W',
            '26. EA Black/White',
            '27. adidas COPA 17.1 Dust Storm',
            '28. adidas COPA 17.1 - CORE BLACK/SOLAR RED/SOLAR RED',
            '28. EA Black/White',
            '29. adidas COPA 17.1 Ocean Storm',
            '30. adidas NEMEZIZ 17.0 Magnetic Storm',
            '30. EA Black/White',
            '31. adidas NEMEZIZ 17.0 Ocean Storm',
            '32. adidas NEMEZIZ 17.0 Thunder Storm',
            '32. EA Black/White',
            '33. adidas NEMEZIZ 17.0 Pyro Storm',
            '34. adidas NEMEZIZ 17.0 Earth Storm',
            '34. EA Black/White',
            '35. adidas NEMEZIZ 17.1 FG W - WHITE/MYSTERY INK/EASY CORAL - W',
            '36. Joma Vulcano 2.0',
            '36. EA Black/White',
            '37. Hummel Rapid X Blade Bluebird',
            '38. adidas NEMEZIZ MESSI 17.0 Ocean Storm',
            '38. EA Black/White',
            '39. Mizuno Wave Ignitus 3 - White/Black/Lime',
            '40. adidas X 17+ 360SPEED FG Magnetic Storm',
            '40. EA Black/White',
            '41. adidas X 17+ 360SPEED FG Ocean Storm',
            '42. adidas X 17+ 360SPEED FG Thunder Storm',
            '42. EA Black/White',
            '43. New Balance Furon - White/Blue/Orange',
            '44. New Balance Visaro - Blue/White/Orange',
            '44. EA Black/White',
            '45. Nike Mercurial Superfly VI - Orange/Black/White',
            '46. Nike Tiempo  Legend VII - Black/White/Laser Orange',
            '46. EA Black/White',
            '47. Nike Magista Obra II DF - Laser Orange/Black/White',
            '48. Nike Hypervenom Phantom II DF - Laser Orange/White/Blk',
            '48. EA Black/White',
            '49. Nike Hypervenom - Wolf Grey/Total Orange/Black',
            '50. Nike Magista - Blue/Blue',
            '50. EA Black/White',
            '51. Nike Magista - Blue/Blue/Black',
            '52. Nike Magista - Grey/Blue/Black',
            '52. EA Black/White',
            '53. Nike Tiempo - Black/Black/Green',
            '54. Nike Tiempo - Green/Green/Black',
            '54. EA Black/White',
            '55. Nike Tiempo - Grey/Green/Black',
            '56. Nike Mercurial Superfly - Black/Black/Pink',
            '56. EA Black/White',
            '57. Nike Mercurial Superfly - Grey/Pink/Black',
            '58. Nike Mercurial Superfly - Pink/Pink/Black',
            '58. EA Black/White',
            '59. Nike Hypervenom - Green/Blue/White - W',
            '60. Nike Magista - Green/Blue/White - W',
            '60. EA Black/White',
            '61. Nike Tiempo - Green/Blue/White - W',
            '62. Nike Mercurial Superfly - Green/Blue/White - W',
            '62. EA Black/White',
            '63. Nike Mercurial Superfly - CR7 Chapter 4',
            '64. Puma evoPOWER 1.2 - White/Orange/Electric Blue',
            '64. EA Black/White',
            '65. PUMA evoPower Vigor 1 Graphic - Fiery Coral/Silver/Black',
            '66. Puma EvoSPEED SL - Electric Blue/White/Orange',
            '66. EA Black/White',
            '67. PUMA One 17.1 - Puma White/Black/Fiery Coral/Silver',
            '68. Umbro Speciali Eternal Pro - Yellow/Blue/White',
            '68. EA Black/White',
            '69. Puma One 17.1 FG - Puma Black/Silver',
            '70. EA Black/White',
            '71. Umbro Medusae II - Electric Blue/White/Blazing Yellow',
            '72. Umbro Velocita 3 - Blazing Yellow/Electric Blue',
            '72. EA Black/White',
            '73. Umbro UX Accuro - Blazing Yellow/Electric Blue',
            '74. Umbro Velocita Pro - Green Gecko/Navy/White',
            '74. EA Black/White',
            '75. Under Armour Clutchfit - Black/After Burn/Steel',
            '76. Under Armour Clutchfit - Hyper Green/Graphite/Black',
            '76. EA Black/White',
            '77. Umbro Velocita 3 - Bluefish/White/Black',
            '78. Umbro Medusae II - Black/White/Bluefish',
            '78. EA Black/White',
            '79. EA Black/White',
            '80. Nike Mercurial Vapor - Black',
            '81. Under Armour Speedform - Yellow/Black/Green',
            '81. EA Black/White',
            '82. EA Black/White',
            '83. Under Armour Clutch Fit Force 3 - Black/White/Neon Coral',
            '84. Under Armour Clutch Fit Force 3 - High Viz/Rocket Red/Black',
            '84. EA Black/White',
            '85. Under Armour Spotlight - White/Phoenix Fire/Black',
            '86. Under Armour Spotlight - Black/Viper Green',
            '86. EA Black/White',
            '87. New Balance Visaro 2.0 - Energy Lime/Military Dark Triumph Green/Alpha Pink',
            '88. New Balance Furon 3.0 - Military Dark Triumph/Energy Lime/Military Urban Grey/Alpha Pink/White',
            '88. EA Black/White',
            '89. EA Black/White',
            '90. EA Black/White',
            '91. EA Black/White',
            '92. EA Black/White',
            '93. Mizuno Rebula V1 JAPAN - Blue Atoll/Black/Silver',
            '94. EA Black/White',
            '95. EA Black/White',
            '96. Mizuno Morelia Neo II - Blueprint/Safety Yellow/White',
            '97. Mizuno Morelia Neo II - Orange Clown Fish/White',
            '97. EA Black/White',
            '98. EA Black/White',
            '99. EA Black/White',
            '100. EA Black/White',
            '101. EA Black/White',
            '102. Diadora Maximus RTX',
            '103. Diadora Brazil Axeler RTX 14',
            '103. EA Black/White',
            '104. EA Black/White',
            '105. ASICS DS LIGHT X-FLY 3',
            '106. ASICS DS LIGHT X-FLY 3 SL',
            '106. EA Black/White',
            '107. EA Black/White',
            '108. EA Black/White',
            '109. EA Black/White',
            '110. EA Black/White',
            '111. Joma Aguila Pro FG',
            '112. Joma Champion Max Black White HG',
            '112. EA Black/White',
            '113. EA Black/White',
            '114. EA Black/White',
            '115. EA Black/White',
            '116. EA Black/White',
            '117. EA Black/White',
            '118. EA Black/White',
            '119. EA Black/White',
            '120. EA Black/White',
            '121. EA Black/White',
            '122. EA Black/White',
            '123. EA Black/White',
            '124. EA Black/White',
            '125. EA Black/White',
            '126. EA Black/White',
            '127. EA Black/White',
            '128. Joma Champion Max Royal Fluo Yellow',
            '129. EA Black/White',
            '130. adidas Ace 16.1 Dark Space',
            '131. adidas Ace 16.1 Mercury Pack',
            '131. EA Black/White',
            '132. adidas Ace 16.1 Viper Pack',
            '133. adidas Ace 16.1 Stellar Pack',
            '133. EA Black/White',
            '134. adidas Ace 16.1 Speed of Light',
            '135. adidas Ace 16+ Dark Space',
            '135. EA Black/White',
            '136. adidas Ace 16+ Mercury Pack',
            '137. adidas Ace 16+ Viper Pack',
            '137. EA Black/White',
            '138. adidas Ace 16+ Speed of Light',
            '139. adidas Ace 16+ Stellar Pack',
            '139. EA Black/White',
            '140. adidas adiZero 99Gram',
            '141. adidas Messi 16.1 Speed of Light',
            '141. EA Black/White',
            '142. adidas Messi 16.1 Mercury Pack',
            '143. adidas Messi 16+ Space Dust',
            '143. EA Black/White',
            '144. adidas Messi 16+ Mercury Pack',
            '145. adidas Messi 16+ Speed of Light',
            '145. EA Black/White',
            '146. adidas X 16.1 Dark Space',
            '147. adidas X 16.1 Mercury Pack',
            '147. EA Black/White',
            '148. adidas X 16.1 Speed of Light',
            '149. adidas X 16.1 Viper Pack',
            '149. EA Black/White',
            '150. adidas X 16.1 Stellar Pack',
            '151. adidas X 16+ Dark Space',
            '151. EA Black/White',
            '152. adidas X 16+ Intersport',
            '153. adidas X 16+ Mercury Pack',
            '153. EA Black/White',
            '154. adidas X 16+ Speed of Light',
            '155. adidas X 16+ Viper Pack',
            '155. EA Black/White',
            '156. adidas X 16+ Stellar Pack',
            '157. adidas Ace 16+ White/Black/White',
            '157. EA Black/White',
            '158. adidas X 16+ Black/White/Black',
            '159. ASICS DS LIGHT X-FLY 2 - Pearl White/Electric Blue',
            '159. EA Black/White',
            '160. ASICS LETHAL LEGACY - Flash Yellow/Black',
            '161. ASICS MENACE 3 - Spice Orange/White',
            '161. EA Black/White',
            '162. Lotto Zhero Gravity VIII 200 - Fanta Fluo/White',
            '163. EA Black/White',
            '164. Joma Champion Max - Blue/Green/White',
            '165. Lotto Zhero Gravity Due',
            '165. EA Black/White',
            '166. EA Black/White',
            '167. Mizuno Basara 101 - Black',
            '168. Mizuno Morelia II - Blue',
            '168. EA Black/White',
            '169. Mizuno Morelia Neo II - Blue',
            '170. Mizuno Wave Ignitus 4 - Red',
            '170. EA Black/White',
            '171. New Balance Furon – Bright Cherry/Galaxy/Firefly',
            '172. New Balance Visaro - Galaxy/Bright Cherry/Firefly',
            '172. EA Black/White',
            '173. Nike Hypervenom Phantom II - Pure Platinum/Black/Green',
            '174. Nike Hypervenom Phantom II - Volt/Black/Hyper Turq',
            '174. EA Black/White',
            '175. Nike Hypervenom Phantom II - White/Black/Total Orange',
            '176. Nike Magista - Total Crimson/Black/Volt',
            '176. EA Black/White',
            '177. Nike Magista - White/Black/Pink Blast',
            '178. Nike Magista Obra II - Pure Platinum/Black/Ghost Green',
            '178. EA Black/White',
            '179. Nike Magista Obra II - Volt/Black/Total Orange/Pink',
            '180. Nike Mercurial Superfly V - Pure Platinum/Black/Ghost Green',
            '180. EA Black/White',
            '181. Nike Mercurial Superfly V - Total Crimson/Volt/Black',
            '182. Nike Mercurial Superfly V - White/Black/Volt/Total Orange',
            '182. EA Black/White',
            '183. Nike Tiempo Legend VI - Clear Jade/Black/Volt',
            '184. Nike Tiempo Legend VI - White/Black/Total Orange',
            '184. EA Black/White',
            '185. Nike Tiempo Legend VI - Wolf Grey/Black/Clear Jade',
            '186. Pirma Brasil Accurate - Aqua/Silver',
            '186. EA Black/White',
            '187. Pirma Imperio Legend - Blue Petrol',
            '188. Pirma Supreme Spry - Black/Red',
            '188. EA Black/White',
            '189. PUMA evoPOWER 1.3 Tricks',
            '190. PUMA evoPOWER 1.3',
            '190. EA Black/White',
            '191. PUMA evoPOWER 1.3',
            '192. PUMA evoSPEED SL-S II',
            '192. EA Black/White',
            '193. PUMA evoSPEED SL-S',
            '194. PUMA evoSPEED 1.5 Tricks',
            '194. EA Black/White',
            '195. PUMA evoTOUCH PRO',
            '196. Umbro Medusae - Black/White/Bluebird',
            '196. EA Black/White',
            '197. Umbro Medusae - Grenadine/White/Black',
            '198. Umbro Medusae - White/Black/Grenadine',
            '198. EA Black/White',
            '199. Umbro UX-Accuro - Black/Metallic/Grenadine',
            '200. Umbro UX-Accuro - Grenadine/Black',
            '200. EA Black/White',
            '201. Umbro UX-Accuro - White/Black/Bluebird',
            '202. Umbro Velocita II - Black/White/Grenadine',
            '202. EA Black/White',
            '203. EA Black/White',
            '204. EA Black/White',
            '205. EA Black/White',
            '206. EA Black/White',
            '207. EA Black/White',
            '208. EA Black/White',
            '209. adidas Ace 17+ Blue Blast Intersport',
            '210. adidas Ace 17+ Chequered Black',
            '210. EA Black/White',
            '211. adidas Ace 17+ Blue Blast',
            '212. adidas Ace 17+ Red Limit',
            '212. EA Black/White',
            '213. adidas Ace 17+ Turbocharge',
            '214. adidas Ace 17+ Camouflage',
            '214. EA Black/White',
            '215. adidas Messi 16+ Blue Blast',
            '216. adidas Messi 16+ Turbocharge',
            '216. EA Black/White',
            '217. adidas Messi 16+ Red Limit',
            '218. adidas X 16+ Blue Blast',
            '218. EA Black/White',
            '219. adidas X 16+ Chequered Black',
            '220. adidas X 16+ Red Limit',
            '220. EA Black/White',
            '221. adidas X 16+ Turbocharge',
            '222. adidas X 16+ Camouflage',
            '222. EA Black/White',
            '223. adidas Copa 17.1 Red Limit',
            '224. adidas Copa 17.1 Chequered Black',
            '224. EA Black/White',
            '225. adidas Copa 17.1 Blue Blast',
            '226. adidas Copa 17.1 Turbocharge',
            '226. EA Black/White',
            '227. adidas Copa 17.1 Crowning Glory',
            '228. EA Black/White',
            '229. EA Black/White',
            '230. EA Black/White',
            '231. EA Black/White',
            '232. EA Black/White',
            '233. EA Black/White',
            '234. EA Black/White',
            '235. EA Black/White',
            '236. EA Black/White',
            '237. EA Black/White',
            '238. EA Black/White',
            '239. EA Black/White',
            '240. EA Black/White',
            '241. EA Black/White',
            '242. EA Black/White',
            '243. EA Black/White',
            '244. EA Black/White',
            '245. EA Black/White',
            '246. EA Black/White',
            '247. EA Black/White',
            '248. EA Black/White',
            '249. EA Black/White',
            '250. EA Black/White',
            '251. EA Black/White',
            '252. EA Black/White',
            '253. EA Black/White',
            '254. EA Black/White',
            '255. EA Black/White',
            '256. EA Black/White',
            '257. EA Black/White',
            '258. EA Black/White',
            '259. EA Black/White',
            '260. EA Black/White',
            '261. EA Black/White',
            '262. EA Black/White',
            '263. EA Black/White',
            '264. EA Black/White',
            '265. EA Black/White',
            '266. EA Black/White',
            '267. EA Black/White',
            '268. EA Black/White',
            '269. EA Black/White',
            '270. EA Black/White',
            '271. EA Black/White',
            '272. EA Black/White',
            '273. EA Black/White',
            '274. EA Black/White',
            '275. EA Black/White',
            '276. EA Black/White',
            '277. EA Black/White',
            '278. EA Black/White',
            '279. EA Black/White',
            '280. EA Black/White',
            '281. EA Black/White',
            '282. EA Black/White',
            '283. EA Black/White',
            '284. EA Black/White',
            '285. EA Black/White',
            '286. EA Black/White',
            '287. EA Black/White',
            '288. EA Black/White',
            '289. EA Black/White',
            '290. EA Black/White',
            '291. EA Black/White',
            '292. EA Black/White',
            '293. EA Black/White',
            '294. EA Black/White',
            '295. EA Black/White',
            '296. EA Black/White',
            '297. EA Black/White',
            '298. EA Black/White',
            '299. EA Black/White',
            '300. EA Black/White',
            '301. EA Black/White',
            '302. EA Black/White',
            '303. EA Black/White',
            '304. EA Black/White',
            '305. EA Black/White',
            '306. EA Black/White',
            '307. EA Black/White',
            '308. EA Black/White',
            '309. EA Black/White',
            '310. EA Black/White',
            '311. EA Black/White',
            '312. EA Black/White',
            '313. EA Black/White',
            '314. EA Black/White',
            '315. EA Black/White',
            '316. EA Black/White',
            '317. EA Black/White',
            '318. EA Black/White',
            '319. EA Black/White',
            '320. EA Black/White',
            '321. EA Black/White',
            '322. EA Black/White',
            '323. EA Black/White',
            '324. EA Black/White',
            '325. EA Black/White',
            '326. EA Black/White',
            '327. EA Black/White',
            '328. EA Black/White',
            '329. EA Black/White',
            '330. EA Black/White',
            '331. EA Black/White',
            '332. EA Black/White',
            '333. EA Black/White',
            '334. EA Black/White',
            '335. EA Black/White',
            '336. EA Black/White',
            '337. EA Black/White',
            '338. EA Black/White',
            '339. EA Black/White',
            '340. EA Black/White',
            '341. EA Black/White',
            '342. EA Black/White',
            '343. EA Black/White',
            '344. adidas NEMEZIZ 17.0 Alex Hunter',
            '345. adidas ACE 17+ PURECONTROL',
            '345. EA Black/White',
            '346. adidas X 17+ PURESPEED',

        )
        
        try:
            return boots_names[int(self.player.shoetypecode)]
        except Exception:
            return  "{}. Unknown".format(self.player.shoetypecode)

    def set_traits(self):
        all_traits = list()
        trait1 = int(self.player.trait1)
        trait2 = int(self.player.trait2)

        if trait1 > 0:
            trait1_names = [
                "Inflexibility",
                "Long Throw-in",
                "Power Free kick",
                "Diver",
                "Injury prone",
                "Injury free",
                "Avoids using weaker foot",
                "Dives into tackles",
                "Tries to beat defensive line",
                "Selfish",
                "Leadership",
                "Argues With Referee",
                "Early crosser",
                "Finesse shot",
                "Flair",
                "Long passer",
                "Long shot taker",
                "Skilled dribbling",
                "Playmaker",
                "GK up for corners",
                "Puncher",
                "GK Long throw",
                "Power header",
                "GK One on One",
                "Giant throw-in",
                "Outsite foot shot",
                "Fans favourite",
                "Swerve Pass",
                "Second Wind",
                "Acrobatic Clearance",
            ]

            trait1_binary = bin(trait1)[2:]
            i = 0
            for t in reversed(trait1_binary):
                if t == '1':
                    all_traits.append(trait1_names[i])
                i += 1

        if trait2 > 0:
            trait2_names = [
                "Skilled Dribbling",
                "Flair Passes",
                "Fancy Flicks",
                "Stutter Penalty",
                "Chipped Penalty",
                "Bicycle Kicks",
                "Diving Header",
                "Driven Pass",
                "GK Flat Kick",
                "One Club Player",
                "Team Player",
                "Chip shot",
                "Technical Dribbler",
                "Rushes Out Of Goal",
                "Backs Into Player",
                "Set Play Specialist",
                "Takes Finesse Free Kicks",
                "Target Forward",
                "Cautious With Crosses",
                "Comes For Crossess",
                "Blames Teammates",
                "Saves with Feet",
                "Set Play Specialist",
                "Tornado Skillmove",
            ]

            trait2_binary = bin(trait2)[2:]
            i = 0
            for t in reversed(trait2_binary):
                if t == '1':
                    all_traits.append(trait2_names[i])
                i += 1

        # remove ',' from the end of string
        #if len(all_traits) >= 1: return all_traits[:-1]
             
        return all_traits

    def get_release_clause(self):
        for i in range(len(self.release_clauses)):
            if self.release_clauses[i].playerid == self.player.playerid:
                clause = self.release_clauses[i].release_clause
                self.formated_release_clause = "{:,}".format(clause)
                return clause

        return 0

    def set_headshot(self):
        if self.player.playerid < 280000:
            return "heads/p{playerid}.png".format(playerid=self.player.playerid)
        else:
            return "youthheads/p{headtypecode}{haircolorcode:02d}.png".format(headtypecode=self.player.headtypecode, haircolorcode=self.player.haircolorcode) 

    def update_positions(self):
        available_positions = ('GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW', 'SUB', 'RES')
        if -1 < self.player.preferredposition1 < len(available_positions):
            self.player.preferredposition1 = available_positions[self.player.preferredposition1]

        if -1 < self.player.preferredposition2 < len(available_positions):
            self.player.preferredposition2 = available_positions[self.player.preferredposition2]

        if -1 < self.player.preferredposition3 < len(available_positions):
            self.player.preferredposition3 = available_positions[self.player.preferredposition3]

        if -1 < self.player.preferredposition4 < len(available_positions):
            self.player.preferredposition4 = available_positions[self.player.preferredposition4]

    def set_contract(self):
        contract = dict()
        
        contract['jointeamdate'] = FifaDate().convert_days_to_py_date(days=self.player.playerjointeamdate)
        contract['enddate'] = FifaDate().convert_to_py_date(fifa_date=self.player.contractvaliduntil)

        contract['isloanedout'] = 0
        if self.query_player_loans is None:
            return contract

        for i in range(len(self.query_player_loans)):
            if self.query_player_loans[i].playerid == self.player.playerid:
                for j in range(len(self.q_teams)):
                    if int(self.query_player_loans[i].teamidloanedfrom) == int(self.q_teams[j].teamid):
                        contract['isloanedout'] = 1
                        contract['loan'] = vars(self.query_player_loans[i])
                        contract['enddate']  = FifaDate().convert_to_py_date(fifa_date=self.query_player_loans[i].loandateend)
                        contract['loanedto_clubid'] = self.player_teams['club_team']['team']['teamid']
                        contract['loanedto_clubname'] = self.player_teams['club_team']['team']['teamname']
                        self.player_teams['club_team']['team'] = vars(self.q_teams[j])
                        return contract

        return contract


    def set_teams(self):
        teams = {}
        max_teams = 2
        league = None
        
        for i in range(len(self.team_player_links)):
            if int(self.team_player_links[i].playerid) == int(self.player.playerid):
                for j in range(len(self.q_teams)):
                    if int(self.q_teams[j].teamid) == int(self.team_player_links[i].teamid):
                        league = self.get_league(self.q_teams[j].teamid)
                        if league:
                            if league[1].leagueid == 78 or league[1].leagueid == 2136:
                                # Men's National or Women's National
                                teams['national_team'] = {
                                    'team': vars(self.q_teams[j]),
                                    'team_links': vars(self.team_player_links[i]),
                                    'league': vars(league[0]),
                                    'league_links': vars(league[1]),
                                } 
                            else:
                                teams['club_team'] = {
                                    'team': vars(self.q_teams[j]),
                                    'team_links': vars(self.team_player_links[i]),
                                    'league': vars(league[0]),
                                    'league_links': vars(league[1]),
                                } 
                        
                        if len(teams) >= max_teams:
                            # Player can only have club team and national team
                            return teams
        return teams


    def get_league(self, teamid):
        for i in range(len(self.league_team_links)):
            if self.league_team_links[i].teamid == teamid:
                for j in range(len(self.leagues)):
                    if self.leagues[j].leagueid == self.league_team_links[i].leagueid:
                        return self.leagues[j], self.league_team_links[i]

        return None