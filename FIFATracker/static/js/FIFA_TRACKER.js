$(document).ready(function(){
  updatePositions();
  updateStrongFoot();
  updateWorkrates();
  changeCurrency();
  changeUnits();
  convertUnits();
  changeProfilePublicStatus();
  cleanUrl();
})

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
    var available_positions = ['GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW']
    
    $('.player-position').each(function() {
        var content = $(this).html();
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
    var params = ["isretiring", "isreal", "isonloan"];
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