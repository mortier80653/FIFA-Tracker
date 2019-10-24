from struct import pack, unpack
from datetime import date, timedelta
try:
    from core.consts import (
        DEFAULT_FIFA_EDITION,
        DEFAULT_DATE,
        UNUSED_TEAMS,
        CURRENCY_CONVERSION,
        BOOTS,
        TRAITS,
    )
    TEST_DEBUG = False
except ModuleNotFoundError:
    from consts import (
        DEFAULT_FIFA_EDITION,
        DEFAULT_DATE,
        UNUSED_TEAMS,
        CURRENCY_CONVERSION,
        BOOTS,
        TRAITS,
    )
    TEST_DEBUG = True


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

        birthdate = date(year=current_date.year - int(age),
                         month=current_date.month, day=current_date.day)
        return (birthdate - start_date).days

    def convert_to_fifa_date(self, current_date):
        """Return days since 14.10.1582 to current date"""
        start_date = date(year=1582, month=10, day=14)
        current_date = self.convert_to_py_date(fifa_date=current_date)
        return (current_date - start_date).days


class PlayerAge():
    def __init__(self, birth_date=141279, current_date=DEFAULT_DATE[str(DEFAULT_FIFA_EDITION)]):
        self.birth_date = FifaDate().convert_days_to_py_date(days=birth_date)
        self.current_date = FifaDate().convert_to_py_date(fifa_date=current_date)
        self.age = self.get_age()

    def get_age(self):
        """returns age of your player"""
        return self.current_date.year - self.birth_date.year - ((self.current_date.month, self.current_date.day) < (self.birth_date.month, self.birth_date.day))


class PlayerWage:
    # All modifiers are defined in "playerwage.ini", "PlayerWageDomesticPrestigeMods.csv" and "PlayerWageProfitabilityMods.csv"
    # Currency conversion in cmsettings.ini
    def __init__(self, ovr=0, age=0, posid=0, player_team=None, currency=1, fifa_edition=DEFAULT_FIFA_EDITION):
        self.fifa_edition = str(fifa_edition)
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
            self._set_currency(currency)

            self.wage = self._calculate_player_wage()
        else:
            self.wage = 500
        self.formated_wage = "{:,}".format(self.wage)

    def _set_currency(self, currency):
        try:
            self.currency = CURRENCY_CONVERSION[self.fifa_edition][currency]
        except IndexError:
            self.currency = CURRENCY_CONVERSION[self.fifa_edition][1]  # Euro

    def _cfloat_mul(self, x, y):
        # Single precision float as in assembler
        return unpack('f', pack('f', x*y))[0]

    def _calculate_player_wage(self):
        league_mod = (
                self._ovr_factor(self.ovr) * self.currency *
                (
                    self._league_factor(self.leagueid) *
                    self._domestic_presitge(self.leagueid, self.club_domestic_prestige) *
                    self._profitability(self.leagueid, self.club_profitability)
                )
        )
        age_mod = self._cfloat_mul(league_mod, self._age_factor(self.age)) / 100.00
        pos_mod = self._cfloat_mul(league_mod, self._position_factor(self.posid)) / 100.00

        player_wage = int(self._round_to_player_wage(
            league_mod + age_mod + pos_mod)
        )
        if TEST_DEBUG:
            print("\nLeague_mod: {}\nage_mod: {}\npos_mod: {}\n player_wage raw: {}\n player_wage: {}\n".format(
                league_mod, age_mod, pos_mod, league_mod + age_mod + pos_mod, player_wage
            ))

        if player_wage < 500:
            player_wage = 500
        return player_wage

    def _league_factor(self, leagueid):
        # playerswages.ini -> [WAGE_LEAGUE]
        factors = {
            '17': {
                13: 70,     # England Premier League
                53: 43,     # Spain Primera
                31: 45,     # Italy Serie A
                19: 50,     # Germany Bundesliga 1
                16: 40,     # France Ligue 1
                10: 22,     # Netherlands
                14: 30,     # England Championship
                20: 20,     # Germany Bundesliga 2
                32: 10,     # Italy Serie B
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
                349: 14,    # JapanJ1
            },
            '18': {
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
            },
            '19': {
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
                2076: 7,    # Germany 3. Liga
                2012: 16,   # China Super League
            },
            '20': {
                13: 70,     # EnglandPremierLeague
                53: 43,     # SpainPrimera
                31: 45,     # ItalySerieA
                19: 50,     # GermanyBundesliga1
                16: 40,     # FranceLigue1
                10: 22,     # Netherlands
                14: 30,     # EnglandChampionship
                20: 20,     # GermanyBundesliga2
                32: 10,     # ItalySerieB
                83: 8,      # Korea
                308: 18,    # Portugal
                54: 12,     # SpainSegundaA
                56: 8,      # Sweden
                189: 20,    # Switzerland
                39: 15,     # MLS
                17: 10,     # FranceLigue2
                341: 25,    # Mexico
                335: 6,     # Chile
                336: 4,     # Colombia
                67: 33,     # Russia
                80: 22,     # Austria
                4: 21,      # Belguim
                1: 20,      # Denmark
                41: 10,     # Norway
                68: 32,     # Turkey
                60: 8,      # EnglandLeagueOne
                66: 13,     # Poland
                350: 25,    # SaudiArabia
                351: 8,     # Australia
                353: 15,    # Argentina
                61: 8,      # EnglandLeagueTwo
                50: 10,     # Scotland
                65: 3,      # Ireland
                7: 15,      # Brazil
                349: 14,    # JapanJ1
                2076: 7,    # Germany3.Liga
                2012: 16,   # ChinaSuperLeague
                330: 12,    # RomaniaLiga1
            }
        }

        try:
            return factors[self.fifa_edition][leagueid]
        except KeyError:
            return 20   # Default League Modifier

    def _ovr_factor(self, ovr):
        # playerswages.ini -> [WAGE_RATINGRANGE]
        factors = {
            '17': (
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                45,
                45,
                45,
                45,
                45,
                45,
                45,
                45,
                45,
                50,
                50,
                50,
                50,
                50,
                50,
                50,
                50,
                50,
                50,
                60,
                60,
                60,
                60,
                60,
                60,
                80,
                80,
                80,
                120,
                120,
                120,
                250,
                250,
                250,
                300,
                300,
                300,
                420,
                420,
                420,
                500,
                500,
                500,
                600,
                600,
                600,
                650,
                650,
                850,
                850,
                1000,
                1000,
                1300,
                1300,
                1300,
                1800,
                1800,
                2000,
                2000,
                2000,
                3000,
                3000,
                5000,
                5000,
                5000,
            ),
            '18': (
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                20,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                45,
                45,
                45,
                45,
                45,
                45,
                45,
                45,
                45,
                50,
                50,
                50,
                50,
                50,
                50,
                50,
                50,
                50,
                50,
                60,
                60,
                60,
                60,
                60,
                60,
                80,
                80,
                80,
                120,
                120,
                120,
                250,
                250,
                250,
                300,
                300,
                300,
                420,
                420,
                420,
                500,
                500,
                500,
                600,
                600,
                600,
                650,
                650,
                850,
                850,
                1000,
                1000,
                1300,
                1300,
                1300,
                1800,
                1800,
                2000,
                2000,
                2000,
                3000,
                3000,
                5000,
                5000,
                5000,
            ),
            '19': (
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                40,
                45,
                45,
                45,
                45,
                45,
                50,
                50,
                50,
                50,
                50,
                55,
                55,
                55,
                55,
                55,
                55,
                55,
                55,
                60,
                60,
                70,
                70,
                80,
                90,
                105,
                120,
                140,
                165,
                195,
                230,
                265,
                300,
                340,
                370,
                400,
                420,
                450,
                480,
                530,
                560,
                600,
                650,
                710,
                780,
                850,
                925,
                1000,
                1200,
                1250,
                1300,
                1600,
                1800,
                2000,
                2000,
                2500,
                2500,
                3000,
                3000,
                5000,
                5000,
            ),
            '20': (
                50,  # If ovr == 0
                50,  # If ovr == 1
                50,  # If ovr == 2
                50,  # If ovr == 3
                50,  # If ovr == 4
                50,  # If ovr == 5
                50,  # If ovr == 6
                50,  # If ovr == 7
                50,  # If ovr == 8
                50,  # If ovr == 9
                50,  # If ovr == 10
                50,  # If ovr == 11
                50,  # If ovr == 12
                50,  # If ovr == 13
                50,  # If ovr == 14
                50,  # If ovr == 15
                50,  # If ovr == 16
                50,  # If ovr == 17
                50,  # If ovr == 18
                50,  # If ovr == 19
                50,  # If ovr == 20
                50,  # If ovr == 21
                50,  # If ovr == 22
                50,  # If ovr == 23
                50,  # If ovr == 24
                50,  # If ovr == 25
                50,  # If ovr == 26
                50,  # If ovr == 27
                50,  # If ovr == 28
                50,  # If ovr == 29
                50,  # If ovr == 30
                50,  # If ovr == 31
                50,  # If ovr == 32
                50,  # If ovr == 33
                50,  # If ovr == 34
                50,  # If ovr == 35
                50,  # If ovr == 36
                50,  # If ovr == 37
                50,  # If ovr == 38
                50,  # If ovr == 39
                50,  # If ovr == 40
                50,  # If ovr == 41
                50,  # If ovr == 42
                50,  # If ovr == 43
                50,  # If ovr == 44
                50,  # If ovr == 45
                55,  # If ovr == 46
                55,  # If ovr == 47
                55,  # If ovr == 48
                55,  # If ovr == 49
                55,  # If ovr == 50
                60,  # If ovr == 51
                60,  # If ovr == 52
                60,  # If ovr == 53
                60,  # If ovr == 54
                60,  # If ovr == 55
                65,  # If ovr == 56
                65,  # If ovr == 57
                65,  # If ovr == 58
                65,  # If ovr == 59
                65,  # If ovr == 60
                70,  # If ovr == 61
                75,  # If ovr == 62
                85,  # If ovr == 63
                95,  # If ovr == 64
                105,  # If ovr == 65
                120,  # If ovr == 66
                140,  # If ovr == 67
                165,  # If ovr == 68
                195,  # If ovr == 69
                230,  # If ovr == 70
                265,  # If ovr == 71
                300,  # If ovr == 72
                340,  # If ovr == 73
                370,  # If ovr == 74
                400,  # If ovr == 75
                420,  # If ovr == 76
                450,  # If ovr == 77
                480,  # If ovr == 78
                530,  # If ovr == 79
                560,  # If ovr == 80
                600,  # If ovr == 81
                650,  # If ovr == 82
                710,  # If ovr == 83
                780,  # If ovr == 84
                850,  # If ovr == 85
                925,  # If ovr == 86
                1000,  # If ovr == 87
                1200,  # If ovr == 88
                1250,  # If ovr == 89
                1300,  # If ovr == 90
                1600,  # If ovr == 91
                1800,  # If ovr == 92
                2000,  # If ovr == 93
                2000,  # If ovr == 94
                2500,  # If ovr == 95
                2500,  # If ovr == 96
                3000,  # If ovr == 97
                3000,  # If ovr == 98
                5000,  # If ovr == 99
            )
        }

        try:
            return factors[self.fifa_edition][ovr]
        except IndexError:
            return 0

    def _age_factor(self, age):
        # playerswages.ini -> [WAGE_AGE]
        factors = {
            '17': (
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -35,
                -35,
                -35,
                -10,
                -10,
                0,
                0,
                0,
                10,
                15,
                15,
                20,
                20,
                15,
                15,
                15,
                15,
                15,
                -15,
                -15,
                -15,
                -15,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
            ),
            '18': (
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -35,
                -35,
                -35,
                -10,
                -10,
                0,
                0,
                0,
                10,
                15,
                15,
                20,
                20,
                15,
                15,
                15,
                15,
                15,
                -15,
                -15,
                -15,
                -15,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
            ),
            '19': (
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -60,
                -45,
                -45,
                -45,
                -15,
                -15,
                0,
                0,
                0,
                10,
                15,
                15,
                20,
                20,
                15,
                15,
                15,
                15,
                15,
                -15,
                -15,
                -15,
                -15,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
                -20,
            ),
            '20': (
                -85,  # If age == 0
                -85,  # If age == 1
                -85,  # If age == 2
                -85,  # If age == 3
                -85,  # If age == 4
                -85,  # If age == 5
                -85,  # If age == 6
                -85,  # If age == 7
                -85,  # If age == 8
                -85,  # If age == 9
                -85,  # If age == 10
                -85,  # If age == 11
                -85,  # If age == 12
                -85,  # If age == 13
                -85,  # If age == 14
                -85,  # If age == 15
                -85,  # If age == 16
                -85,  # If age == 17
                -60,  # If age == 18
                -35,  # If age == 19
                -15,  # If age == 20
                -15,  # If age == 21
                0,  # If age == 22
                0,  # If age == 23
                0,  # If age == 24
                10,  # If age == 25
                15,  # If age == 26
                15,  # If age == 27
                20,  # If age == 28
                20,  # If age == 29
                15,  # If age == 30
                15,  # If age == 31
                15,  # If age == 32
                15,  # If age == 33
                15,  # If age == 34
                -15,  # If age == 35
                -15,  # If age == 36
                -15,  # If age == 37
                -15,  # If age == 38
                      # For some reason age 38 is the max...
            )
        }

        try:
            return factors[self.fifa_edition][age]
        except IndexError:
            return 0

    def _position_factor(self, posid):
        # playerswages.ini -> [WAGE_POSITION]
        factors = {
            '17': (
                -30,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
            ),
            '18': (
                -30,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
            ),
            '19': (
                -30,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                -10,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
            ),
            '20': (
                -30,  # If position == GK
                -10,  # If position == SW
                -10,  # If position == RWB
                -10,  # If position == RB
                -10,  # If position == RCB
                -10,  # If position == CB
                -10,  # If position == LCB
                -10,  # If position == LB
                -10,  # If position == LWB
                -10,  # If position == RDM
                -10,  # If position == CDM
                -10,  # If position == LDM
                0,  # If position == RM
                0,  # If position == RCM
                0,  # If position == CM
                0,  # If position == LCM
                0,  # If position == LM
                0,  # If position == RAM
                0,  # If position == CAM
                0,  # If position == LAM
                10,  # If position == RF
                10,  # If position == CF
                10,  # If position == LF
                10,  # If position == RW
                10,  # If position == RS
                10,  # If position == ST
                10,  # If position == LS
                10,  # If position == LW
                0,  # If position == SUB
                0,  # If position == RES
            )
        }

        try:
            return factors[self.fifa_edition][posid]
        except IndexError:
            return factors[0]

    def _domestic_presitge(self, leagueid, club_domestic_prestige):
        domestic_prestige_table = {
            '17': {
                0: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2,),
                13: (0, 1, 1, 1.1, 1.1, 1.3, 1.3, 1.5, 1.6, 1.6, 1.7,),
                53: (0, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9, 1, 1, 1.5, 3.5,),
                31: (0, 0.7, 0.8, 1, 1, 1.5, 1.5, 1.6, 1.7, 1.7, 2,),
                19: (0, 1, 1, 1, 1.1, 1.1, 1.1, 1.4, 1.2, 1.6, 2,),
                16: (0, 1, 1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.5, 1.6, 1.6,),
                10: (0, 1, 1, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.5, 1.5,),
                14: (0, 0.8, 0.8, 1, 1, 1.8, 1.8, 1.8, 1.8, 2.2, 2.2,),
                20: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2,),
                32: (0, 1, 1, 1, 1.1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.2,),
                83: (0, 1.4, 1.4, 1.5, 1.5, 1.5, 1.6, 1.6, 1.6, 2, 2,),
                308: (0, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4,),
                54: (0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4, 1.5, 1.5,),
                56: (0, 1, 1, 1.2, 1.2, 1.4, 1.4, 1.5, 1.5, 2, 2,),
                189: (0, 1, 1, 1, 1, 1.3, 1.3, 1.6, 1.6, 1.8, 1.8,),
                39: (0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,),
                17: (0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4, 1.5, 1.5,),
                341: (0, 1, 1, 1, 1, 1.5, 1.5, 2, 2, 2.5, 2.5,),
                335: (0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.6, 1.8, 2, 2, 2.3,),
                336: (0, 1.2, 1.2, 1.2, 1.2, 1.4, 1.4, 2, 2.5, 2.5, 3,),
                67: (0, 1, 1, 1, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8,),
                80: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.7, 1.7, 1.8, 1.8,),
                4: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.4, 1.5, 1.5, 2, 2,),
                1: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.4, 1.5, 1.5, 2, 2,),
                41: (0, 1, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.5, 1.5,),
                68: (0, 1, 1, 1, 1, 1.2, 1.2, 1.6, 1.6, 2, 2,),
                60: (0, 1.8, 1.8, 1.8, 2.1, 2.1, 2.1, 2.3, 2.3, 2.5, 2.5,),
                66: (0, 1, 1, 1.2, 1.3, 1.3, 1.6, 1.6, 1.8, 1.8, 1.8,),
                350: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8, 2, 2, 2,),
                351: (0, 1, 1, 1, 1, 1.2, 1.2, 1.4, 1.4, 1.4, 1.4,),
                353: (0, 2, 2, 2, 2, 2.2, 2.2, 2.4, 2.4, 2.6, 2.6,),
                61: (0, 2, 2, 2, 2.5, 2.5, 2.5, 3, 3, 3, 3,),
                50: (0, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5,),
                65: (0, 1.5, 1.5, 1.5, 1.7, 1.7, 1.7, 2, 2, 2, 2,),
                7: (0, 2, 2, 2, 2, 2.2, 2.6, 3, 3.2, 3.2, 3.2,),
                349: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8, 2, 2, 2,),
            },
            '18': {
                0: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2,),
                13: (0, 1, 1, 1.1, 1.1, 1.3, 1.3, 1.5, 1.6, 1.6, 1.7,),
                53: (0, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9, 1, 1, 1.5, 3.5,),
                31: (0, 0.7, 0.8, 1, 1, 1.5, 1.5, 1.6, 1.7, 1.7, 2,),
                19: (0, 1, 1, 1, 1.1, 1.1, 1.1, 1.4, 1.2, 1.6, 2,),
                16: (0, 1, 1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.5, 1.6, 1.6,),
                10: (0, 1, 1, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.5, 1.5,),
                14: (0, 0.8, 0.8, 1, 1, 1.8, 1.8, 1.8, 1.8, 2.2, 2.2,),
                20: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2,),
                32: (0, 1, 1, 1, 1.1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.2,),
                83: (0, 1.4, 1.4, 1.5, 1.5, 1.5, 1.6, 1.6, 1.6, 2, 2,),
                308: (0, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4,),
                54: (0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4, 1.5, 1.5,),
                56: (0, 1, 1, 1.2, 1.2, 1.4, 1.4, 1.5, 1.5, 2, 2,),
                189: (0, 1, 1, 1, 1, 1.3, 1.3, 1.6, 1.6, 1.8, 1.8,),
                39: (0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,),
                17: (0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4, 1.5, 1.5,),
                341: (0, 1, 1, 1, 1, 1.5, 1.5, 2, 2, 2.5, 2.5,),
                335: (0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.6, 1.8, 2, 2, 2.3,),
                336: (0, 1.2, 1.2, 1.2, 1.2, 1.4, 1.4, 2, 2.5, 2.5, 3,),
                67: (0, 1, 1, 1, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8,),
                80: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.7, 1.7, 1.8, 1.8,),
                4: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.4, 1.5, 1.5, 2, 2,),
                1: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.4, 1.5, 1.5, 2, 2,),
                41: (0, 1, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.5, 1.5,),
                68: (0, 1, 1, 1, 1, 1.2, 1.2, 1.6, 1.6, 2, 2,),
                60: (0, 1.8, 1.8, 1.8, 2.1, 2.1, 2.1, 2.3, 2.3, 2.5, 2.5,),
                66: (0, 1, 1, 1.2, 1.3, 1.3, 1.6, 1.6, 1.8, 1.8, 1.8,),
                350: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8, 2, 2, 2,),
                351: (0, 1, 1, 1, 1, 1.2, 1.2, 1.4, 1.4, 1.4, 1.4,),
                353: (0, 2, 2, 2, 2, 2.2, 2.2, 2.4, 2.4, 2.6, 2.6,),
                61: (0, 2, 2, 2, 2.5, 2.5, 2.5, 3, 3, 3, 3,),
                50: (0, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5,),
                65: (0, 1.5, 1.5, 1.5, 1.7, 1.7, 1.7, 2, 2, 2, 2,),
                7: (0, 2, 2, 2, 2, 2.2, 2.6, 3, 3.2, 3.2, 3.2,),
                349: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8, 2, 2, 2,),
                2076: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2,),
            },
            '19': {
                0: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2,),
                13: (0, 1, 1, 1.1, 1.1, 1.3, 1.3, 1.5, 1.6, 1.6, 1.7,),
                53: (0, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9, 1, 1, 1.5, 3.5,),
                31: (0, 0.7, 0.8, 1, 1, 1.5, 1.5, 1.6, 1.7, 1.7, 2,),
                19: (0, 1, 1, 1, 1.1, 1.1, 1.1, 1.4, 1.2, 1.6, 2,),
                16: (0, 1, 1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.5, 1.6, 1.6,),
                10: (0, 1, 1, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.5, 1.5,),
                14: (0, 0.8, 0.8, 1, 1, 1.8, 1.8, 1.8, 1.8, 2.2, 2.2,),
                20: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2,),
                32: (0, 1, 1, 1, 1.1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.2,),
                83: (0, 1.4, 1.4, 1.5, 1.5, 1.5, 1.6, 1.6, 1.6, 2, 2,),
                308: (0, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4,),
                54: (0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4, 1.5, 1.5,),
                56: (0, 1, 1, 1.2, 1.2, 1.4, 1.4, 1.5, 1.5, 2, 2,),
                189: (0, 1, 1, 1, 1, 1.3, 1.3, 1.6, 1.6, 1.8, 1.8,),
                39: (0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,),
                17: (0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4, 1.5, 1.5,),
                341: (0, 1, 1, 1, 1, 1.5, 1.5, 2, 2, 2.5, 2.5,),
                335: (0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.6, 1.8, 2, 2, 2.3,),
                336: (0, 1.2, 1.2, 1.2, 1.2, 1.4, 1.4, 2, 2.5, 2.5, 3,),
                67: (0, 1, 1, 1, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8,),
                80: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.7, 1.7, 1.8, 1.8,),
                4: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.4, 1.5, 1.5, 2, 2,),
                1: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.4, 1.5, 1.5, 2, 2,),
                41: (0, 1, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.5, 1.5,),
                68: (0, 1, 1, 1, 1, 1.2, 1.2, 1.6, 1.6, 2, 2,),
                60: (0, 1.8, 1.8, 1.8, 2.1, 2.1, 2.1, 2.3, 2.3, 2.5, 2.5,),
                66: (0, 1, 1, 1.2, 1.3, 1.3, 1.6, 1.6, 1.8, 1.8, 1.8,),
                350: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8, 2, 2, 2,),
                351: (0, 1, 1, 1, 1, 1.2, 1.2, 1.4, 1.4, 1.4, 1.4,),
                353: (0, 2, 2, 2, 2, 2.2, 2.2, 2.4, 2.4, 2.6, 2.6,),
                61: (0, 2, 2, 2, 2.5, 2.5, 2.5, 3, 3, 3, 3,),
                50: (0, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5,),
                65: (0, 1.5, 1.5, 1.5, 1.7, 1.7, 1.7, 2, 2, 2, 2,),
                7: (0, 2, 2, 2, 2, 2.2, 2.6, 3, 3.2, 3.2, 3.2,),
                349: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8, 2, 2, 2,),
                2076: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2,),
            },
            '20': {
                0: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2),
                13: (0, 1, 1, 1.1, 1.1, 1.3, 1.3, 1.5, 1.6, 1.6, 1.7),
                53: (0, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9, 1, 1, 1.5, 3.5),
                31: (0, 0.7, 0.8, 1, 1, 1.5, 1.5, 1.6, 1.7, 1.7, 2),
                19: (0, 1, 1, 1, 1.1, 1.1, 1.1, 1.4, 1.2, 1.6, 2),
                16: (0, 1, 1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.5, 1.6, 1.6),
                10: (0, 1, 1, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.5, 1.5),
                14: (0, 0.8, 0.8, 1, 1, 1.8, 1.8, 1.8, 1.8, 2.2, 2.2),
                20: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2),
                32: (0, 1, 1, 1, 1.1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.2),
                83: (0, 1.4, 1.4, 1.5, 1.5, 1.5, 1.6, 1.6, 1.6, 2, 2),
                308: (0, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4),
                54: (0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4, 1.5, 1.5),
                56: (0, 1, 1, 1.2, 1.2, 1.4, 1.4, 1.5, 1.5, 2, 2),
                189: (0, 1, 1, 1, 1, 1.3, 1.3, 1.6, 1.6, 1.8, 1.8),
                39: (0, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5),
                17: (0, 1.1, 1.1, 1.2, 1.2, 1.3, 1.3, 1.4, 1.4, 1.5, 1.5),
                341: (0, 1, 1, 1, 1, 1.5, 1.5, 2, 2, 2.5, 2.5),
                335: (0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.6, 1.8, 2, 2, 2.3),
                336: (0, 1.2, 1.2, 1.2, 1.2, 1.4, 1.4, 2, 2.5, 2.5, 3),
                67: (0, 1, 1, 1, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8),
                80: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.7, 1.7, 1.8, 1.8),
                4: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.4, 1.5, 1.5, 2, 2),
                1: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.4, 1.5, 1.5, 2, 2),
                41: (0, 1, 1, 1, 1.1, 1.1, 1.2, 1.2, 1.2, 1.5, 1.5),
                68: (0, 1, 1, 1, 1, 1.2, 1.2, 1.6, 1.6, 2, 2),
                60: (0, 1.8, 1.8, 1.8, 2.1, 2.1, 2.1, 2.3, 2.3, 2.5, 2.5),
                66: (0, 1, 1, 1.2, 1.3, 1.3, 1.6, 1.6, 1.8, 1.8, 1.8),
                350: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8, 2, 2, 2),
                351: (0, 1, 1, 1, 1, 1.2, 1.2, 1.4, 1.4, 1.4, 1.4),
                353: (0, 2, 2, 2, 2, 2.2, 2.2, 2.4, 2.4, 2.6, 2.6),
                61: (0, 2, 2, 2, 2.5, 2.5, 2.5, 3, 3, 3, 3),
                50: (0, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5),
                65: (0, 1.5, 1.5, 1.5, 1.7, 1.7, 1.7, 2, 2, 2, 2),
                7: (0, 2, 2, 2, 2, 2.2, 2.6, 3, 3.2, 3.2, 3.2),
                349: (0, 1.2, 1.2, 1.2, 1.4, 1.4, 1.6, 1.8, 2, 2, 2),
                2076: (0, 1.2, 1.2, 1.4, 1.4, 1.5, 1.8, 1.8, 1.8, 2, 2),
            }
        }

        if club_domestic_prestige > 10:
            club_domestic_prestige = 10
        elif club_domestic_prestige <= 0:
            club_domestic_prestige = 0

        try:
            return domestic_prestige_table[self.fifa_edition][leagueid][club_domestic_prestige]
        except (KeyError, IndexError):
            return domestic_prestige_table[self.fifa_edition][0][club_domestic_prestige]

    def _profitability(self, leagueid, club_profitability):
        profitability_table = {
            '17': {
                0: (0, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1.1, 1.1, 1, 1,),
                13: (0, 1.6, 1.6, 1.5, 1.5, 1.3, 1.3, 1, 1, 1, 1,),
                53: (0, 1.5, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1, 0.8, 0.8,),
                31: (0, 2, 1.8, 1.4, 1.4, 1.2, 1, 0.9, 0.8, 0.8, 0.7,),
                19: (0, 1.5, 1.5, 1.5, 1.2, 1.2, 1, 1, 1, 1, 1,),
                16: (0, 2, 1.8, 1.8, 1.5, 1.2, 1, 1, 1, 0.8, 0.8,),
                10: (0, 1.5, 1.5, 1.3, 1.2, 1.1, 1, 1, 0.9, 0.8, 0.8,),
                14: (0, 1.8, 1.8, 1.6, 1.6, 1.3, 1.3, 1.1, 1.1, 0.8, 0.8,),
                20: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.2, 1.1, 0.8, 0.7, 0.7,),
                32: (0, 1.1, 1.1, 1, 1, 1, 0.9, 0.9, 0.8, 0.8, 0.8,),
                83: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1, 1,),
                308: (0, 1.5, 1.5, 1.3, 1.3, 1.1, 1.1, 1, 1, 0.8, 0.8,),
                54: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3, 1.2, 1.2,),
                56: (0, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1.1, 1.1, 1, 1,),
                189: (0, 2, 2, 1.5, 1.5, 1.3, 1.3, 1, 1, 1, 1,),
                39: (0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,),
                17: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3, 1.2, 1.2,),
                341: (0, 2, 1.8, 1.6, 1.4, 1.2, 1.2, 1, 1, 0.8, 0.8,),
                335: (0, 2, 2, 2, 2, 1.4, 1.4, 1.2, 1.2, 1, 1,),
                336: (0, 1.1, 1.1, 1.1, 1.1, 1, 1, 1, 0.8, 0.8, 0.8,),
                67: (0, 2, 2, 1.8, 1.8, 1.7, 1.7, 1.7, 1.4, 1.4, 1.4,),
                80: (0, 1.8, 1.8, 1.6, 1.4, 1.2, 1, 1, 1, 0.8, 0.8,),
                4: (0, 1.4, 1.4, 1.2, 1.1, 1.1, 1.1, 1.1, 1.1, 1, 1,),
                1: (0, 1.4, 1.4, 1.2, 1.1, 1.1, 1.1, 1.1, 1.1, 1, 1,),
                41: (0, 1.2, 1.2, 1.2, 1.1, 1.1, 1.1, 1, 1, 1, 1,),
                68: (0, 1.8, 1.8, 1.6, 1.4, 1.2, 1, 1, 1, 1, 1,),
                60: (0, 1.6, 1.6, 1.6, 1.5, 1.5, 1.5, 1.4, 1.4, 1, 1,),
                66: (0, 1.2, 1.2, 1, 1, 1, 1, 0.9, 0.9, 0.8, 0.8,),
                350: (0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.3, 1.2, 1, 1,),
                351: (0, 2.5, 2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 1,),
                353: (0, 1.2, 1.2, 1.1, 1.1, 1, 1, 0.9, 0.9, 0.8, 0.8,),
                61: (0, 1.8, 1.8, 1.8, 1.8, 1.8, 1.5, 1.5, 1.5, 1.5, 1.5,),
                50: (0, 2, 2, 2, 2, 2, 1.8, 1.8, 1.8, 1.8, 1.8,),
                65: (0, 1.6, 1.6, 1.6, 1.5, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3,),
                7: (0, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.2, 1, 1, 1,),
                349: (0, 1, 1, 1, 1, 0.8, 0.8, 0.7, 0.7, 0.7, 0.7,),
            },
            '18': {
                0: (0, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1.1, 1.1, 1, 1,),
                13: (0, 1.6, 1.6, 1.5, 1.5, 1.3, 1.3, 1, 1, 1, 1,),
                53: (0, 1.5, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1, 0.8, 0.8,),
                31: (0, 2, 1.8, 1.4, 1.4, 1.2, 1, 0.9, 0.8, 0.8, 0.7,),
                19: (0, 1.5, 1.5, 1.5, 1.2, 1.2, 1, 1, 1, 1, 1,),
                16: (0, 2, 1.8, 1.8, 1.5, 1.2, 1, 1, 1, 0.8, 0.8,),
                10: (0, 1.5, 1.5, 1.3, 1.2, 1.1, 1, 1, 0.9, 0.8, 0.8,),
                14: (0, 1.8, 1.8, 1.6, 1.6, 1.3, 1.3, 1.1, 1.1, 0.8, 0.8,),
                20: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.2, 1.1, 0.8, 0.7, 0.7,),
                32: (0, 1.1, 1.1, 1, 1, 1, 0.9, 0.9, 0.8, 0.8, 0.8,),
                83: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1, 1,),
                308: (0, 1.5, 1.5, 1.3, 1.3, 1.1, 1.1, 1, 1, 0.8, 0.8,),
                54: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3, 1.2, 1.2,),
                56: (0, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1.1, 1.1, 1, 1,),
                189: (0, 2, 2, 1.5, 1.5, 1.3, 1.3, 1, 1, 1, 1,),
                39: (0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,),
                17: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3, 1.2, 1.2,),
                341: (0, 2, 1.8, 1.6, 1.4, 1.2, 1.2, 1, 1, 0.8, 0.8,),
                335: (0, 2, 2, 2, 2, 1.4, 1.4, 1.2, 1.2, 1, 1,),
                336: (0, 1.1, 1.1, 1.1, 1.1, 1, 1, 1, 0.8, 0.8, 0.8,),
                67: (0, 2, 2, 1.8, 1.8, 1.7, 1.7, 1.7, 1.4, 1.4, 1.4,),
                80: (0, 1.8, 1.8, 1.6, 1.4, 1.2, 1, 1, 1, 0.8, 0.8,),
                4: (0, 1.4, 1.4, 1.2, 1.1, 1.1, 1.1, 1.1, 1.1, 1, 1,),
                1: (0, 1.4, 1.4, 1.2, 1.1, 1.1, 1.1, 1.1, 1.1, 1, 1,),
                41: (0, 1.2, 1.2, 1.2, 1.1, 1.1, 1.1, 1, 1, 1, 1,),
                68: (0, 1.8, 1.8, 1.6, 1.4, 1.2, 1, 1, 1, 1, 1,),
                60: (0, 1.6, 1.6, 1.6, 1.5, 1.5, 1.5, 1.4, 1.4, 1, 1,),
                66: (0, 1.2, 1.2, 1, 1, 1, 1, 0.9, 0.9, 0.8, 0.8,),
                350: (0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.3, 1.2, 1, 1,),
                351: (0, 2.5, 2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 1,),
                353: (0, 1.2, 1.2, 1.1, 1.1, 1, 1, 0.9, 0.9, 0.8, 0.8,),
                61: (0, 1.8, 1.8, 1.8, 1.8, 1.8, 1.5, 1.5, 1.5, 1.5, 1.5,),
                50: (0, 2, 2, 2, 2, 2, 1.8, 1.8, 1.8, 1.8, 1.8,),
                65: (0, 1.6, 1.6, 1.6, 1.5, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3,),
                7: (0, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.2, 1, 1, 1,),
                349: (0, 1, 1, 1, 1, 0.8, 0.8, 0.7, 0.7, 0.7, 0.7,),
                2076: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.2, 1.1, 0.8, 0.7, 0.7,),
            },
            '19': {
                0: (0, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1.1, 1.1, 1, 1,),
                13: (0, 1.6, 1.6, 1.5, 1.5, 1.3, 1.3, 1, 1, 1, 1,),
                53: (0, 1.5, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1, 0.8, 0.8,),
                31: (0, 2, 1.8, 1.4, 1.4, 1.2, 1, 0.9, 0.8, 0.8, 0.7,),
                19: (0, 1.5, 1.5, 1.5, 1.2, 1.2, 1, 1, 1, 1, 1,),
                16: (0, 2, 1.8, 1.8, 1.5, 1.2, 1, 1, 1, 0.8, 0.8,),
                10: (0, 1.5, 1.5, 1.3, 1.2, 1.1, 1, 1, 0.9, 0.8, 0.8,),
                14: (0, 1.8, 1.8, 1.6, 1.6, 1.3, 1.3, 1.1, 1.1, 0.8, 0.8,),
                20: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.2, 1.1, 0.8, 0.7, 0.7,),
                32: (0, 1.1, 1.1, 1, 1, 1, 0.9, 0.9, 0.8, 0.8, 0.8,),
                83: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1, 1,),
                308: (0, 1.5, 1.5, 1.3, 1.3, 1.1, 1.1, 1, 1, 0.8, 0.8,),
                54: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3, 1.2, 1.2,),
                56: (0, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1.1, 1.1, 1, 1,),
                189: (0, 2, 2, 1.5, 1.5, 1.3, 1.3, 1, 1, 1, 1,),
                39: (0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,),
                17: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3, 1.2, 1.2,),
                341: (0, 2, 1.8, 1.6, 1.4, 1.2, 1.2, 1, 1, 0.8, 0.8,),
                335: (0, 2, 2, 2, 2, 1.4, 1.4, 1.2, 1.2, 1, 1,),
                336: (0, 1.1, 1.1, 1.1, 1.1, 1, 1, 1, 0.8, 0.8, 0.8,),
                67: (0, 2, 2, 1.8, 1.8, 1.7, 1.7, 1.7, 1.4, 1.4, 1.4,),
                80: (0, 1.8, 1.8, 1.6, 1.4, 1.2, 1, 1, 1, 0.8, 0.8,),
                4: (0, 1.4, 1.4, 1.2, 1.1, 1.1, 1.1, 1.1, 1.1, 1, 1,),
                1: (0, 1.4, 1.4, 1.2, 1.1, 1.1, 1.1, 1.1, 1.1, 1, 1,),
                41: (0, 1.2, 1.2, 1.2, 1.1, 1.1, 1.1, 1, 1, 1, 1,),
                68: (0, 1.8, 1.8, 1.6, 1.4, 1.2, 1, 1, 1, 1, 1,),
                60: (0, 1.6, 1.6, 1.6, 1.5, 1.5, 1.5, 1.4, 1.4, 1, 1,),
                66: (0, 1.2, 1.2, 1, 1, 1, 1, 0.9, 0.9, 0.8, 0.8,),
                350: (0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.3, 1.2, 1, 1,),
                351: (0, 2.5, 2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 1,),
                353: (0, 1.2, 1.2, 1.1, 1.1, 1, 1, 0.9, 0.9, 0.8, 0.8,),
                61: (0, 1.8, 1.8, 1.8, 1.8, 1.8, 1.5, 1.5, 1.5, 1.5, 1.5,),
                50: (0, 2, 2, 2, 2, 2, 1.8, 1.8, 1.8, 1.8, 1.8,),
                65: (0, 1.6, 1.6, 1.6, 1.5, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3,),
                7: (0, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.2, 1, 1, 1,),
                349: (0, 1, 1, 1, 1, 0.8, 0.8, 0.7, 0.7, 0.7, 0.7,),
                2076: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.2, 1.1, 0.8, 0.7, 0.7,),
            },
            '20': {
                0: (0, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1.1, 1.1, 1, 1),
                13: (0, 1.6, 1.6, 1.5, 1.5, 1.3, 1.3, 1, 1, 1, 1),
                53: (0, 1.5, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1, 0.8, 0.8),
                31: (0, 2, 1.8, 1.4, 1.4, 1.2, 1, 0.9, 0.8, 0.8, 0.7),
                19: (0, 1.5, 1.5, 1.5, 1.2, 1.2, 1, 1, 1, 1, 1),
                16: (0, 2, 1.8, 1.8, 1.5, 1.2, 1, 1, 1, 0.8, 0.8),
                10: (0, 1.5, 1.5, 1.3, 1.2, 1.1, 1, 1, 0.9, 0.8, 0.8),
                14: (0, 1.8, 1.8, 1.6, 1.6, 1.3, 1.3, 1.1, 1.1, 0.8, 0.8),
                20: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.2, 1.1, 0.8, 0.7, 0.7),
                32: (0, 1.1, 1.1, 1, 1, 1, 0.9, 0.9, 0.8, 0.8, 0.8),
                83: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1, 1),
                308: (0, 1.5, 1.5, 1.3, 1.3, 1.1, 1.1, 1, 1, 0.8, 0.8),
                54: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3, 1.2, 1.2),
                56: (0, 1.5, 1.5, 1.4, 1.4, 1.2, 1.2, 1.1, 1.1, 1, 1),
                189: (0, 2, 2, 1.5, 1.5, 1.3, 1.3, 1, 1, 1, 1),
                39: (0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5),
                17: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3, 1.2, 1.2),
                341: (0, 2, 1.8, 1.6, 1.4, 1.2, 1.2, 1, 1, 0.8, 0.8),
                335: (0, 2, 2, 2, 2, 1.4, 1.4, 1.2, 1.2, 1, 1),
                336: (0, 1.1, 1.1, 1.1, 1.1, 1, 1, 1, 0.8, 0.8, 0.8),
                67: (0, 2, 2, 1.8, 1.8, 1.7, 1.7, 1.7, 1.4, 1.4, 1.4),
                80: (0, 1.8, 1.8, 1.6, 1.4, 1.2, 1, 1, 1, 0.8, 0.8),
                4: (0, 1.4, 1.4, 1.2, 1.1, 1.1, 1.1, 1.1, 1.1, 1, 1),
                1: (0, 1.4, 1.4, 1.2, 1.1, 1.1, 1.1, 1.1, 1.1, 1, 1),
                41: (0, 1.2, 1.2, 1.2, 1.1, 1.1, 1.1, 1, 1, 1, 1),
                68: (0, 1.8, 1.8, 1.6, 1.4, 1.2, 1, 1, 1, 1, 1),
                60: (0, 1.6, 1.6, 1.6, 1.5, 1.5, 1.5, 1.4, 1.4, 1, 1),
                66: (0, 1.2, 1.2, 1, 1, 1, 1, 0.9, 0.9, 0.8, 0.8),
                350: (0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.3, 1.2, 1, 1),
                351: (0, 2.5, 2.5, 2, 2, 1.5, 1.5, 1, 1, 1, 1),
                353: (0, 1.2, 1.2, 1.1, 1.1, 1, 1, 0.9, 0.9, 0.8, 0.8),
                61: (0, 1.8, 1.8, 1.8, 1.8, 1.8, 1.5, 1.5, 1.5, 1.5, 1.5),
                50: (0, 2, 2, 2, 2, 2, 1.8, 1.8, 1.8, 1.8, 1.8),
                65: (0, 1.6, 1.6, 1.6, 1.5, 1.5, 1.5, 1.4, 1.4, 1.3, 1.3),
                7: (0, 1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.2, 1, 1, 1),
                349: (0, 1, 1, 1, 1, 0.8, 0.8, 0.7, 0.7, 0.7, 0.7),
                2076: (0, 1.6, 1.6, 1.5, 1.5, 1.4, 1.2, 1.1, 0.8, 0.7, 0.7),
            }
        }

        if club_profitability > 10:
            club_profitability = 10
        elif club_profitability <= 0:
            club_profitability = 0

        try:
            return profitability_table[self.fifa_edition][leagueid][club_profitability]
        except (KeyError, IndexError):
            return profitability_table[self.fifa_edition][0][club_profitability]

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
        if reminder > divisor / 2:
            return summed_wage + (divisor - reminder)
        else:
            return summed_wage - reminder


class PlayerValue:
    # All modifiers are defined in "playervalues.ini"
    def __init__(self, ovr=0, pot=0, age=0, posid=0, currency=1, value=None, fifa_edition=DEFAULT_FIFA_EDITION):
        self.fifa_edition = str(fifa_edition)
        if value:
            self.value = value
            self.formated_value = "{:,}".format(self.value)
        else:
            self.ovr = int(ovr)
            self.pot = int(pot)
            self.age = int(age)
            self.posid = int(posid)

            self._set_currency(currency)

            try:
                self.currency = CURRENCY_CONVERSION[self.fifa_edition][currency]
            except IndexError:
                self.currency = CURRENCY_CONVERSION[self.fifa_edition][1]  # Euro

            self.value = self._calculate_player_value()
            self.formated_value = "{:,}".format(self.value)

    def _set_currency(self, currency):
        try:
            self.currency = CURRENCY_CONVERSION[self.fifa_edition][currency]
        except IndexError:
            self.currency = CURRENCY_CONVERSION[self.fifa_edition][1]  # Euro

    def _cfloat_mul(self, x, y):
        # Single precision float as in assembler
        return unpack('f', pack('f', x*y))[0]

    def _calculate_player_value(self):
        basevalue = self._ovr_factor(self.ovr) * self.currency
        pos_mod = (self._cfloat_mul(basevalue, self._position_factor(self.posid))) / 100
        pot_mod = (self._cfloat_mul(basevalue, self._pot_factor(self.pot - self.ovr))) / 100
        age_mod = (self._cfloat_mul(basevalue, self._age_factor(self.age, self.posid))) / 100
        player_value = self._sum_factors(basevalue, pos_mod, pot_mod, age_mod)
        if TEST_DEBUG:
            print("\nbase value: {}\npos_mod: {}\npot_mod: {}\nage_mod: {}\nplayer_value: {}".format(basevalue, pos_mod, pot_mod, age_mod, player_value))

        if player_value <= 0:
            player_value = 0
        elif player_value < 1000:
            player_value = 10000

        return int(player_value)

    def _round_to_player_value(self, summed_value):
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
        if reminder <= (divisor / 2):
            return summed_value - reminder
        else:
            return summed_value + (divisor - reminder)

    def _ovr_factor(self, ovr):
        # playervalues.ini -> [RATINGRANGE]
        # 0-5  = 1000
        # 6-40 = 15000
        # 41-50 = 20000

        factors = {
            '17': (
                0,
                1000,
                1000,
                1000,
                1000,
                1000,
                1000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                14000,
                23000,
                23000,
                23000,
                23000,
                23000,
                23000,
                23000,
                23000,
                23000,
                23000,
                28500,
                34000,
                41000,
                50000,
                60000,
                70000,
                81000,
                92000,
                107000,
                128000,
                156000,
                192500,
                229000,
                296000,
                360000,
                425000,
                496000,
                590000,
                696000,
                915500,
                1125000,
                1450000,
                1975000,
                2312500,
                2800000,
                3600000,
                4750000,
                5800000,
                7000000,
                9750000,
                11500000,
                13700000,
                16000000,
                19800000,
                22800000,
                26850000,
                30900000,
                36000000,
                41500000,
                46500000,
                52000000,
                58000000,
                63500000,
                69500000,
                77000000,
                84000000,
                88000000,
                93000000,
                97000000,
                100000000,
            ),
            '18': (
                0,
                1000,
                1000,
                1000,
                1000,
                1000,
                1000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                25000,
                34000,
                40000,
                46000,
                54000,
                61000,
                70000,
                86000,
                105000,
                140000,
                170000,
                205000,
                250000,
                305000,
                365000,
                435000,
                515000,
                605000,
                710000,
                1200000,
                1600000,
                2100000,
                2700000,
                3800000,
                4500000,
                5200000,
                6000000,
                7000000,
                8500000,
                10000000,
                12000000,
                15000000,
                17500000,
                21000000,
                26000000,
                30000000,
                34000000,
                40000000,
                45000000,
                52000000,
                60000000,
                68000000,
                75000000,
                83000000,
                90000000,
                11000000,
                120000000,
                140000000,
                150000000,
                200000000,
            ),
            '19': (
                0,
                1000,
                1000,
                1000,
                1000,
                1000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                15000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                20000,
                25000,
                34000,
                40000,
                46000,
                54000,
                61000,
                70000,
                86000,
                105000,
                140000,
                170000,
                205000,
                250000,
                305000,
                365000,
                435000,
                515000,
                605000,
                710000,
                1200000,
                1600000,
                2100000,
                2700000,
                3800000,
                4500000,
                5200000,
                6000000,
                7000000,
                8500000,
                10000000,
                12000000,
                15000000,
                17500000,
                21000000,
                26000000,
                30000000,
                34000000,
                40000000,
                45000000,
                52000000,
                60000000,
                68000000,
                75000000,
                83000000,
                90000000,
                110000000,
                120000000,
                140000000,
                150000000,
                200000000,
            ),
            '20': (
                1000,  # If ovr == 0
                1000,  # If ovr == 1
                1000,  # If ovr == 2
                1000,  # If ovr == 3
                1000,  # If ovr == 4
                1000,  # If ovr == 5
                15000,  # If ovr == 6
                15000,  # If ovr == 7
                15000,  # If ovr == 8
                15000,  # If ovr == 9
                15000,  # If ovr == 10
                15000,  # If ovr == 11
                15000,  # If ovr == 12
                15000,  # If ovr == 13
                15000,  # If ovr == 14
                15000,  # If ovr == 15
                15000,  # If ovr == 16
                15000,  # If ovr == 17
                15000,  # If ovr == 18
                15000,  # If ovr == 19
                15000,  # If ovr == 20
                15000,  # If ovr == 21
                15000,  # If ovr == 22
                15000,  # If ovr == 23
                15000,  # If ovr == 24
                15000,  # If ovr == 25
                15000,  # If ovr == 26
                15000,  # If ovr == 27
                15000,  # If ovr == 28
                15000,  # If ovr == 29
                15000,  # If ovr == 30
                15000,  # If ovr == 31
                15000,  # If ovr == 32
                15000,  # If ovr == 33
                15000,  # If ovr == 34
                15000,  # If ovr == 35
                15000,  # If ovr == 36
                15000,  # If ovr == 37
                15000,  # If ovr == 38
                15000,  # If ovr == 39
                15000,  # If ovr == 40
                20000,  # If ovr == 41
                20000,  # If ovr == 42
                20000,  # If ovr == 43
                20000,  # If ovr == 44
                20000,  # If ovr == 45
                20000,  # If ovr == 46
                20000,  # If ovr == 47
                20000,  # If ovr == 48
                20000,  # If ovr == 49
                20000,  # If ovr == 50
                25000,  # If ovr == 51
                34000,  # If ovr == 52
                40000,  # If ovr == 53
                46000,  # If ovr == 54
                54000,  # If ovr == 55
                61000,  # If ovr == 56
                70000,  # If ovr == 57
                86000,  # If ovr == 58
                105000,  # If ovr == 59
                140000,  # If ovr == 60
                170000,  # If ovr == 61
                205000,  # If ovr == 62
                250000,  # If ovr == 63
                305000,  # If ovr == 64
                365000,  # If ovr == 65
                435000,  # If ovr == 66
                515000,  # If ovr == 67
                605000,  # If ovr == 68
                710000,  # If ovr == 69
                1200000,  # If ovr == 70
                1600000,  # If ovr == 71
                2100000,  # If ovr == 72
                2700000,  # If ovr == 73
                3800000,  # If ovr == 74
                4500000,  # If ovr == 75
                5200000,  # If ovr == 76
                6000000,  # If ovr == 77
                7000000,  # If ovr == 78
                8500000,  # If ovr == 79
                10000000,  # If ovr == 80
                12000000,  # If ovr == 81
                15000000,  # If ovr == 82
                17500000,  # If ovr == 83
                21000000,  # If ovr == 84
                26000000,  # If ovr == 85
                30000000,  # If ovr == 86
                34000000,  # If ovr == 87
                40000000,  # If ovr == 88
                45000000,  # If ovr == 89
                52000000,  # If ovr == 90
                60000000,  # If ovr == 91
                68000000,  # If ovr == 92
                75000000,  # If ovr == 93
                83000000,  # If ovr == 94
                90000000,  # If ovr == 95
                110000000,  # If ovr == 96
                120000000,  # If ovr == 97
                140000000,  # If ovr == 98
                150000000,  # If ovr == 99
            )
        }

        try:
            return factors[self.fifa_edition][ovr]
        except IndexError:
            return factors[self.fifa_edition][-1]

    def _position_factor(self, posid):
        # playervalues.ini -> [POSITION]
        factors = {
            '17': (
                -15,
                -18,
                -18,
                -18,
                -15,
                -15,
                -15,
                -18,
                -18,
                -15,
                -15,
                -15,
                10,
                10,
                10,
                10,
                10,
                15,
                15,
                15,
                18,
                15,
                15,
                15,
                18,
                18,
            ),
            '18': (
                -40,
                -15,
                -18,
                -18,
                -15,
                -15,
                -15,
                -18,
                -18,
                -15,
                -15,
                -15,
                15,
                12,
                12,
                12,
                15,
                15,
                15,
                15,
                18,
                18,
                15,
                15,
                18,
                18,
            ),
            '19': (
                -40,
                -15,
                -18,
                -18,
                -15,
                -15,
                -15,
                -18,
                -18,
                -15,
                -15,
                -15,
                15,
                12,
                12,
                12,
                15,
                15,
                15,
                15,
                18,
                18,
                15,
                15,
                18,
                18,
            ),
            '20': (
                -35,  # If position == GK
                0,  # If position == SW
                -8,  # If position == RWB
                -8,  # If position == RB
                -5,  # If position == RCB
                -5,  # If position == CB
                -5,  # If position == LCB
                -8,  # If position == LB
                -8,  # If position == LWB
                -3,  # If position == RDM
                -3,  # If position == CDM
                -3,  # If position == LDM
                15,  # If position == RM
                12,  # If position == RCM
                12,  # If position == CM
                12,  # If position == LCM
                15,  # If position == LM
                15,  # If position == RAM
                15,  # If position == CAM
                15,  # If position == LAM
                0,  # If position == RF
                18,  # If position == CF
                0,  # If position == LF
                15,  # If position == RW
                18,  # If position == RS
                18,  # If position == ST
                18,  # If position == LS
                15,  # If position == LW
                0,  # If position == SUB
                0,  # If position == RES

            )
        }

        try:
            return (factors[self.fifa_edition][posid])
        except IndexError:
            return (factors[self.fifa_edition][0])

    def _pot_factor(self, remaining_potential):
        # playervalues.ini -> [POTENTIAL]
        # The remaining potential for the player ( Overall Potential - current Overall )
        if remaining_potential <= 0:
            return 0

        factors = {
            '17': (
                0,
                15,
                20,
                25,
                30,
                35,
                40,
                45,
                55,
                65,
                75,
                90,
                100,
                120,
                160,
                160,
                160,
                160,
                160,
                160,
                160,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
            ),
            '18': (
                0,
                15,
                20,
                25,
                30,
                35,
                40,
                45,
                55,
                65,
                75,
                90,
                100,
                120,
                160,
                160,
                160,
                160,
                160,
                160,
                160,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
            ),
            '19': (
                0,
                15,
                20,
                25,
                30,
                35,
                40,
                45,
                55,
                65,
                75,
                90,
                100,
                120,
                160,
                160,
                160,
                160,
                160,
                160,
                160,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                190,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
                235,
            ),
            '20': (
                0,  # If pot-ovr == 0
                15,  # If pot-ovr == 1
                20,  # If pot-ovr == 2
                25,  # If pot-ovr == 3
                30,  # If pot-ovr == 4
                35,  # If pot-ovr == 5
                40,  # If pot-ovr == 6
                45,  # If pot-ovr == 7
                55,  # If pot-ovr == 8
                65,  # If pot-ovr == 9
                75,  # If pot-ovr == 10
                90,  # If pot-ovr == 11
                100,  # If pot-ovr == 12
                120,  # If pot-ovr == 13
                160,  # If pot-ovr == 14
                160,  # If pot-ovr == 15
                160,  # If pot-ovr == 16
                160,  # If pot-ovr == 17
                160,  # If pot-ovr == 18
                160,  # If pot-ovr == 19
                160,  # If pot-ovr == 20
                190,  # If pot-ovr == 21
                190,  # If pot-ovr == 22
                190,  # If pot-ovr == 23
                190,  # If pot-ovr == 24
                190,  # If pot-ovr == 25
                190,  # If pot-ovr == 26
                190,  # If pot-ovr == 27
                190,  # If pot-ovr == 28
                190,  # If pot-ovr == 29
                190,  # If pot-ovr == 30
                235,  # If pot-ovr == 31
                235,  # If pot-ovr == 32
                235,  # If pot-ovr == 33
                235,  # If pot-ovr == 34
                235,  # If pot-ovr == 35
                235,  # If pot-ovr == 36
                235,  # If pot-ovr == 37
                235,  # If pot-ovr == 38
                235,  # If pot-ovr == 39
                235,  # If pot-ovr == 40
                235,  # If pot-ovr == 41
                235,  # If pot-ovr == 42
                235,  # If pot-ovr == 43
                235,  # If pot-ovr == 44
                235,  # If pot-ovr == 45
                235,  # If pot-ovr == 46
                235,  # If pot-ovr == 47
                235,  # If pot-ovr == 48
                235,  # If pot-ovr == 49
                235,  # If pot-ovr == 50
                235,  # If pot-ovr == 51
                235,  # If pot-ovr == 52
                235,  # If pot-ovr == 53
                235,  # If pot-ovr == 54
                235,  # If pot-ovr == 55
                235,  # If pot-ovr == 56
                235,  # If pot-ovr == 57
                235,  # If pot-ovr == 58
                235,  # If pot-ovr == 59
                235,  # If pot-ovr == 60
                235,  # If pot-ovr == 61
                235,  # If pot-ovr == 62
                235,  # If pot-ovr == 63
                235,  # If pot-ovr == 64
                235,  # If pot-ovr == 65
                235,  # If pot-ovr == 66
                235,  # If pot-ovr == 67
                235,  # If pot-ovr == 68
                235,  # If pot-ovr == 69
                235,  # If pot-ovr == 70
                235,  # If pot-ovr == 71
                235,  # If pot-ovr == 72
                235,  # If pot-ovr == 73
                235,  # If pot-ovr == 74
                235,  # If pot-ovr == 75
                235,  # If pot-ovr == 76
                235,  # If pot-ovr == 77
                235,  # If pot-ovr == 78
                235,  # If pot-ovr == 79
                235,  # If pot-ovr == 80
                235,  # If pot-ovr == 81
                235,  # If pot-ovr == 82
                235,  # If pot-ovr == 83
                235,  # If pot-ovr == 84
                235,  # If pot-ovr == 85
                235,  # If pot-ovr == 86
                235,  # If pot-ovr == 87
                235,  # If pot-ovr == 88
                235,  # If pot-ovr == 89
                235,  # If pot-ovr == 90
                235,  # If pot-ovr == 91
                235,  # If pot-ovr == 92
                235,  # If pot-ovr == 93
                235,  # If pot-ovr == 94
                235,  # If pot-ovr == 95
                235,  # If pot-ovr == 96
                235,  # If pot-ovr == 97
                235,  # If pot-ovr == 98
                235,  # If pot-ovr == 99
            )
        }

        if remaining_potential > len(factors[self.fifa_edition]):
            return (factors[self.fifa_edition][-1])

        try:
            return (factors[self.fifa_edition][remaining_potential])
        except IndexError:
            return (factors[self.fifa_edition][-1])

    def _age_factor(self, age, posid):
        # playervalues.ini -> [AGE]
        factors = {
            '17': (
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                5,
                10,
                25,
                48,
                48,
                48,
                48,
                48,
                42,
                40,
                35,
                30,
                25,
                20,
                10,
                0,
                -20,
                -40,
                -60,
                -98,
                -100,
                -100,
                -100,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
            ),
            '18': (
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                30,
                42,
                50,
                48,
                48,
                48,
                48,
                46,
                44,
                40,
                35,
                30,
                25,
                15,
                0,
                -25,
                -40,
                -50,
                -65,
                -75,
                -75,
                -75,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
            ),
            '19': (
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                18,
                30,
                42,
                50,
                48,
                48,
                48,
                48,
                46,
                44,
                40,
                35,
                30,
                25,
                15,
                0,
                -25,
                -40,
                -50,
                -65,
                -75,
                -75,
                -75,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
                -1000,
            ),
            '20': (
                18,  # If age == 0
                18,  # If age == 1
                18,  # If age == 2
                18,  # If age == 3
                18,  # If age == 4
                18,  # If age == 5
                18,  # If age == 6
                18,  # If age == 7
                18,  # If age == 8
                18,  # If age == 9
                18,  # If age == 10
                18,  # If age == 11
                18,  # If age == 12
                18,  # If age == 13
                18,  # If age == 14
                18,  # If age == 15
                18,  # If age == 16
                18,  # If age == 17
                30,  # If age == 18
                42,  # If age == 19
                50,  # If age == 20
                48,  # If age == 21
                48,  # If age == 22
                48,  # If age == 23
                48,  # If age == 24
                46,  # If age == 25
                44,  # If age == 26
                40,  # If age == 27
                35,  # If age == 28
                30,  # If age == 29
                25,  # If age == 30
                15,  # If age == 31
                0,  # If age == 32
                -25,  # If age == 33
                -40,  # If age == 34
                -50,  # If age == 35
                -65,  # If age == 36
                -75,  # If age == 37
                -75,  # If age == 38
                -75,  # If age == 39
                -1000,  # If age == 40
                -1000,  # If age == 41
                -1000,  # If age == 42
                -1000,  # If age == 43
                -1000,  # If age == 44
                -1000,  # If age == 45
                -1000,  # If age == 46
                -1000,  # If age == 47
                -1000,  # If age == 48
                -1000,  # If age == 49
                -1000,  # If age == 50
                -1000,  # If age == 51
                -1000,  # If age == 52
                -1000,  # If age == 53
                -1000,  # If age == 54
                -1000,  # If age == 55
                -1000,  # If age == 56
                -1000,  # If age == 57
                -1000,  # If age == 58
                -1000,  # If age == 59
                -1000,  # If age == 60
                -1000,  # If age == 61
                -1000,  # If age == 62
                -1000,  # If age == 63
                -1000,  # If age == 64
                -1000,  # If age == 65
                -1000,  # If age == 66
                -1000,  # If age == 67
                -1000,  # If age == 68
                -1000,  # If age == 69
                -1000,  # If age == 70
                -1000,  # If age == 71
                -1000,  # If age == 72
                -1000,  # If age == 73
                -1000,  # If age == 74
                -1000,  # If age == 75
                -1000,  # If age == 76
                -1000,  # If age == 77
                -1000,  # If age == 78
                -1000,  # If age == 79
                -1000,  # If age == 80
                -1000,  # If age == 81
                -1000,  # If age == 82
                -1000,  # If age == 83
                -1000,  # If age == 84
                -1000,  # If age == 85
                -1000,  # If age == 86
                -1000,  # If age == 87
                -1000,  # If age == 88
                -1000,  # If age == 89
                -1000,  # If age == 90
                -1000,  # If age == 91
                -1000,  # If age == 92
                -1000,  # If age == 93
                -1000,  # If age == 94
                -1000,  # If age == 95
                -1000,  # If age == 96
                -1000,  # If age == 97
                -1000,  # If age == 98
                -1000,  # If age == 99
            )
        }
        gk_age_mod = {
            '17': {
                'GK_AGE_MOD': -3,
                'GK_MIN_AGE_MOD': 28,
            },
            '18': {
                'GK_AGE_MOD': -2,
                'GK_MIN_AGE_MOD': 28,
            },
            '19': {
                'GK_AGE_MOD': -2,
                'GK_MIN_AGE_MOD': 28,
            },
            '20': {
                'GK_AGE_MOD': -2,
                'GK_MIN_AGE_MOD': 28,
            },
        }

        if age > len(factors[self.fifa_edition]):
            return (factors[self.fifa_edition][-1] / 100)

        # For GK
        if posid == 0 and age >= gk_age_mod[self.fifa_edition]['GK_MIN_AGE_MOD']:
            if age >= 40:
                age = 36
            elif age in range(37, 40):
                age = 35
            else:
                age += gk_age_mod[self.fifa_edition]['GK_AGE_MOD']

        try:
            return (factors[self.fifa_edition][age])
        except IndexError:
            return (factors[self.fifa_edition][-1])

    def _sum_factors(self, basevalue, *args):
        summed_value = basevalue
        for a in args:
            summed_value += a

        if TEST_DEBUG:
            print("Before rounding: {}".format(summed_value))
        return int(self._round_to_player_value(summed_value))


class PlayerName():
    def __init__(self, player, dict_cached_queries, fifa_edition=DEFAULT_FIFA_EDITION):
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
        if self.fifa_edition == 17:
            dcplayernames_start_index = 30000
        else:
            dcplayernames_start_index = 34000

        name = {
            'firstname': int(self.player.firstname_id or 0),
            'lastname': int(self.player.lastname_id or 0),
            'commonname': int(self.player.commonname_id or 0),
            'playerjerseyname': int(self.player.playerjerseyname_id or 0),
        }

        playername_set = False
        if self.edited_player_names is not None:
            for i in range(len(self.edited_player_names)):
                if self.edited_player_names[i].playerid == self.player.playerid:
                    validated_firstname = self.edited_player_names[i].firstname
                    # Ugly validation
                    if (
                        validated_firstname is None or
                        len(validated_firstname) <= 1 or
                        not validated_firstname[0].isalnum() or
                        not validated_firstname[0].isupper()
                    ):
                        break
                    name['firstname'] = validated_firstname
                    name['lastname'] = self.edited_player_names[i].surname
                    name['commonname'] = self.edited_player_names[i].commonname
                    name['playerjerseyname'] = self.edited_player_names[i].playerjerseyname
                    playername_set = True
                    break
        
        if not playername_set:
            if self.dc_player_names is not None:
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
            name['knownas'] = " ".join(
                (str(name['firstname']), str(name['lastname'])))

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

        self.fifa_edition = str(fifa_edition)

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
            self.currency = 1  # Set Euro as default currency

        self.player_teams = self.set_teams()

        # q_dcplayernames & q_edited_player_names
        self.player_name = PlayerName(
            self.player, self.dict_cached_queries, self.fifa_edition).playername

        # Player Age
        self.player_age = PlayerAge(self.player.birthdate, current_date)

        # Player Value
        if self.currency == 0:
            # USD
            self.player_value = PlayerValue(
                self.player.overallrating, self.player.potential, self.player_age.age, self.player.preferredposition1,
                self.currency, self.player.value_usd, fifa_edition=self.fifa_edition,
            )
        elif self.currency == 2:
            # GBP
            self.player_value = PlayerValue(
                self.player.overallrating, self.player.potential, self.player_age.age, self.player.preferredposition1,
                self.currency, self.player.value_gbp, fifa_edition=self.fifa_edition
            )
        else:
            # EURO by default
            self.player_value = PlayerValue(
                self.player.overallrating, self.player.potential, self.player_age.age, self.player.preferredposition1,
                self.currency, self.player.value_eur, fifa_edition=self.fifa_edition
            )

        # Player Wage (slow)
        try:
            self.player_wage = PlayerWage(
                self.player.overallrating, self.player_age.age, self.player.preferredposition1,
                self.player_teams['club_team'], int(self.currency), self.fifa_edition,
            )
        except KeyError:
            # print('KeyError: {}'.format(e))
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
            "total": {
                "avg": 0,
                "app": 0,
                "goals": 0,
                "assists": 0,
                "yellowcards": 0,
                "redcards": 0,
                "cleansheets": 0,
            }
        }
        num_of_comps = 0
        for i in range(len(self.players_stats)):
            if self.players_stats[i].playerid == self.player.playerid:
                num_of_comps += 1
                # Avg. Rating
                stats["total"]["avg"] += self.players_stats[i].avg
                # Appearances
                stats["total"]["app"] += self.players_stats[i].app
                stats["total"]["goals"] += self.players_stats[i].goals
                stats["total"]["assists"] += self.players_stats[i].assists
                stats["total"]["yellowcards"] += self.players_stats[i].yellowcards
                stats["total"]["redcards"] += self.players_stats[i].redcards
                stats["total"]["cleansheets"] += self.players_stats[i].cleansheets

        if num_of_comps > 0:
            if num_of_comps >= 2:
                try:
                    stats["total"]["avg"] = int(
                        stats["total"]["avg"] / num_of_comps)
                except ZeroDivisionError:
                    pass

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
            'Tan',
            'Dark Red',
            'Blue',
        )

        try:
            return haircolors[int(self.player.haircolorcode)]
        except Exception:
            return "{}. Unknown".format(self.player.haircolorcode)

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
            return "{}. Unknown".format(self.player.bodytypecode)

    def get_boots_name(self):
        try:
            return BOOTS[self.fifa_edition][int(self.player.shoetypecode)]
        except Exception:
            return "{}. Unknown".format(self.player.shoetypecode)

    def set_traits(self):
        all_traits = list()
        trait1 = int(self.player.trait1)
        trait2 = int(self.player.trait2)

        if trait1 > 0:
            trait1_names = TRAITS[self.fifa_edition]['trait1']

            trait1_binary = bin(trait1)[2:]
            i = 0
            for t in reversed(trait1_binary):
                if t == '1':
                    all_traits.append(trait1_names[i])
                i += 1

        if trait2 > 0:
            trait2_names = TRAITS[self.fifa_edition]['trait2']

            trait2_binary = bin(trait2)[2:]
            i = 0
            for t in reversed(trait2_binary):
                if t == '1':
                    all_traits.append(trait2_names[i])
                i += 1

        # remove ',' from the end of string
        # if len(all_traits) >= 1: return all_traits[:-1]

        return all_traits

    def get_release_clause(self):
        if self.fifa_edition == '17':
            # Release clauses has been added to the game in FIFA 18
            return 0

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
            if self.fifa_edition == '20':
                return "youthheads/p{skintonecode}{headtypecode:04d}{haircolorcode:02d}.png".format(
                    skintonecode=self.player.skintonecode,
                    headtypecode=self.player.headtypecode,
                    haircolorcode=self.player.haircolorcode,
                )
            else:
                if self.player.headtypecode == 0:
                    return "youthheads/p{haircolorcode}.png".format(
                        haircolorcode=self.player.haircolorcode
                    )
                else:
                    return "youthheads/p{headtypecode}{haircolorcode:02d}.png".format(
                        headtypecode=self.player.headtypecode, haircolorcode=self.player.haircolorcode
                    )

    def update_positions(self):
        available_positions = ('GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM',
                               'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW', 'SUB', 'RES')
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

        contract['jointeamdate'] = FifaDate().convert_days_to_py_date(
            days=self.player.playerjointeamdate)
        contract['enddate'] = FifaDate().convert_to_py_date(
            fifa_date=self.player.contractvaliduntil)

        contract['isloanedout'] = 0
        if self.query_player_loans is None:
            return contract

        for i in range(len(self.query_player_loans)):
            if self.query_player_loans[i].playerid == self.player.playerid:
                for j in range(len(self.q_teams)):
                    if int(self.query_player_loans[i].teamidloanedfrom) == int(self.q_teams[j].teamid):
                        end_date = FifaDate().convert_days_to_py_date(
                            days=self.query_player_loans[i].loandateend
                        )

                        # Validate player loan
                        if end_date >= self.current_date_py:
                            contract['isloanedout'] = 1
                            contract['loan'] = vars(self.query_player_loans[i])
                            contract['enddate'] = end_date
                            contract['loanedto_clubid'] = self.player_teams['club_team']['team']['teamid']
                            contract['loanedto_clubname'] = self.player_teams['club_team']['team']['teamname']
                            self.player_teams['club_team']['team'] = vars(
                                self.q_teams[j])
                            return contract

        return contract

    def set_teams(self):
        teams = {}
        max_teams = 2

        for i in range(len(self.team_player_links)):
            if int(self.team_player_links[i].playerid) == int(self.player.playerid):
                for j in range(len(self.q_teams)):
                    if int(self.q_teams[j].teamid) == int(self.team_player_links[i].teamid):
                        league = self.get_league(self.q_teams[j].teamid)
                        if league:
                            if league[1].leagueid == 76 and self.q_teams[j].teamid in UNUSED_TEAMS:
                                # Ignore MLS ALL STARS and ADIDAS (if not managed by user)
                                pass
                            elif league[1].leagueid == 78 or league[1].leagueid == 2136:
                                # Men's National or Women's National
                                teams['national_team'] = {
                                    'team': vars(self.q_teams[j]),
                                    'team_links': vars(self.team_player_links[i]),
                                    'league': vars(league[0]),
                                    'league_links': vars(league[1]),
                                }
                            else:
                                # Club
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


if __name__ == '__main__':
    available_positions = (
        'GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM',
        'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS',
        'LW', 'SUB', 'RES'
    )

    positions = dict()
    for x,y in enumerate(available_positions):
        positions[y] = x

    # PV = PlayerValue(
    #     ovr=89,
    #     pot=89,
    #     age=35,
    #     posid=positions['CB'],
    # )
    # print("Value 0")
    # print(PV._calculate_player_value())

    PW = PlayerWage(
        ovr=49,
        age=40,
        posid=positions['LB'],
        player_team={
            'league': {
                'leagueid': 2012,
            },
            'team': {
                'domesticprestige': 2,
                'profitability': 1,
            }
        }
    )
    print("Wage")
    print(PW._calculate_player_wage())
