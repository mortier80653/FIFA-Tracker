$(document).ready(function(){
    selectizejs();
    enableTooltips();
    bootstrapResponsiveTabs();
    resizeableTables();
    updatePositions();
    updateInGameRatings();
    updateAvgAttr();
    updateStrongFoot();
    updateWorkrates();
    changeCurrency();
    changeUnits();
    convertUnits();
    changeProfilePublicStatus();
    cleanUrl();
    careerFileUpload();
    numberWithCommas();
    ToolsCalculator();
});

function enableTooltips() {
    // Enable Bootstrap 4 tooltips
    $('[data-toggle="tooltip"]').tooltip();
}

function numberWithCommas() {
    // Comma separate 'clubworth' and 'transferbudget'

    // Club Worth
    let cwspan = $(".clubworth");
    cwspan.each(function() {
        $(this).text($(this).text().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,") + ",000");
    });

    // Transfer Budget
    let tbspan = $(".transferbudget");
    tbspan.each(function() {
        $(this).text($(this).text().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,"));
    });

};

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

function updateAvgAttr() {
    let attr_tbl = $('.attrib-table');

    // Return if table not found
    if (attr_tbl.length == 0) { return;}

    // Names
    let section_names = [
        'goalkeeper',
        'attack',
        'defending',
        'skill',
        'power',
        'movement',
        'mentality'
    ]

    let sum = 0;
    let avg = 0;
    let attributes = undefined;
    let span = undefined;
    let progressbar = undefined;

    for (let i = 0; i < attr_tbl.length; i++) {
        // reset sum & avg
        sum = 0;
        avg = 0;

        // table cells containing attribute values
        attributes = $(attr_tbl[i]).find('tr td:nth-child(even) span');

        // Sum attributes of section
        attributes.each(function() {
            sum += parseInt($(this).text());
        });
        
        // Calculate average
        avg = Math.ceil(sum/attributes.length);

        // Update span
        span = $('#avg-' + section_names[i] + '-span');
        span.addClass("avg" + avg);
        span.text(avg);

        // Update progressbar
        progressbar = $('#avg-' + section_names[i] +'-progressbar .progress-bar');
        progressbar.addClass('rat' + avg);
        progressbar.css('width', avg + '%');
    }
}

function updateInGameRatings() {
    let attr_tbl = $('.attrib-table tr');

    // Return if table not found
    if (attr_tbl.length == 0) { return;}

    let attr_val = [];

    attr_tbl.each(function() {
        attr_val.push($(this).find("td:eq(1) > span").text());
    });

    let positions = [
        { position: 'GK',    posid: '0'},
        { position: 'SW',    posid: '1'},
        { position: 'RWB',    posid: '2'},
        { position: 'RB',    posid: '3'},
        { position: 'RCB',    posid: '4'},
        { position: 'CB',    posid: '5'},
        { position: 'LCB',    posid: '6'},
        { position: 'LB',    posid: '7'},
        { position: 'LWB',    posid: '8'},
        { position: 'RDM',    posid: '9'},
        { position: 'CDM',    posid: '10'},
        { position: 'LDM',    posid: '11'},
        { position: 'RM',    posid: '12'},
        { position: 'RCM',    posid: '13'},
        { position: 'CM',    posid: '14'},
        { position: 'LCM',    posid: '15'},
        { position: 'LM',    posid: '16'},
        { position: 'RAM',    posid: '17'},
        { position: 'CAM',    posid: '18'},
        { position: 'LAM',    posid: '19'},
        { position: 'RF',    posid: '20'},
        { position: 'CF',    posid: '21'},
        { position: 'LF',    posid: '22'},
        { position: 'RW',    posid: '23'},
        { position: 'RS',    posid: '24'},
        { position: 'ST',    posid: '25'},
        { position: 'LS',    posid: '26'},
        { position: 'LW',    posid: '27'},
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
            /* Hide 'upload button' */
            $('.js-upload-career-save').css('display', 'none')

            /* Hide 'fifa_edition' select */
            $('.selectize-control').css('display', 'none')

            /* Show upload progress */
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
    } 
    catch(err) {
        return;
    };
};

function bootstrapResponsiveTabs(){
    $('.nav-tabs').responsiveTabs();
}

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

    $('#select-hasstats').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("hasstats")
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
            { position: 'GK',    posid: '0'},
            { position: 'SW',    posid: '1'},
            { position: 'RWB',    posid: '2'},
            { position: 'RB',    posid: '3'},
            { position: 'RCB',    posid: '4'},
            { position: 'CB',    posid: '5'},
            { position: 'LCB',    posid: '6'},
            { position: 'LB',    posid: '7'},
            { position: 'LWB',    posid: '8'},
            { position: 'RDM',    posid: '9'},
            { position: 'CDM',    posid: '10'},
            { position: 'LDM',    posid: '11'},
            { position: 'RM',    posid: '12'},
            { position: 'RCM',    posid: '13'},
            { position: 'CM',    posid: '14'},
            { position: 'LCM',    posid: '15'},
            { position: 'LM',    posid: '16'},
            { position: 'RAM',    posid: '17'},
            { position: 'CAM',    posid: '18'},
            { position: 'LAM',    posid: '19'},
            { position: 'RF',    posid: '20'},
            { position: 'CF',    posid: '21'},
            { position: 'LF',    posid: '22'},
            { position: 'RW',    posid: '23'},
            { position: 'RS',    posid: '24'},
            { position: 'ST',    posid: '25'},
            { position: 'LS',    posid: '26'},
            { position: 'LW',    posid: '27'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.position ? '<span class="position">' + escape(item.position) + '</span>' : '') +
                    '</div>';
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
            { workrate: 'Low',    		workrateValue: '1'},
            { workrate: 'Medium',    	workrateValue: '0'},
            { workrate: 'High',    	workrateValue: '2'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.workrate ? '<span class="workrate">' + escape(item.workrate) + '</span>' : '') +
                    '</div>';
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
            { workrate: 'Low',    		workrateValue: '1'},
            { workrate: 'Medium',    	workrateValue: '0'},
            { workrate: 'High',    	workrateValue: '2'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.workrate ? '<span class="workrate">' + escape(item.workrate) + '</span>' : '') +
                    '</div>';
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

    $('#playerfilterform').submit(function () {
        $(this)
            .find('input[name]')
            .filter(function () {
                return !this.value;
            })
            .prop('name', '');
    });

    $('#teamfilterform').submit(function () {
        $(this)
            .find('input[name]')
            .filter(function () {
                return !this.value;
            })
            .prop('name', '');
    });

    $('#transfersfilterform').submit(function () {
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


    // Tab 3

    $('#select-realface').selectize({
        allowEmptyOption: true,
        onInitialize: function() {
            var value = getUrlParameter("hashighqualityhead")
            if (value) 
                this.setValue(value);
        }
    });

    $("#headmodel-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'headtype',
        labelField: 'headtypename',
        searchField: ['headtype', 'headtypename'],
        options: [
            { headtypename: 'Caucasian',        headtype: '0'},
            { headtypename: 'African',            headtype: '1'},
            { headtypename: 'Latin',            headtype: '2'},
            { headtypename: 'European',        headtype: '3'},
            { headtypename: 'Arabic',            headtype: '4'},
            { headtypename: 'Asian',            headtype: '5'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.headtypename ? '<span class="headtypename">' + escape(item.headtypename) + '</span>' : '') +
                    '</div>';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.headtypename ? '<span class="caption">' + escape(item.headtypename) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("headtype")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    });

    $("#hair-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'valuefield',
        labelField: 'labelfield',
        searchField: ['valuefield', 'labelfield'],
        options: [
            { labelfield: 'Short',    valuefield: '1'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="item">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="caption">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("hairtypecode")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    });

    $("#haircolor-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'valuefield',
        labelField: 'labelfield',
        searchField: ['valuefield', 'labelfield'],
        options: [
            { labelfield: 'Blonde',            valuefield: '0'},
            { labelfield: 'Black',                valuefield: '1'},
            { labelfield: 'Ash Blonde',        valuefield: '2'},
            { labelfield: 'Dark Brown',        valuefield: '3'},
            { labelfield: 'Platinum Blonde',    valuefield: '4'},
            { labelfield: 'Light Brown',        valuefield: '5'},
            { labelfield: 'Brown',                valuefield: '6'},
            { labelfield: 'Red',                valuefield: '7'},
            { labelfield: 'White',                valuefield: '8'},
            { labelfield: 'Gray',                valuefield: '9'},
            { labelfield: 'Green',                valuefield: '10'},
            { labelfield: 'Violet',            valuefield: '11'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="item">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="caption">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("haircolorcode")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    });

    $("#skincolor-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'valuefield',
        labelField: 'labelfield',
        searchField: ['valuefield', 'labelfield'],
        options: [
            { labelfield: 'Light Pink',    valuefield: '1'},
            { labelfield: 'Pink',    valuefield: '2'},
            { labelfield: 'Dark Pink',    valuefield: '3'},
            { labelfield: 'Light Yellow',    valuefield: '4'},
            { labelfield: 'Medium Yellow',    valuefield: '5'},
            { labelfield: 'Dark Yellow',    valuefield: '6'},
            { labelfield: 'Very Light Brown',    valuefield: '7'},
            { labelfield: 'Light Brown',    valuefield: '8'},
            { labelfield: 'Medium Brown',    valuefield: '9'},
            { labelfield: 'Dark Brown',    valuefield: '10'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="item">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="caption">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("skintonecode")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    });

    $("#bodytype-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'valuefield',
        labelField: 'labelfield',
        searchField: ['valuefield', 'labelfield'],
        options: [
            { labelfield: 'Average Height - Lean',    valuefield: '1'},
            { labelfield: 'Average Height - Normal',    valuefield: '2'},
            { labelfield: 'Average Height - Stocky',    valuefield: '3'},
            { labelfield: 'Tall (185+) Height - Lean',    valuefield: '4'},
            { labelfield: 'Tall (185+) Height - Normal',    valuefield: '5'},
            { labelfield: 'Tall (185+) Height - Stocky',    valuefield: '6'},
            { labelfield: 'Short (175-) Height - Lean',    valuefield: '7'},
            { labelfield: 'Short (175-) Height - Normal',    valuefield: '8'},
            { labelfield: 'Short (175-) Height - Stocky',    valuefield: '9'},
            { labelfield: 'Messi',    valuefield: '10'},
            { labelfield: 'Very Tall and Lean',    valuefield: '11'},
            { labelfield: 'Akinfenwa',    valuefield: '12'},
            { labelfield: 'Courtois',    valuefield: '13'},
            { labelfield: 'Neymar',    valuefield: '14'},
            { labelfield: 'Shaqiri',    valuefield: '15'},
            { labelfield: 'Cristiano Ronaldo',    valuefield: '16'},
            { labelfield: 'Leroux (Only Women)',    valuefield: '18'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="item">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="caption">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("bodytypecode")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    }); 

    $("#boots-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'valuefield',
        labelField: 'labelfield',
        searchField: ['valuefield', 'labelfield'],
        options: [
            { labelfield: '21. adidas ACE 17+ PURECONTROL Magnetic Storm',                                                                  valuefield: '21'},
            { labelfield: '22. adidas ACE 17+ PURECONTROL Ocean Storm',                                                                     valuefield: '22'},
            { labelfield: '23. adidas ACE 17+ PURECONTROL Thunder Storm',                                                                   valuefield: '23'},
            { labelfield: '24. adidas ACE 17+ PURECONTROL Pyro Storm',                                                                      valuefield: '24'},
            { labelfield: '25. adidas ACE 17+ PURECONTROL Earth Storm',                                                                     valuefield: '25'},
            { labelfield: '26. adidas ACE 17.1 WOMEN',                                                                                      valuefield: '26'},
            { labelfield: '27. adidas COPA 17.1 Dust Storm',                                                                                valuefield: '27'},
            { labelfield: '28. adidas COPA 17.1 Pyro Storm',                                                                                valuefield: '28'},
            { labelfield: '29. adidas COPA 17.1 Ocean Storm',                                                                               valuefield: '29'},
            { labelfield: '30. adidas NEMEZIZ 17+ Magnetic Storm',                                                                          valuefield: '30'},
            { labelfield: '31. adidas NEMEZIZ 17+ Ocean Storm',                                                                             valuefield: '31'},
            { labelfield: '32. adidas NEMEZIZ 17+ Thunder Storm',                                                                           valuefield: '32'},
            { labelfield: '33. adidas NEMEZIZ 17+ Pyro Storm',                                                                              valuefield: '33'},
            { labelfield: '34. adidas NEMEZIZ 17+ Earth Storm',                                                                             valuefield: '34'},
            { labelfield: '35. adidas NEMEZIZ 17.1 WOMEN',                                                                                  valuefield: '35'},
            { labelfield: '36. Joma Vulcano 2.0',                                                                                           valuefield: '36'},
            { labelfield: '37. Hummel Rapid X Blade Bluebird',                                                                              valuefield: '37'},
            { labelfield: '38. adidas NEMEZIZ MESSI 17+ Ocean Storm',                                                                       valuefield: '38'},
            { labelfield: '39. adidas NEMEZIZ MESSI 17+ Pyro Storm',                                                                        valuefield: '39'},
            { labelfield: '40. adidas X 17+ 360SPEED Magnetic Storm',                                                                       valuefield: '40'},
            { labelfield: '41. adidas X 17+ 360SPEED Ocean Storm',                                                                          valuefield: '41'},
            { labelfield: '42. adidas X 17+ 360SPEED Thunder Storm',                                                                        valuefield: '42'},
            { labelfield: '43. adidas X 17+ 360SPEED Pyro Storm',                                                                           valuefield: '43'},
            { labelfield: '44. adidas X 17+ 360SPEED Earth Storm',                                                                          valuefield: '44'},
            { labelfield: '45. Nike Mercurial Superfly VI - Orange/Black/White',                                                            valuefield: '45'},
            { labelfield: '46. Nike Tiempo Legend VII - Black/White/Laser Orange',                                                          valuefield: '46'},
            { labelfield: '47. Nike Magista Obra II DF - Laser Orange/Black/White',                                                         valuefield: '47'},
            { labelfield: '48. Nike Hypervenom Phantom II DF - Laser Orange/White/Blk',                                                     valuefield: '48'},
            { labelfield: '49. Nike Mercurial Superfly VI - CR7 Chapter 6',                                                                 valuefield: '49'},
            { labelfield: '50. Nike Magista Obra II DF - Black/White/Uni. Red',                                                             valuefield: '50'},
            { labelfield: '51. Nike Magista Obra II DF - Obsidian/White/Gamma Blue',                                                        valuefield: '51'},
            { labelfield: '52. Nike Hypervenom Phantom II DF - Uni. Red/Black/Crimson',                                                     valuefield: '52'},
            { labelfield: '53. Nike Hypervenom Phantom II DF - Obsidian/White',                                                             valuefield: '53'},
            { labelfield: '54. Nike Mercurial Superfly VI - Uni. Red/Black',                                                                valuefield: '54'},
            { labelfield: '55. Nike Mercurial Superfly VI  - Obsidian/White',                                                               valuefield: '55'},
            { labelfield: '56. Nike Tiempo Legend VII - Uni. Red/White/Black',                                                              valuefield: '56'},
            { labelfield: '57. Nike Tiempo Legend VII - Gamma Blue/White/Obsidian',                                                         valuefield: '57'},
            { labelfield: '58. Nike Mercurial Superfly VI - CR7 Chapter 5',                                                                 valuefield: '58'},
            { labelfield: '59. Nike Hypervenom Phantom 3 Elite DF',                                                                         valuefield: '59'},
            { labelfield: '60. Nike Magista Obra II Elite DF',                                                                              valuefield: '60'},
            { labelfield: '61. Nike Tiempo Legend VII Elite',                                                                               valuefield: '61'},
            { labelfield: '62. Nike Mercurial Vapor XI NJR',                                                                                valuefield: '62'},
            { labelfield: '63. Nike Mercurial Superfly V - CR7 Chapter 4',                                                                  valuefield: '63'},
            { labelfield: '64. Nike Vapor XII Elite - Orange',                                                                              valuefield: '64'},
            { labelfield: '65. PUMA evoPower Vigor 1 Graphic - Fiery Coral/Silver/Black',                                                   valuefield: '65'},
            { labelfield: '66. PUMA One 18.1',                                                                                              valuefield: '66'},
            { labelfield: '67. PUMA One 17.1 - Puma White/Black/Fiery Coral/Silver',                                                        valuefield: '67'},
            { labelfield: '68. PUMA One 17.1 FG - Atomic Blue/White/Yellow',                                                                valuefield: '68'},
            { labelfield: '69. Puma One 17.1 FG - Puma Black/Silver',                                                                       valuefield: '69'},
            { labelfield: '71. Umbro Medusae II - Electric Blue/White/Blazing Yellow',                                                      valuefield: '71'},
            { labelfield: '72. Umbro Velocita 3 - Blazing Yellow/Electric Blue',                                                            valuefield: '72'},
            { labelfield: '73. Umbro UX Accuro - Blazing Yellow/Electric Blue',                                                             valuefield: '73'},
            { labelfield: '74. Umbro UX Accuro II - Eclipse/Lava Pink/White',                                                               valuefield: '74'},
            { labelfield: '75. Umbro Medusae II - Eclipse/White/Lava Pink',                                                                 valuefield: '75'},
            { labelfield: '76. Umbro Velocita 3 - White/Eclipse/Lava Pink',                                                                 valuefield: '76'},
            { labelfield: '77. Umbro Velocita 3 - Bluefish/White/Black',                                                                    valuefield: '77'},
            { labelfield: '78. Umbro Medusae II - Black/White/Bluefish',                                                                    valuefield: '78'},
            { labelfield: '80. Nike Mercurial Vapor XI - Black',                                                                            valuefield: '80'},
            { labelfield: '81. Nike Superfly VI Elite DF - Black/Total Orange',                                                             valuefield: '81'},
            { labelfield: '82. Nike Superfly VI Elite DF - Orange/Black',                                                                   valuefield: '82'},
            { labelfield: '83. Under Armour Clutch Fit Force 3 - Black/White/Neon Coral',                                                   valuefield: '83'},
            { labelfield: '84. Under Armour Clutch Fit Force 3 - High Viz/Rocket Red/Black',                                                valuefield: '84'},
            { labelfield: '85. Under Armour Spotlight - White/Phoenix Fire/Black',                                                          valuefield: '85'},
            { labelfield: '86. Under Armour Spotlight - Black/Viper Green',                                                                 valuefield: '86'},
            { labelfield: '87. New Balance Visaro 2.0 - Lime/Military Green',                                                               valuefield: '87'},
            { labelfield: '88. New Balance Furon 3.0 - Military Green/Lime',                                                                valuefield: '88'},
            { labelfield: '89. New Balance Visaro 2.0 - Black/Bolt',                                                                        valuefield: '89'},
            { labelfield: '90. New Balance Furon 3.0 - Bolt/Team Royal',                                                                    valuefield: '90'},
            { labelfield: '91. New Balance Visaro 2.0 - Maldives Blue/Hi-Lite',                                                             valuefield: '91'},
            { labelfield: '92. New Balance Furon 3.0 - Hi-Lite/Maldives Blue',                                                              valuefield: '92'},
            { labelfield: '93. Mizuno Rebula V1 JAPAN - Blue Atoll/Black/Silver',                                                           valuefield: '93'},
            { labelfield: '94. Mizuno Morelia Neo - Seleção',                                                                               valuefield: '94'},
            { labelfield: '95. Mizuno Rebula V1 JAPAN - White Dwarf',                                                                       valuefield: '95'},
            { labelfield: '96. Mizuno Morelia Neo II - Blueprint/Safety Yellow/White',                                                      valuefield: '96'},
            { labelfield: '97. Mizuno Morelia Neo II - Orange Clown Fish/White',                                                            valuefield: '97'},
            { labelfield: '98. Mizuno Rebula V1 JAPAN - Yellow Aurora',                                                                     valuefield: '98'},
            { labelfield: '99. adidas PREDATOR 18+ Sky Stalker',                                                                            valuefield: '99'},
            { labelfield: '100. adidas PREDATOR 18+ Lone Hunter',                                                                           valuefield: '100'},
            { labelfield: '101. adidas PREDATOR 18+ Cold Blooded',                                                                          valuefield: '101'},
            { labelfield: '102. adidas PREDATOR 18+ Nite Crawler',                                                                          valuefield: '102'},
            { labelfield: '103. adidas PREDATOR 18+ Deadly Strike',                                                                         valuefield: '103'},
            { labelfield: '104. adidas PREDATOR 18+ Warm Blooded',                                                                          valuefield: '104'},
            { labelfield: '105. ASICS DS LIGHT X-FLY 3',                                                                                    valuefield: '105'},
            { labelfield: '106. ASICS DS LIGHT X-FLY 3 SL',                                                                                 valuefield: '106'},
            { labelfield: '107. ASICS LETHAL TESTIMONIAL 4 IT',                                                                             valuefield: '107'},
            { labelfield: '108. adidas COPA 18.1 Sky Stalker',                                                                              valuefield: '108'},
            { labelfield: '109. adidas Glitch - Chroma Hacked',                                                                             valuefield: '109'},
            { labelfield: '110. adidas COPA 18.1 Cold Blooded',                                                                             valuefield: '110'},
            { labelfield: '111. Joma Aguila Pro FG',                                                                                        valuefield: '111'},
            { labelfield: '112. Joma Champion Max Black White HG',                                                                          valuefield: '112'},
            { labelfield: '113. adidas COPA 18.1 Nite Crawler',                                                                             valuefield: '113'},
            { labelfield: '114. adidas COPA 18.1 Deadly Strike',                                                                            valuefield: '114'},
            { labelfield: '115. adidas NEMEZIZ 17+ Sky Stalker',                                                                            valuefield: '115'},
            { labelfield: '116. adidas NEMEZIZ 17+ Lone Hunter',                                                                            valuefield: '116'},
            { labelfield: '117. adidas NEMEZIZ 17+ Cold Blooded',                                                                           valuefield: '117'},
            { labelfield: '126. adidas X 17+ PURESPEED Nite Crawler',                                                                       valuefield: '126'},
            { labelfield: '127. adidas X 17+ PURESPEED Deadly Strike',                                                                      valuefield: '127'},
            { labelfield: '128. Joma Champion Max Royal Fluo Yellow',                                                                       valuefield: '128'},
            { labelfield: '129. 129_Auth-FullChar',                                                                                         valuefield: '129'},
            { labelfield: '130. adidas Ace 16.1 Dark Space',                                                                                valuefield: '130'},
            { labelfield: '131. adidas Ace 16.1 Mercury Pack',                                                                              valuefield: '131'},
            { labelfield: '132. adidas Ace 16.1 Viper Pack',                                                                                valuefield: '132'},
            { labelfield: '133. adidas Ace 16.1 Stellar Pack',                                                                              valuefield: '133'},
            { labelfield: '134. adidas Ace 16.1 Speed of Light',                                                                            valuefield: '134'},
            { labelfield: '135. adidas Ace 16+ Dark Space',                                                                                 valuefield: '135'},
            { labelfield: '136. adidas Ace 16+ Mercury Pack',                                                                               valuefield: '136'},
            { labelfield: '137. adidas Ace 16+ Viper Pack',                                                                                 valuefield: '137'},
            { labelfield: '138. adidas Ace 16+ Speed of Light',                                                                             valuefield: '138'},
            { labelfield: '139. adidas Ace 16+ Stellar Pack',                                                                               valuefield: '139'},
            { labelfield: '140. adidas adiZero 99Gram',                                                                                     valuefield: '140'},
            { labelfield: '141. adidas Messi 16.1 Speed of Light',                                                                          valuefield: '141'},
            { labelfield: '142. adidas Messi 16.1 Mercury Pack',                                                                            valuefield: '142'},
            { labelfield: '143. adidas Messi 16+ Space Dust',                                                                               valuefield: '143'},
            { labelfield: '144. adidas Messi 16+ Mercury Pack',                                                                             valuefield: '144'},
            { labelfield: '145. adidas Messi 16+ Speed of Light',                                                                           valuefield: '145'},
            { labelfield: '146. adidas X 16.1 Dark Space',                                                                                  valuefield: '146'},
            { labelfield: '147. adidas X 16.1 Mercury Pack',                                                                                valuefield: '147'},
            { labelfield: '148. adidas X 16.1 Speed of Light',                                                                              valuefield: '148'},
            { labelfield: '149. adidas X 16.1 Viper Pack',                                                                                  valuefield: '149'},
            { labelfield: '150. adidas X 16.1 Stellar Pack',                                                                                valuefield: '150'},
            { labelfield: '151. adidas X 16+ Dark Space',                                                                                   valuefield: '151'},
            { labelfield: '152. adidas X 16+ Intersport',                                                                                   valuefield: '152'},
            { labelfield: '153. adidas X 16+ Mercury Pack',                                                                                 valuefield: '153'},
            { labelfield: '154. adidas X 16+ Speed of Light',                                                                               valuefield: '154'},
            { labelfield: '155. adidas X 16+ Viper Pack',                                                                                   valuefield: '155'},
            { labelfield: '156. adidas X 16+ Stellar Pack',                                                                                 valuefield: '156'},
            { labelfield: '157. adidas Ace 16+ White/Black/White',                                                                          valuefield: '157'},
            { labelfield: '158. adidas X 16+ Black/White/Black',                                                                            valuefield: '158'},
            { labelfield: '159. ASICS DS LIGHT X-FLY 2 - Pearl White/Electric Blue',                                                        valuefield: '159'},
            { labelfield: '160. ASICS LETHAL LEGACY - Flash Yellow/Black',                                                                  valuefield: '160'},
            { labelfield: '161. ASICS MENACE 3 - Spice Orange/White',                                                                       valuefield: '161'},
            { labelfield: '162. Lotto Zhero Gravity VIII 200 - Fanta Fluo/White',                                                           valuefield: '162'},
            { labelfield: '164. Joma Champion Max - Blue/Green/White',                                                                      valuefield: '164'},
            { labelfield: '167. Mizuno Basara 101 - Black',                                                                                 valuefield: '167'},
            { labelfield: '168. Mizuno Morelia II - Blue',                                                                                  valuefield: '168'},
            { labelfield: '169. Mizuno Morelia Neo II - Blue',                                                                              valuefield: '169'},
            { labelfield: '170. Mizuno Wave Ignitus 4 - Red',                                                                               valuefield: '170'},
            { labelfield: '171. New Balance Furon – Bright Cherry/Galaxy/Firefly',                                                          valuefield: '171'},
            { labelfield: '172. New Balance Visaro - Galaxy/Bright Cherry/Firefly',                                                         valuefield: '172'},
            { labelfield: '173. Nike Hypervenom Phantom II - Pure Platinum/Black/Green',                                                    valuefield: '173'},
            { labelfield: '174. Nike Hypervenom Phantom II - Volt/Black/Hyper Turq',                                                        valuefield: '174'},
            { labelfield: '175. Nike Hypervenom Phantom II - White/Black/Total Orange',                                                     valuefield: '175'},
            { labelfield: '176. Nike Magista - Total Crimson/Black/Volt',                                                                   valuefield: '176'},
            { labelfield: '177. Nike Magista - White/Black/Pink Blast',                                                                     valuefield: '177'},
            { labelfield: '178. Nike Magista Obra II - Pure Platinum/Black/Ghost Green',                                                    valuefield: '178'},
            { labelfield: '179. Nike Magista Obra II - Volt/Black/Total Orange/Pink',                                                       valuefield: '179'},
            { labelfield: '180. Nike Mercurial Superfly V - Pure Platinum/Black/Ghost Green',                                               valuefield: '180'},
            { labelfield: '181. Nike Mercurial Superfly V - Total Crimson/Volt/Black',                                                      valuefield: '181'},
            { labelfield: '182. Nike Mercurial Superfly V - White/Black/Volt/Total Orange',                                                 valuefield: '182'},
            { labelfield: '183. Nike Tiempo Legend VI - Clear Jade/Black/Volt',                                                             valuefield: '183'},
            { labelfield: '184. Nike Tiempo Legend VI - White/Black/Total Orange',                                                          valuefield: '184'},
            { labelfield: '185. Nike Tiempo Legend VI - Wolf Grey/Black/Clear Jade',                                                        valuefield: '185'},
            { labelfield: '186. Pirma Brasil Accurate - Aqua/Silver',                                                                       valuefield: '186'},
            { labelfield: '187. Pirma Imperio Legend - Blue Petrol',                                                                        valuefield: '187'},
            { labelfield: '188. Pirma Supreme Spry - Black/Red',                                                                            valuefield: '188'},
            { labelfield: '189. PUMA evoPOWER 1.3 Tricks',                                                                                  valuefield: '189'},
            { labelfield: '190. PUMA evoPOWER 1.3',                                                                                         valuefield: '190'},
            { labelfield: '191. PUMA evoPOWER 1.3',                                                                                         valuefield: '191'},
            { labelfield: '192. PUMA evoSPEED SL-S II',                                                                                     valuefield: '192'},
            { labelfield: '193. PUMA evoSPEED SL-S',                                                                                        valuefield: '193'},
            { labelfield: '194. PUMA evoSPEED 1.5 Tricks',                                                                                  valuefield: '194'},
            { labelfield: '195. PUMA evoTOUCH PRO',                                                                                         valuefield: '195'},
            { labelfield: '196. Umbro Medusae - Black/White/Bluebird',                                                                      valuefield: '196'},
            { labelfield: '197. Umbro Medusae - Grenadine/White/Black',                                                                     valuefield: '197'},
            { labelfield: '198. Umbro Medusae - White/Black/Grenadine',                                                                     valuefield: '198'},
            { labelfield: '199. Umbro UX-Accuro - Black/Metallic/Grenadine',                                                                valuefield: '199'},
            { labelfield: '200. Umbro UX-Accuro - Grenadine/Black',                                                                         valuefield: '200'},
            { labelfield: '201. Umbro UX-Accuro - White/Black/Bluebird',                                                                    valuefield: '201'},
            { labelfield: '202. Umbro Velocita II - Black/White/Grenadine',                                                                 valuefield: '202'},
            { labelfield: '209. adidas Ace 17+ Blue Blast Intersport',                                                                      valuefield: '209'},
            { labelfield: '210. adidas Ace 17+ Chequered Black',                                                                            valuefield: '210'},
            { labelfield: '211. adidas Ace 17+ Blue Blast',                                                                                 valuefield: '211'},
            { labelfield: '212. adidas Ace 17+ Red Limit',                                                                                  valuefield: '212'},
            { labelfield: '213. adidas Ace 17+ Turbocharge',                                                                                valuefield: '213'},
            { labelfield: '214. adidas Ace 17+ Camouflage',                                                                                 valuefield: '214'},
            { labelfield: '215. adidas Messi 16+ Blue Blast',                                                                               valuefield: '215'},
            { labelfield: '216. adidas Messi 16+ Turbocharge',                                                                              valuefield: '216'},
            { labelfield: '217. adidas Messi 16+ Red Limit',                                                                                valuefield: '217'},
            { labelfield: '218. adidas X 16+ Blue Blast',                                                                                   valuefield: '218'},
            { labelfield: '219. adidas X 16+ Chequered Black',                                                                              valuefield: '219'},
            { labelfield: '220. adidas X 16+ Red Limit',                                                                                    valuefield: '220'},
            { labelfield: '221. adidas X 16+ Turbocharge',                                                                                  valuefield: '221'},
            { labelfield: '222. adidas X 16+ Camouflage',                                                                                   valuefield: '222'},
            { labelfield: '223. adidas Copa 17.1 Red Limit',                                                                                valuefield: '223'},
            { labelfield: '224. adidas Copa 17.1 Chequered Black',                                                                          valuefield: '224'},
            { labelfield: '225. adidas Copa 17.1 Blue Blast',                                                                               valuefield: '225'},
            { labelfield: '226. adidas Copa 17.1 Turbocharge',                                                                              valuefield: '226'},
            { labelfield: '227. adidas Copa 17.1 Crowning Glory',                                                                           valuefield: '227'},
            { labelfield: '344. adidas NEMEZIZ 17+',                                                                                        valuefield: '344'},
            { labelfield: '345. adidas ACE 17+ PURECONTROL',                                                                                valuefield: '345'},
            { labelfield: '346. adidas X 17+ PURESPEED',                                                                                    valuefield: '346'},            
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="item">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.labelfield ? '<span class="caption">' + escape(item.labelfield) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("shoetypecode")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    });

    $("#traits-input").selectize({
        delimiter: ',',
        persist: false,
        valueField: 'traitvalue',
        labelField: 'traitname',
        searchField: ['traitvalue', 'traitname'],
        options: [
            { traitname: 'Inflexibility',    traitvalue: '1_1'},
            { traitname: 'Long Throw-in',    traitvalue: '1_2'},
            { traitname: 'Power Free kick',    traitvalue: '1_4'},
            { traitname: 'Diver',    traitvalue: '1_8'},
            { traitname: 'Injury prone',    traitvalue: '1_16'},
            { traitname: 'Injury free',    traitvalue: '1_32'},
            { traitname: 'Avoids using weaker foot',    traitvalue: '1_64'},
            { traitname: 'Dives into tackles',    traitvalue: '1_128'},
            { traitname: 'Tries to beat defensive line',    traitvalue: '1_256'},
            { traitname: 'Selfish',    traitvalue: '1_512'},
            { traitname: 'Leadership',    traitvalue: '1_1024'},
            { traitname: 'Argues With Referee',    traitvalue: '1_2048'},
            { traitname: 'Early crosser',    traitvalue: '1_4096'},
            { traitname: 'Finesse shot',    traitvalue: '1_8192'},
            { traitname: 'Flair',    traitvalue: '1_16384'},
            { traitname: 'Long passer',    traitvalue: '1_32768'},
            { traitname: 'Long shot taker',    traitvalue: '1_65536'},
            { traitname: 'Skilled dribbling',    traitvalue: '1_131072'},
            { traitname: 'Playmaker',    traitvalue: '1_262144'},
            { traitname: 'GK up for corners',    traitvalue: '1_524288'},
            { traitname: 'Puncher',    traitvalue: '1_1048576'},
            { traitname: 'GK Long throw',    traitvalue: '1_2097152'},
            { traitname: 'Power header',    traitvalue: '1_4194304'},
            { traitname: 'GK One on One',    traitvalue: '1_8388608'},
            { traitname: 'Giant throw-in',    traitvalue: '1_16777216'},
            { traitname: 'Outsite foot shot',    traitvalue: '1_33554432'},
            { traitname: 'Fans favourite',    traitvalue: '1_67108864'},
            { traitname: 'Swerve Pass',    traitvalue: '1_134217728'},
            { traitname: 'Second Wind',    traitvalue: '1_268435456'},
            { traitname: 'Acrobatic Clearance',    traitvalue: '1_536870912'},
            { traitname: 'Skilled Dribbling',    traitvalue: '2_1'},
            { traitname: 'Flair Passes',    traitvalue: '2_2'},
            { traitname: 'Fancy Flicks',    traitvalue: '2_4'},
            { traitname: 'Stutter Penalty',    traitvalue: '2_8'},
            { traitname: 'Chipped Penalty',    traitvalue: '2_16'},
            { traitname: 'Bicycle Kicks',    traitvalue: '2_32'},
            { traitname: 'Diving Header',    traitvalue: '2_64'},
            { traitname: 'Driven Pass',    traitvalue: '2_128'},
            { traitname: 'GK Flat Kick',    traitvalue: '2_256'},
            { traitname: 'One Club Player',    traitvalue: '2_512'},
            { traitname: 'Team Player',    traitvalue: '2_1024'},
            { traitname: 'Chip shot',    traitvalue: '2_2048'},
            { traitname: 'Technical Dribbler',    traitvalue: '2_4096'},
            { traitname: 'Rushes Out Of Goal',    traitvalue: '2_8192'},
            { traitname: 'Backs Into Player',    traitvalue: '2_16384'},
            { traitname: 'Set Play Specialist',    traitvalue: '2_32768'},
            { traitname: 'Takes Finesse Free Kicks',    traitvalue: '2_65536'},
            { traitname: 'Target Forward',    traitvalue: '2_131072'},
            { traitname: 'Cautious With Crosses',    traitvalue: '2_262144'},
            { traitname: 'Comes For Crossess',    traitvalue: '2_524288'},
            { traitname: 'Blames Teammates',    traitvalue: '2_1048576'},
            { traitname: 'Saves with Feet',    traitvalue: '2_2097152'},
            { traitname: 'Set Play Specialist',    traitvalue: '2_4194304'},
            { traitname: 'Tornado Skillmove',    traitvalue: '2_8388608'},
        ],
        render: {
            item: function(item, escape) {
                return '<div>' +
                    (item.traitname ? '<span class="traitname">' + escape(item.traitname) + '</span>' : '') +
                    '</div>';
            },
            option: function (item, escape) {
                return '<div>' +
                    (item.traitname ? '<span class="caption">' + escape(item.traitname) + '</span>' : '') +
                    '</div>';
            },
        },
        onInitialize: function() {
            var value = getUrlParameter("traits")
            if (value) 
                if (value.includes(','))
                    value = value.split(',')
                this.setValue(value);
        }
    });
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
        console.log("GLGGL")
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
        for(let i = 0; i < posIDsArray.length; i++) {
            let posID = posIDsArray[i];
            re = new RegExp("(^|[\\s])("+posID+"{1})([\\s]|$)", "g");
            content = content.replace(re, "$1"+available_positions[posID]+"$3");
        }
        /*
        for (let posID of posIDsArray) { 
            re = new RegExp("(^|[\\s])("+posID+"{1})([\\s]|$)", "g");
            content = content.replace(re, "$1"+available_positions[posID]+"$3");
        }
        */
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
    var params = ["isretiring", "isreal", "isonloan", "hasreleaseclause", "hasstats", "teamtype", "iscputransfer", "isloan", "isloanbuy", "issnipe", "result", "hashighqualityhead"];
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

function sortTable(tableid, column) {
    let shouldSort, sorting, table, rows, x, y, changes;
    changes = 0;
    shouldSort = false;
    sorting = true;
    table = $('#' + tableid);

    while (sorting) {
        rows = table.find('tr');
        sorting = false;
        for (i = 1; i < (rows.length - 1); i++) {
            row_x = $(rows[i]).find('td');
            row_y = $(rows[i + 1]).find('td');
            [x,y] = toCompare(column, row_x, row_y);

            // ascending direction
            if (x > y) {
                shouldSort = true;
                break;
            }
        }

        if (shouldSort) {
            try {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                sorting = true;
                changes += 1;
            } 
            catch (error) {
                sorting = false;
            }
        }
    }

    // descending direction
    if (changes == 0) {
        $('#' + tableid + " tbody").each(function(){
            var arr = $.makeArray($("tr",this).detach());
            arr.reverse();
            $(this).append(arr);
        });
    }
}

function toCompare(column, row_x, row_y){
    let x = 0;
    let y = 0;
    switch (column) {
        case 1:
            // Column - PlayerPos
            x = posToID(row_x[column].innerText);
            y = posToID(row_y[column].innerText);
            break;
        case 2:
            // Column - Player (order by jersey number)
            x = parseInt(row_x[column].innerText.match(/(\d{1,2})/g)[0]);
            y = parseInt(row_y[column].innerText.match(/(\d{1,2})/g)[0]);
            break;
        case 3:
        case 4:
        case 5:
            // Column - OVR/POT/AGE
            x = parseInt(row_x[column].innerText);
            y = parseInt(row_y[column].innerText);
            break;
        case 7:
            // Column - PlayerValue
            try {
                x = parseInt(row_x[column].innerText.match(/(\d{1,3},\d{1,3},\d{1,3})/g)[0].replace(',',''));
            } 
            catch (error) {
                x = 0;
            }

            try {
                y = parseInt(row_y[column].innerText.match(/(\d{1,3},\d{1,3},\d{1,3})/g)[0].replace(',',''));
            } 
            catch (error) {
                y = 0;
            }
            break;
        default:
            break;
    }
    return [x,y];
}

function posToID(position) {
    let positions = [
        { position: 'GK',    posid: 0},
        { position: 'SW',    posid: 1},
        { position: 'RWB',    posid: 2},
        { position: 'RB',    posid: 3},
        { position: 'RCB',    posid: 4},
        { position: 'CB',    posid: 5},
        { position: 'LCB',    posid: 6},
        { position: 'LB',    posid: 7},
        { position: 'LWB',    posid: 8},
        { position: 'RDM',    posid: 9},
        { position: 'CDM',    posid: 10},
        { position: 'LDM',    posid: 11},
        { position: 'RM',    posid: 12},
        { position: 'RCM',    posid: 13},
        { position: 'CM',    posid: 14},
        { position: 'LCM',    posid: 15},
        { position: 'LM',    posid: 16},
        { position: 'RAM',    posid: 17},
        { position: 'CAM',    posid: 18},
        { position: 'LAM',    posid: 19},
        { position: 'RF',    posid: 20},
        { position: 'CF',    posid: 21},
        { position: 'LF',    posid: 22},
        { position: 'RW',    posid: 23},
        { position: 'RS',    posid: 24},
        { position: 'ST',    posid: 25},
        { position: 'LS',    posid: 26},
        { position: 'LW',    posid: 27},
        { position: 'SUB',    posid: 28},
        { position: 'RES',    posid: 29},
    ];

    for (let i = 0; i < positions.length; i++) {
        if (positions[i]['position'] == position) {
            return positions[i]['posid'];
        }
    };
}