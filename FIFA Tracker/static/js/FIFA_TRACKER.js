function updatePositions() {
    var available_positions = ['GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW']
    
    $('.player-position').each(function() {
        var content = $(this).html();
        console.log(content)
        var posIDsArray = $(this).text().match(/(\d{1,2})/g);
        var re = "";
        for (var posID of posIDsArray) { 
            re = new RegExp("(^|[\\s])("+posID+"{1})([\\s]|$)", "g");
            content = content.replace(re, "$1"+available_positions[posID]+"$3")
        }
         $(this).html(content); 
    });
}

function updateStrongFoot() {
    $('.strong-foot').each(function() {
        var content = $(this).text();
        if (content == "1") {
            $(this).text("Right");
        } else {
            $(this).text("Left");
        }
    });
}

function updateWorkrates() {
    $('.workrate').each(function() {
        var content = $(this).text();
        if (content == "2") {
            $(this).text("High");
        } else if (content== "1") {
            $(this).text("Low");
        } else {
            $(this).text("Medium");
        }
    });
}

function faceNotFound(image, path) {
    image.onerror = "";
    image.src = path + "img/assets/heads/p0.png";
    return true;
}