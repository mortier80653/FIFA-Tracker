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

from django.db import transaction, connection, reset_queries

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
    DataUsersCareerUsers,
    DataUsersCareerCalendar,
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
    DataUsersCareerTransferOffer,
    DataUsersCareerCompdataClubNegotiations,
    DataUsersCareerManagerhistory,
)

from file_uploads.models import (
    CareerSaveFileModel
)


class ReadBytesHelper:
    """
        Convert bytes helper class
    """
    def read_int64(self, x, as_string=False):
        n = x[0] | x[1] << 8 | x[2] << 16 | x[3] << 24 | x[4] << 32 | x[5] << 40 | x[6] << 48 | x[7] << 56
        if as_string:
            return str(n)
        else:
            return int(n)

    def read_int32(self, x, as_string=False):
        n = x[0] | x[1] << 8 | x[2] << 16 | x[3] << 24
        if as_string:
            return str(n)
        else:
            return int(n)

    def read_int16(self, x, as_string=False):
        n = x[0] | x[1] << 8
        if as_string:
            return str(n)
        else:
            return int(n)

    def read_int8(self, x, as_string=False):
        n = x[0]
        if as_string:
            return str(n)
        else:
            return int(n)

    def read_float(self, x, as_string=False):
        n = self.read_int32(x)
        if as_string:
            return str(float(n))
        else:
            return float(n)

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


class CalculateValues(ReadBytesHelper):
    """ Calculate Values of all players and save it in "players.csv"
        Parameters
        ----------
        csv_path : str
            Path containing .csv files.
    """

    def __init__(self, currency, currdate, csv_dest_path, fifa_edition='19'):
        self.players_real_ovr = dict()

        self.fifa_edition = fifa_edition
        self.currdate = currdate
        self.currency = currency
        self.csv_path = csv_dest_path

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

                pv = PlayerValue(ovr, pot, age, posid, 0, fifa_edition=self.fifa_edition)
                pvalue_usd = pv.value

                pv._set_currency(1)
                pvalue_eur = pv._calculate_player_value()

                pv._set_currency(2)
                pvalue_gbp = pv._calculate_player_value()
                pwage = '0'
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


def delete_from_model(model, user_id, ft_slot, ft_season):
    """ delete data before update """
    delete_filter = {
        "ft_user_id": user_id,
        "ft_slot": ft_slot,
    }

    if ft_season >= 0:
        delete_filter['ft_season'] = ft_season

    try:
        model.objects.filter(**delete_filter).delete()
    except Exception:
        pass


def copy_from_csv(csv_path, tables):
    """ Populate data in table with content from csv file """
    # Run "import_career_data.py"
    s1 = time.time()
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
    logging.info('Tables imported in {}s.'.format(
        round(time.time() - s1, 3)
    ))


def import_career_data(
    user_id,
    ft_slot,
    ft_season,
    fifa_edition,
    csv_path,
):
    """Import data from csv files to PostgreSQL database

        Parameters
        ----------
        csv_path : str
            Path to csv files. ex: media/<USERNAME>/data/csv
    """

    to_import = []

    for csv in SUPPORTED_TABLES:
        # example: media\<user>\data\csv\career_calendar.csv
        full_csv_path = os.path.join(csv_path, csv) + ".csv"

        if csv == "players":
            if fifa_edition == '18':
                csv = "players"
            else:
                csv = "players{}".format(fifa_edition)

        model_name = "datausers{}".format(csv.replace("_", ""))

        ct = ContentType.objects.get(model=model_name)
        model = ct.model_class()
        delete_from_model(model=model, user_id=user_id, ft_slot=ft_slot, ft_season=ft_season)

        if os.path.exists(full_csv_path):
            to_import.append(csv)

    copy_from_csv(csv_path=csv_path, tables=to_import)


def set_currency(user, currency):
    user.profile.currency = currency
    user.save()


def get_csv_val(csv_dest_path, fname, fieldname):
    fpath = os.path.join(csv_dest_path, fname)
    ret_val = None
    if not os.path.isfile(fpath):
        return None

    with open(fpath, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ret_val = row[fieldname]
            break

    return ret_val

def rest_release_clauses_to_csv(
    mm,
    username,
    user_id,
    csv_dest_path,
    rb,
):
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
        num_of_players = rb.read_int32(mm.read(4))
        if num_of_players > 25000 or num_of_players < 0:
            # invalid number of players
            offset = mm.find(sign, offset + len(sign))
            continue

        playerid = rb.read_int32(mm.read(4))
        if playerid > 400000 or playerid < 0:
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
    num_of_players = rb.read_int32(mm.read(4))
    with open(os.path.join(csv_dest_path, "career_rest_releaseclauses.csv"), 'w+', encoding='utf-8') as f_csv:
        # create columns
        headers = "username,ft_user_id,playerid,teamid,release_clause\n"
        f_csv.write(headers)

        for p in range(num_of_players):
            to_write = [
                username, user_id,
                rb.read_int32(mm.read(4)),  # playerid
                rb.read_int32(mm.read(4)),  # teamid
                rb.read_int32(mm.read(4)),  # clause
            ]

            # fix problem with invalid release clause
            # if not (1 <= clause <= 2147483646):
            if not (1 <= to_write[4] <= 2147483646):
                continue

            f_csv.write(','.join([str(x) for x in to_write]) + '\n')


def get_stats_offset(mm, compdata_end):
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
        if verify_index(mm, struct_size, 255):
            return offset

        offset = mm.find(sign, mm.tell() + 1, compdata_end)

    return -1


def verify_index(mm, struct_size, range_max):
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


def rest_players_stats_to_csv(
    mm,
    username,
    user_id,
    csv_dest_path,
    rb
):
    """Current season players statistics"""
    sign_mp002 = b"\x6D\x70\x30\x30\x32\x00"  # mp002 - MonitoredPlayers
    sign_jo002 = b"\x6A\x6F\x30\x30\x32\x00"  # jo002 - JobOffers?
    MP002_SIZE = 1616  # 0x650

    mm.seek(0)
    offset_start = mm.find(sign_mp002) + MP002_SIZE
    if offset_start < MP002_SIZE:
        # logging.error("_players_stats - mp002 not found")
        return False
    offset_end = mm.find(sign_jo002)
    if offset_end < 0:
        # logging.error("_players_stats - jo002 not found")
        return False

    stats_offset = get_stats_offset(mm, offset_end)

    if stats_offset < 0:
        # logging.error("_players_stats - stats_offset not found")
        return False

    # Save to file
    with open(os.path.join(csv_dest_path, "career_compdata_playerstats.csv"), 'w+', encoding='utf-8') as f_csv:
        # create columns
        headers = "username,ft_user_id,teamid,playerid,tournamentid,unk1,avg,app,goals,unk2,assists,unk3" \
                  ",yellowcards,redcards,unk6,unk7,cleansheets,unk9,unk10,unk11,unk12,unk13,date1,date2,date3\n"
        f_csv.write(headers)

        cur_pos = stats_offset
        mm.seek(cur_pos, 0)

        for p in range(7000):
            mm.read(3)  # index
            to_write = [
                username,
                user_id,
                rb.read_int32(mm.read(4)),  # teamid
                rb.read_int32(mm.read(4)),  # playerid
                rb.read_int16(mm.read(2)),  # tournamentid
            ]

            # If teamid == -1 and playerid == -1
            if to_write[2] == 4294967295 and to_write[3] == 4294967295:
                break

            to_write.extend([
                rb.read_int16(mm.read(2)),  # unk1
                rb.read_int16(mm.read(2)),  # avg
                rb.read_int8(mm.read(1)),  # app
                rb.read_int8(mm.read(1)),  # goals
                rb.read_int8(mm.read(1)),  # unk2
                rb.read_int8(mm.read(1)),  # assists
                rb.read_int8(mm.read(1)),  # unk3
                rb.read_int8(mm.read(1)),  # yellowcards
                rb.read_int8(mm.read(1)),  # redcards
                rb.read_int8(mm.read(1)),  # unk6
                rb.read_int8(mm.read(1)),  # unk7
                rb.read_int8(mm.read(1)),  # cleansheets
                rb.read_int8(mm.read(1)),  # unk9
                rb.read_int32(mm.read(4)),  # unk10
                rb.read_int8(mm.read(1)),  # unk11
                rb.read_int16(mm.read(2)),  # unk12
                rb.read_int8(mm.read(1)),  # unk13
                rb.read_int32(mm.read(4)),  # date1
                rb.read_int32(mm.read(4)),  # date2
                rb.read_int32(mm.read(4)),  # date3
            ])

            # if app > 1
            if to_write[7] > 1:
                # avg = int(avg / app)
                to_write[6] = to_write[6] // to_write[7]

            f_csv.write(','.join([str(x) for x in to_write]) + '\n')

# def rest_clb_neg_to_csv(mm):
#     sign_clbneg = b"\x63\x6C\x62\x6E\x65\x67\x00"    # clbneg
#     mm.seek(0)
#
#     offsets = []
#
#     offset = mm.find(sign_clbneg)
    # while offset >= 0:
    #     cur_pos = offset + len(sign_clbneg)
    #     mm.seek(cur_pos, 0)
    #     offsets.append(cur_pos)
    #     offset = mm.find(sign_clbneg)
    #
    # if len(offsets) != 4:
    #     return
    #
    # # clbneg_1 all teams transfers?
    # # clbneg_2 all teams loans?
    # # clbneg_3 my team transfers?
    # # clbneg_4 my team loans?
    # clbneg_structs = {
    #     'clbneg_1': {
    #         'playerid': 4,
    #         'offerteamid': 4,
    #         'teamid': 4,
    #         'unk1': 1,
    #         'isusertransfer': 1,
    #         'unk3': 8,
    #         'unk4': 8,
    #         'transfer_sum1': 4,
    #         'transfer_sum2': 4,
    #         'stage': 4,
    #         'unk6': 60,
    #         'unk7': 1,
    #         'unk8': 1,
    #         'isofferrejected': 1,
    #         'unk10': 1,
    #         'offer_history': {
    #             'num': 4,
    #             'size_of': 12,
    #         },
    #         'counter_offer_history': {
    #             'num': 4,
    #             'size_of': 16,
    #         },
    #     },
    #     'clbneg_2': {
    #         'playerid': 4,
    #         'offerteamid': 4,
    #         'teamid': 4,
    #         'unk1': 1,
    #         'isusertransfer': 1,
    #         'unk3': 4,
    #         'unk4': 4,
    #         'unk5': 4,
    #         'unk6': 60,
    #         'unk7': 1,
    #         'unk8': 1,
    #         'unk9': 1,
    #         'unk10': 1,
    #         'unk11': {
    #             'num': 4,
    #             'size_of': 12,
    #         },
    #         'unk12': {
    #             'num': 4,
    #             'size_of': 12,
    #         },
    #     },
    #     'clbneg_3': {
    #         'playerid': 4,
    #         'offerteamid': 4,
    #         'teamid': 4,
    #         'offer_history': {
    #             'num': 4,
    #             'size_of': 84,
    #         },
    #         'counter_offer_history': {
    #             'num': 4,
    #             'size_of': 88,
    #         },
    #         'status': {
    #             'num': 4,
    #             'size_of': 12,
    #         },
    #     },
    #     'clbneg_4': {
    #         'playerid': 4,
    #         'offerteamid': 4,
    #         'teamid': 4,
    #         'unk1': {
    #             'num': 4,
    #             'size_of': 28,
    #         },
    #         'unk2': {
    #             'num': 4,
    #             'size_of': 28,
    #         },
    #         'unk3': {
    #             'num': 4,
    #             'size_of': 12,
    #         },
    #     },
    # }
    # clbneg_data = {}
    # try:
    #     for i, off in enumerate(offsets):
    #         mm.seek(off, 0)
    #         length = self.read_int32(mm.read(4))
    #         key = 'clbneg_{}'.format(i+1)
    #         clbneg_struct = clbneg_structs[key]
    #         clbneg_data[key] = []
    #         for l in range(length):
    #             result = {}
    #             for k, v in clbneg_struct.items():
    #                 if isinstance(v, dict):
    #                     length_child = self.read_int32(mm.read(4))
    #                     child_data = {}
    #                     loops = int(v['size_of']/4)
    #                     for j in range(length_child):
    #                         child_data[j] = []
    #                         for data in range(loops):
    #                             child_data[j].append(self.read_int32(mm.read(4)))
    #                     val = child_data
    #                 elif v == 1:
    #                     val = bool(self.read_int8(mm.read(1)))
    #                 elif v == 4:
    #                     val = self.read_int32(mm.read(4))
    #                 elif v == 8:
    #                     val = self.read_int64(mm.read(8))
    #                 else:
    #                     loops = int(v/4)
    #                     child_data = []
    #                     for data in range(loops):
    #                         child_data.append(self.read_int32(mm.read(4)))
    #                     val = child_data
    #
    #                 result[k] = val
    #             clbneg_data[key].append(result)
    # except Exception as e:
    #     logging.error("_club_neg error {}".format(str(e)))
    #     return
    #
    # # Save to file
    # headers = [
    #     'username',
    #     'ft_user_id',
    #     'playerid',
    #     'teamid',
    #     'offerteamid',
    #     'stage',
    #     'iscputransfer',
    #     'isloanoffer',
    #     'isofferrejected',
    #     'offeredfee',
    # ]
    # with open(
    #     os.path.join(self.dest_path, "career_compdata_clubnegotiations.csv"), 'w+', encoding='utf-8'
    # ) as f_csv:
    #     # create columns
    #     f_csv.write("{}\n".format(','.join(headers)))
    #
    #     for i in range(4):
    #         for neg in clbneg_data['clbneg_{}'.format(i + 1)]:
    #
    #             stage = 2
    #             isofferrejected = False
    #             offeredfee = 0
    #
    #             if i == 0:
    #                 stage = neg['stage']
    #                 isofferrejected = neg['isofferrejected']
    #
    #                 offers = neg['offer_history']   # dict
    #                 counter_offers = neg['counter_offer_history']  # dict
    #                 if offers and counter_offers:
    #                     merged_offers = []
    #                     for k, v in offers.items():
    #                         merged_offers.append(v)
    #
    #                     for k, v in counter_offers.items():
    #                         merged_offers.append(v)
    #
    #                     # sort by offer date
    #                     merged_offers.sort(key=lambda d: d[1])
    #
    #                     # last offer should be our offeredfee
    #                     offeredfee = merged_offers[-1][0]
    #                 else:
    #                     continue
    #             elif i == 2:
    #                 offers = neg['offer_history']   # dict
    #                 counter_offers = neg['counter_offer_history'] # dict
    #                 if offers and counter_offers:
    #                     merged_offers = []
    #                     for k, v in offers.items():
    #                         amount = v[5]
    #                         if amount == 4294967295:
    #                             continue
    #                         merged_offers.append(amount)
    #
    #                     for k, v in counter_offers.items():
    #                         amount = v[6]
    #                         if amount == 4294967295:
    #                             continue
    #                         merged_offers.append(amount)
    #
    #                     # max offer should be our offeredfee
    #                     offeredfee = max(merged_offers)
    #                 else:
    #                     continue
    #
    #             # is cpu transfer
    #             try:
    #                 if neg['isusertransfer']:
    #                     iscputransfer = False
    #                 else:
    #                     iscputransfer = True
    #             except KeyError:
    #                 if i == 2 or i == 3:
    #                     iscputransfer = False
    #                 else:
    #                     iscputransfer = True
    #
    #             # isloanoffer
    #             if i == 1 or i == 3:
    #                 isloanoffer = True
    #             else:
    #                 isloanoffer = False
    #
    #             to_write = [
    #                 self.username,
    #                 str(self.user_id),
    #                 str(neg['playerid']),
    #                 str(neg['teamid']),
    #                 str(neg['offerteamid']),
    #                 str(stage),
    #                 str(iscputransfer),
    #                 str(isloanoffer),
    #                 str(isofferrejected),
    #                 str(offeredfee),
    #             ]
    #             f_csv.write("{}\n".format(','.join(to_write)))


def convert_rest_to_csv(
    data_path,
    user,
    csv_dest_path,
    rb,
):
    username = user.username
    user_id = str(user.id)

    rf_full_path = os.path.join(data_path, "rest")
    # Check if file exists
    if not os.path.isfile(rf_full_path):
        return

    with open(rf_full_path, 'rb') as rf:
        mm = mmap.mmap(rf.fileno(), length=0, access=mmap.ACCESS_READ)

    rest_release_clauses_to_csv(mm, username, user_id, csv_dest_path, rb)
    rest_players_stats_to_csv(mm, username, user_id, csv_dest_path, rb)


def convert_db_to_csv(
    data_path,
    user,
    meta,
    db_name,
    csv_path,
    slot,
    rb,
    season='',
    start_setupdate=0,
):
    username = user.username
    user_id = str(user.id)

    xml_table_names = meta['table_names']
    xml_field_names = meta['field_names']
    xml_field_range = meta['field_range']

    # Create csv path dir
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)

    database_full_path = os.path.join(
        data_path, db_name
    )

    if not os.path.isfile(database_full_path):
        logging.error('File not found: {}'.format(database_full_path))
        raise Exception('DB file not found.')
    with open(database_full_path, 'rb') as f:
        # FIFA Database file header
        database_header = b"\x44\x42\x00\x08\x00\x00\x00\x00"

        mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
    offset = mm.find(database_header)

    if offset == -1:
        logging.error("File header not matching")
        return  # File header not matching
    mm.seek(offset + len(database_header))
    db_size = rb.read_int32(mm.read(4))  # 0x8

    if db_size != mm.size():
        logging.error("Invalid DBSize. {} != {}".format(db_size, mm.size()))
        return  # Invalid file size

    mm.seek(4, 1)  # Skip unknown 4 bytes, 0xC
    # Num of tables in database
    count_tables = rb.read_int32(mm.read(4))  # 0x10

    # CRC32 (POLYNOMIAL = 0x04C11DB7)
    mm.seek(4, 1)

    # CrcHeader = self.ReadInt32(mm.read(4))     # CRC32, 0x14

    table_names = []
    table_offsets = []

    for x in range(count_tables):
        table_names.append(
            mm.read(4).decode("utf-8")
        )
        table_offsets.append(
            rb.read_int32(mm.read(4))
        )

    mm.seek(4, 1)
    # CrcShortNames = self.ReadInt32(mm.read(4))   # CRC32

    tables_start_offset = mm.tell()
    all_shortnames = []

    new_csv_content = {}

    s1 = time.time()

    for t in range(count_tables):
        # Skip invalid database tables (not stored in database meta)
        # Most probably user picked wrong FIFA or it's save from console
        try:
            table_name = xml_table_names[table_names[t]]
        except KeyError as e:
            logging.warning("Invalid table {}".format(e))
            continue

        # Ignore tables we don't use (faster file processing)
        if table_name not in SUPPORTED_TABLES:
            continue

        mm.seek(tables_start_offset + table_offsets[t])
        mm.seek(4, 1)  # unknown
        record_size = rb.read_int32(mm.read(4))  # Size of the record
        mm.seek(10, 1)  # Not needed atm.
        # mm.seek(4, 1)  #
        # mm.seek(4, 1)  #
        # mm.seek(2, 1)  # Total record
        num_of_valid_records = rb.read_int16(mm.read(2))  # Number of valid records
        mm.seek(4, 1)  # Unknown
        num_of_fields = rb.read_int8(mm.read(1))  # Number of fields
        mm.seek(11, 1)  # Not needed atm.
        # mm.seek(7, 1)  # Unknown
        # mm.seek(4, 1)  # CRC32

        if num_of_valid_records <= 0:
            continue

        # Temporary (not sorted)
        tmp_fieldtypes = []
        tmp_bitoffsets = []
        tmp_shortnames = []
        tmp_bitdepth = []
        str_field_index = []

        for y in range(num_of_fields):
            # Fieldtypes
            # DBOFIELDTYPE_STRING = 0
            # DBOFIELDTYPE_STRING = 13 (Compressed)
            # DBOFIELDTYPE_INTEGER = 3
            # DBOFIELDTYPE_TIME = ??
            # DBOFIELDTYPE_DATE = 3
            # DBOFIELDTYPE_REAL = 4

            fieldtype = rb.read_int32(mm.read(4))

            # not sorted
            tmp_fieldtypes.append(fieldtype)  # fieldtypes
            tmp_bitoffsets.append(rb.read_int32(mm.read(4)))  # bitoffset
            tmp_shortnames.append(mm.read(4).decode("utf-8"))  # shortname
            tmp_bitdepth.append(rb.read_int32(mm.read(4)))  # depth

            # String
            if fieldtype == 0:
                str_field_index.append(y)

        # Sort
        sorted_bit_offsets = sorted(
            range(len(tmp_bitoffsets)), key=tmp_bitoffsets.__getitem__
        )

        # CSV - table headers
        headers = ["username,ft_user_id,ft_slot"]

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
                headers.append(xml_field_names[shortnames[v]])
            except KeyError:
                # print("missing {}:{}\n".format(table_name, shortnames[v]))
                # headers += str(shortnames[v]).lower() + ","
                logging.exception()
                raise KeyError(
                    'Database contains invalid columns. Did you choose correct FIFA version?'
                )

        all_shortnames.append(shortnames)
        new_csv_content[table_name] = {
            'content': '',
        }
        new_content = [','.join(headers)]
        ident = [username, user_id, slot]
        # Read all records
        for i in range(num_of_valid_records):
            csv_line = ident.copy()
            tmp_byte = 0
            currentbitpos = 0

            cur_position = mm.tell()
            for j in range(num_of_fields):
                fieldtype = fieldtypes[j]
                if fieldtype == 0:
                    # String
                    tmp_byte = 0
                    currentbitpos = 0

                    mm.seek(cur_position + (bitoffsets[j] >> 3))
                    writevalue = rb.read_nullbyte_str(
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
                        tmp_byte = rb.read_int8(mm.read(1))
                        val += tmp_byte << startbit
                        startbit += 8

                    # Remember bit position for next iteration
                    currentbitpos = (depth + 8 - startbit & 7)
                    val &= (1 << depth) - 1

                    # Add range_low to the value
                    range_low_key = xml_table_names[table_names[t]] + xml_field_names[shortnames[j]]
                    writevalue = str(val + xml_field_range[range_low_key])
                elif fieldtype == 4:
                    # Float
                    mm.seek(cur_position + (bitoffsets[j] >> 3))
                    writevalue = str(rb.read_float(mm.read(4)))
                else:
                    # Unsupported
                    raise KeyError(
                        'Unsupported field type. {} = {}'.format(shortnames[j], fieldtype)
                    )
                csv_line.append(writevalue)
            mm.seek(cur_position + record_size)

            new_content.append(
                ','.join(csv_line)
            )

        content_as_str = '\n'.join(new_content)
        new_csv_content[table_name]['content'] = content_as_str

    mm.close()  # Close mmap
    logging.info('Tables processed in {}s.'.format(
        round(time.time() - s1, 3)
    ))

    s1 = time.time()
    # Save in CSV

    if not season:
        setupdate = int(new_csv_content['career_calendar']['content'].split('\n')[1].split(',')[len(ident) + 3][2:4])
        season = str(setupdate - start_setupdate)

    # anonymize_data
    if 'career_users' in new_csv_content:
        firstname_index = len(ident)
        surname_index = firstname_index + 1
        lines = new_csv_content['career_users']['content'].split('\n')
        for i, line in enumerate(lines[1:]):
            fields = line.split(',')
            fields[firstname_index] = fields[firstname_index][0] + ('*' * 5)    # first name
            fields[surname_index] = fields[surname_index][0] + ('*' * 5)        # surname
            lines[i+1] = ','.join(fields)
        new_csv_content['career_users']['content'] = '\n'.join(lines)

    for table_name, content in new_csv_content.items():
        # add season
        lines = content['content'].split('\n')
        lines[0] += ',ft_season'
        for i, line in enumerate(lines[1:]):
            lines[i+1] += ',{}'.format(season)

        content['content'] = '\n'.join(lines)

        with open(os.path.join(csv_path, "{}.csv".format(table_name)), 'w+', encoding='utf-8') as f_csv:
            f_csv.write(content['content'])

    logging.info('Files created in {}s.'.format(
        round(time.time() - s1, 5)
    ))
    # os.remove(database_full_path)  # Remove FIFA database file
    return season


def parse_fifa_db_xml(
    xml_file,
):
    """ Read data from meta XML file for a FIFA database. """

    meta = {
        'table_names': {},
        'field_names': {},
        'field_range': {},
        'pkeys': {},
    }

    tree = ET.parse(xml_file)
    root = tree.getroot()

    for child in root:
        try:
            for node in child.getiterator():
                try:
                    meta['table_names'][node.attrib['shortname']] = node.attrib['name']
                    for a in node.getiterator():
                        if a.tag == 'field':
                            meta['field_names'][a.attrib['shortname']] = a.attrib['name']
                            if a.attrib['type'] == "DBOFIELDTYPE_INTEGER":
                                meta['field_range'][node.attrib['name'] + a.attrib['name']] = \
                                    int(a.attrib['rangelow'])
                            else:
                                meta['field_range'][node.attrib['name'] + a.attrib['name']] = 0

                            if 'key' in a.attrib:
                                if a.attrib['key'] == "True":
                                    meta['pkeys'][node.attrib['name']] = a.attrib['name']
                except ValueError:
                    continue
        except (KeyError, IndexError):
            pass

    return meta

def remove_savefile(career_file_fullpath):
    try:
        if os.path.exists(career_file_fullpath):
            os.remove(career_file_fullpath)
            return True
    except PermissionError:
        logging.exception('PermissionError - remove_savefile')
    except TypeError:
        pass

    return False


def unpack_all_dbs(
    career_file_fullpath,
    data_path,
    fifa_edition,
    rb,
):
    # Recognize FIFA Edition basing on file size
    fifa_signatures = {
        b'\x6E\x40\x72\x00': '17',
        b'\x63\x7D\xA9\x00': '18',
        b'\x17\x5E\xC6\x00': '19',
    }
    unpacked_dbs = 0

    with open(career_file_fullpath, 'rb') as f:
        mm = mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)

    # FIFA Database file signature
    database_header = b"\x44\x42\x00\x08\x00\x00\x00\x00"
    offset = mm.find(database_header)

    # Signature not found
    if offset < 0:
        return 0

    cur_pos = mm.tell()  # Save cursor position
    mm.seek(14)  # 0xE - FILE SIZE
    fifa_sign = mm.read(4)  # Read sign (0x4 bytes)

    if not fifa_edition:
        try:
            fifa_edition = fifa_signatures[fifa_sign]
        except KeyError:
            logging.warning("Unknown fifa_sign: {}".format(fifa_sign))
            fifa_edition = str(DEFAULT_FIFA_EDITION)

    # Restore cursor position
    mm.seek(cur_pos)

    # Data before databases section
    with open(os.path.join(data_path, "data_before_db"), "wb") as data_before_db:
        data_before_db.write(mm[:offset])

    # Databases section
    while offset >= 0:
        cur_pos = offset + len(database_header)
        mm.seek(cur_pos, 0)
        dbSize = rb.read_int32(mm.read(4))
        end_of_data = offset + dbSize

        # Create .db file
        with open(os.path.join(data_path, "{}.db".format(unpacked_dbs + 1)), "wb") as database_file:
            # Write data to .db file
            database_file.write(mm[offset:end_of_data])

        offset = mm.find(database_header, end_of_data)
        unpacked_dbs += 1

        # Data after databases section
        with open(os.path.join(data_path, "rest"), "wb") as rest:
            rest.write(mm[end_of_data:])

    return unpacked_dbs


def update_savefile_model(cs_model, code, msg):
    logging.info(msg)
    cs_model.file_process_status_code = code
    cs_model.file_process_status_msg = msg
    cs_model.save()


def get_basic_cm_save_info(
    career_file_fullpath
):
    with open(career_file_fullpath, 'rb') as rf:
        mm = mmap.mmap(rf.fileno(), length=0, access=mmap.ACCESS_READ)

    result = {}

    rb = ReadBytesHelper()
    mm.seek(0x12)
    result['save_original_name'] = rb.read_nullbyte_str(mm, 96)

    mm.seek(0x92)
    result['teamid'] = rb.read_int32(mm.read(4))
    result['last_game_home_teamid'] = rb.read_int32(mm.read(4))
    result['last_game_away_teamid'] = rb.read_int32(mm.read(4))
    result['ing_date'] = rb.read_int32(mm.read(4), as_string=True)
    result['last_game_home_score'] = rb.read_int32(mm.read(4))
    result['last_game_away_score'] = rb.read_int32(mm.read(4))
    result['next_game_vs_teamid'] = rb.read_int32(mm.read(4))
    result['unk1'] = rb.read_int32(mm.read(4))
    result['unk2'] = rb.read_int32(mm.read(4))
    result['unk3'] = rb.read_int32(mm.read(4))
    result['save_type'] = rb.read_int32(mm.read(4))

    return result


def parse_career_save(
    career_file_fullpath,
    data_path,
    user,
    slot,
    xml_file=None,
    fifa_edition=None,
    cs_model=None
):
    """Parse FIFA Career Save.
        Parameters
        ----------
        career_file_fullpath : str
            Full path to save file. media/<USERNAME>/CareerData

        data_path : str
            Path where data will be unpacked and stored. (csv files)

        user : obj
            Django User model object.

        slot : str
            Career Slot number

        xml_file : str
            Full path to "fifa_ng_db-meta.xml" file

        fifa_edition : str
            Which FIFA.

        cs_model : obj
            CareerSaveFileModel
    """

    # Count time spent on processing save
    reset_queries()
    start = time.time()
    logging.info(
        "{}: Process Career Save Started, slot: {}".format(user.username, slot)
    )

    if cs_model.is_update:
        fifa_edition = user.profile.slots_data[slot]['fifa_edition']

    if fifa_edition and (not isinstance(fifa_edition, str)):
        fifa_edition = str(fifa_edition)

    # Create Data Path
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # Make copy of career save file
    f_backup = os.path.join(data_path, "savefile")
    if os.path.exists(f_backup):
        os.remove(f_backup)

    shutil.copy2(career_file_fullpath, f_backup)

    # Unpack databases from career file.
    update_savefile_model(
        cs_model=cs_model, code=0, msg=_("Unpacking database from career file.")
    )

    read_b = ReadBytesHelper()
    # Num of unpacked DB files
    unpacked_dbs = unpack_all_dbs(
        career_file_fullpath,
        data_path,
        fifa_edition,
        rb=read_b,
    )

    if unpacked_dbs == 0:
        remove_savefile(career_file_fullpath)
        raise ValueError("No .db files in career save.")
    elif unpacked_dbs > 3:
        remove_savefile(career_file_fullpath)
        raise ValueError("Too many .db files")

    if not xml_file:
        # Path to meta XML file for a FIFA database.
        xml_file = os.path.join(
            settings.BASE_DIR, "scripts", "Data", fifa_edition, "XML", "fifa_ng_db-meta.xml"
        )

    csv_dest_path = os.path.join(data_path, "csv")
    if os.path.exists(csv_dest_path):
        shutil.rmtree(csv_dest_path)

    # Parse XML
    meta = parse_fifa_db_xml(xml_file)

    # Export data from FIFA database to csv files.
    update_savefile_model(
        cs_model=cs_model, code=0, msg=_("Exporting data from FIFA database to csv files.")
    )

    s1 = time.time()
    season = -1
    try:
        # Only:
        # 1.db - carrer_*
        # 2.db
        # self.unpacked_dbs + 1 for all DBS
        season = convert_db_to_csv(
            data_path=data_path,
            user=user,
            meta=meta,
            db_name="1.db",
            csv_path=csv_dest_path,
            slot=slot,
            rb=read_b,
            start_setupdate=int(fifa_edition) - 2,
        )

        for db in range(2, unpacked_dbs):
            convert_db_to_csv(
                data_path=data_path,
                user=user,
                meta=meta,
                db_name="{}.db".format(db),
                csv_path=csv_dest_path,
                slot=slot,
                rb=read_b,
                season=season,
            )

    except Exception as e:
        logging.exception('Traceback')
        raise Exception(e)

    logging.info(
        '{},{}: DB to CSV in {}s.'.format(
            user.username, slot,
            round(time.time() - s1, 3)
        )
    )

    s1 = time.time()
    # Convert rest of the data to csv file format.
    convert_rest_to_csv(
        data_path=data_path,
        user=user,
        csv_dest_path=csv_dest_path,
        rb=read_b,
    )
    logging.info('{},{}: Rest to CSV in {}s.'.format(
        user.username, slot,
        round(time.time() - s1, 3)
    ))

    # Set current date
    currdate = get_csv_val(csv_dest_path, "career_calendar.csv", "currdate") or DEFAULT_DATE[fifa_edition]

    # Set Default Currency
    currency = get_csv_val(csv_dest_path, "career_managerpref.csv", "currency") or 1    # or Euro
    set_currency(
        user,
        currency
    )

    # Calculate Values of all players and save it in "players.csv"
    update_savefile_model(
        cs_model=cs_model, code=0, msg=_("Calculating Players Values and Teams Ratings")
    )

    s1 = time.time()
    CalculateValues(
        currency=currency, currdate=currdate, csv_dest_path=csv_dest_path,
        fifa_edition=fifa_edition
    )
    logging.info('{},{}: CalculateValues in {}s.'.format(
        user.username, slot,
        round(time.time() - s1, 3)
    ))

    # Import data from csv to our PostgreSQL database
    update_savefile_model(
        cs_model=cs_model, code=0, msg=_("Importing data to FIFA Tracker database.")
    )

    season_to_delete = -1
    if cs_model.is_update:
        season_to_delete = int(season)

    user_id = str(user.id)
    import_career_data(
        user_id=user_id,
        ft_slot=slot,
        ft_season=season_to_delete,
        fifa_edition=fifa_edition,
        csv_path=csv_dest_path
    )

    # Delete Files on production
    if not settings.DEBUG:
        if os.path.exists(data_path):
            shutil.rmtree(data_path)

        if os.path.isfile(career_file_fullpath):
            os.remove(career_file_fullpath)

    logging.info('{},{}: Rest to CSV in {}s.'.format(
        user.username, slot,
        round(time.time() - s1, 3)
    ))

    logging.info('{},{}: Completed in {}s'.format(
        user.username, slot,
        round(time.time() - start, 3)
    ))

    slots_data = user.profile.slots_data
    slots_data[slot] = {
        'last_season': season,
        'fifa_edition': fifa_edition,
    }
    user.profile.slots_data = slots_data
    user.save()

    try:
        cs_model.delete()
    except AttributeError:
        pass
    except Exception:
        logging.exception('cs_model.delete()')
