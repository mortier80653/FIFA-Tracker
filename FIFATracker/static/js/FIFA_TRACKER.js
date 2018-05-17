$(document).ready(function(){
  selectizejs();
  resizeableTables();
  updatePositions();
  updateInGameRatings();
  updateStrongFoot();
  updateWorkrates();
  changeCurrency();
  changeUnits();
  convertUnits();
  changeProfilePublicStatus();
  cleanUrl();
  careerFileUpload();
  ToolsCalculator();
});

function ToolsCalculator() {

    // Calculate Player Potential
    $('#btn-calc-pot').on("click", function() {
        let currency = $("#calcpot-currency").val();

        let playerValue = $("#calcpot-val").val().replace(/\D/g,'');
        if (playerValue == null || playerValue=='') {
            alert("Player value input cannot be empty and must contain digits.");
            return;
        }

        let positionid = $("#calcpot-position").val();

        let age = $("#calcpot-age").val();
        if (age == null || age=='') {
            alert("Age input cannot be empty.");
            return;
        }

        let ovr = $("#calcpot-ovr").val();
        if (ovr == null || ovr=='') {
            alert("Overall rating input cannot be empty.");
            return;
        }

        $("#calcpot-result").text("Calculating...");

        $.ajax({
            url: '/tools/calculator/ajax/calc-pot/',
            data: {
                "currency": currency,
                "player_value": playerValue,
                "positionid": positionid,
                "age": age,
                "ovr": ovr,
            },
            dataType: 'json',
            success: function (data) {
                alert(data.result);
                $("#calcpot-result").text(data.result);
            }
        });
    });


    // Calculate Player Wage
    $('#btn-calc-wage').on("click", function() {
        let currency = $("#calcwage-currency").val();

        let leagueid = $("#leagues-input").val();

        let teamid = $("#teams-input").val();
        if (teamid == null || teamid=='') {
            alert("Please, select team.");
            return;
        }

        let positionid = $("#calcwage-position").val();

        let age = $("#calcwage-age").val();
        if (age == null || age=='') {
            alert("Age input cannot be empty.");
            return;
        }

        let ovr = $("#calcwage-ovr").val();
        if (ovr == null || ovr=='') {
            alert("Overall rating input cannot be empty.");
            return;
        }

        $("#calcwage-result").text("Calculating...");

        $.ajax({
            url: '/tools/calculator/ajax/calc-wage/',
            data: {
                "currency": currency,
                "leagueid": leagueid,
                "teamid": teamid,
                "positionid": positionid,
                "age": age,
                "ovr": ovr,
            },
            dataType: 'json',
            success: function (data) {
                alert(data.result);
                $("#calcwage-result").text(data.result);
            }
        });
    });

}

function resizeableTables() {
    $("table").colResizable();
};

function updateInGameRatings() {
    let attr_tbl = $('.attrib-table tr'); 

    // Return if table not found
    if (attr_tbl.length == 0) { return;}

    let attr_val = [];

    attr_tbl.each(function() {
        attr_val.push($(this).find("td:eq(1) > span").text());
    });

    let positions = [
        { position: 'GK', 	posid: '0'},
        { position: 'SW', 	posid: '1'},
        { position: 'RWB', 	posid: '2'},
        { position: 'RB', 	posid: '3'},
        { position: 'RCB', 	posid: '4'},
        { position: 'CB', 	posid: '5'},
        { position: 'LCB', 	posid: '6'},
        { position: 'LB', 	posid: '7'},
        { position: 'LWB', 	posid: '8'},
        { position: 'RDM', 	posid: '9'},
        { position: 'CDM', 	posid: '10'},
        { position: 'LDM', 	posid: '11'},
        { position: 'RM', 	posid: '12'},
        { position: 'RCM', 	posid: '13'},
        { position: 'CM', 	posid: '14'},
        { position: 'LCM', 	posid: '15'},
        { position: 'LM', 	posid: '16'},
        { position: 'RAM', 	posid: '17'},
        { position: 'CAM', 	posid: '18'},
        { position: 'LAM', 	posid: '19'},
        { position: 'RF', 	posid: '20'},
        { position: 'CF', 	posid: '21'},
        { position: 'LF', 	posid: '22'},
        { position: 'RW', 	posid: '23'},
        { position: 'RS', 	posid: '24'},
        { position: 'ST', 	posid: '25'},
        { position: 'LS', 	posid: '26'},
        { position: 'LW', 	posid: '27'},
    ];

    for (var i = 0; i < positions.length; i++) {
        // Skip SW position
        if (i === 1) { continue; }

        // Calculate OVR for position id
        posid = positions[i].posid;
        igr = calculateInGameRating(parseInt(posid), attr_val);

        // Fill pitch for lg and md screen
        let div_igr = $('#pitch-igr-' + i);
        div_igr.addClass('rat' + igr);

        let pos_name = div_igr.find('div:eq(0) > span');
        pos_name.text(positions[i].position);

        let pos_ovr = div_igr.find('div:eq(1) > span');
        pos_ovr.text(igr);
        
        // Fill Table for sm and xs screen
        $('.ingameratings-table').append('<tr><td>' + positions[i].position + '</td><td align="right"><span class="ratinglabel rat' + igr + '">' + igr +'</span></td></tr>');
    };
};

function calculateInGameRating(posid, attr_val) {
    let ovr = [];
    switch (posid) {
        case 0:
            // GK (id = 0)
            ovr.push(parseFloat(attr_val[26] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 11%
            ovr.push(parseFloat(attr_val[0] * 0.21).toFixed(2));			// PLAYER_ATTRIBUTE_GK_DIVING * 21%
            ovr.push(parseFloat(attr_val[1] * 0.21).toFixed(2));			// PLAYER_ATTRIBUTE_GK_HANDLING * 21%
            ovr.push(parseFloat(attr_val[2] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_GK_KICKING * 5%
            ovr.push(parseFloat(attr_val[4] * 0.21).toFixed(2));			// PLAYER_ATTRIBUTE_GK_REFLEXES * 21%
            ovr.push(parseFloat(attr_val[3] * 0.21).toFixed(2));			// PLAYER_ATTRIBUTE_GK_POSITIONING * 21%
            break;
        case 1:
            // Don't calculate rating for 'SW' position.
            ovr = 0
            break;
        case 2:
            // RWB (id = 2)
            ovr.push(parseFloat(attr_val[23] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.push(parseFloat(attr_val[24] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 6%
            ovr.push(parseFloat(attr_val[20] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 10%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[30] * 0.12).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 12%
            ovr.push(parseFloat(attr_val[17] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 8%
            ovr.push(parseFloat(attr_val[5] * 0.12).toFixed(2));			// PLAYER_ATTRIBUTE_CROSSING * 12%
            ovr.push(parseFloat(attr_val[13] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 4%
            ovr.push(parseFloat(attr_val[8] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 10%
            ovr.push(parseFloat(attr_val[10] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 7%
            ovr.push(parseFloat(attr_val[11] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 8%
            ovr.push(parseFloat(attr_val[12] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 11%
            break;
        case 3:
        	// RB (id = 3)
            ovr.push(parseFloat(attr_val[23] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 5%
            ovr.push(parseFloat(attr_val[24] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 7%
            ovr.push(parseFloat(attr_val[20] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 8%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[30] * 0.12).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 12%
            ovr.push(parseFloat(attr_val[17] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 7%
            ovr.push(parseFloat(attr_val[5] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_CROSSING * 9%
            ovr.push(parseFloat(attr_val[7] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 4%
            ovr.push(parseFloat(attr_val[8] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 7%
            ovr.push(parseFloat(attr_val[10] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 8%
            ovr.push(parseFloat(attr_val[11] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 11%
            ovr.push(parseFloat(attr_val[12] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 14%
            break;
        case 4:
    		// RCB (id = 4)
            ovr.push(parseFloat(attr_val[24] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 2%
            ovr.push(parseFloat(attr_val[19] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_JUMPING * 3%
            ovr.push(parseFloat(attr_val[21] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_STRENGTH * 10%
            ovr.push(parseFloat(attr_val[26] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 5%
            ovr.push(parseFloat(attr_val[28] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_AGGRESSION * 7%
            ovr.push(parseFloat(attr_val[30] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 13%
            ovr.push(parseFloat(attr_val[17] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 4%
            ovr.push(parseFloat(attr_val[7] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 10%
            ovr.push(parseFloat(attr_val[8] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 5%
            ovr.push(parseFloat(attr_val[10] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 14%
            ovr.push(parseFloat(attr_val[11] * 0.17).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 17%
            ovr.push(parseFloat(attr_val[12] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 10%
            break;
        case 5:
			// CB (id = 5)
            ovr.push(parseFloat(attr_val[24] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 2%
            ovr.push(parseFloat(attr_val[19] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_JUMPING * 3%
            ovr.push(parseFloat(attr_val[21] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_STRENGTH * 10%
            ovr.push(parseFloat(attr_val[26] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 5%
            ovr.push(parseFloat(attr_val[28] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_AGGRESSION * 7%
            ovr.push(parseFloat(attr_val[30] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 13%
            ovr.push(parseFloat(attr_val[17] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 4%
            ovr.push(parseFloat(attr_val[7] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 10%
            ovr.push(parseFloat(attr_val[8] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 5%
            ovr.push(parseFloat(attr_val[10] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 14%
            ovr.push(parseFloat(attr_val[11] * 0.17).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 17%
            ovr.push(parseFloat(attr_val[12] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 10%
            break;
        case 6:
        	// LCB (id = 6)
            ovr.push(parseFloat(attr_val[24] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 2%
            ovr.push(parseFloat(attr_val[19] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_JUMPING * 3%
            ovr.push(parseFloat(attr_val[21] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_STRENGTH * 10%
            ovr.push(parseFloat(attr_val[26] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 5%
            ovr.push(parseFloat(attr_val[28] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_AGGRESSION * 7%
            ovr.push(parseFloat(attr_val[30] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 13%
            ovr.push(parseFloat(attr_val[17] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 4%
            ovr.push(parseFloat(attr_val[7] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 10%
            ovr.push(parseFloat(attr_val[8] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 5%
            ovr.push(parseFloat(attr_val[10] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 14%
            ovr.push(parseFloat(attr_val[11] * 0.17).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 17%
            ovr.push(parseFloat(attr_val[12] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 10%
            break;
        case 7:
        	// LB (id = 7)
            ovr.push(parseFloat(attr_val[23] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 5%
            ovr.push(parseFloat(attr_val[24] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 7%
            ovr.push(parseFloat(attr_val[20] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 8%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[30] * 0.12).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 12%
            ovr.push(parseFloat(attr_val[17] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 7%
            ovr.push(parseFloat(attr_val[5] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_CROSSING * 9%
            ovr.push(parseFloat(attr_val[7] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 4%
            ovr.push(parseFloat(attr_val[8] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 7%
            ovr.push(parseFloat(attr_val[10] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 8%
            ovr.push(parseFloat(attr_val[11] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 11%
            ovr.push(parseFloat(attr_val[12] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 14%
            break;
        case 8:
    		// LWB (id = 8)
            ovr.push(parseFloat(attr_val[23] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.push(parseFloat(attr_val[24] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 6%
            ovr.push(parseFloat(attr_val[20] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 10%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[30] * 0.12).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 12%
            ovr.push(parseFloat(attr_val[17] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 8%
            ovr.push(parseFloat(attr_val[5] * 0.12).toFixed(2));			// PLAYER_ATTRIBUTE_CROSSING * 12%
            ovr.push(parseFloat(attr_val[13] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 4%
            ovr.push(parseFloat(attr_val[8] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 10%
            ovr.push(parseFloat(attr_val[10] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 7%
            ovr.push(parseFloat(attr_val[11] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 8%
            ovr.push(parseFloat(attr_val[12] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 11%
            break;
        case 9:
			// RDM (id = 9)
            ovr.push(parseFloat(attr_val[20] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 6%
            ovr.push(parseFloat(attr_val[21] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_STRENGTH * 4%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[28] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_AGGRESSION * 5%
            ovr.push(parseFloat(attr_val[30] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 14%
            ovr.push(parseFloat(attr_val[32] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 4%
            ovr.push(parseFloat(attr_val[17] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 10%
            ovr.push(parseFloat(attr_val[16] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 10%
            ovr.push(parseFloat(attr_val[8] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 14%
            ovr.push(parseFloat(attr_val[10] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 9%
            ovr.push(parseFloat(attr_val[11] * 0.12).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 12%
            ovr.push(parseFloat(attr_val[12] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 5%
            break;
        case 10:
   			// CDM (id = 10)
            ovr.push(parseFloat(attr_val[20] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 6%
            ovr.push(parseFloat(attr_val[21] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_STRENGTH * 4%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[28] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_AGGRESSION * 5%
            ovr.push(parseFloat(attr_val[30] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 14%
            ovr.push(parseFloat(attr_val[32] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 4%
            ovr.push(parseFloat(attr_val[17] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 10%
            ovr.push(parseFloat(attr_val[16] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 10%
            ovr.push(parseFloat(attr_val[8] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 14%
            ovr.push(parseFloat(attr_val[10] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 9%
            ovr.push(parseFloat(attr_val[11] * 0.12).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 12%
            ovr.push(parseFloat(attr_val[12] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 5%
            break;
        case 11:
 			// LDM (id = 11)
            ovr.push(parseFloat(attr_val[20] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 6%
            ovr.push(parseFloat(attr_val[21] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_STRENGTH * 4%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[28] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_AGGRESSION * 5%
            ovr.push(parseFloat(attr_val[30] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 14%
            ovr.push(parseFloat(attr_val[32] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 4%
            ovr.push(parseFloat(attr_val[17] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 10%
            ovr.push(parseFloat(attr_val[16] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 10%
            ovr.push(parseFloat(attr_val[8] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 14%
            ovr.push(parseFloat(attr_val[10] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_MARKING * 9%
            ovr.push(parseFloat(attr_val[11] * 0.12).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 12%
            ovr.push(parseFloat(attr_val[12] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SLIDING_TACKLE * 5%
            break;
        case 12:
    		// RM (id = 12)
            ovr.push(parseFloat(attr_val[23] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 7%
            ovr.push(parseFloat(attr_val[24] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 6%
            ovr.push(parseFloat(attr_val[20] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 5%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[31] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 8%
            ovr.push(parseFloat(attr_val[32] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 7%
            ovr.push(parseFloat(attr_val[17] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 13%
            ovr.push(parseFloat(attr_val[5] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_CROSSING * 10%
            ovr.push(parseFloat(attr_val[13] * 0.15).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 15%
            ovr.push(parseFloat(attr_val[6] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 6%
            ovr.push(parseFloat(attr_val[16] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 5%
            ovr.push(parseFloat(attr_val[8] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 11%
            break;
        case 13:
        	// RCM (id = 13)
            ovr.push(parseFloat(attr_val[20] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 6%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[30] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 5%
            ovr.push(parseFloat(attr_val[31] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 6%
            ovr.push(parseFloat(attr_val[32] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 13%
            ovr.push(parseFloat(attr_val[17] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 14%
            ovr.push(parseFloat(attr_val[13] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 7%
            ovr.push(parseFloat(attr_val[6] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 2%
            ovr.push(parseFloat(attr_val[16] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 13%
            ovr.push(parseFloat(attr_val[8] * 0.17).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 17%
            ovr.push(parseFloat(attr_val[22] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            ovr.push(parseFloat(attr_val[11] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 5%
            break;
        case 14:
        	// CM (id = 14)
            ovr.push(parseFloat(attr_val[20] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 6%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[30] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 5%
            ovr.push(parseFloat(attr_val[31] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 6%
            ovr.push(parseFloat(attr_val[32] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 13%
            ovr.push(parseFloat(attr_val[17] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 14%
            ovr.push(parseFloat(attr_val[13] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 7%
            ovr.push(parseFloat(attr_val[6] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 2%
            ovr.push(parseFloat(attr_val[16] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 13%
            ovr.push(parseFloat(attr_val[8] * 0.17).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 17%
            ovr.push(parseFloat(attr_val[22] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            ovr.push(parseFloat(attr_val[11] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 5%
            break;
        case 15:
            // LCM (id = 15)
            ovr.push(parseFloat(attr_val[20] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 6%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[30] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_INTERCEPTIONS * 5%
            ovr.push(parseFloat(attr_val[31] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 6%
            ovr.push(parseFloat(attr_val[32] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 13%
            ovr.push(parseFloat(attr_val[17] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 14%
            ovr.push(parseFloat(attr_val[13] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 7%
            ovr.push(parseFloat(attr_val[6] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 2%
            ovr.push(parseFloat(attr_val[16] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 13%
            ovr.push(parseFloat(attr_val[8] * 0.17).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 17%
            ovr.push(parseFloat(attr_val[22] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            ovr.push(parseFloat(attr_val[11] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_STANDING_TACKLE * 5%
            break;
        case 16:
        	// LM (id = 16)
            ovr.push(parseFloat(attr_val[23] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 7%
            ovr.push(parseFloat(attr_val[24] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 6%
            ovr.push(parseFloat(attr_val[20] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_STAMINA * 5%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[31] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 8%
            ovr.push(parseFloat(attr_val[32] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 7%
            ovr.push(parseFloat(attr_val[17] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 13%
            ovr.push(parseFloat(attr_val[5] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_CROSSING * 10%
            ovr.push(parseFloat(attr_val[13] * 0.15).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 15%
            ovr.push(parseFloat(attr_val[6] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 6%
            ovr.push(parseFloat(attr_val[16] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 5%
            ovr.push(parseFloat(attr_val[8] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 11%
            break;
        case 17:
        	// RAM (id = 17)
            ovr.push(parseFloat(attr_val[23] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.push(parseFloat(attr_val[24] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 3%
            ovr.push(parseFloat(attr_val[25] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_AGILITY * 3%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[31] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 9%
            ovr.push(parseFloat(attr_val[32] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 14%
            ovr.push(parseFloat(attr_val[17] * 0.15).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 15%
            ovr.push(parseFloat(attr_val[13] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 13%
            ovr.push(parseFloat(attr_val[6] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 7%
            ovr.push(parseFloat(attr_val[16] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 4%
            ovr.push(parseFloat(attr_val[8] * 0.16).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 16%
            ovr.push(parseFloat(attr_val[22] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 5%
            break;
        case 18:
        	// CAM (id = 18)
            ovr.push(parseFloat(attr_val[23] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.push(parseFloat(attr_val[24] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 3%
            ovr.push(parseFloat(attr_val[25] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_AGILITY * 3%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[31] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 9%
            ovr.push(parseFloat(attr_val[32] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 14%
            ovr.push(parseFloat(attr_val[17] * 0.15).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 15%
            ovr.push(parseFloat(attr_val[13] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 13%
            ovr.push(parseFloat(attr_val[6] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 7%
            ovr.push(parseFloat(attr_val[16] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 4%
            ovr.push(parseFloat(attr_val[8] * 0.16).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 16%
            ovr.push(parseFloat(attr_val[22] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 5%
            break;
        case 19:
        	// LAM (id = 19)
            ovr.push(parseFloat(attr_val[23] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.push(parseFloat(attr_val[24] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 3%
            ovr.push(parseFloat(attr_val[25] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_AGILITY * 3%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[31] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 9%
            ovr.push(parseFloat(attr_val[32] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 14%
            ovr.push(parseFloat(attr_val[17] * 0.15).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 15%
            ovr.push(parseFloat(attr_val[13] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 13%
            ovr.push(parseFloat(attr_val[6] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 7%
            ovr.push(parseFloat(attr_val[16] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_LONG_PASSING * 4%
            ovr.push(parseFloat(attr_val[8] * 0.16).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 16%
            ovr.push(parseFloat(attr_val[22] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 5%
            break;
        case 20:
        	// RF (id = 20)
            ovr.push(parseFloat(attr_val[23] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 5%
            ovr.push(parseFloat(attr_val[24] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 5%
            ovr.push(parseFloat(attr_val[26] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 9%
            ovr.push(parseFloat(attr_val[31] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 13%
            ovr.push(parseFloat(attr_val[32] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 8%
            ovr.push(parseFloat(attr_val[17] * 0.15).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 15%
            ovr.push(parseFloat(attr_val[13] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 14%
            ovr.push(parseFloat(attr_val[6] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 11%
            ovr.push(parseFloat(attr_val[7] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 2%
            ovr.push(parseFloat(attr_val[8] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 9%
            ovr.push(parseFloat(attr_val[18] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SHOT_POWER * 5%
            ovr.push(parseFloat(attr_val[22] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            break;
        case 21:
        	// CF (id = 21)
            ovr.push(parseFloat(attr_val[23] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 5%
            ovr.push(parseFloat(attr_val[24] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 5%
            ovr.push(parseFloat(attr_val[26] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 9%
            ovr.push(parseFloat(attr_val[31] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 13%
            ovr.push(parseFloat(attr_val[32] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 8%
            ovr.push(parseFloat(attr_val[17] * 0.15).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 15%
            ovr.push(parseFloat(attr_val[13] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 14%
            ovr.push(parseFloat(attr_val[6] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 11%
            ovr.push(parseFloat(attr_val[7] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 2%
            ovr.push(parseFloat(attr_val[8] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 9%
            ovr.push(parseFloat(attr_val[18] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SHOT_POWER * 5%
            ovr.push(parseFloat(attr_val[22] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            break;
        case 22:
        	// LF (id = 22)
            ovr.push(parseFloat(attr_val[23] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 5%
            ovr.push(parseFloat(attr_val[24] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 5%
            ovr.push(parseFloat(attr_val[26] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 9%
            ovr.push(parseFloat(attr_val[31] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 13%
            ovr.push(parseFloat(attr_val[32] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 8%
            ovr.push(parseFloat(attr_val[17] * 0.15).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 15%
            ovr.push(parseFloat(attr_val[13] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 14%
            ovr.push(parseFloat(attr_val[6] * 0.11).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 11%
            ovr.push(parseFloat(attr_val[7] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 2%
            ovr.push(parseFloat(attr_val[8] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 9%
            ovr.push(parseFloat(attr_val[18] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SHOT_POWER * 5%
            ovr.push(parseFloat(attr_val[22] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            break;
        case 23:
        	// RW (id = 23)
            ovr.push(parseFloat(attr_val[23] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 7%
            ovr.push(parseFloat(attr_val[24] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 6%
            ovr.push(parseFloat(attr_val[25] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_AGILITY * 3%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[31] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 9%
            ovr.push(parseFloat(attr_val[32] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 6%
            ovr.push(parseFloat(attr_val[17] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 14%
            ovr.push(parseFloat(attr_val[5] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_CROSSING * 9%
            ovr.push(parseFloat(attr_val[13] * 0.16).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 16%
            ovr.push(parseFloat(attr_val[6] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 10%
            ovr.push(parseFloat(attr_val[8] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 9%
            ovr.push(parseFloat(attr_val[22] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            break;
        case 24:
        	// RS (id = 24)
            ovr.push(parseFloat(attr_val[23] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.push(parseFloat(attr_val[24] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 5%
            ovr.push(parseFloat(attr_val[21] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_STRENGTH * 5%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[31] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 13%
            ovr.push(parseFloat(attr_val[17] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 10%
            ovr.push(parseFloat(attr_val[13] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 7%
            ovr.push(parseFloat(attr_val[6] * 0.18).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 18%
            ovr.push(parseFloat(attr_val[7] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 10%
            ovr.push(parseFloat(attr_val[8] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 5%
            ovr.push(parseFloat(attr_val[18] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_SHOT_POWER * 10%
            ovr.push(parseFloat(attr_val[22] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 3%
            ovr.push(parseFloat(attr_val[9] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_VOLLEYS * 2%
            break;
        case 25:
        	// ST (id = 25)
            ovr.push(parseFloat(attr_val[23] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.push(parseFloat(attr_val[24] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 5%
            ovr.push(parseFloat(attr_val[21] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_STRENGTH * 5%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[31] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 13%
            ovr.push(parseFloat(attr_val[17] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 10%
            ovr.push(parseFloat(attr_val[13] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 7%
            ovr.push(parseFloat(attr_val[6] * 0.18).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 18%
            ovr.push(parseFloat(attr_val[7] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 10%
            ovr.push(parseFloat(attr_val[8] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 5%
            ovr.push(parseFloat(attr_val[18] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_SHOT_POWER * 10%
            ovr.push(parseFloat(attr_val[22] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 3%
            ovr.push(parseFloat(attr_val[9] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_VOLLEYS * 2%
            break;
        case 26:
        	// LS (id = 26)
            ovr.push(parseFloat(attr_val[23] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 4%
            ovr.push(parseFloat(attr_val[24] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 5%
            ovr.push(parseFloat(attr_val[21] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_STRENGTH * 5%
            ovr.push(parseFloat(attr_val[26] * 0.08).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 8%
            ovr.push(parseFloat(attr_val[31] * 0.13).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 13%
            ovr.push(parseFloat(attr_val[17] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 10%
            ovr.push(parseFloat(attr_val[13] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 7%
            ovr.push(parseFloat(attr_val[6] * 0.18).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 18%
            ovr.push(parseFloat(attr_val[7] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_HEADING_ACCURACY * 10%
            ovr.push(parseFloat(attr_val[8] * 0.05).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 5%
            ovr.push(parseFloat(attr_val[18] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_SHOT_POWER * 10%
            ovr.push(parseFloat(attr_val[22] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 3%
            ovr.push(parseFloat(attr_val[9] * 0.02).toFixed(2));			// PLAYER_ATTRIBUTE_VOLLEYS * 2%
            break;
        case 27:
        	// LW (id = 27)
            ovr.push(parseFloat(attr_val[23] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_ACCELERATION * 7%
            ovr.push(parseFloat(attr_val[24] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_SPRINT_SPEED * 6%
            ovr.push(parseFloat(attr_val[25] * 0.03).toFixed(2));			// PLAYER_ATTRIBUTE_AGILITY * 3%
            ovr.push(parseFloat(attr_val[26] * 0.07).toFixed(2));			// PLAYER_ATTRIBUTE_REACTIONS * 7%
            ovr.push(parseFloat(attr_val[31] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_POSITIONING * 9%
            ovr.push(parseFloat(attr_val[32] * 0.06).toFixed(2));			// PLAYER_ATTRIBUTE_VISION * 6%
            ovr.push(parseFloat(attr_val[17] * 0.14).toFixed(2));			// PLAYER_ATTRIBUTE_BALL_CONTROL * 14%
            ovr.push(parseFloat(attr_val[5] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_CROSSING * 9%
            ovr.push(parseFloat(attr_val[13] * 0.16).toFixed(2));			// PLAYER_ATTRIBUTE_DRIBBLING * 16%
            ovr.push(parseFloat(attr_val[6] * 0.10).toFixed(2));			// PLAYER_ATTRIBUTE_FINISHING * 10%
            ovr.push(parseFloat(attr_val[8] * 0.09).toFixed(2));			// PLAYER_ATTRIBUTE_SHORT_PASSING * 9%
            ovr.push(parseFloat(attr_val[22] * 0.04).toFixed(2));			// PLAYER_ATTRIBUTE_POWER_SHOT_ACCURACY * 4%
            break;
        default:
            ovr = 0;
    }

    if (Array.isArray(ovr)) {
        let sum = 0;
        for (let i = 0; i < ovr.length; i++) {
            sum += parseFloat(ovr[i]);
        };
        ovr = Math.round(sum);
    }
    return ovr;
}

function careerFileUpload() {
    /* https://simpleisbetterthancomplex.com/tutorial/2016/11/22/django-multiple-file-upload-using-ajax.html */

    $(".js-upload-career-save").click(function () {
      $("#fileupload").click();
    });
    
    try {
        $("#fileupload").fileupload({
        dataType: 'json',
        singleFileUploads: true,
        start: function (e) {
            $('.js-upload-career-save').css('display', 'none')
            $('.progress').css('display', '')
            $( "p:first" ).text("Uploading your FIFA career save: 0%");
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $( "p:first" ).text("Uploading your FIFA career save: " + progress + "%");
            $('.upload-progress-bar').css(
                'width',
                progress + '%'
            );
        },
        done: function (e, data) {  
            if (data.result.is_valid) {
            $( "p:first" ).text("Upload completed. You will be redirected in a second.");
            $('.progress').css('display', 'none');
            location.reload();
            } else {
                alert("data is not valid.");
                $( "p:first" ).text("Uploading your FIFA career save: FAILED");
                $('.progress').css('display', 'none');
                location.reload();
            }
        }
        });
    } catch(err) {
        return;
    };
};

function selectizejs() {
    /* Calculator */

    $('.just-selectize').selectize({
        allowEmptyOption: true
    });

    /* Upload */

    $('#select-fifa').selectize({
        allowEmptyOption: true,
    });

    /* Filters */
    $('#select-max_per_page').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("max_per_page")
            if (value) 
                this.setValue(value);
        }
    });

    $('#select-iscputransfer').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("iscputransfer")
            if (value) 
                this.setValue(value);
        }
    });
    $('#select-isloan').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("isloan")
            if (value) 
                this.setValue(value);
        }
    });
    $('#select-isloanbuy').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("isloanbuy")
            if (value) 
                this.setValue(value);
        }
    });

    $('#select-issnipe').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("issnipe")
            if (value) 
                this.setValue(value);
        }
    });

    $('#select-result').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("result")
            if (value) 
                this.setValue(value);
        }
    });

    $("#offerteamid-input").selectize({
        valueField: 'teamid',
        labelField: 'teamname',
        searchField: 'teamname',
        options: [],
        plugins: ['remove_button'],
        create: false,
        render: {
            option: function (item, escape) {
                return '<div>' +
                    (item.teamname ? '<span class="teamname">' + escape(item.teamname) + '</span>' : '') +
                    '</div>';
            }
        },
        load: function (query, callback) {
            if (!query.length) return callback();
            this.settings.load = null;
            $.ajax({
                url: '/players/ajax/teams/',
                data: {
                    'username': $('.current_user').text()
                },
                dataType: 'json',
                error: function () {
                    callback();
                },
                success: function (res) {
                    callback(res.teams);
                }
            });
        },
        onInitialize: function() {
            var value = getUrlParameter("offerteamid")
            var selectized = this
            if (value) 
                $.ajax({
                    url: '/players/ajax/teams/',
                    data: {
                        'username': $('.current_user').text(),
                        'selected': value
                    },
                    dataType: 'json',
                    success: function (res) {
                      var teams = res.teams;
                      var teamsids = [];
                      for (var i = 0; i < teams.length; i++) {
                        selectized.addOption({"teamid": teams[i].teamid, "teamname": teams[i].teamname});
                        teamsids.push(teams[i].teamid)
                      }
                      selectized.setValue(teamsids);
                    }
                });	
        }
    });

    $("#fromteamid-input").selectize({
        valueField: 'teamid',
        labelField: 'teamname',
        searchField: 'teamname',
        options: [],
        plugins: ['remove_button'],
        create: false,
        render: {
            option: function (item, escape) {
                return '<div>' +
                    (item.teamname ? '<span class="teamname">' + escape(item.teamname) + '</span>' : '') +
                    '</div>';
            }
        },
        load: function (query, callback) {
            if (!query.length) return callback();
            this.settings.load = null;
            $.ajax({
                url: '/players/ajax/teams/',
                data: {
                    'username': $('.current_user').text()
                },
                dataType: 'json',
                error: function () {
                    callback();
                },
                success: function (res) {
                    callback(res.teams);
                }
            });
        },
        onInitialize: function() {
            var value = getUrlParameter("fromteamid")
            var selectized = this
            if (value) 
                $.ajax({
                    url: '/players/ajax/teams/',
                    data: {
                        'username': $('.current_user').text(),
                        'selected': value
                    },
                    dataType: 'json',
                    success: function (res) {
                      var teams = res.teams;
                      var teamsids = [];
                      for (var i = 0; i < teams.length; i++) {
                        selectized.addOption({"teamid": teams[i].teamid, "teamname": teams[i].teamname});
                        teamsids.push(teams[i].teamid)
                      }
                      selectized.setValue(teamsids);
                    }
                });	
        }
    });

    $('#select-teamtype').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("teamtype")
            if (value) 
                this.setValue(value);
        }
    });

    $("#team-search-input").selectize({
        valueField: 'teamid',
        labelField: 'teamname',
        searchField: 'teamname',
        sortField: [
            {
                field: 'overallrating',
                direction: 'desc'
            },
            {
                field: '$score'
            }
        ],
        option: [],
        create: false,
        maxItems: 1,
        render: {					
            option: function (item, escape) {
                return '<div>' +
                    (item.overallrating ? '<span class="ratinglabel rat' + item.overallrating + '" style="width: 25px; margin-right: 10px;">' + escape(item.overallrating) + '</span>' : '') +
                    (item.teamname ? '<span class="teamname">' + escape(item.teamname) + '</span>' : '') +
                    '</div>';
            }
        },
        load: function (query, callback) {
            if (!query.length) return callback();
            var selectized = this
            $.ajax({
                url: 'ajax/team-by-name/',
                data: {
                    'username': $('.current_user').text(),
                    'teamname': $("#team-search-input-selectized").val(),
                },
                dataType: 'json',
                error: function () {
                    callback();
                },
                success: function (res) {
                    selectized.clearOptions();
                    callback(res.teams);
                }
            });
        },
        onDropdownOpen: function() {
            var selectized = this;
            this.$dropdown_content.on("mousedown", function (event) {
                var dropdown_data = $(this)[0]['childNodes']
                for (var i = 0; i < dropdown_data.length; i++) {
                    if (dropdown_data[i].className === "active") {
                        var teamid = dropdown_data[i].getAttribute('data-value');
                        window.location.href = "/teams/" + teamid;
                        selectized.disable();
                        break;
                    }
                }
            });
        },
    });


    $('#select-isretiring').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("isretiring")
            if (value) 
                this.setValue(value);
        }
    });
    $('#select-isreal').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("isreal")
            if (value) 
                this.setValue(value);
        }
    });
    $('#select-isonloan').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("isonloan")
            if (value) 
                this.setValue(value);
        }
    });
    $('#select-hasreleaseclause').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("hasreleaseclause")
            if (value) 
                this.setValue(value);
        }
    });

    $("#positions-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'posid',
        labelField: 'position',
        searchField: ['posid', 'position'],
        options: [
            { position: 'GK', 	posid: '0'},
            { position: 'SW', 	posid: '1'},
            { position: 'RWB', 	posid: '2'},
            { position: 'RB', 	posid: '3'},
            { position: 'RCB', 	posid: '4'},
            { position: 'CB', 	posid: '5'},
            { position: 'LCB', 	posid: '6'},
            { position: 'LB', 	posid: '7'},
            { position: 'LWB', 	posid: '8'},
            { position: 'RDM', 	posid: '9'},
            { position: 'CDM', 	posid: '10'},
            { position: 'LDM', 	posid: '11'},
            { position: 'RM', 	posid: '12'},
            { position: 'RCM', 	posid: '13'},
            { position: 'CM', 	posid: '14'},
            { position: 'LCM', 	posid: '15'},
            { position: 'LM', 	posid: '16'},
            { position: 'RAM', 	posid: '17'},
            { position: 'CAM', 	posid: '18'},
            { position: 'LAM', 	posid: '19'},
            { position: 'RF', 	posid: '20'},
            { position: 'CF', 	posid: '21'},
            { position: 'LF', 	posid: '22'},
            { position: 'RW', 	posid: '23'},
            { position: 'RS', 	posid: '24'},
            { position: 'ST', 	posid: '25'},
            { position: 'LS', 	posid: '26'},
            { position: 'LW', 	posid: '27'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.position ? '<span class="position">' + escape(item.position) + '</span>' : '') +
                    '/div';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.position ? '<span class="caption">' + escape(item.position) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("preferredpositions")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    });

    $( "#awr-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'workrateValue',
        labelField: 'workrate',
        searchField: ['workrateValue', 'workrate'],
        options: [
            { workrate: 'Low', 			workrateValue: '1'},
            { workrate: 'Medium', 		workrateValue: '0'},
            { workrate: 'High', 		workrateValue: '2'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.workrate ? '<span class="workrate">' + escape(item.workrate) + '</span>' : '') +
                    '/div';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.workrate ? '<span class="caption">' + escape(item.workrate) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("attackingworkrate")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    });

    $( "#dwr-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'workrateValue',
        labelField: 'workrate',
        searchField: ['workrateValue', 'workrate'],
        options: [
            { workrate: 'Low', 			workrateValue: '1'},
            { workrate: 'Medium', 		workrateValue: '0'},
            { workrate: 'High', 		workrateValue: '2'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.workrate ? '<span class="workrate">' + escape(item.workrate) + '</span>' : '') +
                    '/div';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.workrate ? '<span class="caption">' + escape(item.workrate) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("defensiveworkrate")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    });

    $( "#nationality-input").selectize({
        valueField: 'nationid',
        labelField: 'nationname',
        searchField: 'nationname',
        options: [],
        plugins: ['remove_button'],
        create: false,
        render: {
            option: function(item, escape) {
                return '<div>' +
                    (item.nationname ? '<span class="nationname">' + escape(item.nationname) + '</span>' : '') +
                '</div>';
            }
        },
        load: function(query, callback) {
            if (!query.length) return callback();
            this.settings.load = null;
            $.ajax({
                url: 'ajax/nationality/',
                dataType: 'json',
                error: function() {
                    callback();
                },
                success: function (res) {
                  callback(res.nations);
                }
            });
        },
        onInitialize: function() {
            var value = getUrlParameter("nationalityid")
            var selectized = this
            if (value) 
                $.ajax({
                    url: 'ajax/nationality/',
                    data: {
                        'selected': value
                    },
                    dataType: 'json',
                    success: function (res) {
                      var nations = res.nations;
                      var nationids = [];
                      for (var i = 0; i < nations.length; i++) {
                        selectized.addOption({"nationid": nations[i].nationid, "nationname": nations[i].nationname});
                        nationids.push(nations[i].nationid)
                      }
                      selectized.setValue(nationids);
                    }
                });	
        }
    });

    $("#leagues-input").selectize({
        valueField: 'leagueid',
        labelField: 'leaguename',
        searchField: 'leaguename',
        options: [],
        plugins: ['remove_button'],
        create: false,
        render: {
            option: function (item, escape) {
                return '<div>' +
                    (item.leaguename ? '<span class="leaguename">' + escape(item.leaguename) + '</span>' : '') +
                    '</div>';
            }
        },
        load: function (query, callback) {
            if (!query.length) return callback();
            this.settings.load = null;
            $.ajax({
                url: '/players/ajax/leagues/',
                data: {
                    'username': $('.current_user').text()
                },
                dataType: 'json',
                error: function () {
                    callback();
                },
                success: function (res) {
                    callback(res.leagues);
                }
            });
        },
        onInitialize: function() {
            var value = getUrlParameter("leagueid")
            var selectized = this
            if (value) 
                $.ajax({
                    url: '/players/ajax/leagues/',
                    data: {
                        'username': $('.current_user').text(),
                        'selected': value
                    },
                    dataType: 'json',
                    success: function (res) {
                      var leagues = res.leagues;
                      var leaguesids = [];
                      for (var i = 0; i < leagues.length; i++) {
                        selectized.addOption({"leagueid": leagues[i].leagueid, "leaguename": leagues[i].leaguename});
                        leaguesids.push(leagues[i].leagueid)
                      }
                      selectized.setValue(leaguesids);
                    }
                });	
        }
    });

    $("#player-search-input").selectize({
        valueField: 'playerid',
        labelField: 'playername',
        searchField: 'playername',
        sortField: [
            {
                field: 'overallrating',
                direction: 'desc'
            },
            {
                field: '$score'
            }
        ],
        option: [],
        create: false,
        maxItems: 1,
        render: {					
            option: function (item, escape) {
                return '<div>' +
                    (item.overallrating ? '<span class="ratinglabel rat' + item.overallrating + '" style="width: 25px; margin-right: 10px;">' + escape(item.overallrating) + '</span>' : '') +
                    (item.playername ? '<span class="knownas">' + escape(item.playername) + '</span>' : '') +
                    (item.position ? '<span class="position"> (' + escape(item.position) + ')</span>' : '') +
                    '</div>';
            }
        },
        load: function (query, callback) {
            if (!query.length) return callback();
            var selectized = this
            $.ajax({
                url: 'ajax/players-by-name/',
                data: {
                    'username': $('.current_user').text(),
                    'playername': $("#player-search-input-selectized").val(),
                },
                dataType: 'json',
                error: function () {
                    callback();
                },
                success: function (res) {
                    selectized.clearOptions();
                    callback(res.players);
                }
            });
        },
        onDropdownOpen: function() {
            var selectized = this;
            this.$dropdown_content.on("mousedown", function (event) {
                var dropdown_data = $(this)[0]['childNodes']
                for (var i = 0; i < dropdown_data.length; i++) {
                    if (dropdown_data[i].className === "active") {
                        var playerid = dropdown_data[i].getAttribute('data-value');
                        window.location.href = "/players/" + playerid;
                        selectized.disable();
                        break;
                    }
                }
            });
        },
    });

    $("#teams-input").selectize({
        valueField: 'teamid',
        labelField: 'teamname',
        searchField: 'teamname',
        options: [],
        plugins: ['remove_button'],
        create: false,
        render: {
            option: function (item, escape) {
                return '<div>' +
                    (item.teamname ? '<span class="teamname">' + escape(item.teamname) + '</span>' : '') +
                    '</div>';
            }
        },
        load: function (query, callback) {
            if (!query.length) return callback();
            this.settings.load = null;
            $.ajax({
                url: '/players/ajax/teams/',
                data: {
                    'username': $('.current_user').text()
                },
                dataType: 'json',
                error: function () {
                    callback();
                },
                success: function (res) {
                    callback(res.teams);
                }
            });
        },
        onInitialize: function() {
            var value = getUrlParameter("teamid")
            var selectized = this
            if (value) 
                $.ajax({
                    url: '/players/ajax/teams/',
                    data: {
                        'username': $('.current_user').text(),
                        'selected': value
                    },
                    dataType: 'json',
                    success: function (res) {
                      var teams = res.teams;
                      var teamsids = [];
                      for (var i = 0; i < teams.length; i++) {
                        selectized.addOption({"teamid": teams[i].teamid, "teamname": teams[i].teamname});
                        teamsids.push(teams[i].teamid)
                      }
                      selectized.setValue(teamsids);
                    }
                });	
        }
    });

    $('#playerfilter').submit(function () {
        $(this)
            .find('input[name]')
            .filter(function () {
                return !this.value;
            })
            .prop('name', '');
    });

    $('#teamfilter').submit(function () {
        $(this)
            .find('input[name]')
            .filter(function () {
                return !this.value;
            })
            .prop('name', '');
    });

    $('#transfersfilter').submit(function () {
        $(this)
            .find('input[name]')
            .filter(function () {
                return !this.value;
            })
            .prop('name', '');
    });


    $('#btn-reset').click(function () {
        window.location = window.location.pathname;
    });

    $( "#tabs" ).tabs();
};

function convertUnits() {
    $('#p_height').each(function() {
        var unit_system = $('#id_unit_imperial').attr('class');
        var current_value = $(this).text();
        if (unit_system == "dropdown-item-active") {
            current_value = parseInt(current_value);
            var inches = (current_value*0.393700787).toFixed(0);
            var feet = Math.floor(inches / 12);
            inches %= 12;
            $(this).text(feet + "'" + inches + '"');
        } else {
            $(this).text(current_value + " cm");
        }
    });

    $('#p_weight').each(function() {
        var unit_system = $('#id_unit_imperial').attr('class');
        var current_value = $(this).text();
        if (unit_system == "dropdown-item-active") {
            current_value = parseInt(current_value);
            var pounds = Math.floor(current_value*2.2046);
            $(this).text(pounds + " lbs");
        } else {
            $(this).text(current_value + " kg");
        }
    });

}

function changeUnits() {
    $('#id_unit_metric').on("click", function() {
        $.ajax({
            url: '/settings/ajax/change-unit-system/',
            data: {
                "units": 0
            },
            dataType: 'json',
            success: function (unit_system) {
                location.reload();
              }
        });
    });

    $('#id_unit_imperial').on("click", function() {
        $.ajax({
            url: '/settings/ajax/change-unit-system/',
            data: {
                "units": 1
            },
            dataType: 'json',
            success: function (unit_system) {
                location.reload();
              }
        });
    });
}

function changeCurrency() {
    $('#id_cur_usd').on("click", function() {
        $.ajax({
            url: '/settings/ajax/change-currency/',
            data: {
                "currency": 0
            },
            dataType: 'json',
            success: function (currency) {
                location.reload();
              }
        });
    });

    $('#id_cur_eur').on("click", function() {
        $.ajax({
            url: '/settings/ajax/change-currency/',
            data: {
                "currency": 1
            },
            dataType: 'json',
            success: function (currency) {
                location.reload();
              }
        });
    });

    $('#id_cur_gbp').on("click", function() {
        $.ajax({
            url: '/settings/ajax/change-currency/',
            data: {
                "currency": 2
            },
            dataType: 'json',
            success: function (currency) {
                location.reload();
              }
        });
    });
}

function updatePositions() {
    let available_positions = ['GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW', 'SUB', 'RES'];
    
    let posclass = $('.player-position');

    // Return if not found
    if (posclass.length == 0) { return;}

    posclass.each(function() {
        let content = $(this).html();
        let posIDsArray = $(this).text().match(/(\d{1,2})/g);
        let re = "";
        for (let posID of posIDsArray) { 
            re = new RegExp("(^|[\\s])("+posID+"{1})([\\s]|$)", "g");
            content = content.replace(re, "$1"+available_positions[posID]+"$3");
        }
        $(this).html(content); 
    });
}

function updateStrongFoot() {
    let strongfootclass = $('.strong-foot');

    // Return if not found
    if (strongfootclass.length == 0) { return;}

    strongfootclass.each(function() {
        let content = $(this).text();
        if (content == "1") {
            $(this).text("Right");
        } else {
            $(this).text("Left");
        }
    });
}

function updateWorkrates() {
    let wrclass = $('.workrate');

    // Return if not found
    if (wrclass.length == 0) { return;}

    wrclass.each(function() {
        let content = $(this).text();
        if (content == "2") {
            $(this).text("High");
        } else if (content== "1") {
            $(this).text("Low");
        } else {
            $(this).text("Medium");
        }
    });
}

function copyShareLink() {
    $('#shareinput').select();
    document.execCommand("copy");
}

function changeProfilePublicStatus() {
    $("#isprofilepublic").on("change", function() { 
        if($(this).is(":checked")) { 
            $.ajax({
                url: '/settings/ajax/change-profile-public-status/',
                data: { "is_profile_public": 1 },
                dataType: 'json',
                success: function (is_profile_public) {
                    alert(is_profile_public.status);
                }
            });
        } else {
            $.ajax({
                url: '/settings/ajax/change-profile-public-status/',
                data: { "is_profile_public": 0 },
                dataType: 'json',
                success: function (is_profile_public) {
                    alert(is_profile_public.status);
                }
            });
        }
    }); 
}

function cleanUrl() {
    var params = ["isretiring", "isreal", "isonloan", "hasreleaseclause", "teamtype", "iscputransfer", "isloan", "isloanbuy", "issnipe", "result"];
    for (i = 0; i < params.length; i++) {
        if (getUrlParameter(params[i]) == "-1")
            removeParam(params[i])
    }
}

 // http://www.jquerybyexample.net/2012/06/get-url-parameters-using-jquery.html
function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

//  https://stackoverflow.com/a/16941921
function removeParam(parameter) {
  
  var url=document.location.href;
  var urlparts= url.split('?');

  if (urlparts.length>=2) {
    var urlBase=urlparts.shift(); 
    var queryString=urlparts.join("?"); 

    var prefix = encodeURIComponent(parameter)+'=';
    var pars = queryString.split(/[&;]/g);
    for (var i= pars.length; i-->0;)               
        if (pars[i].lastIndexOf(prefix, 0)!==-1)   
            pars.splice(i, 1);
    url = urlBase+'?'+pars.join('&');
    window.history.pushState('',document.title,url);
  }
  
  return url;
}