from datetime import date  
from datetime import timedelta  

class PlayerAge:
    def __init__(self, birthdatedays, currdate=date(2020, 7, 16)):
        self.birthdate = date(1582, 10, 14) + timedelta(days=birthdatedays)
        self.currdate = currdate

    def getAge(self):
        return self.currdate.year - self.birthdate.year - ((self.currdate.month, self.currdate.day) < (self.birthdate.month, self.birthdate.day))