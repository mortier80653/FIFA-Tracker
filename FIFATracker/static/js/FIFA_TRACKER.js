$(document).ready(function(){
  selectizejs();
  updatePositions();
  updateStrongFoot();
  updateWorkrates();
  changeCurrency();
  changeUnits();
  convertUnits();
  changeProfilePublicStatus();
  cleanUrl();
  careerFileUpload();
});

function careerFileUpload() {
    /* https://simpleisbetterthancomplex.com/tutorial/2016/11/22/django-multiple-file-upload-using-ajax.html */

    $(".js-upload-career-save").click(function () {
      $("#fileupload").click();
    });
  
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
        }
      }
    });
};

function selectizejs() {
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
                url: 'ajax/leagues/',
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
                    url: 'ajax/leagues/',
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
    var available_positions = ['GK', 'SW', 'RWB', 'RB', 'RCB', 'CB', 'LCB', 'LB', 'LWB', 'RDM', 'CDM', 'LDM', 'RM', 'RCM', 'CM', 'LCM', 'LM', 'RAM', 'CAM', 'LAM', 'RF', 'CF', 'LF', 'RW', 'RS', 'ST', 'LS', 'LW', 'SUB', 'RES']
    
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
    var params = ["isretiring", "isreal", "isonloan", "teamtype", "iscputransfer", "isloan", "isloanbuy", "issnipe", "result"];
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