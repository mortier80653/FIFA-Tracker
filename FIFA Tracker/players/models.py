from django.db import models

class UserDataQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(username=user)

class UserDataManager(models.Manager):
    def get_queryset(self):
        return UserDataQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)

class DataUsersCareerCalendar(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    transferwindowend1 = models.IntegerField(blank=True, null=True)
    transferwindowstart1 = models.IntegerField(blank=True, null=True)
    transferwindowend2 = models.IntegerField(blank=True, null=True)
    setupdate = models.IntegerField(blank=True, null=True)
    dateid = models.IntegerField(blank=True, null=True)
    enddate = models.IntegerField(blank=True, null=True)
    currdate = models.IntegerField(blank=True, null=True)
    startdate = models.IntegerField(blank=True, null=True)
    transferwindowstart2 = models.IntegerField(blank=True, null=True)
    objectivecheckdate = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_career_calendar'

class DataUsersCareerUsers(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    firstname = models.CharField(max_length=64, blank=True, null=True)
    surname = models.CharField(max_length=64, blank=True, null=True)
    agentname = models.CharField(max_length=64, blank=True, null=True)
    nationalityid = models.IntegerField(blank=True, null=True)
    goalnews = models.IntegerField(blank=True, null=True)
    playertype = models.IntegerField(blank=True, null=True)
    nationalteamid = models.IntegerField(blank=True, null=True)
    leagueseasonmessagesent = models.IntegerField(blank=True, null=True)
    sponsorid = models.IntegerField(blank=True, null=True)
    leagueid = models.IntegerField(blank=True, null=True)
    clubteamid = models.IntegerField(blank=True, null=True)
    wage = models.IntegerField(blank=True, null=True)
    primarycompobjid = models.IntegerField(blank=True, null=True)
    seasoncount = models.IntegerField(blank=True, null=True)
    usertype = models.IntegerField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_career_users'

class DataUsersCareerPlayercontract(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    offered_wage = models.IntegerField(blank=True, null=True)
    isperformancebonusachieved = models.IntegerField(blank=True, null=True)
    salary_demand = models.IntegerField(blank=True, null=True)
    offered_bonus = models.IntegerField(blank=True, null=True)
    contract_status = models.IntegerField(blank=True, null=True)
    performancebonuscount = models.IntegerField(blank=True, null=True)
    contract_status_change_date = models.IntegerField(blank=True, null=True)
    playerrole = models.IntegerField(blank=True, null=True)
    wage = models.IntegerField(blank=True, null=True)
    performancebonusvalue = models.IntegerField(blank=True, null=True)
    performancebonustype = models.IntegerField(blank=True, null=True)
    extension_years = models.IntegerField(blank=True, null=True)
    currentrole = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    negotiation_status = models.IntegerField(blank=True, null=True)
    bonus = models.IntegerField(blank=True, null=True)
    negotiation_date = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    performancebonuscountachieved = models.IntegerField(blank=True, null=True)
    was_years_accept = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_career_playercontract'

class DataUsersCareerYouthplayers(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    playertier = models.IntegerField(blank=True, null=True)
    playertype = models.IntegerField(blank=True, null=True)
    swinglowpotential = models.IntegerField(blank=True, null=True)
    potentialvariance = models.IntegerField(blank=True, null=True)
    monthsinsquad = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_career_youthplayers'

class DataUsersTeams(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    assetid = models.IntegerField(blank=True, null=True)
    balltype = models.IntegerField(blank=True, null=True)
    teamcolor1g = models.IntegerField(blank=True, null=True)
    teamcolor1r = models.IntegerField(blank=True, null=True)
    clubworth = models.IntegerField(blank=True, null=True)
    teamcolor2b = models.IntegerField(blank=True, null=True)
    teamcolor2r = models.IntegerField(blank=True, null=True)
    foundationyear = models.IntegerField(blank=True, null=True)
    teamcolor3r = models.IntegerField(blank=True, null=True)
    teamcolor1b = models.IntegerField(blank=True, null=True)
    opponentweakthreshold = models.IntegerField(blank=True, null=True)
    latitude = models.IntegerField(blank=True, null=True)
    teamcolor3g = models.IntegerField(blank=True, null=True)
    opponentstrongthreshold = models.IntegerField(blank=True, null=True)
    teamcolor2g = models.IntegerField(blank=True, null=True)
    teamname = models.CharField(max_length=60, blank=True, null=True)
    adboardid = models.IntegerField(blank=True, null=True)
    teamcolor3b = models.IntegerField(blank=True, null=True)
    defmentality = models.IntegerField(blank=True, null=True)
    powid = models.IntegerField(blank=True, null=True)
    rightfreekicktakerid = models.IntegerField(blank=True, null=True)
    domesticprestige = models.IntegerField(blank=True, null=True)
    genericint2 = models.IntegerField(blank=True, null=True)
    jerseytype = models.IntegerField(blank=True, null=True)
    popularity = models.IntegerField(blank=True, null=True)
    teamstadiumcapacity = models.IntegerField(blank=True, null=True)
    iscompetitionscarfenabled = models.IntegerField(blank=True, null=True)
    cityid = models.IntegerField(blank=True, null=True)
    rivalteam = models.IntegerField(blank=True, null=True)
    isbannerenabled = models.IntegerField(blank=True, null=True)
    midfieldrating = models.IntegerField(blank=True, null=True)
    matchdayoverallrating = models.IntegerField(blank=True, null=True)
    matchdaymidfieldrating = models.IntegerField(blank=True, null=True)
    attackrating = models.IntegerField(blank=True, null=True)
    longitude = models.IntegerField(blank=True, null=True)
    buspassing = models.IntegerField(blank=True, null=True)
    matchdaydefenserating = models.IntegerField(blank=True, null=True)
    defenserating = models.IntegerField(blank=True, null=True)
    iscompetitionpoleflagenabled = models.IntegerField(blank=True, null=True)
    skinnyflags = models.IntegerField(blank=True, null=True)
    defteamwidth = models.IntegerField(blank=True, null=True)
    longkicktakerid = models.IntegerField(blank=True, null=True)
    bodytypeid = models.IntegerField(blank=True, null=True)
    trait1vweak = models.IntegerField(blank=True, null=True)
    busdribbling = models.IntegerField(blank=True, null=True)
    rightcornerkicktakerid = models.IntegerField(blank=True, null=True)
    suitvariationid = models.IntegerField(blank=True, null=True)
    domesticcups = models.IntegerField(blank=True, null=True)
    defaggression = models.IntegerField(blank=True, null=True)
    ethnicity = models.IntegerField(blank=True, null=True)
    leftcornerkicktakerid = models.IntegerField(blank=True, null=True)
    youthdevelopment = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    trait1vequal = models.IntegerField(blank=True, null=True)
    suittypeid = models.IntegerField(blank=True, null=True)
    numtransfersin = models.IntegerField(blank=True, null=True)
    stanchionflamethrower = models.IntegerField(blank=True, null=True)
    captainid = models.IntegerField(blank=True, null=True)
    personalityid = models.IntegerField(blank=True, null=True)
    leftfreekicktakerid = models.IntegerField(blank=True, null=True)
    leaguetitles = models.IntegerField(blank=True, null=True)
    genericbanner = models.IntegerField(blank=True, null=True)
    buspositioning = models.IntegerField(blank=True, null=True)
    ccpositioning = models.IntegerField(blank=True, null=True)
    busbuildupspeed = models.IntegerField(blank=True, null=True)
    transferbudget = models.IntegerField(blank=True, null=True)
    ccshooting = models.IntegerField(blank=True, null=True)
    overallrating = models.IntegerField(blank=True, null=True)
    ccpassing = models.IntegerField(blank=True, null=True)
    profitability = models.IntegerField(blank=True, null=True)
    utcoffset = models.IntegerField(blank=True, null=True)
    penaltytakerid = models.IntegerField(blank=True, null=True)
    freekicktakerid = models.IntegerField(blank=True, null=True)
    crowdskintonecode = models.IntegerField(blank=True, null=True)
    defdefenderline = models.IntegerField(blank=True, null=True)
    internationalprestige = models.IntegerField(blank=True, null=True)
    trainingstadium = models.IntegerField(blank=True, null=True)
    form = models.IntegerField(blank=True, null=True)
    genericint1 = models.IntegerField(blank=True, null=True)
    cccrossing = models.IntegerField(blank=True, null=True)
    trait1vstrong = models.IntegerField(blank=True, null=True)
    matchdayattackrating = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_teams'

class DataUsersLeagueteamlinks(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    homega = models.IntegerField(blank=True, null=True)
    previousyeartableposition = models.IntegerField(blank=True, null=True)
    homegf = models.IntegerField(blank=True, null=True)
    currenttableposition = models.IntegerField(blank=True, null=True)
    awaygf = models.IntegerField(blank=True, null=True)
    awayga = models.IntegerField(blank=True, null=True)
    teamshortform = models.IntegerField(blank=True, null=True)
    hasachievedobjective = models.IntegerField(blank=True, null=True)
    yettowin = models.IntegerField(blank=True, null=True)
    unbeatenallcomps = models.IntegerField(blank=True, null=True)
    unbeatenleague = models.IntegerField(blank=True, null=True)
    champion = models.IntegerField(blank=True, null=True)
    leagueid = models.IntegerField(blank=True, null=True)
    prevleagueid = models.IntegerField(blank=True, null=True)
    highestpossible = models.IntegerField(blank=True, null=True)
    teamform = models.IntegerField(blank=True, null=True)
    highestprobable = models.IntegerField(blank=True, null=True)
    homewins = models.IntegerField(blank=True, null=True)
    artificialkey = models.IntegerField(blank=True, null=True)
    nummatchesplayed = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    grouping = models.IntegerField(blank=True, null=True)
    awaywins = models.IntegerField(blank=True, null=True)
    objective = models.IntegerField(blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    actualvsexpectations = models.IntegerField(blank=True, null=True)
    homelosses = models.IntegerField(blank=True, null=True)
    unbeatenhome = models.IntegerField(blank=True, null=True)
    lastgameresult = models.IntegerField(blank=True, null=True)
    unbeatenaway = models.IntegerField(blank=True, null=True)
    awaylosses = models.IntegerField(blank=True, null=True)
    awaydraws = models.IntegerField(blank=True, null=True)
    homedraws = models.IntegerField(blank=True, null=True)
    teamlongform = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_leagueteamlinks'

class DataUsersTeamplayerlinks(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    leaguegoals = models.IntegerField(blank=True, null=True)
    isamongtopscorers = models.IntegerField(blank=True, null=True)
    yellows = models.IntegerField(blank=True, null=True)
    isamongtopscorersinteam = models.IntegerField(blank=True, null=True)
    jerseynumber = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    artificialkey = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True) #models.ForeignKey(DataUsersTeams, to_field='faf', db_column='teamid', on_delete=models.CASCADE)
    leaguegoalsprevmatch = models.IntegerField(blank=True, null=True)
    injury = models.IntegerField(blank=True, null=True)
    leagueappearances = models.IntegerField(blank=True, null=True)
    istopscorer = models.IntegerField(blank=True, null=True)
    leaguegoalsprevthreematches = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    form = models.IntegerField(blank=True, null=True)
    reds = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_teamplayerlinks'

class DataNations(models.Model):
    isocountrycode = models.CharField(max_length=3, blank=True, null=True)
    nationname = models.CharField(max_length=50, blank=True, null=True)
    confederation = models.IntegerField(blank=True, null=True)
    top_tier = models.IntegerField(blank=True, null=True)
    nationstartingfirstletter = models.IntegerField(blank=True, null=True)
    groupid = models.IntegerField(blank=True, null=True)
    nationid = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'data_nations'

class DataPlayernames(models.Model):
    name = models.CharField(max_length=77, blank=True, null=True)
    nameid = models.IntegerField(primary_key=True)
    commentaryid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data_playernames'

class DataUsersEditedplayernames(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    firstname = models.CharField(max_length=45, blank=True, null=True)
    commonname = models.CharField(max_length=45, blank=True, null=True)
    playerjerseyname = models.CharField(max_length=45, blank=True, null=True)
    surname = models.CharField(max_length=45, blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_editedplayernames'


class DataUsersLeagues(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    countryid = models.IntegerField(blank=True, null=True)
    leaguename = models.CharField(max_length=120, blank=True, null=True)
    level = models.IntegerField(blank=True, null=True)
    iscompetitionscarfenabled = models.IntegerField(blank=True, null=True)
    isbannerenabled = models.IntegerField(blank=True, null=True)
    leagueid = models.IntegerField(blank=True, null=True)
    iscompetitionpoleflagenabled = models.IntegerField(blank=True, null=True)
    iscompetitioncrowdcardsenabled = models.IntegerField(blank=True, null=True)
    leaguetimeslice = models.IntegerField(blank=True, null=True)
    iswithintransferwindow = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()
    
    class Meta:
        managed = False
        db_table = 'data_users_leagues'


class DataUsersManager(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    firstname = models.CharField(max_length=45, blank=True, null=True)
    surname = models.CharField(max_length=45, blank=True, null=True)
    managerid = models.IntegerField(blank=True, null=True)
    headid = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    hashighqualityhead = models.IntegerField(blank=True, null=True)
    gender = models.IntegerField(blank=True, null=True)
    suitvariationid = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    suittypeid = models.IntegerField(blank=True, null=True)
    eyecolorcode = models.IntegerField(blank=True, null=True)
    headclasscode = models.IntegerField(blank=True, null=True)
    skintonecode = models.IntegerField(blank=True, null=True)
    bodytypecode = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data_users_manager'

class DataUsersPlayers(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    firstname = models.ForeignKey(DataPlayernames, related_name='firstname', db_column='firstnameid', null=True, on_delete=models.CASCADE)
    lastname = models.ForeignKey(DataPlayernames, related_name='lastname',  db_column='lastnameid', null=True, on_delete=models.CASCADE)
    playerjerseyname = models.ForeignKey(DataPlayernames, related_name='playerjerseyname', db_column='playerjerseynameid', null=True, on_delete=models.CASCADE)
    commonname = models.ForeignKey(DataPlayernames, related_name='commonname', db_column='commonnameid', null=True, on_delete=models.CASCADE)
    trait2 = models.IntegerField(blank=True, null=True)
    haircolorcode = models.IntegerField(blank=True, null=True)
    facialhairtypecode = models.IntegerField(blank=True, null=True)
    curve = models.IntegerField(blank=True, null=True)
    jerseystylecode = models.IntegerField(blank=True, null=True)
    agility = models.IntegerField(blank=True, null=True)
    accessorycode4 = models.IntegerField(blank=True, null=True)
    gksavetype = models.IntegerField(blank=True, null=True)
    positioning = models.IntegerField(blank=True, null=True)
    tattooleftarm = models.IntegerField(blank=True, null=True)
    hairtypecode = models.IntegerField(blank=True, null=True)
    standingtackle = models.IntegerField(blank=True, null=True)
    tattoobackneck = models.IntegerField(blank=True, null=True)
    preferredposition3 = models.IntegerField(blank=True, null=True)
    longpassing = models.IntegerField(blank=True, null=True)
    penalties = models.IntegerField(blank=True, null=True)
    animfreekickstartposcode = models.IntegerField(blank=True, null=True)
    animpenaltieskickstylecode = models.IntegerField(blank=True, null=True)
    isretiring = models.IntegerField(blank=True, null=True)
    longshots = models.IntegerField(blank=True, null=True)
    gkdiving = models.IntegerField(blank=True, null=True)
    interceptions = models.IntegerField(blank=True, null=True)
    shoecolorcode2 = models.IntegerField(blank=True, null=True)
    crossing = models.IntegerField(blank=True, null=True)
    potential = models.IntegerField(blank=True, null=True)
    gkreflexes = models.IntegerField(blank=True, null=True)
    finishingcode1 = models.IntegerField(blank=True, null=True)
    reactions = models.IntegerField(blank=True, null=True)
    composure = models.IntegerField(blank=True, null=True)
    vision = models.IntegerField(blank=True, null=True)
    contractvaliduntil = models.IntegerField(blank=True, null=True)
    animpenaltiesapproachcode = models.IntegerField(blank=True, null=True)
    finishing = models.IntegerField(blank=True, null=True)
    dribbling = models.IntegerField(blank=True, null=True)
    slidingtackle = models.IntegerField(blank=True, null=True)
    accessorycode3 = models.IntegerField(blank=True, null=True)
    accessorycolourcode1 = models.IntegerField(blank=True, null=True)
    headtypecode = models.IntegerField(blank=True, null=True)
    sprintspeed = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    hasseasonaljersey = models.IntegerField(blank=True, null=True)
    preferredposition2 = models.IntegerField(blank=True, null=True)
    strength = models.IntegerField(blank=True, null=True)
    shoetypecode = models.IntegerField(blank=True, null=True)
    birthdate = models.IntegerField(blank=True, null=True)
    preferredposition1 = models.IntegerField(blank=True, null=True)
    ballcontrol = models.IntegerField(blank=True, null=True)
    shotpower = models.IntegerField(blank=True, null=True)
    trait1 = models.IntegerField(blank=True, null=True)
    socklengthcode = models.IntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    hashighqualityhead = models.IntegerField(blank=True, null=True)
    gkglovetypecode = models.IntegerField(blank=True, null=True)
    tattoorightarm = models.IntegerField(blank=True, null=True)
    balance = models.IntegerField(blank=True, null=True)
    gender = models.IntegerField(blank=True, null=True)
    gkkicking = models.IntegerField(blank=True, null=True)
    internationalrep = models.IntegerField(blank=True, null=True)
    animpenaltiesmotionstylecode = models.IntegerField(blank=True, null=True)
    shortpassing = models.IntegerField(blank=True, null=True)
    freekickaccuracy = models.IntegerField(blank=True, null=True)
    skillmoves = models.IntegerField(blank=True, null=True)
    usercaneditname = models.IntegerField(blank=True, null=True)
    attackingworkrate = models.IntegerField(blank=True, null=True)
    finishingcode2 = models.IntegerField(blank=True, null=True)
    aggression = models.IntegerField(blank=True, null=True)
    acceleration = models.IntegerField(blank=True, null=True)
    headingaccuracy = models.IntegerField(blank=True, null=True)
    iscustomized = models.IntegerField(blank=True, null=True)
    eyebrowcode = models.IntegerField(blank=True, null=True)
    runningcode2 = models.IntegerField(blank=True, null=True)
    modifier = models.IntegerField(blank=True, null=True)
    gkhandling = models.IntegerField(blank=True, null=True)
    eyecolorcode = models.IntegerField(blank=True, null=True)
    jerseysleevelengthcode = models.IntegerField(blank=True, null=True)
    accessorycolourcode3 = models.IntegerField(blank=True, null=True)
    accessorycode1 = models.IntegerField(blank=True, null=True)
    playerjointeamdate = models.IntegerField(blank=True, null=True)
    headclasscode = models.IntegerField(blank=True, null=True)
    defensiveworkrate = models.IntegerField(blank=True, null=True)
    nationality = models.ForeignKey(DataNations, db_column='nationality', on_delete=models.CASCADE)
    preferredfoot = models.IntegerField(blank=True, null=True)
    sideburnscode = models.IntegerField(blank=True, null=True)
    weakfootabilitytypecode = models.IntegerField(blank=True, null=True)
    jumping = models.IntegerField(blank=True, null=True)
    skintypecode = models.IntegerField(blank=True, null=True)
    tattoorightneck = models.IntegerField(blank=True, null=True)
    gkkickstyle = models.IntegerField(blank=True, null=True)
    stamina = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    marking = models.IntegerField(blank=True, null=True)
    accessorycolourcode4 = models.IntegerField(blank=True, null=True)
    gkpositioning = models.IntegerField(blank=True, null=True)
    headvariation = models.IntegerField(blank=True, null=True)
    skintonecode = models.IntegerField(blank=True, null=True)
    shortstyle = models.IntegerField(blank=True, null=True)
    overallrating = models.IntegerField(db_index=True,blank=True, null=True)
    tattooleftneck = models.IntegerField(blank=True, null=True)
    emotion = models.IntegerField(blank=True, null=True)
    jerseyfit = models.IntegerField(blank=True, null=True)
    accessorycode2 = models.IntegerField(blank=True, null=True)
    shoedesigncode = models.IntegerField(blank=True, null=True)
    shoecolorcode1 = models.IntegerField(blank=True, null=True)
    hairstylecode = models.IntegerField(blank=True, null=True)
    bodytypecode = models.IntegerField(blank=True, null=True)
    animpenaltiesstartposcode = models.IntegerField(blank=True, null=True)
    runningcode1 = models.IntegerField(blank=True, null=True)
    preferredposition4 = models.IntegerField(blank=True, null=True)
    volleys = models.IntegerField(blank=True, null=True)
    accessorycolourcode2 = models.IntegerField(blank=True, null=True)
    facialhaircolorcode = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_players'

class DataUsersPlayerloans(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(db_index=True, max_length=150, blank=True, null=True)
    teamidloanedfrom = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    loandateend = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        managed = False
        db_table = 'data_users_playerloans'