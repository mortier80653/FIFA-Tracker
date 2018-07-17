from datetime import date, timedelta
from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from players.models import (
    DataUsersPlayers,
    DataUsersTeamplayerlinks,
    DataUsersTeams,
    DataUsersLeagueteamlinks,
    DataUsersLeagues,
    DataNations,
    DataPlayernames,
    DataUsersCareerRestReleaseClauses,
    DataUsersCareerCompdataPlayerStats,
)

from core.fifa_utils import FifaPlayer, FifaDate, PlayerAge, PlayerWage, PlayerValue, PlayerName
from core.views import home, privacypolicy, about, contact, donate, upload_career_save_file

# fifa_utils tests.
class PlayerValueTests(TestCase):
    def test_player_value(self):
        test_player1 = {
            "ovr": 94,
            "pot": 94,
            "age": 32,
            "posid": 27,    # LW
            "currency": 0,  # USD
        }

        test_player2 = {
            "ovr": 46,
            "pot": 81,
            "age": 16,
            "posid": 0,     # GK
            "currency": 0,  # USD
        }

        test_player3 = {
            "ovr": 58,
            "pot": 58,
            "age": 37,
            "posid": 5,     # CB
            "currency": 0,  # USD
        }

        test_player4 = {
            "ovr": 46,
            "pot": 46,
            "age": 48,
            "posid": 0,     # GK
            "currency": 0,  # USD
        }

        # test_player1
        test_playervalue = PlayerValue(ovr=test_player1["ovr"], pot=test_player1["pot"], age=test_player1["age"], posid=test_player1["posid"], currency=test_player1["currency"]).value
        self.assertEquals(test_playervalue, 107000000)

        # test_player2
        test_playervalue = PlayerValue(ovr=test_player2["ovr"], pot=test_player2["pot"], age=test_player2["age"], posid=test_player2["posid"], currency=test_player2["currency"]).value
        self.assertEquals(test_playervalue, 70000)

        # test_player3
        test_playervalue = PlayerValue(ovr=test_player3["ovr"], pot=test_player3["pot"], age=test_player3["age"], posid=test_player3["posid"], currency=test_player3["currency"]).value
        self.assertEquals(test_playervalue, 10000)

        # test_player4
        test_playervalue = PlayerValue(ovr=test_player4["ovr"], pot=test_player4["pot"], age=test_player4["age"], posid=test_player4["posid"], currency=test_player4["currency"]).value
        self.assertEquals(test_playervalue, 0)


class FifaPlayerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create User
        test_user1 = User.objects.create_user(
            username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(
            username='testuser2', password='12345')
        test_user2.save()

        # Create Nation
        brazil = DataNations.objects.create(
            nationid=54,
            nationname="Brazil",
        )

        # Create playernames
        firstname = DataPlayernames.objects.create(
            nameid=16653,
            name="Malcom Filipe",
        )

        commonname = DataPlayernames.objects.create(
            nameid=16652,
            name="Malcom",
        )

        lastname = DataPlayernames.objects.create(
            nameid=24479,
            name="Silva de Oliveira",
        )

        # Create player

        # Malcom
        player = DataUsersPlayers.objects.create(
            username="testuser1",
            ft_user=test_user1,
            playerid=222737,
            firstname=firstname,
            lastname=lastname,
            commonname=commonname,
            playerjerseyname=commonname,
            birthdate=151346,               # 1997-02-26
            nationality=brazil,             # Brazil
            height=171,
            weight=75,
            playerjointeamdate=160289,      # 2021-08-22
            contractvaliduntil=2023,
            preferredposition1=23,          # RW
            preferredposition2=12,          # RM
            preferredposition3=-1,          # None
            preferredposition4=-1,          # None
            internationalrep=2,
            overallrating=88,
            potential=88,
            trait1=0,
            trait2=0,
            value_usd=65000000,
            value_eur=58000000,
            value_gbp=51000000,
        )

        player.save()

        # Team-Player Links
        team_player_links = DataUsersTeamplayerlinks.objects.create(
            username="testuser1",
            ft_user=test_user1,
            playerid=222737,
            teamid=5,
        )

        team_player_links.save()

        # Team
        team = DataUsersTeams.objects.create(
            username="testuser1",
            ft_user=test_user1,
            teamid=5,
            teamname="Chelsea",
            profitability=2,
            domesticprestige=10,
            internationalprestige=10,
        )
        team.save()

        # League
        league = DataUsersLeagues.objects.create(
            username="testuser1",
            ft_user=test_user1,
            leaguename="England Premier League (1)",
            leagueid=13,
        )
        league.save()

        # Team-League Links
        league_team_links = DataUsersLeagueteamlinks.objects.create(
            username="testuser1",
            ft_user=test_user1,
            teamid=5,           # Chelsea
            leagueid=13,        # England Premier League (1)
        )
        league_team_links.save()

        # stats
        player_stats = DataUsersCareerCompdataPlayerStats.objects.create(
            username="testuser1",
            ft_user=test_user1,
            teamid = 5, # Chelsea
            playerid = 222737, # Malcom
            tournamentid = 0, #Unk
            unk1 = 0,
            avg = 100,
            app = 1,
            goals = 5,
            unk2 = 0,
            assists = 3,
            unk3 = 0,
            yellowcards = 7,
            redcards = 2,
            unk6 = 0,
            unk7 = 0,
            cleansheets = 2,
            unk9 = 0,
            unk10 = 0,
            unk11 = 0,
            unk12 = 0,
            unk13 = 0,
            date1 = 20170701,
            date2 = 20170701,
            date3 = 20170701,
        )
        player_stats.save()

    def test_player_team(self):
        # TEST Malcom
        player = DataUsersPlayers.objects.for_user(
            "testuser1").filter(playerid=222737).first()

        qdata_dict = dict()
        qdata_dict['q_team_player_links'] = list(
            DataUsersTeamplayerlinks.objects.for_user("testuser1").iterator())
        qdata_dict['q_teams'] = list(
            DataUsersTeams.objects.for_user("testuser1").iterator())
        qdata_dict['q_league_team_links'] = list(
            DataUsersLeagueteamlinks.objects.for_user("testuser1").iterator())
        #qdata_dict['q_player_loans'] = list(DataUsersTeams.objects.for_user("testuser1").iterator())
        qdata_dict['q_leagues'] = list(
            DataUsersLeagues.objects.for_user("testuser1").iterator())
        qdata_dict['q_release_clauses'] = list(
            DataUsersCareerRestReleaseClauses.objects.for_user("testuser1").iterator())
        qdata_dict['q_players_stats'] = list(
            DataUsersCareerCompdataPlayerStats.objects.for_user("testuser1").iterator())

        testplayer1 = FifaPlayer(player, username="testuser1", current_date="20260419",
                                 dict_cached_queries=qdata_dict, currency=1, fifa_edition=18)
        testteam = testplayer1.player_teams['club_team']['team']
        self.assertEquals(testteam['teamname'], "Chelsea")
        self.assertEquals(testteam['teamid'], 5)
        self.assertEquals(testteam['domesticprestige'], 10)
        self.assertEquals(testteam['internationalprestige'], 10)

    def test_player_age(self):
        player = DataUsersPlayers.objects.for_user(
            "testuser1").filter(playerid=222737).first()

        qdata_dict = dict()
        qdata_dict['q_team_player_links'] = list(
            DataUsersTeamplayerlinks.objects.for_user("testuser1").iterator())
        qdata_dict['q_teams'] = list(
            DataUsersTeams.objects.for_user("testuser1").iterator())
        qdata_dict['q_league_team_links'] = list(
            DataUsersLeagueteamlinks.objects.for_user("testuser1").iterator())
        #qdata_dict['q_player_loans'] = list(DataUsersTeams.objects.for_user("testuser1").iterator())
        qdata_dict['q_leagues'] = list(
            DataUsersLeagues.objects.for_user("testuser1").iterator())
        qdata_dict['q_release_clauses'] = list(
            DataUsersCareerRestReleaseClauses.objects.for_user("testuser1").iterator())
        qdata_dict['q_players_stats'] = list(
            DataUsersCareerCompdataPlayerStats.objects.for_user("testuser1").iterator())

        testplayer_age = FifaPlayer(player, username="testuser1", current_date="20260419",
                                    dict_cached_queries=qdata_dict, currency=1, fifa_edition=18).player_age.age
        self.assertEquals(testplayer_age, 29)

    def test_player_value(self):
        # TEST Malcom
        player = DataUsersPlayers.objects.for_user(
            "testuser1").filter(playerid=222737).first()

        qdata_dict = dict()
        qdata_dict['q_team_player_links'] = list(
            DataUsersTeamplayerlinks.objects.for_user("testuser1").iterator())
        qdata_dict['q_teams'] = list(
            DataUsersTeams.objects.for_user("testuser1").iterator())
        qdata_dict['q_league_team_links'] = list(
            DataUsersLeagueteamlinks.objects.for_user("testuser1").iterator())
        #qdata_dict['q_player_loans'] = list(DataUsersTeams.objects.for_user("testuser1").iterator())
        qdata_dict['q_leagues'] = list(
            DataUsersLeagues.objects.for_user("testuser1").iterator())
        qdata_dict['q_release_clauses'] = list(
            DataUsersCareerRestReleaseClauses.objects.for_user("testuser1").iterator())
        qdata_dict['q_players_stats'] = list(
            DataUsersCareerCompdataPlayerStats.objects.for_user("testuser1").iterator())

        testplayer_value_usd = FifaPlayer(player, username="testuser1", current_date="20260419",
                                          dict_cached_queries=qdata_dict, currency=0, fifa_edition=18).player_value.value
        self.assertEquals(testplayer_value_usd, 65000000)

        testplayer_value_euro = FifaPlayer(player, username="testuser1", current_date="20260419",
                                           dict_cached_queries=qdata_dict, currency=1, fifa_edition=18).player_value.value
        self.assertEquals(testplayer_value_euro, 58000000)

        testplayer_value_gbp = FifaPlayer(player, username="testuser1", current_date="20260419",
                                          dict_cached_queries=qdata_dict, currency=2, fifa_edition=18).player_value.value
        self.assertEquals(testplayer_value_gbp, 51000000)

# Views tests.


class HomePageTests(TestCase):
    def test_homepage_view_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_homepage_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func, home)


class PrivacyPolicyTests(TestCase):
    def test_privaypolicy_view_status_code(self):
        url = reverse('privacypolicy')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_privaypolicy_url_resolves_home_view(self):
        view = resolve('/privacy-policy/')
        self.assertEquals(view.func, privacypolicy)


class AboutTests(TestCase):
    def test_about_view_status_code(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_about_url_resolves_home_view(self):
        view = resolve('/about/')
        self.assertEquals(view.func, about)


class ContactTests(TestCase):
    def test_contact_view_status_code(self):
        url = reverse('contact')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_contact_url_resolves_home_view(self):
        view = resolve('/contact/')
        self.assertEquals(view.func, contact)


class DonateTests(TestCase):
    def test_donate_view_status_code(self):
        url = reverse('donate')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_donate_url_resolves_home_view(self):
        view = resolve('/donate/')
        self.assertEquals(view.func, donate)


class UploadCareerSaveFileTests(TestCase):
    def setUp(self):
        # Create User
        test_user1 = User.objects.create_user(
            username='testuser1', password='12345')
        test_user1.save()

    def test_upload_career_save_file_not_authenticated_view_status_code(self):
        url = reverse('upload_career_save_file')
        response = self.client.get(url)
        # should redirect to home page
        self.assertEquals(response.status_code, 302)
        self.assertTrue(response.url == '/')

    def test_upload_career_save_file_authenticated_view_status_code(self):
        login = self.client.login(username='testuser1', password='12345')

        url = reverse('upload_career_save_file')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_upload_career_save_file_url_resolves_home_view(self):
        view = resolve('/upload/')
        self.assertEquals(view.func, upload_career_save_file)
