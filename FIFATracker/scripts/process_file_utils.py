import os
import csv
import shutil
import sys
import mmap
import functools
import xml.etree.ElementTree as ET
import time
import logging

from django.db import connection
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned
from django.utils.translation import ugettext_lazy as _

from core.consts import DEFAULT_DATE

from core.fifa_utils import (
    PlayerAge,
    PlayerValue,
)

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
    DataUsersPlayers19,
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
    DataUsersPlayersuspensions,
    DataUsersBannerplayers,
    DataUsersPlayerformdiff,
    DataUsersTeamformdiff,
    DataUsersVersion,
)


class CalculateValues():
    """ Calculate Values of all players and save it in "players.csv"
        Parameters
        ----------
        csv_path : str
            Path containing .csv files.
    """

    def __init__(self, csv_path, fifa_edition=19):
        self.fifa_edition = str(fifa_edition)
        self.csv_path = csv_path

        self.players_real_ovr = dict()

        self.currdate = self._get_csv_val("career_calendar.csv", "currdate") or DEFAULT_DATE[self.fifa_edition]
        self.currency = self._get_csv_val("career_managerpref.csv", "currency") or 1

        self._calc()
        self._calc_teams_rating()

    def _calc(self):
        """ Calculate"""
        def_positions = (0, 1, 2, 3, 4, 5, 6, 7, 8)
        mid_positions = (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
        att_positions = (20, 21, 22, 23, 24, 25, 26, 27)

        links = self._get_teamplayers_links()

        players_file = os.path.join(self.csv_path, "players.csv")
        if not os.path.isfile(players_file):
            return None

        with open(players_file, 'r', encoding='utf-8') as csvfile:
            data = csvfile.readlines()

            # Add custom columns
            data[0] = data[0][:-1] + ",value_usd,value_eur,value_gbp,wage\n"

            csvfile.seek(0)
            reader = csv.DictReader(csvfile)

            i = 1
            for row in reader:
                # Calc Real Player OVR for actuall position

                playerid = int(row['playerid'])
                teamids, posids = self._get_team_and_pos(playerid, links)

                if teamids and posids:
                    for x in range(len(teamids)):
                        posid = int(posids[x])
                        ovr = self._calc_real_ovr(row, posid)
                        try:
                            players_real_ovr_list = self.players_real_ovr[int(
                                teamids[x])]
                        except KeyError:
                            self.players_real_ovr[int(teamids[x])] = {
                                "DEF": list(),
                                "MID": list(),
                                "ATT": list(),
                            }
                            players_real_ovr_list = self.players_real_ovr[int(
                                teamids[x])]
                        if posid in def_positions:
                            players_real_ovr_list["DEF"].append(ovr)
                        elif posid in mid_positions:
                            players_real_ovr_list["MID"].append(ovr)
                        elif posid in att_positions:
                            players_real_ovr_list["ATT"].append(ovr)
                        else:
                            logging.warning(
                                "POS NOT MATCH. Playerid {} - Posid {}".format(playerid, posid))

                # Calc Player Value in all currencies

                ovr = row['overallrating']
                pot = row['potential']
                age = PlayerAge(row['birthdate'], self.currdate).age
                posid = row['preferredposition1']
                pvalue_usd = PlayerValue(ovr, pot, age, posid, 0, fifa_edition=self.fifa_edition).value
                pvalue_eur = PlayerValue(ovr, pot, age, posid, 1, fifa_edition=self.fifa_edition).value
                pvalue_gbp = PlayerValue(ovr, pot, age, posid, 2, fifa_edition=self.fifa_edition).value
                pwage = 0
                data[i] = data[i][:-1] + \
                    ",{},{},{},{}\n".format(
                        pvalue_usd, pvalue_eur, pvalue_gbp, pwage)
                i += 1

        # Write data
        if not os.path.isfile(players_file):
            return None

        with open(players_file, 'w', encoding='utf-8') as csvfile:
            csvfile.writelines(data)

    def _calc_teams_rating(self):
        """ Calculate Teams ovr, att, mid, def ratings. And Save Data in teams.csv """
        players_ovr = self.players_real_ovr

        # save
        teams_csv = os.path.join(self.csv_path, "teams.csv")
        with open(teams_csv, 'r', encoding='utf-8') as csvfile:
            data = csvfile.readlines()

            # important!
            csvfile.seek(0)

            headers = data[0].split(",")
            reader = csv.DictReader(csvfile)

            i = 1
            for row in reader:
                teamid = int(row['teamid'])
                team_ovr, team_def, team_mid, team_att = self._get_team_ratings(
                    players_ovr, teamid)

                data[i] = self._edited_line(headers=headers, line=data[i].split(","), to_edit={
                                            'overallrating': team_ovr, 'attackrating': team_att, 'midfieldrating': team_mid, 'defenserating': team_def, })
                i += 1

        # Write data
        with open(teams_csv, 'w', encoding='utf-8') as csvfile:
            csvfile.writelines(data)

    def _get_team_ratings(self, players_ovr, teamid):
        """ return team ovr, def, mid, att for teamid"""
        team_ovr = 0
        team_def = 0
        team_mid = 0
        team_att = 0

        for k in players_ovr:
            if k == teamid:
                # calc
                team_ovr = int(
                    (sum(players_ovr[k]['DEF']) + sum(players_ovr[k]['MID']) + sum(players_ovr[k]['ATT'])) / 11)
                try:
                    team_def = int(
                        sum(players_ovr[k]['DEF']) / len(players_ovr[k]['DEF']))
                except ZeroDivisionError:
                    pass

                try:
                    team_mid = int(
                        sum(players_ovr[k]['MID']) / len(players_ovr[k]['MID']))
                except ZeroDivisionError:
                    pass

                try:
                    team_att = int(
                        sum(players_ovr[k]['ATT']) / len(players_ovr[k]['ATT']))
                except ZeroDivisionError:
                    pass

                return team_ovr, team_def, team_mid, team_att

        return team_ovr, team_def, team_mid, team_att

    def _edited_line(self, headers, line, to_edit):
        """Edit line"""

        max_edits = len(to_edit)
        edits_made = 0
        for k in to_edit:
            for x in range(len(headers)):
                if headers[x] == k:
                    line[x] = to_edit[k]
                    edits_made += 1
                    if edits_made >= max_edits:
                        break

        return ",".join(map(str, line))

    def _get_csv_val(self, fname, fieldname):
        fpath = os.path.join(self.csv_path, fname)
        ret_val = None

        if not os.path.isfile(fpath):
            return None

        with open(fpath, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ret_val = row[fieldname]
                break

        return ret_val

    def _get_teamplayers_links(self):
        """ return dict with starting 11 posids of all teams """
        teamplayerlinks_file = os.path.join(
            self.csv_path, "teamplayerlinks.csv")

        teamplayers = dict()
        with open(teamplayerlinks_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # skip SUB/RES players
                if int(row['position']) > 27:
                    continue

                try:
                    playerslist = teamplayers[int(row['playerid'])]
                except KeyError:
                    teamplayers[int(row['playerid'])] = dict()
                    playerslist = teamplayers[int(row['playerid'])]

                playerslist[row['teamid']] = int(row['position'])

        return teamplayers

    def _get_team_and_pos(self, pid, links):
        teamids = list()
        posids = list()

        try:
            player = links[int(pid)]
        except KeyError:
            return None, None

        for k, v in player.items():
            teamids.append(k)
            posids.append(v)

        return teamids, posids

    def _calc_real_ovr(self, row, posid):
        # Return player real ovr
        if posid > 27 or posid == 1:
            return 0

        ovr = list()

        if posid == 0:
            # GK
            # PLAYER_ATTRIBUTE_REACTIONS * 11%
            ovr.append(round(float(row['reactions']) * 0.11, 2))
            # PLAYER_ATTRIBUTE_GK_DIVING * 21%
            ovr.append(round(float(row['gkdiving']) * 0.21, 2))
            # PLAYER_ATTRIBUTE_GK_HANDLING * 21%
            ovr.append(round(float(row['gkhandling']) * 0.21, 2))
            # PLAYER_ATTRIBUTE_GK_KICKING * 5%
            ovr.append(round(float(row['gkkicking']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_GK_REFLEXES * 21%
            ovr.append(round(float(row['gkreflexes']) * 0.21, 2))
            # PLAYER_ATTRIBUTE_GK_POSITIONING * 21%
            ovr.append(round(float(row['gkpositioning']) * 0.21, 2))
        elif posid == 2 or posid == 8:
            # RWB or LWB
            # PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.append(round(float(row['acceleration']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_SPRINT_SPEED * 6%
            ovr.append(round(float(row['sprintspeed']) * 0.06, 2))
            # PLAYER_ATTRIBUTE_STAMINA * 10%
            ovr.append(round(float(row['stamina']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.append(round(float(row['reactions']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_INTERCEPTIONS * 12%
            ovr.append(round(float(row['interceptions']) * 0.12, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 8%
            ovr.append(round(float(row['ballcontrol']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_CROSSING * 12%
            ovr.append(round(float(row['crossing']) * 0.12, 2))
            # PLAYER_ATTRIBUTE_DRIBBLING * 4%
            ovr.append(round(float(row['dribbling']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 10%
            ovr.append(round(float(row['shortpassing']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_MARKING * 7%
            ovr.append(round(float(row['marking']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_STANDING_TACKLE * 8%
            ovr.append(round(float(row['standingtackle']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_SLIDING_TACKLE * 11%
            ovr.append(round(float(row['slidingtackle']) * 0.11, 2))
        elif posid == 3 or posid == 7:
            # RB or LB
            # PLAYER_ATTRIBUTE_ACCELERATION * 5%
            ovr.append(round(float(row['acceleration']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_SPRINT_SPEED * 7%
            ovr.append(round(float(row['sprintspeed']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_STAMINA * 8%
            ovr.append(round(float(row['stamina']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.append(round(float(row['reactions']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_INTERCEPTIONS * 12%
            ovr.append(round(float(row['interceptions']) * 0.12, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 7%
            ovr.append(round(float(row['ballcontrol']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_CROSSING * 9%
            ovr.append(round(float(row['crossing']) * 0.09, 2))
            # PLAYER_ATTRIBUTE_HEADING_ACCURACY * 4%
            ovr.append(round(float(row['headingaccuracy']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 7%
            ovr.append(round(float(row['shortpassing']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_MARKING * 8%
            ovr.append(round(float(row['marking']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_STANDING_TACKLE * 11%
            ovr.append(round(float(row['standingtackle']) * 0.11, 2))
            # PLAYER_ATTRIBUTE_SLIDING_TACKLE * 14%
            ovr.append(round(float(row['slidingtackle']) * 0.14, 2))
        elif posid == 4 or posid == 5 or posid == 6:
            # RCB or CB or LCB
            # PLAYER_ATTRIBUTE_SPRINT_SPEED * 2%
            ovr.append(round(float(row['sprintspeed']) * 0.02, 2))
            # PLAYER_ATTRIBUTE_JUMPING * 3%
            ovr.append(round(float(row['jumping']) * 0.03, 2))
            # PLAYER_ATTRIBUTE_STRENGTH * 10%
            ovr.append(round(float(row['strength']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 5%
            ovr.append(round(float(row['reactions']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_AGGRESSION * 7%
            ovr.append(round(float(row['aggression']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_INTERCEPTIONS * 13%
            ovr.append(round(float(row['interceptions']) * 0.13, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 4%
            ovr.append(round(float(row['ballcontrol']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_HEADING_ACCURACY * 10%
            ovr.append(round(float(row['headingaccuracy']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 5%
            ovr.append(round(float(row['shortpassing']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_MARKING * 14%
            ovr.append(round(float(row['marking']) * 0.14, 2))
            # PLAYER_ATTRIBUTE_STANDING_TACKLE * 17%
            ovr.append(round(float(row['standingtackle']) * 0.17, 2))
            # PLAYER_ATTRIBUTE_SLIDING_TACKLE * 10%
            ovr.append(round(float(row['slidingtackle']) * 0.10, 2))
        elif posid == 9 or posid == 10 or posid == 11:
            # RDM or CDM or LDM
            # PLAYER_ATTRIBUTE_STAMINA * 6%
            ovr.append(round(float(row['stamina']) * 0.06, 2))
            # PLAYER_ATTRIBUTE_STRENGTH * 4%
            ovr.append(round(float(row['strength']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.append(round(float(row['reactions']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_AGGRESSION * 5%
            ovr.append(round(float(row['aggression']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_INTERCEPTIONS * 14%
            ovr.append(round(float(row['interceptions']) * 0.14, 2))
            # PLAYER_ATTRIBUTE_VISION * 4%
            ovr.append(round(float(row['vision']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 10%
            ovr.append(round(float(row['ballcontrol']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_LONG_PASSING * 10%
            ovr.append(round(float(row['longpassing']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 14%
            ovr.append(round(float(row['shortpassing']) * 0.14, 2))
            # PLAYER_ATTRIBUTE_MARKING * 9%
            ovr.append(round(float(row['marking']) * 0.09, 2))
            # PLAYER_ATTRIBUTE_STANDING_TACKLE * 12%
            ovr.append(round(float(row['standingtackle']) * 0.12, 2))
            # PLAYER_ATTRIBUTE_SLIDING_TACKLE * 5%
            ovr.append(round(float(row['slidingtackle']) * 0.05, 2))
        elif posid == 12 or posid == 16:
            # RM or LM
            # PLAYER_ATTRIBUTE_ACCELERATION * 7%
            ovr.append(round(float(row['acceleration']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_SPRINT_SPEED * 6%
            ovr.append(round(float(row['sprintspeed']) * 0.06, 2))
            # PLAYER_ATTRIBUTE_STAMINA * 5%
            ovr.append(round(float(row['stamina']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.append(round(float(row['reactions']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_POSITIONING * 8%
            ovr.append(round(float(row['positioning']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_VISION * 7%
            ovr.append(round(float(row['vision']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 13%
            ovr.append(round(float(row['ballcontrol']) * 0.13, 2))
            # PLAYER_ATTRIBUTE_CROSSING * 10%
            ovr.append(round(float(row['crossing']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_DRIBBLING * 15%
            ovr.append(round(float(row['dribbling']) * 0.15, 2))
            # PLAYER_ATTRIBUTE_FINISHING * 6%
            ovr.append(round(float(row['finishing']) * 0.06, 2))
            # PLAYER_ATTRIBUTE_LONG_PASSING * 5%
            ovr.append(round(float(row['longpassing']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 11%
            ovr.append(round(float(row['shortpassing']) * 0.11, 2))
        elif posid == 13 or posid == 14 or posid == 15:
            # RCM or CM or LCM
            # PLAYER_ATTRIBUTE_STAMINA * 6%
            ovr.append(round(float(row['stamina']) * 0.06, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.append(round(float(row['reactions']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_INTERCEPTIONS * 5%
            ovr.append(round(float(row['interceptions']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_POSITIONING * 6%
            ovr.append(round(float(row['positioning']) * 0.06, 2))
            # PLAYER_ATTRIBUTE_VISION * 13%
            ovr.append(round(float(row['vision']) * 0.13, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 14%
            ovr.append(round(float(row['ballcontrol']) * 0.14, 2))
            # PLAYER_ATTRIBUTE_DRIBBLING * 7%
            ovr.append(round(float(row['dribbling']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_FINISHING * 2%
            ovr.append(round(float(row['finishing']) * 0.02, 2))
            # PLAYER_ATTRIBUTE_LONG_PASSING * 13%
            ovr.append(round(float(row['longpassing']) * 0.13, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 17%
            ovr.append(round(float(row['shortpassing']) * 0.17, 2))
            # PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            ovr.append(round(float(row['shotpower']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_STANDING_TACKLE * 5%
            ovr.append(round(float(row['standingtackle']) * 0.05, 2))
        elif posid == 17 or posid == 18 or posid == 19:
            # RAM or CAM or LAM
            # PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.append(round(float(row['acceleration']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_SPRINT_SPEED * 3%
            ovr.append(round(float(row['sprintspeed']) * 0.03, 2))
            # PLAYER_ATTRIBUTE_AGILITY * 3%
            ovr.append(round(float(row['agility']) * 0.03, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.append(round(float(row['reactions']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_POSITIONING * 9%
            ovr.append(round(float(row['positioning']) * 0.09, 2))
            # PLAYER_ATTRIBUTE_VISION * 14%
            ovr.append(round(float(row['vision']) * 0.14, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 15%
            ovr.append(round(float(row['ballcontrol']) * 0.15, 2))
            # PLAYER_ATTRIBUTE_DRIBBLING * 13%
            ovr.append(round(float(row['dribbling']) * 0.13, 2))
            # PLAYER_ATTRIBUTE_FINISHING * 7%
            ovr.append(round(float(row['finishing']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_LONG_PASSING * 4%
            ovr.append(round(float(row['longpassing']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 16%
            ovr.append(round(float(row['shortpassing']) * 0.16, 2))
            # PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 5%
            ovr.append(round(float(row['shotpower']) * 0.05, 2))
        elif posid == 20 or posid == 21 or posid == 22:
            # RF or CF or LF
            # PLAYER_ATTRIBUTE_ACCELERATION * 5%
            ovr.append(round(float(row['acceleration']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_SPRINT_SPEED * 5%
            ovr.append(round(float(row['sprintspeed']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 9%
            ovr.append(round(float(row['reactions']) * 0.09, 2))
            # PLAYER_ATTRIBUTE_POSITIONING * 13%
            ovr.append(round(float(row['positioning']) * 0.13, 2))
            # PLAYER_ATTRIBUTE_VISION * 8%
            ovr.append(round(float(row['vision']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 15%
            ovr.append(round(float(row['ballcontrol']) * 0.15, 2))
            # PLAYER_ATTRIBUTE_DRIBBLING * 14%
            ovr.append(round(float(row['dribbling']) * 0.14, 2))
            # PLAYER_ATTRIBUTE_FINISHING * 11%
            ovr.append(round(float(row['finishing']) * 0.11, 2))
            # PLAYER_ATTRIBUTE_HEADING_ACCURACY * 2%
            ovr.append(round(float(row['headingaccuracy']) * 0.02, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 9%
            ovr.append(round(float(row['shortpassing']) * 0.09, 2))
            # PLAYER_ATTRIBUTE_SHOT_POWER * 5%
            ovr.append(round(float(row['shotpower']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            ovr.append(round(float(row['shotpower']) * 0.04, 2))
        elif posid == 23 or posid == 27:
            # RW or LW
            # PLAYER_ATTRIBUTE_ACCELERATION * 7%
            ovr.append(round(float(row['acceleration']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_SPRINT_SPEED * 6%
            ovr.append(round(float(row['sprintspeed']) * 0.06, 2))
            # PLAYER_ATTRIBUTE_AGILITY * 3%
            ovr.append(round(float(row['agility']) * 0.03, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.append(round(float(row['reactions']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_POSITIONING * 9%
            ovr.append(round(float(row['positioning']) * 0.09, 2))
            # PLAYER_ATTRIBUTE_VISION * 6%
            ovr.append(round(float(row['vision']) * 0.06, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 14%
            ovr.append(round(float(row['ballcontrol']) * 0.14, 2))
            # PLAYER_ATTRIBUTE_CROSSING * 9%
            ovr.append(round(float(row['crossing']) * 0.09, 2))
            # PLAYER_ATTRIBUTE_DRIBBLING * 16%
            ovr.append(round(float(row['dribbling']) * 0.16, 2))
            # PLAYER_ATTRIBUTE_FINISHING * 10%
            ovr.append(round(float(row['finishing']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 9%
            ovr.append(round(float(row['shortpassing']) * 0.09, 2))
            # PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            ovr.append(round(float(row['shotpower']) * 0.04, 2))
        elif posid == 24 or posid == 25 or posid == 26:
            # RS or ST or LS
            # PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.append(round(float(row['acceleration']) * 0.04, 2))
            # PLAYER_ATTRIBUTE_SPRINT_SPEED * 5%
            ovr.append(round(float(row['sprintspeed']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_STRENGTH * 5%
            ovr.append(round(float(row['strength']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.append(round(float(row['reactions']) * 0.08, 2))
            # PLAYER_ATTRIBUTE_POSITIONING * 13%
            ovr.append(round(float(row['positioning']) * 0.13, 2))
            # PLAYER_ATTRIBUTE_BALL_CONTROL * 10%
            ovr.append(round(float(row['ballcontrol']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_DRIBBLING * 7%
            ovr.append(round(float(row['dribbling']) * 0.07, 2))
            # PLAYER_ATTRIBUTE_FINISHING * 18%
            ovr.append(round(float(row['finishing']) * 0.18, 2))
            # PLAYER_ATTRIBUTE_HEADING_ACCURACY * 10%
            ovr.append(round(float(row['headingaccuracy']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_SHORT_PASSING * 5%
            ovr.append(round(float(row['shortpassing']) * 0.05, 2))
            # PLAYER_ATTRIBUTE_SHOT_POWER * 10%
            ovr.append(round(float(row['shotpower']) * 0.10, 2))
            # PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 3%
            ovr.append(round(float(row['shotpower']) * 0.03, 2))
            # PLAYER_ATTRIBUTE_VOLLEYS * 2%
            ovr.append(round(float(row['volleys']) * 0.02, 2))

        return int(sum(ovr))


class RestToCSV():
    """Convert Data after .db section to .csv format.
        Parameters
        ----------
        rest_path : str
            Path containing rest file

        user : obj
            Django User model object.

        dest_path : str
            Path where csv files will be exported. Default="<rest_path>\\csv"
    """

    def __init__(self, rest_path, user, dest_path=None):
        self.path = rest_path
        self.username = user.username
        self.user_id = user.id

        if dest_path:
            self.dest_path = dest_path
        else:
            self.dest_path = os.path.join(self.path, "csv")

    def convert_to_csv(self):
        rf_full_path = os.path.join(self.path, "rest")

        # Check if file exists
        if not os.path.isfile(rf_full_path):
            return

        with open(rf_full_path, 'rb') as rf:
            mm = mmap.mmap(rf.fileno(), length=0, access=mmap.ACCESS_READ)
            self._release_clauses(mm)
            self._players_stats(mm)

    def _players_stats(self, mm):
        """Current season players statistics"""
        sign_mp002 = b"\x6D\x70\x30\x30\x32\x00"  # mp002 - MonitoredPlayers
        sign_jo002 = b"\x6A\x6F\x30\x30\x32\x00"  # jo002 - JobOffers?
        MP002_SIZE = 1616   # 0x650

        mm.seek(0)
        offset_start = mm.find(sign_mp002) + MP002_SIZE
        if offset_start < MP002_SIZE:
            # logging.error("_players_stats - mp002 not found")
            return False

        offset_end = mm.find(sign_jo002)
        if offset_end < 0:
            # logging.error("_players_stats - jo002 not found")
            return False

        stats_offset = self._get_stats_offset(mm, offset_end)

        if stats_offset < 0:
            # logging.error("_players_stats - stats_offset not found")
            return False

        # Save to file
        with open(os.path.join(self.dest_path, "career_compdata_playerstats.csv"), 'w+', encoding='utf-8') as f_csv:
            # create columns
            headers = "username,ft_user_id,teamid,playerid,tournamentid,unk1,avg,app,goals,unk2,assists,unk3,yellowcards,redcards,unk6,unk7,cleansheets,unk9,unk10,unk11,unk12,unk13,date1,date2,date3\n"
            f_csv.write(headers)

            cur_pos = stats_offset
            mm.seek(cur_pos, 0)

            for p in range(7000):
                mm.read(3)  # index
                teamid = self.ReadInt32(mm.read(4))
                playerid = self.ReadInt32(mm.read(4))
                tournamentid = self.ReadInt16(mm.read(2))

                if teamid == 4294967295 and playerid == 4294967295:
                    break

                unk1 = self.ReadInt16(mm.read(2))
                avg = self.ReadInt16(mm.read(2))
                app = self.ReadInt8(mm.read(1))
                goals = self.ReadInt8(mm.read(1))
                unk2 = self.ReadInt8(mm.read(1))
                assists = self.ReadInt8(mm.read(1))
                unk3 = self.ReadInt8(mm.read(1))
                yellowcards = self.ReadInt8(mm.read(1))
                redcards = self.ReadInt8(mm.read(1))
                unk6 = self.ReadInt8(mm.read(1))
                unk7 = self.ReadInt8(mm.read(1))
                cleansheets = self.ReadInt8(mm.read(1))
                unk9 = self.ReadInt8(mm.read(1))
                unk10 = self.ReadInt32(mm.read(4))
                unk11 = self.ReadInt8(mm.read(1))
                unk12 = self.ReadInt16(mm.read(2))
                unk13 = self.ReadInt8(mm.read(1))
                date1 = self.ReadInt32(mm.read(4))
                date2 = self.ReadInt32(mm.read(4))
                date3 = self.ReadInt32(mm.read(4))

                if app > 1:
                    avg = int(avg / app)
                f_csv.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(self.username, self.user_id, teamid, playerid, tournamentid,
                                                                                                                  unk1, avg, app, goals, unk2, assists, unk3, yellowcards, redcards, unk6, unk7, cleansheets, unk9, unk10, unk11, unk12, unk13, date1, date2, date3))

    def _release_clauses(self, mm):
        """Players Release Clauses"""
        sign = b"\x72\x6C\x63\x74\x72\x6B\x00"  # rlctrk - release clause sign (?)
        mm.seek(0)
        offset = mm.find(sign)

        if offset < 0:
            # release clause sign not found
            return

        # Validate signature
        valid_offset = -1
        while offset >= 0:
            cur_pos = offset + len(sign)
            mm.seek(cur_pos, 0)

            # Number of players with release clause
            num_of_players = self.ReadInt32(mm.read(4))

            if num_of_players > 25000 or num_of_players < 0:
                # invalid number of players
                offset = mm.find(sign, offset + len(sign))
                continue

            playerid = self.ReadInt32(mm.read(4))
            if playerid > 300000 or playerid < 0:
                # invalid playerid
                offset = mm.find(sign, offset + len(sign))
                continue

            # save valid offset
            valid_offset = cur_pos
            break

        if valid_offset == -1:
            # valid offset not found
            return

        mm.seek(valid_offset, 0)
        num_of_players = self.ReadInt32(mm.read(4))
        with open(os.path.join(self.dest_path, "career_rest_releaseclauses.csv"), 'w+', encoding='utf-8') as f_csv:
            # create columns
            headers = "username,ft_user_id,playerid,teamid,release_clause\n"
            f_csv.write(headers)

            for p in range(num_of_players):
                playerid = self.ReadInt32(mm.read(4))
                teamid = self.ReadInt32(mm.read(4))
                clause = self.ReadInt32(mm.read(4))
                f_csv.write("{},{},{},{},{}\n".format(
                    self.username, self.user_id, playerid, teamid, clause))

    def _get_stats_offset(self, mm, compdata_end):
        '''Return offset to stats at compdata'''
        # stats
        # Struct size   -   48         (0x30)
        # Records       -   7000(?)    (0x1B58)

        struct_size = 48

        sign = b"\x00\x00\x01"
        offset = mm.find(sign, mm.tell(), compdata_end)

        if offset < 0:
            return -1

        while offset >= 0:
            if offset > compdata_end:
                return -1

            # Set cursor at offset
            mm.seek(offset, 0)

            # verify first 255 players
            if self._verify_index(mm, struct_size, 255):
                return offset

            offset = mm.find(sign, mm.tell() + 1, compdata_end)

        return -1

    def _verify_index(self, mm, struct_size, range_max):
        """Verify compobj index"""

        mm.seek(struct_size, 1)
        for x in range(1, range_max):
            current_pos = mm.tell()
            next_unit = bytes([x]) + b"\x00\x01"
            find = mm.find(next_unit, current_pos, current_pos + struct_size)
            if find != current_pos:
                return False
            mm.seek(struct_size, 1)

        return True

    def ReadInt8(self, x):
        return int(x[0])

    def ReadInt16(self, x):
        return int(x[0]) | int(x[1]) << 8

    def ReadInt32(self, x):
        return int(x[0]) | int(x[1]) << 8 | int(x[2]) << 16 | int(x[3]) << 24

    def ReadInt64(self, x):
        return int(x[0]) | int(x[1]) << 8 | int(x[2]) << 16 | int(x[3]) << 24 | int(x[4]) << 32 | int(x[5]) << 40 | int(x[6]) << 48 | int(x[7]) << 56


class DatabaseToCSV():
    """Convert FIFA .db to .csv format.
        Parameters
        ----------
        dbs_path : str
            Path containing FIFA .db files.

        user : obj
            Django User model object.

        num_of_db : int
            Number of .db files in <dbs_path>

        xml_file : str
            Full path to "fifa_ng_db-meta.xml" file

        dest_path : str
            Path where csv files will be exported. Default="<dbs_path>\\csv"

    """

    def __init__(self, dbs_path, user, num_of_db, xml_file, dest_path=None):
        self.path = dbs_path
        self.username = user.username
        self.user_id = user.id
        self.max_databases = num_of_db
        self.xml_file = xml_file

        if dest_path:
            self.dest_path = dest_path
        else:
            self.dest_path = os.path.join(self.path, "csv")
            if os.path.exists(self.dest_path):
                shutil.rmtree(self.dest_path)

    def convert_to_csv(self):
        '''Export data from FIFA database tables to csv files and returns xml_field_pkey.'''

        # Read XML FILE
        xml_table_names, xml_field_names, xml_field_range, xml_field_pkey = self.ParseXML(
            XML_FULL_PATH=self.xml_file)

        database_path = self.path
        csv_path = self.dest_path

        # Create csv path dir
        if not os.path.exists(csv_path):
            os.makedirs(csv_path)

        max_databases = self.max_databases
        if max_databases == 0:
            max_databases = 1

        if not self.username:
            username = ""
        else:
            username = self.username

        if not self.user_id:
            user_id = ""
        else:
            user_id = str(self.user_id)

        for db in range(1, max_databases + 1):
            database_full_path = os.path.join(
                database_path, "{}.db".format(db))
            if os.path.exists(database_full_path):
                # Open FIFA Database
                with open(database_full_path, 'rb') as f:
                    database_header = b"\x44\x42\x00\x08\x00\x00\x00\x00"    # FIFA Database file header
                    mm = mmap.mmap(f.fileno(), length=0,
                                   access=mmap.ACCESS_READ)
                    offset = mm.find(database_header)

                    if offset == -1:
                        continue   # File header not matching

                    mm.seek(offset + len(database_header))
                    dbSize = self.ReadInt32(mm.read(4))

                    if dbSize != mm.size():
                        continue     # Invalid file size

                    mm.seek(4, 1)  # Skip unknown 4 bytes
                    # Num of tables in database
                    countTables = self.ReadInt32(mm.read(4))
                    CrcHeader = self.ReadInt32(mm.read(4))   # CRC32

                    table_names = list()
                    TableOffsets = list()

                    for x in range(countTables):
                        table_names.append(mm.read(4).decode("utf-8"))
                        TableOffsets.append(self.ReadInt32(mm.read(4)))

                    CrcShortNames = self.ReadInt32(mm.read(4))   # CRC32
                    TablesStartOffset = mm.tell()
                    allshortnames = list()
                    allRecords = list()
                    allRecordsValues = list()

                    for x in range(countTables):
                        mm.seek(TablesStartOffset + TableOffsets[x])
                        mm.seek(4, 1)  # unknown
                        RecordSize = self.ReadInt32(mm.read(4))  # RecordSize
                        mm.read(4)  # NBitRecords
                        CompressedStringLen = self.ReadInt32(
                            mm.read(4))  # CompressedStringLength
                        CountRecords = self.ReadInt16(
                            mm.read(2))  # CountRecords
                        CountValidRecords = self.ReadInt16(
                            mm.read(2))  # ValidRecords
                        mm.read(4)  # Unknown
                        CountFields = int(mm.read(1)[0])  # CountFields
                        mm.seek(7, 1)  # Unknown
                        mm.read(4)  # CRC32

                        if CountValidRecords <= 0:
                            continue

                        # Skip unsupported database tables
                        try:
                            table_name = xml_table_names[table_names[x]]
                        except KeyError:
                            continue

                        with open(os.path.join(csv_path, "{}.csv".format(table_name)), 'w+', encoding='utf-8') as f_csv:
                            fieldtypes = list()
                            bitoffsets = list()
                            bitdepth = list()
                            shortnames = list()
                            strFieldIndex = list()

                            for y in range(CountFields):
                                fieldtype = self.ReadInt32(mm.read(4))
                                fieldtypes.append(fieldtype)  # fieldtypes
                                bitoffsets.append(self.ReadInt32(
                                    mm.read(4)))  # bitoffset
                                shortnames.append(
                                    mm.read(4).decode("utf-8"))  # shortname
                                bitdepth.append(
                                    self.ReadInt32(mm.read(4)))  # depth

                                if fieldtype == 0:      # String
                                    strFieldIndex.append(y)
                                elif fieldtype == 3:    # Int
                                    pass
                                else:                   # Float aka REAL?
                                    pass

                            # Sort
                            copybitoffsets = list(bitoffsets)
                            sortedBitOffsets = sorted(
                                range(len(bitoffsets)), key=bitoffsets.__getitem__)
                            copyfieldtypes = list(fieldtypes)
                            copyshortnames = list(shortnames)
                            copybitdepth = list(bitdepth)
                            if username and user_id:
                                headers = "username,ft_user_id,"
                            else:
                                headers = ""
                            for v in range(CountFields):
                                # [rdx]
                                fieldtypes[v] = copyfieldtypes[sortedBitOffsets[v]]
                                # [r10+4] (r10 == rdx)
                                bitoffsets[v] = copybitoffsets[sortedBitOffsets[v]]
                                shortnames[v] = copyshortnames[sortedBitOffsets[v]]
                                # [r10+C]
                                bitdepth[v] = copybitdepth[sortedBitOffsets[v]]
                                try:
                                    headers += (xml_field_names[shortnames[v]] + ",")
                                except KeyError:
                                    # print("missing {}:{}\n".format(table_name, shortnames[v]))
                                    # headers += str(shortnames[v]).lower() + ","
                                    raise KeyError('Database contains unsupported columns. Did you choose correct FIFA version?')

                            # CSV - table headers
                            f_csv.write(headers.rstrip(',') + "\n")

                            allshortnames.append(shortnames)
                            RecordValues = list()
                            currentbyte = 0
                            currentbitpos = 0
                            values = username + "," + user_id + ","
                            for i in range(CountValidRecords):
                                position = mm.tell()
                                for j in range(CountFields):
                                    num = int(bitoffsets[j] / 8)
                                    fieldtype = fieldtypes[j]
                                    if fieldtype == 0:  # String
                                        mm.seek(position + num)
                                        currentbyte = 0
                                        currentbitpos = 0
                                        writevalue = self.ReadNullByteStr(
                                            mm, int(bitdepth[j] / 8))
                                    elif fieldtype == 4:  # Float
                                        mm.seek(position + num)
                                        writevalue = self.ReadFloat(mm.read(4))
                                    else:  # Int and ... ?
                                        num = 0
                                        depth = bitdepth[j]
                                        k = 0
                                        if currentbitpos != 0:
                                            k = 8 - currentbitpos
                                            num = currentbyte >> currentbitpos
                                        while k < depth:
                                            # Read single byte
                                            currentbyte = int(mm.read(1)[0])
                                            num += currentbyte << k
                                            k += 8
                                        currentbitpos = (depth + 8 - k & 7)
                                        num2 = int(int(1 << depth) - 1)
                                        num &= num2
                                        writevalue = num + \
                                            int(xml_field_range[xml_table_names[table_names[x]] + xml_field_names[shortnames[j]]])
                                    values += (str(writevalue) + ",")
                                f_csv.write(values.rstrip(',') + '\n')
                                values = username + "," + user_id + ","
                                mm.seek(position + RecordSize)
                                currentbyte = 0
                                currentbitpos = 0

                    mm.close()  # Close mmap
            # os.remove(database_full_path) # Remove FIFA database file
        return xml_field_pkey

    def ReadFloat(self, x):
        return float(self.ReadInt32(x))

    def ReadInt32(self, x):
        return int(x[0]) | int(x[1]) << 8 | int(x[2]) << 16 | int(x[3]) << 24

    def ReadInt16(self, x):
        return int(x[0]) | int(x[1]) << 8

    def ReadNullByteStr(self, mm, strlength):
        nullbyte = b'\x00'
        curpos = mm.tell()
        nbpos = mm.find(nullbyte)
        ret = mm.read(nbpos - curpos)
        mm.seek(curpos + strlength)

        try:
            ret = ret.decode('utf-8', 'ignore')
            # replace unallowed characters
            unallowed_characters = (
                '"',
                ',',
                '\a',
                '\b',
                '\f',
                '\r',
                '\t',
            )
            for x in range(len(unallowed_characters)):
                ret = ret.replace(unallowed_characters[x], "")

            ret = ret.replace('\n', '\\n')

            return ret
        except Exception as e:
            return ""

    def ParseXML(self, XML_FULL_PATH):
        """ Read data from meta XML file for a FIFA database.

        Returns
        -------
        dict
            dict with all table names

        dict
            dict with all field names

        dict
            dict with rangelow values
        """
        tree = ET.parse(XML_FULL_PATH)
        root = tree.getroot()
        table_names = dict()
        field_names = dict()
        field_range_low = dict()
        field_pkey = dict()

        for child in root:
            try:
                for node in child.getiterator():
                    try:
                        table_names[node.attrib['shortname']] = node.attrib['name']
                        for a in node.getiterator():
                            if a.tag == 'field':
                                field_names[a.attrib['shortname']] = a.attrib['name']
                                if a.attrib['type'] == "DBOFIELDTYPE_INTEGER":
                                    field_range_low[node.attrib['name'] + a.attrib['name']] = a.attrib['rangelow']
                                else:
                                    field_range_low[node.attrib['name'] + a.attrib['name']] = 0

                                if 'key' in a.attrib:
                                    if a.attrib['key'] == "True":
                                        field_pkey[node.attrib['name']] = a.attrib['name']
                    except (ValueError):
                        continue
            except (KeyError, IndexError):
                pass

        return table_names, field_names, field_range_low, field_pkey


class UnpackDatabase():
    """Unpack FIFA .db files from FIFA Career Save.
        Parameters
        ----------
        career_file_fullpath : str
            Full path to save file. Example: C:\\Users\\<USER>\\Documents\\FIFA 18\\settings\\Career20180305213744

        dest_path : str
            Path where data will be unpacked. (default source_path)

        to_csv : bool
            Convert .db to .csv? (default True)

        username : str
            Website username. Ignore if you don't upload data to the external database

        user_id : int
            Website user_id. Ignore if you don't upload data to the external database

        max_databases : int
            Number of .db files to unpack from Career Save. Default = 0 (unpack all)
    """

    def __init__(self, career_file_fullpath, dest_path):
        self.career_file_fullpath = career_file_fullpath
        self.dest_path = dest_path

        # Create dest_path path dir
        if not os.path.exists(self.dest_path):
            os.makedirs(self.dest_path)

    def unpack(self):
        """ Unpack databases from career file.

        Returns
        -------
        int
            Number of unpacked .db files from FIFA Career Save.
        """

        # Open Career Save
        with open(self.career_file_fullpath, 'rb') as f:
            # FIFA Database file signature
            database_header = b"\x44\x42\x00\x08\x00\x00\x00\x00"
            mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
            offset = mm.find(database_header)

            # Signature not found
            if offset < 0:
                return 0

            # Data before databases section
            with open(os.path.join(self.dest_path, "data_before_db"), "wb") as data_before_db:
                data_before_db.write(mm[:offset])

            # Databases section
            current_db = 0
            while offset >= 0:
                current_db += 1

                cur_pos = offset + len(database_header)
                mm.seek(cur_pos, 0)
                dbSize = self.ReadInt32(mm.read(4))
                end_of_data = offset + dbSize

                # Create .db file
                with open(os.path.join(self.dest_path, "{}.db".format(current_db)), "wb") as database_file:
                    # Write data to .db file
                    database_file.write(mm[offset:end_of_data])

                offset = mm.find(database_header, end_of_data)

            # Data after databases section
            with open(os.path.join(self.dest_path, "rest"), "wb") as rest:
                rest.write(mm[end_of_data:])

        return current_db

    def ReadInt32(self, x):
        return int(x[0]) | int(x[1]) << 8 | int(x[2]) << 16 | int(x[3]) << 24


class ParseCareerSave():
    """Parse FIFA Career Save.
        Parameters
        ----------
        career_file_fullpath : str
            Full path to save file. media/<USERNAME>/CareerData

        careersave_data_path : str
            Path where data will be unpacked and stored. (csv files)

        user : obj
            Django User model object.

        xml_file : str
            Full path to "fifa_ng_db-meta.xml" file
    """

    def __init__(self, career_file_fullpath, careersave_data_path, user, xml_file, fifa_edition):
        start = time.time()
        self.cs_model = CareerSaveFileModel.objects.filter(
            user_id=user.id).first()

        self.career_file_fullpath = career_file_fullpath
        self.data_path = careersave_data_path
        self.user = user
        self.xml_file = xml_file
        self.fifa_edition = int(fifa_edition)

        # Create Data Path
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        # '''
        # Make copy of career save file
        f_backup = os.path.join(self.data_path, "savefile")
        if os.path.exists(f_backup):
            os.remove(f_backup)
        shutil.copy2(self.career_file_fullpath, f_backup)

        # Unpack databases from career file.
        self._update_savefile_model(
            0, _("Unpacking database from career file."))
        self.unpacked_dbs = UnpackDatabase(
            career_file_fullpath=self.career_file_fullpath, dest_path=self.data_path).unpack()

        if self.unpacked_dbs == 0:
            self._remove_savefile()
            raise ValueError("No .db files in career save.")
        elif self.unpacked_dbs > 3:
            self._remove_savefile()
            raise ValueError(
                "Too many .db files - found {}".format(current_db))

        # Export data from FIFA database to csv files.
        self._update_savefile_model(
            0, _("Exporting data from FIFA database to csv files."))

        db_to_csv = DatabaseToCSV(dbs_path=self.data_path, user=self.user,
                                  num_of_db=self.unpacked_dbs, xml_file=self.xml_file)
        try:
            self.xml_pkeys = db_to_csv.convert_to_csv()
        except Exception as e:
            raise Exception(e)

        # Convert rest of the data to csv file format.
        RestToCSV(rest_path=self.data_path, user=self.user).convert_to_csv()

        csv_path = db_to_csv.dest_path

        # Calculate Values of all players and save it in "players.csv"
        self._update_savefile_model(
            0, _("Calculating Players Values and Teams Ratings"))
        currency = CalculateValues(csv_path=csv_path, fifa_edition=self.fifa_edition).currency

        # Set Default Currency
        self._set_currency(currency=currency)

        # Import data from csv to our PostgreSQL database
        self._update_savefile_model(
            0, _("Importing data to FIFA Tracker database."))
        self.importCareerData(csv_path=csv_path)
        self.protectprivacy()

        # Delete Files
        if os.path.exists(self.data_path):
            shutil.rmtree(self.data_path)

        if os.path.isfile(self.career_file_fullpath):
            os.remove(self.career_file_fullpath)

        end = time.time()

        self._update_savefile_model(
            2, _("Completed in {}s").format(round(end - start, 3)))

    def protectprivacy(self):
        ''' data in DataUsersCareerUsers may contain real user firstname and surname '''
        user_careeruser = DataUsersCareerUsers.objects.filter(
            ft_user_id=self.user.id)
        if user_careeruser:
            for user in user_careeruser:
                firstname = user.firstname
                surname = user.surname

                try:
                    user.firstname = firstname.replace(
                        firstname[1:], "*" * (len(firstname) - 1))
                except AttributeError:
                    # logging.exception("protectprivacy error")
                    user.firstname = "Mr."

                try:
                    user.surname = surname.replace(
                        surname[1:], "*" * (len(surname) - 1))
                except AttributeError:
                    # logging.exception("protectprivacy error")
                    user.surname = "Manager"

                user.save()

    def _set_currency(self, currency):
        self.user.profile.currency = currency
        self.user.save()

    def importCareerData(self, csv_path):
        """Import data from csv files to PostgreSQL database

            Parameters
            ----------
            csv_path : str
                Path to csv files. ex: media/<USERNAME>/data/csv
        """

        # List of csv files that we want to import to our PostgreSQL database
        # '''
        csv_list = [
            "career_compdata_playerstats",
            "career_rest_releaseclauses",
            "career_calendar",
            "career_playercontract",
            "career_users",
            "career_youthplayers",
            "career_managerinfo",
            "career_scouts",
            "career_precontract",
            "career_presignedcontract",
            "career_transferoffer",
            "career_squadranking",
            "career_youthplayerhistory",
            "career_playermatchratinghistory",
            "career_playerlastmatchhistory",
            "career_teamofweek",
            "career_playerawards",
            "career_managerawards",
            "career_managerhistory",
            "career_playergrowthuserseason",
            "career_trophies",
            "career_playasplayer",
            "career_playasplayerhistory",
            "career_managerpref",
            "teamstadiumlinks",
            "teamkits",
            "player_grudgelove",
            "editedplayernames",
            "dcplayernames",
            "leagues",
            "leagueteamlinks",
            "manager",
            "playerloans",
            "teams",
            "competition",
            "rivals",
            "rowteamnationlinks",
            "teamnationlinks",
            # "referee",
            # "leaguerefereelinks",
            # "fixtures",
            # "playersuspensions",
            # "bannerplayers",
            # "playerformdiff",
            # "teamformdiff",
            # "version",
            "formations",
            "default_teamsheets",
            "previousteam",
            "teamplayerlinks",
            "players",
        ]

        '''
        csv_list = [
            "players",
        ]
        #'''

        # Get user id
        user_id = self.user.id
        for csv in csv_list:
            # example: media\<user>\data\csv\career_calendar.csv
            full_csv_path = os.path.join(csv_path, csv) + ".csv"
            if os.path.exists(full_csv_path):
                if csv == "players":
                    if self.fifa_edition == 18:
                        csv = "players"
                    else:
                        csv = "players{}".format(self.fifa_edition)

                model_name = "datausers{}".format(csv.replace("_", ""))
                # career_calendar --> public.datauserscareercalendar
                postgresql_table_name = "public.datausers{}".format(
                    csv.replace("_", ""))

                ct = ContentType.objects.get(model=model_name)
                model = ct.model_class()
                self._delete_data(model=model, user_id=user_id)
                self._copy_from_csv(table=csv, full_csv_path=full_csv_path)

    def _update_table_from_csv(self, model, model_filter, table, full_csv_path, user_id):
        """ Updates database model with content from csv file """

        # Evaluate query to speed up the update process
        models_data_list = list(model_filter.values().iterator())

        # Enum start
        self.enum_start = 0

        # Prepare set of valid pkeys to update
        valid_pkeys_set = set()
        for i in range(len(models_data_list)):
            valid_pkeys_set.add(
                int(models_data_list[i][self.xml_pkeys[table]]))

        # Prepare list for "bulk_create"
        new_rows_array = list()

        # updated = 0

        with open(full_csv_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            reader_sorted = sorted(
                reader, key=lambda d: float(d[self.xml_pkeys[table]]))

        for row in reader_sorted:
            # create lookup
            lookup = self._create_lookup(user_id, table, row)

            # update fk_id
            if table == "players":
                row['nationality_id'] = row['nationality']
                row['firstname_id'] = row['firstnameid']
                row['lastname_id'] = row['lastnameid']
                row['playerjerseyname_id'] = row['playerjerseynameid']
                row['commonname_id'] = row['commonnameid']

                del row['nationality'], row['firstnameid'], row['lastnameid'], row['playerjerseynameid'], row['commonnameid']

            # find
            valid_index = self._dict_filter(
                models_data_list, lookup, table, valid_pkeys_set)

            if valid_index < 0:
                # create
                new_rows_array.append(model(**row))
            else:
                # check if data has changed and update if needed
                if self._is_update_needed(models_data_list[valid_index], row):
                    obj = self._get_model_obj(
                        model_filter, models_data_list[valid_index])
                    if obj is not None:
                        # updated += 1
                        for key, value in row.items():
                            setattr(obj, key, value)

                        obj.save()
                    else:
                        new_rows_array.append(model(**row))

                # delete checked data.
                del models_data_list[valid_index]

        # objects.bulk_create
        if len(new_rows_array) > 0:
            model.objects.bulk_create(new_rows_array)

        # delete unused data
        if len(models_data_list) > 0:
            self._delete_unused(model, models_data_list)

    def _delete_unused(self, model, models_data_list):
        """ delete unused data. players from other save etc."""
        d_len = len(models_data_list)

        primary_keys = list()
        for i in range(d_len):
            primary_keys.append(models_data_list[i]['primary_key'])

        model.objects.filter(primary_key__in=primary_keys).delete()

    def _get_model_obj(self, model_filter, model_data):
        ''' Return model to update '''

        for i, m in enumerate(model_filter, self.enum_start - 1):
            if int(model_data['primary_key']) == m.primary_key:
                # start next iteration from i
                self.enum_start = i
                return m

        return None

    def _delete_data(self, model, user_id):
        """ delete data before update """
        try:
            model.objects.filter(ft_user_id=user_id).delete()
        except Exception as e:
            logging.exception("_delete_data")

    def _create_lookup(self, user_id, table, row):
        lookup = {"ft_user_id": user_id,
                  self.xml_pkeys[table]: row[self.xml_pkeys[table]]}

        # tables with duplicated primary keys. lookup needs to be extended to find unique objects in model.
        if table == "career_transferoffer":
            lookup.update({
                "offerteamid": row['offerteamid'],
                "teamid": row['teamid'],
                "playerid": row['playerid'],
            })
        elif table == "teamkits":
            lookup.update({
                "teamkittypetechid": row['teamkittypetechid'],
                "teamkitid": row['teamkitid'],
            })
        elif table == "player_grudgelove":
            lookup.update({
                "emotional_teamid": row['emotional_teamid'],
            })
        elif table == "rivals":
            lookup.update({
                "teamid2": row['teamid2'],
            })
        elif table == "smrivals":
            lookup.update({
                "teamid2": row['teamid2'],
            })
        elif table == "leaguerefereelinks":
            lookup.update({
                "refereeid": row['refereeid'],
            })
        elif table == "bannerplayers":
            lookup.update({
                "teamtechid": row['teamtechid'],
            })
        elif table == "playerformdiff":
            lookup.update({
                "playerid": row['playerid'],
            })
        elif table == "career_playerlastmatchhistory":
            lookup.update({
                "playerid": row['playerid'],
                "teamid": row['teamid'],
            })

        return lookup

    def _copy_from_csv(self, table, full_csv_path):
        """ Populate data in table with content from csv file """
        if not os.path.isfile(full_csv_path):
            return None

        with connection.cursor() as cur:
            with open(full_csv_path, 'r', encoding='utf-8') as f:
                columns = f.readline()
                SQL_COPY_STATEMENT = """ COPY public.datausers%s (%s) FROM STDIN WITH CSV DELIMITER AS ',' ENCODING 'UTF-8' """
                cur.copy_expert(sql=SQL_COPY_STATEMENT %
                                (table.replace("_", ""), columns), file=f)
                connection.commit()

    def _is_update_needed(self, model_dict, row):
        """ Return true if we need to update data in database """

        for key, value in row.items():
            if str(model_dict[key]) != value:
                return True

        return False

    def _dict_filter(self, dict_data, q, table, valid_pkeys_set):
        """ return index of valid dict """

        valid_index = -1
        d_len = len(dict_data)
        pkey = self.xml_pkeys[table]

        # Check if model contains pkey from lookup
        if int(q[pkey]) not in valid_pkeys_set:
            return -1

        # find
        for i in range(d_len):
            if self._check_model(dict_data[i], q):
                return i

        return valid_index

    def _check_model(self, model_dict, q):
        """ return true if model matches lookup """
        for key, value in q.items():
            if str(model_dict[key]) != str(value):
                return False

        return True

    def _update_savefile_model(self, code, msg):
        logging.info(msg)

        cs_model = self.cs_model

        cs_model.file_process_status_code = code
        cs_model.file_process_status_msg = msg
        cs_model.save()

    def _remove_savefile(self):
        try:
            if os.path.exists(self.career_file_fullpath):
                os.remove(self.career_file_fullpath)
                return True
        except PermissionError as e:
            logging.warning("PermissionError: {}".format(e))
        except TypeError:
            pass

        return False
