from django.test import TestCase
from django.contrib.auth.models import User
from players.models import DataUsersCareerCalendar
from core.fifa_utils import FifaDate

from datetime import date, timedelta  

# Create your tests here.

class DataUsersCareerCalendarTestCase(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        DataUsersCareerCalendar.objects.create(username="testuser1", ft_user=test_user1, currdate="20230918")
        DataUsersCareerCalendar.objects.create(username="testuser2", ft_user=test_user2, currdate="20170701")

    def test_calendar_currdate(self):
        test_user1 = DataUsersCareerCalendar.objects.get(username="testuser1")
        test_user2 = DataUsersCareerCalendar.objects.get(username="testuser2")

        test_user1_Date = FifaDate().convert_to_py_date(fifa_date=test_user1.currdate)
        test_user2_Date = FifaDate().convert_to_py_date(fifa_date=test_user2.currdate)

        self.assertEquals(test_user1_Date, date(2023, 9, 18))
        self.assertEquals(test_user2_Date, date(2017, 7, 1))

