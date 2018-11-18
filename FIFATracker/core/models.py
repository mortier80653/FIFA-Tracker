from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


class UserDataQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(username=user)


class UserDataManager(models.Manager):
    def get_queryset(self):
        return UserDataQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)


def user_dir_path(instance, filename):
    return '{0}/{1}'.format(instance.user.username, 'CareerData')


class CareerSaveFileModel(models.Model):
    def validate_size(filefield_obj):
        filesize = filefield_obj.file.size
        min_size = 6500000
        max_size = 15000000
        if filesize < min_size:
            raise ValidationError("Your file is not a valid FIFA Career File.")
        elif filesize > max_size:
            raise ValidationError("Your file is not a valid FIFA Career File.")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploadedfile = models.FileField(
        verbose_name='FIFA 19 Career File', upload_to=user_dir_path, validators=[validate_size])
    fifa_edition = models.IntegerField(blank=True, null=True, default=19)
    file_process_status_code = models.IntegerField(
        blank=True, null=True, default=0)
    file_process_status_msg = models.CharField(
        max_length=120, blank=True, null=True)


class DataUsersCareerManagerpref(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='managerpref', on_delete=models.CASCADE, null=True,)
    managerprefid = models.IntegerField(blank=True, null=True)
    clubformation1 = models.IntegerField(blank=True, null=True)
    clubformation5 = models.IntegerField(blank=True, null=True)
    intlformation4 = models.IntegerField(blank=True, null=True)
    bonuspercentage = models.IntegerField(blank=True, null=True)
    startofseasonplayerwages = models.IntegerField(blank=True, null=True)
    startofseasonwagebudget = models.IntegerField(blank=True, null=True)
    startofseasontransferbudget = models.IntegerField(blank=True, null=True)
    matchdifficulty = models.IntegerField(blank=True, null=True)
    halflength = models.IntegerField(blank=True, null=True)
    transferbudget = models.IntegerField(blank=True, null=True)
    stadiumid = models.IntegerField(blank=True, null=True)
    clubformation4 = models.IntegerField(blank=True, null=True)
    intlformation1 = models.IntegerField(blank=True, null=True)
    intlformation5 = models.IntegerField(blank=True, null=True)
    wagebudget = models.IntegerField(blank=True, null=True)
    intlformation3 = models.IntegerField(blank=True, null=True)
    clubformation2 = models.IntegerField(blank=True, null=True)
    usedsquad = models.IntegerField(blank=True, null=True)
    boardaidifficulty = models.IntegerField(blank=True, null=True)
    boardfinancialstrictness = models.IntegerField(blank=True, null=True)
    currency = models.IntegerField(blank=True, null=True)
    intlformation2 = models.IntegerField(blank=True, null=True)
    clubformation3 = models.IntegerField(blank=True, null=True)
    skipfirsttransfer = models.IntegerField(blank=True, null=True)
    playasaiteam = models.IntegerField(blank=True, null=True)

    # FIFA 18 - Nintendo Switch
    rsjn = models.IntegerField(blank=True, null=True)
    dgou = models.IntegerField(blank=True, null=True)
    nket = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareermanagerpref"


class DataUsersCareerManagerInfo(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='managerinfo', on_delete=models.CASCADE, null=True,)
    seasonobjectiveresult1 = models.IntegerField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)
    internationalteamid = models.IntegerField(blank=True, null=True)
    playersreleasedthisseason = models.IntegerField(blank=True, null=True)
    bigwinoppscore = models.IntegerField(blank=True, null=True)
    seasonobjective2 = models.IntegerField(blank=True, null=True)
    boardconfidence = models.IntegerField(blank=True, null=True)
    seasonobjective3 = models.IntegerField(blank=True, null=True)
    biglossuserscore = models.IntegerField(blank=True, null=True)
    bigwinoppteamid = models.IntegerField(blank=True, null=True)
    managerreputation = models.IntegerField(blank=True, null=True)
    bigwindate = models.IntegerField(blank=True, null=True)
    clubteamid = models.IntegerField(blank=True, null=True)
    biglossoppteamid = models.IntegerField(blank=True, null=True)
    wage = models.IntegerField(blank=True, null=True)
    seasonobjectiveresult2 = models.IntegerField(blank=True, null=True)
    bigwinuserscore = models.IntegerField(blank=True, null=True)
    bigwinuserteamid = models.IntegerField(blank=True, null=True)
    seasonobjective1 = models.IntegerField(blank=True, null=True)
    losingstreak = models.IntegerField(blank=True, null=True)
    biglossuserteamid = models.IntegerField(blank=True, null=True)
    biglossdate = models.IntegerField(blank=True, null=True)
    seasonobjectiveresult3 = models.IntegerField(blank=True, null=True)
    biglossoppscore = models.IntegerField(blank=True, null=True)
    totalearnings = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = 'datauserscareermanagerinfo'


class DataUsersCareerScouts(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='scouts', on_delete=models.CASCADE, null=True,)
    firstname = models.CharField(max_length=60, blank=True, null=True)
    lastname = models.CharField(max_length=60, blank=True, null=True)
    scoutid = models.IntegerField(blank=True, null=True)
    knowledge = models.IntegerField(blank=True, null=True)
    nationality = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    regionid = models.IntegerField(blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = 'datauserscareerscouts'


class DataUsersCareerPrecontract(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='precontract', on_delete=models.CASCADE, null=True,)
    offerid = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    offeredcontracttype = models.IntegerField(blank=True, null=True)
    iscputransfer = models.IntegerField(blank=True, null=True)
    squadrole = models.IntegerField(blank=True, null=True)
    offerteamid = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    date = models.IntegerField(blank=True, null=True)
    offeredwage = models.IntegerField(blank=True, null=True)
    completedate = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareerprecontract"


class DataUsersCareerPresignedContract(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='presignedcontract', on_delete=models.CASCADE, null=True,)
    offerid = models.IntegerField(blank=True, null=True)
    offeredfee = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    offeredcontracttype = models.IntegerField(blank=True, null=True)
    signonbonus = models.IntegerField(blank=True, null=True)
    performancebonuscount = models.IntegerField(blank=True, null=True)
    signeddate = models.IntegerField(blank=True, null=True)
    iscomingthisseason = models.IntegerField(blank=True, null=True)
    isloanbuy = models.IntegerField(blank=True, null=True)
    currentcontractwage = models.IntegerField(blank=True, null=True)
    squadrole = models.IntegerField(blank=True, null=True)
    performancebonustype = models.IntegerField(blank=True, null=True)
    offerteamid = models.IntegerField(blank=True, null=True)
    releaseclause = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    future_fee = models.IntegerField(blank=True, null=True)
    exchangeplayerid = models.IntegerField(blank=True, null=True)
    offeredwage = models.IntegerField(blank=True, null=True)
    completedate = models.IntegerField(blank=True, null=True)
    performancebonusvalue = models.IntegerField(blank=True, null=True)
    exchangeplayerwage = models.IntegerField(blank=True, null=True)

    # FIFA 19
    isdirectapproach = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareerpresignedcontract"


class DataUsersCareerTransferOffer(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='transferoffer', on_delete=models.CASCADE, null=True,)
    offerid = models.IntegerField(blank=True, null=True)
    offeredfee = models.IntegerField(blank=True, null=True)
    snipedteamid = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    offeredcontracttype = models.IntegerField(blank=True, null=True)
    precontract = models.IntegerField(blank=True, null=True)
    desiredfee = models.IntegerField(blank=True, null=True)
    offeredbonus = models.IntegerField(blank=True, null=True)
    startdate = models.IntegerField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    iscputransfer = models.IntegerField(blank=True, null=True)
    isloanbuy = models.IntegerField(blank=True, null=True)
    valuation = models.IntegerField(blank=True, null=True)
    isloan = models.IntegerField(blank=True, null=True)
    squadrole = models.IntegerField(blank=True, null=True)
    transferwindow = models.IntegerField(blank=True, null=True)
    currentcontractlength = models.IntegerField(blank=True, null=True)
    issnipe = models.IntegerField(blank=True, null=True)
    offerteamid = models.IntegerField(blank=True, null=True)
    counteroffers = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    exchangeplayerid = models.IntegerField(blank=True, null=True)
    date = models.IntegerField(blank=True, null=True)
    offeredwage = models.IntegerField(blank=True, null=True)
    approachreason = models.IntegerField(blank=True, null=True)
    stage = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareertransferoffer"


class DataUsersCareerCompdataClubNegotiations(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='compdataclubnegotiations', on_delete=models.CASCADE, null=True,
    )

    playerid = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    offerteamid = models.IntegerField(blank=True, null=True)
    stage = models.IntegerField(blank=True, null=True)
    iscputransfer = models.BooleanField(default=False)
    isloanoffer = models.BooleanField(default=False)
    isofferrejected = models.BooleanField(default=False)
    offeredfee = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = 'datauserscareercompdataclubnegotiations'


class DataUsersCareerSquadRanking(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='squadranking', on_delete=models.CASCADE, null=True,)
    playerid = models.IntegerField(blank=True, null=True)
    curroverall = models.IntegerField(blank=True, null=True)
    lastoverall = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareersquadranking"


class DataUsersCareerYouthPlayerHistory(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='youthplayerhistory', on_delete=models.CASCADE, null=True,)
    playerid = models.IntegerField(blank=True, null=True)
    appearances = models.IntegerField(blank=True, null=True)
    goals = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareeryouthplayerhistory"


class DataUsersCareerPlayermatchratinghistory(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='playermatchratinghistory', on_delete=models.CASCADE, null=True,)
    artificialkey = models.IntegerField(blank=True, null=True)
    minsplayed = models.IntegerField(blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    date = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareerplayermatchratinghistory"


class DataUsersCareerManagerhistory(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='managerhistory', on_delete=models.CASCADE, null=True,)
    artificialkey = models.IntegerField(blank=True, null=True)
    leagueobjective = models.IntegerField(blank=True, null=True)
    continentalcuptrophies = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    tableposition = models.IntegerField(blank=True, null=True)
    goals_against = models.IntegerField(blank=True, null=True)
    forfeits = models.IntegerField(blank=True, null=True)
    domestic_cup_objective = models.IntegerField(blank=True, null=True)
    domestic_cup_result = models.IntegerField(blank=True, null=True)
    points = models.IntegerField(blank=True, null=True)
    losses = models.IntegerField(blank=True, null=True)
    bigsellamount = models.IntegerField(blank=True, null=True)
    games_played = models.IntegerField(blank=True, null=True)
    bigbuyamount = models.IntegerField(blank=True, null=True)
    leagueid = models.IntegerField(blank=True, null=True)
    leaguetrophies = models.IntegerField(blank=True, null=True)
    domesticcuptrophies = models.IntegerField(blank=True, null=True)
    season = models.IntegerField(blank=True, null=True)
    wins = models.IntegerField(blank=True, null=True)
    draws = models.IntegerField(blank=True, null=True)
    goals_for = models.IntegerField(blank=True, null=True)
    europe_cup_objective = models.IntegerField(blank=True, null=True)
    leagueobjectiveresult = models.IntegerField(blank=True, null=True)
    bigsellplayername = models.CharField(max_length=256, blank=True, null=True)
    bigbuyplayername = models.CharField(max_length=256, blank=True, null=True)
    europe_cup_result = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareermanagerhistory"


class DataUsersCareerPlayerlastmatchhistory(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='playerlastmatchhistory', on_delete=models.CASCADE, null=True,)
    artificialkey = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    minsplayed = models.IntegerField(blank=True, null=True)
    playeroverall = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    playerfact = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareerplayerlastmatchhistory"


class DataUsersCareerTeamofweek(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='teamofweek', on_delete=models.CASCADE, null=True,)
    artificialkey = models.IntegerField(blank=True, null=True)
    matchrating = models.IntegerField(blank=True, null=True)
    weekswon = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareerteamofweek"


class DataUsersCareerPlayerawards(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='playerawards', on_delete=models.CASCADE, null=True,)
    artificialkey = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    typeid = models.IntegerField(blank=True, null=True)
    season = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    compobjid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareerplayerawards"


class DataUsersCareerManagerawards(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='managerawards', on_delete=models.CASCADE, null=True,)
    artificialkey = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    typeid = models.IntegerField(blank=True, null=True)
    season = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)
    compobjid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareermanagerawards"


class DataUsersCareerTrophies(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='trophies', on_delete=models.CASCADE, null=True,)
    season = models.IntegerField(blank=True, null=True)
    flags = models.IntegerField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareertrophies"


class DataUsersCareerPlayergrowthuserseason(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='playergrowthuserseason', on_delete=models.CASCADE, null=True,)
    playerid = models.IntegerField(blank=True, null=True)
    gkkicking = models.IntegerField(blank=True, null=True)
    dribbling = models.IntegerField(blank=True, null=True)
    shotpower = models.IntegerField(blank=True, null=True)
    balance = models.IntegerField(blank=True, null=True)
    marking = models.IntegerField(blank=True, null=True)
    penalties = models.IntegerField(blank=True, null=True)
    volleys = models.IntegerField(blank=True, null=True)
    slidingtackle = models.IntegerField(blank=True, null=True)
    jumping = models.IntegerField(blank=True, null=True)
    headingaccuracy = models.IntegerField(blank=True, null=True)
    dribspeed = models.IntegerField(blank=True, null=True)
    aggression = models.IntegerField(blank=True, null=True)
    longpassing = models.IntegerField(blank=True, null=True)
    gkpositioning = models.IntegerField(blank=True, null=True)
    curve = models.IntegerField(blank=True, null=True)
    strength = models.IntegerField(blank=True, null=True)
    shortpassing = models.IntegerField(blank=True, null=True)
    interceptions = models.IntegerField(blank=True, null=True)
    finishing = models.IntegerField(blank=True, null=True)
    gkhandling = models.IntegerField(blank=True, null=True)
    sprintspeed = models.IntegerField(blank=True, null=True)
    acceleration = models.IntegerField(blank=True, null=True)
    stamina = models.IntegerField(blank=True, null=True)
    reactions = models.IntegerField(blank=True, null=True)
    crossing = models.IntegerField(blank=True, null=True)
    gkdiving = models.IntegerField(blank=True, null=True)
    longshots = models.IntegerField(blank=True, null=True)
    standingtackle = models.IntegerField(blank=True, null=True)
    agility = models.IntegerField(blank=True, null=True)
    overall = models.IntegerField(blank=True, null=True)
    freekickaccuracy = models.IntegerField(blank=True, null=True)
    positioning = models.IntegerField(blank=True, null=True)
    vision = models.IntegerField(blank=True, null=True)
    gkreflexes = models.IntegerField(blank=True, null=True)
    composure = models.IntegerField(blank=True, null=True)
    ballcontrol = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareerplayergrowthuserseason"


class DataUsersCareerPlayasplayer(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='playasplayer', on_delete=models.CASCADE, null=True,)
    userid = models.IntegerField(blank=True, null=True)
    playedlastmatch = models.IntegerField(blank=True, null=True)
    requestactiondays = models.IntegerField(blank=True, null=True)
    numwithdrawrequests = models.IntegerField(blank=True, null=True)
    numconsecnatbenched = models.IntegerField(blank=True, null=True)
    playerrequest = models.IntegerField(blank=True, null=True)
    numloanrequests = models.IntegerField(blank=True, null=True)
    lastwithdrawdate = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    numconsecclubbenched = models.IntegerField(blank=True, null=True)
    numtransferrequests = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareerplayasplayer"


class DataUsersCareerPlayasplayerhistory(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='playasplayerhistory', on_delete=models.CASCADE, null=True,)
    playasplayerhistoryid = models.IntegerField(blank=True, null=True)
    clublevel = models.IntegerField(blank=True, null=True)
    continentalcuptrophies = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    appearances = models.IntegerField(blank=True, null=True)
    tableposition = models.IntegerField(blank=True, null=True)
    totalreds = models.IntegerField(blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    totaltackles = models.IntegerField(blank=True, null=True)
    passesontarget = models.IntegerField(blank=True, null=True)
    goalsconceded = models.IntegerField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    totalpasses = models.IntegerField(blank=True, null=True)
    loses = models.IntegerField(blank=True, null=True)
    matchratings = models.IntegerField(blank=True, null=True)
    totalshots = models.IntegerField(blank=True, null=True)
    tacklesontarget = models.IntegerField(blank=True, null=True)
    leagueid = models.IntegerField(blank=True, null=True)
    wage = models.IntegerField(blank=True, null=True)
    totalyellows = models.IntegerField(blank=True, null=True)
    leaguetrophies = models.IntegerField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)
    domesticcuptrophies = models.IntegerField(blank=True, null=True)
    season = models.IntegerField(blank=True, null=True)
    assists = models.IntegerField(blank=True, null=True)
    wins = models.IntegerField(blank=True, null=True)
    cleansheets = models.IntegerField(blank=True, null=True)
    draws = models.IntegerField(blank=True, null=True)
    motm = models.IntegerField(blank=True, null=True)
    overall = models.IntegerField(blank=True, null=True)
    fouls = models.IntegerField(blank=True, null=True)
    saveattemps = models.IntegerField(blank=True, null=True)
    shotsontarget = models.IntegerField(blank=True, null=True)
    position = models.IntegerField(blank=True, null=True)
    goals = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscareerplayasplayerhistory"


class DataUsersTeamstadiumlinks(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='teamstadiumlinks', on_delete=models.CASCADE, null=True,)
    teamid = models.IntegerField(blank=True, null=True)
    stadiumname = models.CharField(max_length=510, blank=True, null=True)
    forcedhome = models.IntegerField(blank=True, null=True)
    stadiumid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersteamstadiumlinks"


class DataUsersPreviousteam(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='previousteam', on_delete=models.CASCADE, null=True,)
    playerid = models.IntegerField(blank=True, null=True)
    previousteamid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserspreviousteam"


class DataUsersPlayerGrudgelove(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='playerdrudgelove', on_delete=models.CASCADE, null=True,)
    playerid = models.IntegerField(blank=True, null=True)
    level_of_emotion = models.IntegerField(blank=True, null=True)
    emotional_teamid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersplayergrudgelove"


class DataUsersTeamkits(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='teamkits', on_delete=models.CASCADE, null=True,)
    teamtechid = models.IntegerField(blank=True, null=True)
    jerseynumbercolorterg = models.IntegerField(blank=True, null=True)
    jerseyfit = models.IntegerField(blank=True, null=True)
    shortsnumbercolorprimg = models.IntegerField(blank=True, null=True)
    isembargoed = models.IntegerField(blank=True, null=True)
    jerseyfrontnumberplacementcode = models.IntegerField(blank=True, null=True)
    isinheritbasedetailmap = models.IntegerField(blank=True, null=True)
    jerseycollargeometrytype = models.IntegerField(blank=True, null=True)
    shortsnumbercolorsecg = models.IntegerField(blank=True, null=True)
    teamcolorprimb = models.IntegerField(blank=True, null=True)
    teamcolorprimr = models.IntegerField(blank=True, null=True)
    teamcolorsecpercent = models.IntegerField(blank=True, null=True)
    hasadvertisingkit = models.IntegerField(blank=True, null=True)
    shortsnumbercolorsecr = models.IntegerField(blank=True, null=True)
    shortsnumberplacementcode = models.IntegerField(blank=True, null=True)
    jerseyshapestyle = models.IntegerField(blank=True, null=True)
    shortsnumbercolorsecb = models.IntegerField(blank=True, null=True)
    teamkittypetechid = models.IntegerField(blank=True, null=True)
    teamcolorprimg = models.IntegerField(blank=True, null=True)
    shortsnumbercolorprimr = models.IntegerField(blank=True, null=True)
    jerseynamelayouttype = models.IntegerField(blank=True, null=True)
    jerseynumbercolorterr = models.IntegerField(blank=True, null=True)
    jerseynumbercolorterb = models.IntegerField(blank=True, null=True)
    shortsnumbercolorprimb = models.IntegerField(blank=True, null=True)
    teamcolortertr = models.IntegerField(blank=True, null=True)
    shortsnumbercolorterr = models.IntegerField(blank=True, null=True)
    teamcolorprimpercent = models.IntegerField(blank=True, null=True)
    jerseynamecolorg = models.IntegerField(blank=True, null=True)
    islocked = models.IntegerField(blank=True, null=True)
    jerseynamefonttype = models.IntegerField(blank=True, null=True)
    shortsnumbercolorterb = models.IntegerField(blank=True, null=True)
    teamcolortertb = models.IntegerField(blank=True, null=True)
    jerseyrenderingdetailmaptype = models.IntegerField(blank=True, null=True)
    jerseynumbercolorprimb = models.IntegerField(blank=True, null=True)
    jerseynumbercolorsecr = models.IntegerField(blank=True, null=True)
    numberfonttype = models.IntegerField(blank=True, null=True)
    renderingmaterialtype = models.IntegerField(blank=True, null=True)
    teamcolorsecg = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    teamcolortertpercent = models.IntegerField(blank=True, null=True)
    jerseynumbercolorprimr = models.IntegerField(blank=True, null=True)
    jerseynumbercolorsecb = models.IntegerField(blank=True, null=True)
    powid = models.IntegerField(blank=True, null=True)
    shortsrenderingdetailmaptype = models.IntegerField(blank=True, null=True)
    teamcolorsecr = models.IntegerField(blank=True, null=True)
    dlc = models.IntegerField(blank=True, null=True)
    shortsnumberfonttype = models.IntegerField(blank=True, null=True)
    jerseynumbercolorsecg = models.IntegerField(blank=True, null=True)
    jerseynumbercolorprimg = models.IntegerField(blank=True, null=True)
    teamcolorsecb = models.IntegerField(blank=True, null=True)
    jerseynamecolorr = models.IntegerField(blank=True, null=True)
    jerseybacknameplacementcode = models.IntegerField(blank=True, null=True)
    shortstyle = models.IntegerField(blank=True, null=True)
    shortsnumbercolorterg = models.IntegerField(blank=True, null=True)
    teamcolortertg = models.IntegerField(blank=True, null=True)
    teamkitid = models.IntegerField(blank=True, null=True)
    jerseybacknamefontcase = models.IntegerField(blank=True, null=True)
    jerseynamecolorb = models.IntegerField(blank=True, null=True)

    # FIFA 19
    chestbadge = models.IntegerField(blank=True, null=True)
    captainarmband = models.IntegerField(blank=True, null=True)
    jerseyleftsleevebadge = models.IntegerField(blank=True, null=True)
    jerseyrightsleevebadge = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersteamkits"


class DataUsersFormations(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='formations', on_delete=models.CASCADE, null=True,)
    formationid = models.IntegerField(blank=True, null=True)
    position3 = models.IntegerField(blank=True, null=True)
    position7 = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    midfielders = models.FloatField(null=True, blank=True, default=None)
    offset8y = models.FloatField(null=True, blank=True, default=None)
    offensiverating = models.IntegerField(blank=True, null=True)
    formationaudioid = models.IntegerField(blank=True, null=True)
    offset9y = models.FloatField(null=True, blank=True, default=None)
    offset9x = models.FloatField(null=True, blank=True, default=None)
    playerinstruction10_2 = models.IntegerField(blank=True, null=True)
    offset8x = models.FloatField(null=True, blank=True, default=None)
    attackers = models.FloatField(null=True, blank=True, default=None)
    defenders = models.FloatField(null=True, blank=True, default=None)
    playerinstruction8_1 = models.IntegerField(blank=True, null=True)
    playerinstruction9_1 = models.IntegerField(blank=True, null=True)
    playerinstruction0_1 = models.IntegerField(blank=True, null=True)
    playerinstruction1_1 = models.IntegerField(blank=True, null=True)
    playerinstruction3_1 = models.IntegerField(blank=True, null=True)
    playerinstruction2_1 = models.IntegerField(blank=True, null=True)
    playerinstruction6_1 = models.IntegerField(blank=True, null=True)
    playerinstruction7_1 = models.IntegerField(blank=True, null=True)
    playerinstruction5_1 = models.IntegerField(blank=True, null=True)
    playerinstruction4_1 = models.IntegerField(blank=True, null=True)
    position6 = models.IntegerField(blank=True, null=True)
    position2 = models.IntegerField(blank=True, null=True)
    offset1x = models.FloatField(null=True, blank=True, default=None)
    position10 = models.IntegerField(blank=True, null=True)
    offset4y = models.FloatField(null=True, blank=True, default=None)
    formationname = models.CharField(max_length=50, blank=True, null=True)
    offset5y = models.FloatField(null=True, blank=True, default=None)
    position8 = models.IntegerField(blank=True, null=True)
    offset0x = models.FloatField(null=True, blank=True, default=None)
    position0 = models.IntegerField(blank=True, null=True)
    position4 = models.IntegerField(blank=True, null=True)
    relativeformationid = models.IntegerField(blank=True, null=True)
    offset7y = models.FloatField(null=True, blank=True, default=None)
    offset10x = models.FloatField(null=True, blank=True, default=None)
    offset2x = models.FloatField(null=True, blank=True, default=None)
    offset3x = models.FloatField(null=True, blank=True, default=None)
    offset6y = models.FloatField(null=True, blank=True, default=None)
    offset3y = models.FloatField(null=True, blank=True, default=None)
    offset6x = models.FloatField(null=True, blank=True, default=None)
    offset10y = models.FloatField(null=True, blank=True, default=None)
    playerinstruction10_1 = models.IntegerField(blank=True, null=True)
    offset7x = models.FloatField(null=True, blank=True, default=None)
    offset2y = models.FloatField(null=True, blank=True, default=None)
    formationfullnameid = models.IntegerField(blank=True, null=True)
    position9 = models.IntegerField(blank=True, null=True)
    offset5x = models.FloatField(null=True, blank=True, default=None)
    position5 = models.IntegerField(blank=True, null=True)
    position1 = models.IntegerField(blank=True, null=True)
    offset0y = models.FloatField(null=True, blank=True, default=None)
    playerinstruction1_2 = models.IntegerField(blank=True, null=True)
    playerinstruction0_2 = models.IntegerField(blank=True, null=True)
    playerinstruction2_2 = models.IntegerField(blank=True, null=True)
    playerinstruction3_2 = models.IntegerField(blank=True, null=True)
    playerinstruction7_2 = models.IntegerField(blank=True, null=True)
    playerinstruction6_2 = models.IntegerField(blank=True, null=True)
    playerinstruction4_2 = models.IntegerField(blank=True, null=True)
    playerinstruction5_2 = models.IntegerField(blank=True, null=True)
    offset1y = models.FloatField(null=True, blank=True, default=None)
    offset4x = models.FloatField(null=True, blank=True, default=None)
    playerinstruction9_2 = models.IntegerField(blank=True, null=True)
    playerinstruction8_2 = models.IntegerField(blank=True, null=True)

    # FIFA 18 - Nintendo Switch
    igcc = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersformations"


class DataUsersDefaultTeamsheets(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='defaultteamsheets', on_delete=models.CASCADE, null=True,)
    teamid = models.IntegerField(blank=True, null=True)
    customsub1in = models.IntegerField(blank=True, null=True)
    customsub2out = models.IntegerField(blank=True, null=True)
    customsub0in = models.IntegerField(blank=True, null=True)
    customsub2in = models.IntegerField(blank=True, null=True)
    position3 = models.IntegerField(blank=True, null=True)
    playerid51 = models.IntegerField(blank=True, null=True)
    position7 = models.IntegerField(blank=True, null=True)
    penaltytakerid = models.IntegerField(blank=True, null=True)
    playerid10 = models.IntegerField(blank=True, null=True)
    customsub1out = models.IntegerField(blank=True, null=True)
    playerid49 = models.IntegerField(blank=True, null=True)
    busbuildupspeed = models.IntegerField(blank=True, null=True)
    playerid14 = models.IntegerField(blank=True, null=True)
    playerid41 = models.IntegerField(blank=True, null=True)
    sourceformationid = models.IntegerField(blank=True, null=True)
    playerid45 = models.IntegerField(blank=True, null=True)
    playerid18 = models.IntegerField(blank=True, null=True)
    captainid = models.IntegerField(blank=True, null=True)
    cccrossing = models.IntegerField(blank=True, null=True)
    playerid30 = models.IntegerField(blank=True, null=True)
    playerid34 = models.IntegerField(blank=True, null=True)
    offset8y = models.FloatField(null=True, blank=True, default=None)
    playerid6 = models.IntegerField(blank=True, null=True)
    playerid2 = models.IntegerField(blank=True, null=True)
    playerid38 = models.IntegerField(blank=True, null=True)
    longkicktakerid = models.IntegerField(blank=True, null=True)
    buspositioning = models.IntegerField(blank=True, null=True)
    playerid28 = models.IntegerField(blank=True, null=True)
    playerid20 = models.IntegerField(blank=True, null=True)
    playerid24 = models.IntegerField(blank=True, null=True)
    formationaudioid = models.IntegerField(blank=True, null=True)
    offset9y = models.FloatField(null=True, blank=True, default=None)
    playerid29 = models.IntegerField(blank=True, null=True)
    offset9x = models.FloatField(null=True, blank=True, default=None)
    playerid25 = models.IntegerField(blank=True, null=True)
    leftcornerkicktakerid = models.IntegerField(blank=True, null=True)
    playerid21 = models.IntegerField(blank=True, null=True)
    playerinstruction10_2 = models.IntegerField(blank=True, null=True)
    offset8x = models.FloatField(null=True, blank=True, default=None)
    playerid35 = models.IntegerField(blank=True, null=True)
    playerid31 = models.IntegerField(blank=True, null=True)
    playerid3 = models.IntegerField(blank=True, null=True)
    playerid39 = models.IntegerField(blank=True, null=True)
    playerid7 = models.IntegerField(blank=True, null=True)
    defdefenderline = models.IntegerField(blank=True, null=True)
    playerid15 = models.IntegerField(blank=True, null=True)
    playerid48 = models.IntegerField(blank=True, null=True)
    playerinstruction8_1 = models.IntegerField(blank=True, null=True)
    playerinstruction9_1 = models.IntegerField(blank=True, null=True)
    playerid11 = models.IntegerField(blank=True, null=True)
    playerinstruction0_1 = models.IntegerField(blank=True, null=True)
    playerinstruction1_1 = models.IntegerField(blank=True, null=True)
    playerid19 = models.IntegerField(blank=True, null=True)
    playerid44 = models.IntegerField(blank=True, null=True)
    playerinstruction3_1 = models.IntegerField(blank=True, null=True)
    playerinstruction2_1 = models.IntegerField(blank=True, null=True)
    playerinstruction6_1 = models.IntegerField(blank=True, null=True)
    playerid40 = models.IntegerField(blank=True, null=True)
    playerinstruction7_1 = models.IntegerField(blank=True, null=True)
    playerinstruction5_1 = models.IntegerField(blank=True, null=True)
    playerinstruction4_1 = models.IntegerField(blank=True, null=True)
    position6 = models.IntegerField(blank=True, null=True)
    playerid50 = models.IntegerField(blank=True, null=True)
    position2 = models.IntegerField(blank=True, null=True)
    offset1x = models.FloatField(null=True, blank=True, default=None)
    playerid42 = models.IntegerField(blank=True, null=True)
    playerid46 = models.IntegerField(blank=True, null=True)
    position10 = models.IntegerField(blank=True, null=True)
    playerid13 = models.IntegerField(blank=True, null=True)
    busdribbling = models.IntegerField(blank=True, null=True)
    ccpositioning = models.IntegerField(blank=True, null=True)
    offset4y = models.FloatField(null=True, blank=True, default=None)
    freekicktakerid = models.IntegerField(blank=True, null=True)
    playerid17 = models.IntegerField(blank=True, null=True)
    offset5y = models.FloatField(null=True, blank=True, default=None)
    position8 = models.IntegerField(blank=True, null=True)
    leftfreekicktakerid = models.IntegerField(blank=True, null=True)
    offset0x = models.FloatField(null=True, blank=True, default=None)
    position0 = models.IntegerField(blank=True, null=True)
    position4 = models.IntegerField(blank=True, null=True)
    offset7y = models.FloatField(null=True, blank=True, default=None)
    playerid23 = models.IntegerField(blank=True, null=True)
    playerid27 = models.IntegerField(blank=True, null=True)
    defteamwidth = models.IntegerField(blank=True, null=True)
    offset10x = models.FloatField(null=True, blank=True, default=None)
    ccshooting = models.IntegerField(blank=True, null=True)
    customsub0out = models.IntegerField(blank=True, null=True)
    offset2x = models.FloatField(null=True, blank=True, default=None)
    playerid5 = models.IntegerField(blank=True, null=True)
    offset3x = models.FloatField(null=True, blank=True, default=None)
    tacticid = models.IntegerField(blank=True, null=True)
    playerid1 = models.IntegerField(blank=True, null=True)
    offset6y = models.FloatField(null=True, blank=True, default=None)
    playerid33 = models.IntegerField(blank=True, null=True)
    playerid9 = models.IntegerField(blank=True, null=True)
    playerid37 = models.IntegerField(blank=True, null=True)
    buspassing = models.IntegerField(blank=True, null=True)
    playerid0 = models.IntegerField(blank=True, null=True)
    playerid4 = models.IntegerField(blank=True, null=True)
    offset3y = models.FloatField(null=True, blank=True, default=None)
    playerid36 = models.IntegerField(blank=True, null=True)
    playerid32 = models.IntegerField(blank=True, null=True)
    playerid8 = models.IntegerField(blank=True, null=True)
    defmentality = models.IntegerField(blank=True, null=True)
    offset6x = models.FloatField(null=True, blank=True, default=None)
    playerid26 = models.IntegerField(blank=True, null=True)
    offset10y = models.FloatField(null=True, blank=True, default=None)
    playerid22 = models.IntegerField(blank=True, null=True)
    rightcornerkicktakerid = models.IntegerField(blank=True, null=True)
    playerinstruction10_1 = models.IntegerField(blank=True, null=True)
    offset7x = models.FloatField(null=True, blank=True, default=None)
    defaggression = models.IntegerField(blank=True, null=True)
    offset2y = models.FloatField(null=True, blank=True, default=None)
    formationfullnameid = models.IntegerField(blank=True, null=True)
    position9 = models.IntegerField(blank=True, null=True)
    offset5x = models.FloatField(null=True, blank=True, default=None)
    position5 = models.IntegerField(blank=True, null=True)
    position1 = models.IntegerField(blank=True, null=True)
    offset0y = models.FloatField(null=True, blank=True, default=None)
    playerinstruction1_2 = models.IntegerField(blank=True, null=True)
    playerinstruction0_2 = models.IntegerField(blank=True, null=True)
    playerinstruction2_2 = models.IntegerField(blank=True, null=True)
    playerid47 = models.IntegerField(blank=True, null=True)
    playerinstruction3_2 = models.IntegerField(blank=True, null=True)
    playerid43 = models.IntegerField(blank=True, null=True)
    playerinstruction7_2 = models.IntegerField(blank=True, null=True)
    playerinstruction6_2 = models.IntegerField(blank=True, null=True)
    playerinstruction4_2 = models.IntegerField(blank=True, null=True)
    playerinstruction5_2 = models.IntegerField(blank=True, null=True)
    offset1y = models.FloatField(null=True, blank=True, default=None)
    ccpassing = models.IntegerField(blank=True, null=True)
    playerid16 = models.IntegerField(blank=True, null=True)
    rightfreekicktakerid = models.IntegerField(blank=True, null=True)
    offset4x = models.FloatField(null=True, blank=True, default=None)
    playerinstruction9_2 = models.IntegerField(blank=True, null=True)
    playerid12 = models.IntegerField(blank=True, null=True)
    playerinstruction8_2 = models.IntegerField(blank=True, null=True)

    # FIFA 17
    busbuildupspeedvstrong = models.IntegerField(blank=True, null=True)
    busbuildupspeedvequal = models.IntegerField(blank=True, null=True)
    busbuildupspeedvweak = models.IntegerField(blank=True, null=True)
    buspassingvstrong = models.IntegerField(blank=True, null=True)
    buspassingvequal = models.IntegerField(blank=True, null=True)
    buspassingvweak = models.IntegerField(blank=True, null=True)
    defmentalityvstrong = models.IntegerField(blank=True, null=True)
    defmentalityvequal = models.IntegerField(blank=True, null=True)
    defmentalityvsweak = models.IntegerField(blank=True, null=True)

    # FIFA 19
    offensivewidth = models.IntegerField(blank=True, null=True)
    defensivestyle = models.IntegerField(blank=True, null=True)
    playersinboxfk = models.IntegerField(blank=True, null=True)
    playersinboxcross = models.IntegerField(blank=True, null=True)
    offensivestyle = models.IntegerField(blank=True, null=True)
    defensivedepth = models.IntegerField(blank=True, null=True)
    playersinboxcorner = models.IntegerField(blank=True, null=True)
    defensivewidth = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersdefaultteamsheets"


class DataUsersCompetition(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='competition', on_delete=models.CASCADE, null=True,)
    competitionid = models.IntegerField(blank=True, null=True)
    iscenterpitchflagenabled = models.IntegerField(blank=True, null=True)
    onpitchgraphics = models.IntegerField(blank=True, null=True)
    isvanishingsprayenabled = models.IntegerField(blank=True, null=True)
    adboardplacement = models.IntegerField(blank=True, null=True)
    competitioncolor2b = models.IntegerField(blank=True, null=True)
    colorregion = models.IntegerField(blank=True, null=True)
    adboardplacementstage = models.IntegerField(blank=True, null=True)
    competitioncolor2r = models.IntegerField(blank=True, null=True)
    isstadiumdressingunique = models.IntegerField(blank=True, null=True)
    isgoallinetechcompenabled = models.IntegerField(blank=True, null=True)
    replay360degree = models.IntegerField(blank=True, null=True)
    competitioncolor1b = models.IntegerField(blank=True, null=True)
    iscompetitionpodiumenabled = models.IntegerField(blank=True, null=True)
    isflamethrowercannonsenabled = models.IntegerField(blank=True, null=True)
    isintroconfettienabledstage = models.IntegerField(blank=True, null=True)
    isballplinthenabledstage = models.IntegerField(blank=True, null=True)
    stanchionflamethrower = models.IntegerField(blank=True, null=True)
    isballplinthenabled = models.IntegerField(blank=True, null=True)
    competitioncolor1r = models.IntegerField(blank=True, null=True)
    competitionimportance = models.IntegerField(blank=True, null=True)
    pitchtarps = models.IntegerField(blank=True, null=True)
    competitioncolor1g = models.IntegerField(blank=True, null=True)
    abbapenalties = models.IntegerField(blank=True, null=True)
    ispitchtarpsenabledstage = models.IntegerField(blank=True, null=True)
    isgoallinetechcompenabledstage = models.IntegerField(blank=True, null=True)
    isuniquetrophypedestalenabled = models.IntegerField(blank=True, null=True)
    iscompetitionpoleflagenabled = models.IntegerField(blank=True, null=True)
    isstadiumdressinguniquestage = models.IntegerField(blank=True, null=True)
    introconfetti = models.IntegerField(blank=True, null=True)
    competitioncolor2g = models.IntegerField(blank=True, null=True)
    isteampitchflagenabledstage = models.IntegerField(blank=True, null=True)
    isuniqueadboardscompenabled = models.IntegerField(blank=True, null=True)
    isarchwayenabledstage = models.IntegerField(blank=True, null=True)
    isteampitchflagenabled = models.IntegerField(blank=True, null=True)
    crowdskintonecode = models.IntegerField(blank=True, null=True)
    stadiumcrowdmap = models.IntegerField(blank=True, null=True)
    iscenterpitchflagenabledstage = models.IntegerField(blank=True, null=True)
    isinjuryboardenabled = models.IntegerField(blank=True, null=True)
    goaljingle = models.IntegerField(blank=True, null=True)
    isuniqueleagueflagenabled = models.IntegerField(blank=True, null=True)
    languageregion = models.IntegerField(blank=True, null=True)
    isgoalnetadsenabledstage = models.IntegerField(blank=True, null=True)
    isvanishingsprayhomeenabled = models.IntegerField(blank=True, null=True)
    iscompetitionscarfenabled = models.IntegerField(blank=True, null=True)
    isarchwayenabled = models.IntegerField(blank=True, null=True)
    inflatables = models.IntegerField(blank=True, null=True)
    isstadiumdressingenabledstage = models.IntegerField(blank=True, null=True)
    ballid = models.IntegerField(blank=True, null=True)
    isbannerenabled = models.IntegerField(blank=True, null=True)
    isstanchionflamethrowerenabledstage = models.IntegerField(
        blank=True, null=True)
    isflamethrowercannonsenabledstage = models.IntegerField(
        blank=True, null=True)
    isgoallinetechhomeleagueenabled = models.IntegerField(
        blank=True, null=True)
    goalnetads = models.IntegerField(blank=True, null=True)
    iscompetitioncrowdcardsenabled = models.IntegerField(blank=True, null=True)
    isstadiumdressingenabled = models.IntegerField(blank=True, null=True)
    authenticpodiumskin = models.IntegerField(blank=True, null=True)
    isuniquehandshakeboardenabled = models.IntegerField(blank=True, null=True)

    # FIFA 19
    badge_rs_champions = models.IntegerField(blank=True, null=True)
    country_lock = models.IntegerField(blank=True, null=True)
    celebrationmediapen = models.IntegerField(blank=True, null=True)
    winterballid = models.IntegerField(blank=True, null=True)
    badge_rs = models.IntegerField(blank=True, null=True)
    celebrationarchedboard = models.IntegerField(blank=True, null=True)
    custombibs = models.IntegerField(blank=True, null=True)
    hasvikingclap = models.IntegerField(blank=True, null=True)
    hasmediarope = models.IntegerField(blank=True, null=True)
    pitchbranding = models.IntegerField(blank=True, null=True)
    celebrationbackboard = models.IntegerField(blank=True, null=True)
    badge_chest = models.IntegerField(blank=True, null=True)
    competitionchampionid = models.IntegerField(blank=True, null=True)
    badge_ls = models.IntegerField(blank=True, null=True)
    introteamportrait = models.IntegerField(blank=True, null=True)
    introanthemidle = models.IntegerField(blank=True, null=True)
    celebrationsponsorboard = models.IntegerField(blank=True, null=True)
    armband_type_0 = models.IntegerField(blank=True, null=True)
    armband_type_1 = models.IntegerField(blank=True, null=True)
    badge_ls_champions = models.IntegerField(blank=True, null=True)
    celebrationstage = models.IntegerField(blank=True, null=True)
    badge_chest_champions = models.IntegerField(blank=True, null=True)
    finalballid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserscompetition"


class DataUsersRivals(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='rivals', on_delete=models.CASCADE, null=True,)
    teamid1 = models.IntegerField(blank=True, null=True)
    teamid2 = models.IntegerField(blank=True, null=True)
    rivaltype = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersrivals"


class DataUsersRowteamnationlinks(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='rowteamnationlinks', on_delete=models.CASCADE, null=True,)
    teamid = models.IntegerField(blank=True, null=True)
    nationid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersrowteamnationlinks"


class DataUsersTeamnationlinks(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='teamnationlinks', on_delete=models.CASCADE, null=True,)
    teamid = models.IntegerField(blank=True, null=True)
    nationid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersteamnationlinks"


class DataUsersReferee(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='referee', on_delete=models.CASCADE, null=True,)
    refereeid = models.IntegerField(blank=True, null=True)
    headvariation = models.IntegerField(blank=True, null=True)
    haircolorcode = models.IntegerField(blank=True, null=True)
    firstname = models.CharField(max_length=38, blank=True, null=True)
    headclasscode = models.IntegerField(blank=True, null=True)
    birthdate = models.IntegerField(blank=True, null=True)
    socklengthcode = models.IntegerField(blank=True, null=True)
    surname = models.CharField(max_length=38, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    shoetypecode = models.IntegerField(blank=True, null=True)
    bodytypecode = models.IntegerField(blank=True, null=True)
    skintypecode = models.IntegerField(blank=True, null=True)
    skintonecode = models.IntegerField(blank=True, null=True)
    facialhaircolorcode = models.IntegerField(blank=True, null=True)
    sideburnscode = models.IntegerField(blank=True, null=True)
    shoecolorcode2 = models.IntegerField(blank=True, null=True)
    cardstrictness = models.IntegerField(blank=True, null=True)
    hairtypecode = models.IntegerField(blank=True, null=True)
    gender = models.IntegerField(blank=True, null=True)
    sockheightcode = models.IntegerField(blank=True, null=True)
    eyecolorcode = models.IntegerField(blank=True, null=True)
    leagueid = models.IntegerField(blank=True, null=True)
    facialhairtypecode = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    eyebrowcode = models.IntegerField(blank=True, null=True)
    shoedesigncode = models.IntegerField(blank=True, null=True)
    foulstrictness = models.IntegerField(blank=True, null=True)
    isreal = models.IntegerField(blank=True, null=True)
    shortstyle = models.IntegerField(blank=True, null=True)
    shoecolorcode1 = models.IntegerField(blank=True, null=True)
    headtypecode = models.IntegerField(blank=True, null=True)
    hairstylecode = models.IntegerField(blank=True, null=True)
    nationalitycode = models.IntegerField(blank=True, null=True)
    jerseysleevelengthcode = models.IntegerField(blank=True, null=True)

    # FIFA 17
    proxyheadclass = models.IntegerField(blank=True, null=True)
    homecitycode = models.IntegerField(blank=True, null=True)
    wrinkleid = models.IntegerField(blank=True, null=True)
    hairpartcode = models.IntegerField(blank=True, null=True)
    hairvariationid = models.IntegerField(blank=True, null=True)
    hairlinecode = models.IntegerField(blank=True, null=True)
    sweatid = models.IntegerField(blank=True, null=True)
    proxyhaircolorid = models.IntegerField(blank=True, null=True)
    stylecode = models.IntegerField(blank=True, null=True)
    haireffecttypecode = models.IntegerField(blank=True, null=True)
    hairstateid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersreferee"


class DataUsersLeaguerefereelinks(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='leaguerefereelinks', on_delete=models.CASCADE, null=True,)
    leagueid = models.IntegerField(blank=True, null=True)
    refereeid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersleaguerefereelinks"


class DataUsersFixtures(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='fixtures', on_delete=models.CASCADE, null=True,)
    fixtureid = models.IntegerField(blank=True, null=True)
    fanflags = models.IntegerField(blank=True, null=True)
    awayteamskill = models.IntegerField(blank=True, null=True)
    fancards = models.IntegerField(blank=True, null=True)
    textid_gameotw = models.IntegerField(blank=True, null=True)
    hometeamid = models.IntegerField(blank=True, null=True)
    currhomeprevscore = models.IntegerField(blank=True, null=True)
    awayteamid = models.IntegerField(blank=True, null=True)
    stageofcompetition = models.IntegerField(blank=True, null=True)
    competitionid = models.IntegerField(blank=True, null=True)
    fixturedate = models.IntegerField(blank=True, null=True)
    multipleleg = models.IntegerField(blank=True, null=True)
    stadiumid = models.IntegerField(blank=True, null=True)
    currawayprevscore = models.IntegerField(blank=True, null=True)
    refereeid = models.IntegerField(blank=True, null=True)
    fixturetime = models.IntegerField(blank=True, null=True)
    matchimportance = models.IntegerField(blank=True, null=True)
    leaguefixturenumber = models.IntegerField(blank=True, null=True)
    hometeamskill = models.IntegerField(blank=True, null=True)
    predictedwinner = models.IntegerField(blank=True, null=True)
    livegametype = models.IntegerField(blank=True, null=True)
    legno = models.IntegerField(blank=True, null=True)
    drawmode = models.IntegerField(blank=True, null=True)
    competitiontype = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersfixtures"


class DataUsersSmrivals(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='smrivals', on_delete=models.CASCADE, null=True,)
    teamid1 = models.IntegerField(blank=True, null=True)
    teamid2 = models.IntegerField(blank=True, null=True)
    rivaltype = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datauserssmrivals"


class DataUsersPlayersuspensions(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='playersuspensions', on_delete=models.CASCADE, null=True,)
    artificialkey = models.IntegerField(blank=True, null=True)
    teamid = models.IntegerField(blank=True, null=True)
    enddate = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)
    games = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersplayersuspensions"


class DataUsersBannerplayers(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='bannerplayers', on_delete=models.CASCADE, null=True,)
    playertechid = models.IntegerField(blank=True, null=True)
    teamtechid = models.IntegerField(blank=True, null=True)
    legend = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersbannerplayers"


class DataUsersPlayerformdiff(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='playerformdiff', on_delete=models.CASCADE, null=True,)
    teamid = models.IntegerField(blank=True, null=True)
    newoverallrating = models.IntegerField(blank=True, null=True)
    overallratingdiff = models.IntegerField(blank=True, null=True)
    oldoverallrating = models.IntegerField(blank=True, null=True)
    playerid = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersplayerformdiff"


class DataUsersTeamformdiff(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='teamformdiff', on_delete=models.CASCADE, null=True,)
    teamid = models.IntegerField(blank=True, null=True)
    oldmidfieldrating = models.IntegerField(blank=True, null=True)
    newmidfieldrating = models.IntegerField(blank=True, null=True)
    newoverallrating = models.IntegerField(blank=True, null=True)
    overallratingdiff = models.IntegerField(blank=True, null=True)
    newdefenserating = models.IntegerField(blank=True, null=True)
    oldoverallrating = models.IntegerField(blank=True, null=True)
    olddefenserating = models.IntegerField(blank=True, null=True)
    oldattackrating = models.IntegerField(blank=True, null=True)
    newattackrating = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersteamformdiff"


class DataUsersVersion(models.Model):
    primary_key = models.BigAutoField(primary_key=True)
    username = models.CharField(
        db_index=True, max_length=150, blank=True, null=True)
    ft_user = models.ForeignKey(
        User, related_name='version', on_delete=models.CASCADE, null=True,)
    artificialkey = models.IntegerField(blank=True, null=True)
    major = models.IntegerField(blank=True, null=True)
    exportdate = models.IntegerField(blank=True, null=True)
    minor = models.IntegerField(blank=True, null=True)
    schema = models.CharField(max_length=80, blank=True, null=True)
    isonline = models.IntegerField(blank=True, null=True)

    objects = UserDataManager()

    class Meta:
        db_table = "datausersversion"
