import time

from django.contrib.contenttypes.models import ContentType 

from players.models import (
    DataUsersCareerCalendar,
    DataUsersCareerUsers,
    DataUsersCareerPlayercontract,
    DataUsersCareerYouthplayers,
    DataUsersTeams,
    DataUsersLeagueteamlinks,
    DataUsersTeamplayerlinks,
    DataUsersDcplayernames,
    DataUsersEditedplayernames,
    DataUsersLeagues,
    DataUsersManager,
    DataUsersPlayers,
    DataUsersPlayers17,
    DataUsersPlayerloans,
)

from core.models import (
    CareerSaveFileModel,
    DataUsersCareerManagerInfo,
    DataUsersCareerScouts,
    DataUsersCareerPrecontract,
    DataUsersCareerPresignedContract,
    DataUsersCareerTransferOffer,
    DataUsersCareerSquadRanking,
    DataUsersCareerYouthPlayerHistory,
    DataUsersCareerPlayermatchratinghistory,
    DataUsersCareerManagerhistory,
    DataUsersCareerPlayerlastmatchhistory,
    DataUsersCareerTeamofweek,
    DataUsersCareerPlayerawards,
    DataUsersCareerManagerawards,
    DataUsersCareerTrophies,
    DataUsersCareerPlayergrowthuserseason,
    DataUsersCareerPlayasplayer,
    DataUsersCareerPlayasplayerhistory,
    DataUsersTeamstadiumlinks,
    DataUsersPreviousteam,
    DataUsersPlayerGrudgelove,
    DataUsersTeamkits,
    DataUsersFormations,
    DataUsersDefaultTeamsheets,
    DataUsersCompetition,
    DataUsersRivals,
    DataUsersRowteamnationlinks,
    DataUsersTeamnationlinks,
    DataUsersReferee,
    DataUsersLeaguerefereelinks,
    DataUsersFixtures,
    DataUsersSmrivals,
    DataUsersPlayersuspensions,
    DataUsersBannerplayers,
    DataUsersPlayerformdiff,
    DataUsersTeamformdiff,
    DataUsersVersion,
)



def delete_data(user_id):
    # Models which will be cleaned
    model_names = [
        "datauserscareercalendar",
        "datauserscareerusers",
        "datauserscareerplayercontract",
        "datauserscareeryouthplayers",
        "datausersteams",
        "datausersleagueteamlinks",
        "datausersteamplayerlinks",
        "datausersdcplayernames",
        "datauserseditedplayernames",
        "datausersleagues",
        "datausersmanager",
        "datausersplayers",
        "datausersplayers17",
        "datausersplayerloans",
        "datauserscareermanagerinfo",
        "datauserscareerscouts",
        "datauserscareerprecontract",
        "datauserscareerpresignedcontract",
        "datauserscareertransferoffer",
        "datauserscareersquadranking",
        "datauserscareeryouthplayerhistory",
        "datauserscareerplayermatchratinghistory",
        "datauserscareermanagerhistory",
        "datauserscareerplayerlastmatchhistory",
        "datauserscareerteamofweek",
        "datauserscareerplayerawards",
        "datauserscareermanagerawards",
        "datauserscareertrophies",
        "datauserscareerplayergrowthuserseason",
        "datauserscareerplayasplayer",
        "datauserscareerplayasplayerhistory",
        "datausersteamstadiumlinks",
        "datauserspreviousteam",
        "datausersplayergrudgelove",
        "datausersteamkits",
        "datausersformations",
        "datausersdefaultteamsheets",
        "datauserscompetition",
        "datausersrivals",
        "datausersrowteamnationlinks",
        "datausersteamnationlinks",
        "datausersreferee",
        "datausersleaguerefereelinks",
        "datausersfixtures",
        "datauserssmrivals",
        "datausersplayersuspensions",
        "datausersbannerplayers",
        "datausersplayerformdiff",
        "datausersteamformdiff",
        "datausersversion",
    ]

    rows_deleted = 0
    
    start = time.time()
    for model_name in model_names:
        ct = ContentType.objects.get(model=model_name) 
        model = ct.model_class()
        rows_deleted += model.objects.filter(ft_user_id=user_id).delete()[0]

    end = time.time()
    print("Deleted {} rows for userid: {} - in {}s.".format(rows_deleted, user_id, round(end - start, 5)))

# python manage.py runscript delete_user_data --script-args 14
def run(*args):
    user_id = args[0]
    delete_data(user_id)
    cs_model = CareerSaveFileModel.objects.filter(user_id=user_id)
    if cs_model:
        cs_model.delete()
