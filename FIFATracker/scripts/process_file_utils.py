import shlex
import subprocess
import os
import csv
import shutil
import mmap
import xml.etree.ElementTree as ET
import time
import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from core.consts import (
    DEFAULT_DATE,
    DEFAULT_FIFA_EDITION,
    SUPPORTED_TABLES,
)

from core.fifa_utils import (
    PlayerAge,
    PlayerValue,
)

from players.models import (
    DataUsersCareerCalendar,
    DataUsersCareerUsers,
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
    DataUsersCareerTransferOffer,
    DataUsersCareerCompdataClubNegotiations,
)


class ReadBytesBase:
    def read_int64(self, x):
        return int(x[0] | x[1] << 8 | x[2] << 16 | x[3] << 24 | x[4] << 32 | x[5] << 40 | x[6] << 48 | x[7] << 56)

    def read_int32(self, x):
        return int(x[0] | x[1] << 8 | x[2] << 16 | x[3] << 24)

    def read_int16(self, x):
        return int(x[0] | x[1] << 8)

    def read_int8(self, x):
        return int(x[0])

    def read_float(self, x):
        return float(self.read_int32(x))

    def read_nullbyte_str(self, mm, str_len):
        start = mm.tell()
        ret = mm.read(mm.find(b'\x00') - start)  # Read only from start to null byte
        mm.seek(start + str_len)

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

            # escape new line
            ret = ret.replace('\n', '\\n')

            return ret
        except Exception:
            return ""


class CalculateValues(ReadBytesBase):
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

        # Defensive position ids
        def_positions = (0, 1, 2, 3, 4, 5, 6, 7, 8)

        # Midfield position ids
        mid_positions = (9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19)

        # Attack position ids
        att_positions = (20, 21, 22, 23, 24, 25, 26, 27)

        links = self._get_teamplayers_links()

        players_file = os.path.join(self.csv_path, "players.csv")
        if not os.path.isfile(players_file):
            return None

        calulcated_data = []
        with open(players_file, 'r', encoding='utf-8') as csvfile:
            data = csvfile.readlines()

            # Add custom columns
            calulcated_data.append(data[0][:-1] + ",value_usd,value_eur,value_gbp,wage\n")

            csvfile.seek(0)
            reader = csv.DictReader(csvfile)

            i = 1
            for row in reader:
                # Validate
                nationality = int(row['nationality'])
                if nationality == 0:
                    i += 1
                    continue

                # Calc Real Player OVR for actuall position

                playerid = int(row['playerid'])
                teamids, posids = self._get_team_and_pos(playerid, links)

                if teamids and posids:
                    for x in range(len(teamids)):
                        posid = int(posids[x])
                        ovr = self._calc_real_ovr(row, posid)
                        try:
                            players_real_ovr_list = self.players_real_ovr[int(teamids[x])]
                        except KeyError:
                            self.players_real_ovr[int(teamids[x])] = {
                                "DEF": list(),
                                "MID": list(),
                                "ATT": list(),
                            }
                            players_real_ovr_list = self.players_real_ovr[int(teamids[x])]
                        if posid in def_positions:
                            players_real_ovr_list["DEF"].append(ovr)
                        elif posid in mid_positions:
                            players_real_ovr_list["MID"].append(ovr)
                        elif posid in att_positions:
                            players_real_ovr_list["ATT"].append(ovr)
                        else:
                            logging.warning(
                                "POS NOT MATCH. Playerid {} - Posid {}".format(playerid, posid)
                            )

                # Calc Player Value in all currencies

                ovr = row['overallrating']
                pot = row['potential']
                age = PlayerAge(row['birthdate'], self.currdate).age
                posid = row['preferredposition1']
                pvalue_usd = PlayerValue(ovr, pot, age, posid, 0, fifa_edition=self.fifa_edition).value
                pvalue_eur = PlayerValue(ovr, pot, age, posid, 1, fifa_edition=self.fifa_edition).value
                pvalue_gbp = PlayerValue(ovr, pot, age, posid, 2, fifa_edition=self.fifa_edition).value
                pwage = 0
                calulcated_data.append(data[i][:-1] + ",{},{},{},{}\n".format(
                    pvalue_usd, pvalue_eur, pvalue_gbp, pwage
                ))

                i += 1

        # Write data
        if not os.path.isfile(players_file):
            return None

        with open(players_file, 'w', encoding='utf-8') as csvfile:
            csvfile.writelines(calulcated_data)

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
                team_ovr = (sum(players_ovr[k]['DEF']) + sum(players_ovr[k]['MID']) + sum(players_ovr[k]['ATT'])) // 11

                try:
                    team_def = sum(players_ovr[k]['DEF']) // len(players_ovr[k]['DEF'])
                except ZeroDivisionError:
                    pass

                try:
                    team_mid = sum(players_ovr[k]['MID']) // len(players_ovr[k]['MID'])
                except ZeroDivisionError:
                    pass

                try:
                    team_att = sum(players_ovr[k]['ATT']) // len(players_ovr[k]['ATT'])
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

        # Defined in Database table called 'attributeprefpositionformula'
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
            ovr.append(round(float(row['longshots']) * 0.04, 2))
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
            ovr.append(round(float(row['longshots']) * 0.05, 2))
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
            ovr.append(round(float(row['longshots']) * 0.04, 2))
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
            ovr.append(round(float(row['longshots']) * 0.04, 2))
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
            ovr.append(round(float(row['longshots']) * 0.03, 2))
            # PLAYER_ATTRIBUTE_VOLLEYS * 2%
            ovr.append(round(float(row['volleys']) * 0.02, 2))

        return int(sum(ovr))


class RestToCSV(ReadBytesBase):
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
            # self._club_neg(mm) TODO UNCOMMENT WHEN FIXED

    def _club_neg(self, mm):
        sign_clbneg = b"\x63\x6C\x62\x6E\x65\x67\x00"    # clbneg
        mm.seek(0)

        offsets = []

        offset = mm.find(sign_clbneg)
        while offset >= 0:
            cur_pos = offset + len(sign_clbneg)
            mm.seek(cur_pos, 0)
            offsets.append(cur_pos)
            offset = mm.find(sign_clbneg)

        if len(offsets) != 4:
            return

        # clbneg_1 all teams transfers?
        # clbneg_2 all teams loans?
        # clbneg_3 my team transfers?
        # clbneg_4 my team loans?
        clbneg_structs = {
            'clbneg_1': {
                'playerid': 4,
                'offerteamid': 4,
                'teamid': 4,
                'unk1': 1,
                'isusertransfer': 1,
                'unk3': 8,
                'unk4': 8,
                'transfer_sum1': 4,
                'transfer_sum2': 4,
                'stage': 4,
                'unk6': 60,
                'unk7': 1,
                'unk8': 1,
                'isofferrejected': 1,
                'unk10': 1,
                'offer_history': {
                    'num': 4,
                    'size_of': 12,
                },
                'counter_offer_history': {
                    'num': 4,
                    'size_of': 16,
                },
            },
            'clbneg_2': {
                'playerid': 4,
                'offerteamid': 4,
                'teamid': 4,
                'unk1': 1,
                'isusertransfer': 1,
                'unk3': 4,
                'unk4': 4,
                'unk5': 4,
                'unk6': 60,
                'unk7': 1,
                'unk8': 1,
                'unk9': 1,
                'unk10': 1,
                'unk11': {
                    'num': 4,
                    'size_of': 12,
                },
                'unk12': {
                    'num': 4,
                    'size_of': 12,
                },
            },
            'clbneg_3': {
                'playerid': 4,
                'offerteamid': 4,
                'teamid': 4,
                'offer_history': {
                    'num': 4,
                    'size_of': 84,
                },
                'counter_offer_history': {
                    'num': 4,
                    'size_of': 88,
                },
                'status': {
                    'num': 4,
                    'size_of': 12,
                },
            },
            'clbneg_4': {
                'playerid': 4,
                'offerteamid': 4,
                'teamid': 4,
                'unk1': {
                    'num': 4,
                    'size_of': 28,
                },
                'unk2': {
                    'num': 4,
                    'size_of': 28,
                },
                'unk3': {
                    'num': 4,
                    'size_of': 12,
                },
            },
        }
        clbneg_data = {}
        try:
            for i, off in enumerate(offsets):
                mm.seek(off, 0)
                length = self.read_int32(mm.read(4))
                key = 'clbneg_{}'.format(i+1)
                clbneg_struct = clbneg_structs[key]
                clbneg_data[key] = []
                for l in range(length):
                    result = {}
                    for k, v in clbneg_struct.items():
                        if isinstance(v, dict):
                            length_child = self.read_int32(mm.read(4))
                            child_data = {}
                            loops = int(v['size_of']/4)
                            for j in range(length_child):
                                child_data[j] = []
                                for data in range(loops):
                                    child_data[j].append(self.read_int32(mm.read(4)))
                            val = child_data
                        elif v == 1:
                            val = bool(self.read_int8(mm.read(1)))
                        elif v == 4:
                            val = self.read_int32(mm.read(4))
                        elif v == 8:
                            val = self.read_int64(mm.read(8))
                        else:
                            loops = int(v/4)
                            child_data = []
                            for data in range(loops):
                                child_data.append(self.read_int32(mm.read(4)))
                            val = child_data

                        result[k] = val
                    clbneg_data[key].append(result)
        except Exception as e:
            logging.error("_club_neg error {}".format(str(e)))
            return

        # Save to file
        headers = [
            'username',
            'ft_user_id',
            'playerid',
            'teamid',
            'offerteamid',
            'stage',
            'iscputransfer',
            'isloanoffer',
            'isofferrejected',
            'offeredfee',
        ]
        with open(
            os.path.join(self.dest_path, "career_compdata_clubnegotiations.csv"), 'w+', encoding='utf-8'
        ) as f_csv:
            # create columns
            f_csv.write("{}\n".format(','.join(headers)))

            for i in range(4):
                for neg in clbneg_data['clbneg_{}'.format(i + 1)]:

                    stage = 2
                    isofferrejected = False
                    offeredfee = 0

                    if i == 0:
                        stage = neg['stage']
                        isofferrejected = neg['isofferrejected']

                        offers = neg['offer_history']   # dict
                        counter_offers = neg['counter_offer_history']  # dict
                        if offers and counter_offers:
                            merged_offers = []
                            for k, v in offers.items():
                                merged_offers.append(v)

                            for k, v in counter_offers.items():
                                merged_offers.append(v)

                            # sort by offer date
                            merged_offers.sort(key=lambda d: d[1])

                            # last offer should be our offeredfee
                            offeredfee = merged_offers[-1][0]
                        else:
                            continue
                    elif i == 2:
                        offers = neg['offer_history']   # dict
                        counter_offers = neg['counter_offer_history'] # dict
                        if offers and counter_offers:
                            merged_offers = []
                            for k, v in offers.items():
                                amount = v[5]
                                if amount == 4294967295:
                                    continue
                                merged_offers.append(amount)

                            for k, v in counter_offers.items():
                                amount = v[6]
                                if amount == 4294967295:
                                    continue
                                merged_offers.append(amount)

                            # max offer should be our offeredfee
                            offeredfee = max(merged_offers)
                        else:
                            continue

                    # is cpu transfer
                    try:
                        if neg['isusertransfer']:
                            iscputransfer = False
                        else:
                            iscputransfer = True
                    except KeyError:
                        if i == 2 or i == 3:
                            iscputransfer = False
                        else:
                            iscputransfer = True

                    # isloanoffer
                    if i == 1 or i == 3:
                        isloanoffer = True
                    else:
                        isloanoffer = False

                    to_write = [
                        self.username,
                        str(self.user_id),
                        str(neg['playerid']),
                        str(neg['teamid']),
                        str(neg['offerteamid']),
                        str(stage),
                        str(iscputransfer),
                        str(isloanoffer),
                        str(isofferrejected),
                        str(offeredfee),
                    ]
                    f_csv.write("{}\n".format(','.join(to_write)))

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
                teamid = self.read_int32(mm.read(4))
                playerid = self.read_int32(mm.read(4))
                tournamentid = self.read_int16(mm.read(2))

                if teamid == 4294967295 and playerid == 4294967295:
                    break

                unk1 = self.read_int16(mm.read(2))
                avg = self.read_int16(mm.read(2))
                app = self.read_int8(mm.read(1))
                goals = self.read_int8(mm.read(1))
                unk2 = self.read_int8(mm.read(1))
                assists = self.read_int8(mm.read(1))
                unk3 = self.read_int8(mm.read(1))
                yellowcards = self.read_int8(mm.read(1))
                redcards = self.read_int8(mm.read(1))
                unk6 = self.read_int8(mm.read(1))
                unk7 = self.read_int8(mm.read(1))
                cleansheets = self.read_int8(mm.read(1))
                unk9 = self.read_int8(mm.read(1))
                unk10 = self.read_int32(mm.read(4))
                unk11 = self.read_int8(mm.read(1))
                unk12 = self.read_int16(mm.read(2))
                unk13 = self.read_int8(mm.read(1))
                date1 = self.read_int32(mm.read(4))
                date2 = self.read_int32(mm.read(4))
                date3 = self.read_int32(mm.read(4))

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
            num_of_players = self.read_int32(mm.read(4))

            if num_of_players > 25000 or num_of_players < 0:
                # invalid number of players
                offset = mm.find(sign, offset + len(sign))
                continue

            playerid = self.read_int32(mm.read(4))
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
        num_of_players = self.read_int32(mm.read(4))
        with open(os.path.join(self.dest_path, "career_rest_releaseclauses.csv"), 'w+', encoding='utf-8') as f_csv:
            # create columns
            headers = "username,ft_user_id,playerid,teamid,release_clause\n"
            f_csv.write(headers)

            for p in range(num_of_players):
                playerid = self.read_int32(mm.read(4))
                teamid = self.read_int32(mm.read(4))
                clause = self.read_int32(mm.read(4))
                # fix problem with invalid release clause
                if not (1 <= clause <= 2147483646):
                    continue

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


class DatabaseToCSV(ReadBytesBase):
    """Convert FIFA .db to .csv format.
        Parameters
        ----------
        dbs_path : str
            Path containing FIFA .db files.

        user : obj
            Django User model object.

        db_name: str
            Name of the db file

        num_of_db : int
            Number of .db files in <dbs_path>

        xml_file : str
            Full path to "fifa_ng_db-meta.xml" file

        dest_path : str
            Path where csv files will be exported. Default="<dbs_path>\\csv"

    """

    def __init__(
        self,
        dbs_path,
        user,
        db_name,
        xml_table_names,
        xml_field_names,
        xml_field_range,
        xml_field_pkeys,
        dest_path=None
    ):
        self.path = dbs_path
        self.username = user.username
        self.user_id = user.id
        self.db_name = db_name

        self.xml_table_names = xml_table_names
        self.xml_field_names = xml_field_names
        self.xml_field_range = xml_field_range
        self.xml_field_pkeys = xml_field_pkeys

        if dest_path:
            self.dest_path = dest_path
        else:
            self.dest_path = os.path.join(self.path, "csv")
            if os.path.exists(self.dest_path):
                shutil.rmtree(self.dest_path)

    def convert_to_csv(self):
        """Export data from FIFA database tables to csv files."""

        database_path = self.path
        csv_path = self.dest_path

        # Create csv path dir
        if not os.path.exists(csv_path):
            os.makedirs(csv_path)

        if not self.username:
            username = ""
        else:
            username = self.username

        if not self.user_id:
            user_id = ""
        else:
            user_id = str(self.user_id)

        database_full_path = os.path.join(
            database_path, self.db_name
        )
        if os.path.exists(database_full_path):
            # Open FIFA Database
            with open(database_full_path, 'rb') as f:
                database_header = b"\x44\x42\x00\x08\x00\x00\x00\x00"    # FIFA Database file header
                mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
                offset = mm.find(database_header)

                if offset == -1:
                    logging.error("File header not matching")
                    return   # File header not matching

                mm.seek(offset + len(database_header))
                dbSize = self.read_int32(mm.read(4))  # 0x8

                if dbSize != mm.size():
                    logging.error("Invalid DBSize. {} != {}".format(dbSize, mm.size()))
                    return     # Invalid file size

                mm.seek(4, 1)  # Skip unknown 4 bytes, 0xC
                # Num of tables in database
                countTables = self.read_int32(mm.read(4))   # 0x10

                # CRC32 (POLYNOMIAL = 0x04C11DB7)
                mm.seek(4, 1)
                # CrcHeader = self.ReadInt32(mm.read(4))     # CRC32, 0x14

                table_names = list()
                TableOffsets = list()

                for x in range(countTables):
                    table_names.append(mm.read(4).decode("utf-8"))
                    TableOffsets.append(self.read_int32(mm.read(4)))

                mm.seek(4, 1)
                # CrcShortNames = self.ReadInt32(mm.read(4))   # CRC32

                TablesStartOffset = mm.tell()
                allshortnames = list()

                for x in range(countTables):
                    # Skip unsupported database tables
                    try:
                        table_name = self.xml_table_names[table_names[x]]
                    except KeyError as e:
                        logging.warning("Unsupported database table {}".format(e))
                        continue

                    # Ignore tables we don't use
                    if table_name not in SUPPORTED_TABLES:
                        continue

                    mm.seek(TablesStartOffset + TableOffsets[x])
                    mm.seek(4, 1)  # unknown
                    record_size = self.read_int32(mm.read(4))  # Size of the record
                    mm.seek(10, 1)   # Don't need it right now
                    # mm.seek(4, 1)  #
                    # mm.seek(4, 1)  #
                    # mm.seek(2, 1)  # Total record
                    num_of_valid_records = self.read_int16(mm.read(2))  # Number of valid records
                    mm.seek(4, 1)  # Unknown
                    num_of_fields = self.read_int8(mm.read(1))  # Number of fields
                    mm.seek(11, 1)  # Don't need it right now
                    # mm.seek(7, 1)  # Unknown
                    # mm.seek(4, 1)  # CRC32

                    if num_of_valid_records <= 0:
                        continue

                    with open(os.path.join(csv_path, "{}.csv".format(table_name)), 'w+', encoding='utf-8') as f_csv:
                        tmp_fieldtypes = list()
                        tmp_bitoffsets = list()
                        tmp_shortnames = list()
                        tmp_bitdepth = list()
                        str_field_index = list()

                        for y in range(num_of_fields):
                            # Fieldtypes
                            # DBOFIELDTYPE_STRING = 0
                            # DBOFIELDTYPE_STRING = 13 (Compressed)
                            # DBOFIELDTYPE_INTEGER = 3
                            # DBOFIELDTYPE_TIME = ??
                            # DBOFIELDTYPE_DATE = 3
                            # DBOFIELDTYPE_REAL = 4

                            fieldtype = self.read_int32(mm.read(4))

                            # not sorted
                            tmp_fieldtypes.append(fieldtype)  # fieldtypes
                            tmp_bitoffsets.append(self.read_int32(mm.read(4)))  # bitoffset
                            tmp_shortnames.append(mm.read(4).decode("utf-8"))  # shortname
                            tmp_bitdepth.append(self.read_int32(mm.read(4)))  # depth

                            # String
                            if fieldtype == 0:
                                str_field_index.append(y)

                        # Sort
                        sorted_bit_offsets = sorted(
                            range(len(tmp_bitoffsets)), key=tmp_bitoffsets.__getitem__
                        )

                        # CSV - table headers
                        if username and user_id:
                            headers = "username,ft_user_id,"
                        else:
                            headers = ""

                        fieldtypes = list()
                        bitoffsets = list()
                        shortnames = list()
                        bitdepth = list()

                        for v in range(num_of_fields):
                            # [rdx]
                            fieldtypes.append(tmp_fieldtypes[sorted_bit_offsets[v]])
                            # [r10+4] (r10 == rdx)
                            bitoffsets.append(tmp_bitoffsets[sorted_bit_offsets[v]])
                            shortnames.append(tmp_shortnames[sorted_bit_offsets[v]])
                            # [r10+C]
                            bitdepth.append(tmp_bitdepth[sorted_bit_offsets[v]])
                            try:
                                headers += (self.xml_field_names[shortnames[v]] + ",")
                            except KeyError:
                                # print("missing {}:{}\n".format(table_name, shortnames[v]))
                                # headers += str(shortnames[v]).lower() + ","
                                raise KeyError(
                                    'Database contains unsupported columns. Did you choose correct FIFA version?'
                                )

                        f_csv.write(headers.rstrip(',') + "\n")

                        allshortnames.append(shortnames)
                        # Read all records
                        for i in range(num_of_valid_records):
                            tmp_byte = 0
                            currentbitpos = 0
                            values = username + "," + user_id + ","

                            cur_position = mm.tell()
                            for j in range(num_of_fields):
                                fieldtype = fieldtypes[j]
                                if fieldtype == 0:
                                    # String
                                    tmp_byte = 0
                                    currentbitpos = 0

                                    mm.seek(cur_position + (bitoffsets[j] >> 3))
                                    writevalue = self.read_nullbyte_str(
                                        mm, bitdepth[j] >> 3
                                    )
                                elif fieldtype == 3:
                                    # INTEGER
                                    val = 0
                                    startbit = 0

                                    depth = bitdepth[j]
                                    if currentbitpos != 0:
                                        startbit = 8 - currentbitpos
                                        val = tmp_byte >> currentbitpos

                                    while startbit < depth:
                                        # Read single byte
                                        tmp_byte = self.read_int8(mm.read(1))
                                        val += tmp_byte << startbit
                                        startbit += 8

                                    # Remember bit position for next iteration
                                    currentbitpos = (depth + 8 - startbit & 7)
                                    val &= (1 << depth) - 1

                                    # Add range_low to the value
                                    range_low_key = self.xml_table_names[table_names[x]] + self.xml_field_names[shortnames[j]]
                                    writevalue = val + int(self.xml_field_range[range_low_key])
                                elif fieldtype == 4:
                                    # Float
                                    mm.seek(cur_position + (bitoffsets[j] >> 3))
                                    writevalue = self.read_float(mm.read(4))
                                else:
                                    # Unsupported
                                    raise KeyError(
                                        'Unsupported field type. {} = {}'.format(shortnames[j], fieldtype)
                                    )
                                values += (str(writevalue) + ",")

                            f_csv.write(values.rstrip(',') + '\n')
                            mm.seek(cur_position + record_size)

                mm.close()  # Close mmap
        # os.remove(database_full_path) # Remove FIFA database file


class ParseCareerSave(ReadBytesBase):
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
    def __init__(
        self,
        career_file_fullpath,
        careersave_data_path,
        user,
        xml_file=None,
        fifa_edition=None,
    ):
        # Count time spent on processing save
        start = time.time()

        # career save file model
        self.cs_model = CareerSaveFileModel.objects.filter(
            user_id=user.id
        ).first()

        self.career_file_fullpath = career_file_fullpath
        self.data_path = careersave_data_path
        self.user = user
        self.xml_file = xml_file

        if fifa_edition:
            self.fifa_edition = int(fifa_edition)

        # Create Data Path
        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        # Make copy of career save file
        f_backup = os.path.join(self.data_path, "savefile")
        if os.path.exists(f_backup):
            os.remove(f_backup)
        shutil.copy2(self.career_file_fullpath, f_backup)

        # Unpack databases from career file.
        self._update_savefile_model(0, _("Unpacking database from career file."))
        self.unpacked_dbs = self.unpack_all_dbs()

        if self.unpacked_dbs == 0:
            self._remove_savefile()
            raise ValueError("No .db files in career save.")
        elif self.unpacked_dbs > 3:
            self._remove_savefile()
            raise ValueError(
                "Too many .db files"
            )

        if not self.xml_file:
            # Path to meta XML file for a FIFA database.
            self.xml_file = os.path.join(
                settings.BASE_DIR, "scripts", "Data", str(self.fifa_edition), "XML", "fifa_ng_db-meta.xml"
            )

        csv_dest_path = os.path.join(self.data_path, "csv")
        if os.path.exists(csv_dest_path):
            shutil.rmtree(csv_dest_path)

        # Parse XML
        self.xml_table_names = dict()
        self.xml_field_names = dict()
        self.xml_field_range = dict()
        self.xml_pkeys = dict()
        self.parse_fifa_db_xml()

        # Export data from FIFA database to csv files.
        self._update_savefile_model(0, _("Exporting data from FIFA database to csv files."))

        try:
            # Only:
            # 1.db - carrer_*
            # 2.db
            # self.unpacked_dbs + 1 for all DBS

            for db in range(1, self.unpacked_dbs):
                db_name = "{}.db".format(db)

                db_to_csv = DatabaseToCSV(
                    dbs_path=self.data_path,
                    user=self.user,
                    db_name=db_name,
                    xml_table_names=self.xml_table_names,
                    xml_field_names=self.xml_field_names,
                    xml_field_range=self.xml_field_range,
                    xml_field_pkeys=self.xml_pkeys,
                    dest_path=csv_dest_path,
                )
                db_to_csv.convert_to_csv()
        except Exception as e:
            raise Exception(e)

        # Convert rest of the data to csv file format.
        RestToCSV(
            rest_path=self.data_path,
            user=self.user,
            dest_path=csv_dest_path,
        ).convert_to_csv()

        # Calculate Values of all players and save it in "players.csv"
        self._update_savefile_model(0, _("Calculating Players Values and Teams Ratings"))
        currency = CalculateValues(csv_path=csv_dest_path, fifa_edition=self.fifa_edition).currency
        # Set Default Currency
        self._set_currency(currency=currency)

        # Import data from csv to our PostgreSQL database
        self._update_savefile_model(
            0, _("Importing data to FIFA Tracker database.")
        )
        self.importCareerData(csv_path=csv_dest_path)
        self.protectprivacy()

        # Delete Files on production
        if not settings.DEBUG:
            if os.path.exists(self.data_path):
                shutil.rmtree(self.data_path)

            if os.path.isfile(self.career_file_fullpath):
                os.remove(self.career_file_fullpath)

        self._update_savefile_model(
            2, _("Completed in {}s").format(round(time.time() - start, 3))
        )

    def parse_fifa_db_xml(self):
        """ Read data from meta XML file for a FIFA database. """

        tree = ET.parse(self.xml_file)
        root = tree.getroot()

        for child in root:
            try:
                for node in child.getiterator():
                    try:
                        self.xml_table_names[node.attrib['shortname']] = node.attrib['name']
                        for a in node.getiterator():
                            if a.tag == 'field':
                                self.xml_field_names[a.attrib['shortname']] = a.attrib['name']
                                if a.attrib['type'] == "DBOFIELDTYPE_INTEGER":
                                    self.xml_field_range[node.attrib['name'] + a.attrib['name']] = a.attrib['rangelow']
                                else:
                                    self.xml_field_range[node.attrib['name'] + a.attrib['name']] = 0

                                if 'key' in a.attrib:
                                    if a.attrib['key'] == "True":
                                        self.xml_pkeys[node.attrib['name']] = a.attrib['name']
                    except (ValueError):
                        continue
            except (KeyError, IndexError):
                pass

    def unpack_all_dbs(self):
        """
        :return int: Number of unpacked .db files from FIFA Career Save.
        """
        # Recognize FIFA Edition basing on file size
        fifa_signatures = {
            b'\x6E\x40\x72\x00': '17',
            b'\x63\x7D\xA9\x00': '18',
            b'\x17\x5E\xC6\x00': '19',
        }
        unpacked_dbs = 0

        with open(self.career_file_fullpath, 'rb') as f:
            # FIFA Database file signature
            database_header = b"\x44\x42\x00\x08\x00\x00\x00\x00"

            mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
            offset = mm.find(database_header)

            # Signature not found
            if offset < 0:
                return 0

            cur_pos = mm.tell()         # Save cursor position
            mm.seek(14)                 # 0xE - FILE SIZE
            fifa_sign = mm.read(4)      # Read sign (0x4 bytes)

            if not self.fifa_edition:
                try:
                    self.fifa_edition = fifa_signatures[fifa_sign]
                except KeyError:
                    logging.warning("Unknown size of save file (sign): {}".format(fifa_sign))
                    self.fifa_edition = DEFAULT_FIFA_EDITION

            # Restore cursor position
            mm.seek(cur_pos)

            # Data before databases section
            with open(os.path.join(self.data_path, "data_before_db"), "wb") as data_before_db:
                data_before_db.write(mm[:offset])

            # Databases section
            while offset >= 0:
                cur_pos = offset + len(database_header)
                mm.seek(cur_pos, 0)
                dbSize = self.read_int32(mm.read(4))
                end_of_data = offset + dbSize

                # Create .db file
                with open(os.path.join(self.data_path, "{}.db".format(unpacked_dbs + 1)), "wb") as database_file:
                    # Write data to .db file
                    database_file.write(mm[offset:end_of_data])

                offset = mm.find(database_header, end_of_data)
                unpacked_dbs += 1

            # Data after databases section
            with open(os.path.join(self.data_path, "rest"), "wb") as rest:
                rest.write(mm[end_of_data:])

        return unpacked_dbs

    def protectprivacy(self):
        ''' data in DataUsersCareerUsers may contain real user firstname and surname '''
        user_careeruser = DataUsersCareerUsers.objects.filter(
            ft_user_id=self.user.id
        )
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

        to_import = []

        # Get user id
        user_id = self.user.id
        for csv in SUPPORTED_TABLES:
            # example: media\<user>\data\csv\career_calendar.csv
            full_csv_path = os.path.join(csv_path, csv) + ".csv"

            if csv == "players":
                if self.fifa_edition == 18:
                    csv = "players"
                else:
                    csv = "players{}".format(self.fifa_edition)

            model_name = "datausers{}".format(csv.replace("_", ""))

            ct = ContentType.objects.get(model=model_name)
            model = ct.model_class()
            self._delete_data(model=model, user_id=user_id)

            if os.path.exists(full_csv_path):
                to_import.append(csv)

        self._copy_from_csv(csv_path=csv_path, tables=to_import)

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
        except Exception:
            pass

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

    def _copy_from_csv(self, csv_path, tables):
        """ Populate data in table with content from csv file """
        # Run "import_career_data.py"
        if settings.DEBUG:
            python_ver = "python"  # My LocalHost
        else:
            python_ver = "python3.6"

        # python manage.py runscript process_career_file --script-args 14 18
        command = '{} manage.py runscript import_career_data --script-args "{}" "{}"'.format(
            python_ver, csv_path, ','.join(tables)
        )

        args = shlex.split(command)
        p = subprocess.Popen(args, close_fds=True)
        p.wait()

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
