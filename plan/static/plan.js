var getUrlParameter = function getUrlParameter(sParam) {
  var sPageURL = window.location.search.substring(1),
      sURLVariables = sPageURL.split('&'),
      sParameterName,
      i;

  for (i = 0; i < sURLVariables.length; i++) {
      sParameterName = sURLVariables[i].split('=');
      if (sParameterName[0] === sParam) {
          return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
      }
  }
};


function fillTable (race, weeks, spw, level, cross) {
  const speed = getCookie('vma');
  const hrmax = getCookie('hrmax');
  const gender = getCookie('gender');
  const age = getCookie('age');

  $('#plan').empty()

  var hash = getUrlParameter('hash');
  var url;
  if (hash) {
    url  = '/api/plan?hash=' + hash;
  } else {
    url = '/api/plan?vma=' + speed + '&race=' + race + '&weeks=' + weeks +
          '&spw=' + spw + '&level=' + level + '&cross=' + cross + '&hrmax=' + hrmax
          + '&gender=' +  gender + '&age=' + age;
  }

  $.getJSON(url, function (data) {
    const plan = data.plan

    $('#planTitle').text(plan.title)
    $('#plan').append('<p>' + plan.description + '</p>')
    $('#plan').append('<p><a href="/plan?hash='+ plan.hash +'">Lien permanent vers ce plan</a></p>')
    $.each(plan.weeks, function (key, week) {
      const div = $('#plan').append('<div id="week-' + week.num + '"></div>')
      div.append('<h3 class="ui header"><i class="arrow alternate circle right outline icon"></i>Semaine ' + week.num + ' | ' + week.type + '</h3>')
      div.append('<p>' + week.description + '</p>')
      div.append("<table class='ui celled table dataTable no-footer' id='tweek-" + week.num + "'></table>")

      $('#tweek-' + week.num).DataTable({
        data: week.sessions,
        paging: false,
        searching: false,
        ordering: false,
        info: false,
        columns: [
          { title: 'Séance', data: 'num' },
          { title: 'Type', data: 'type' },
          { title: 'Description', data: 'description' },
          { title: 'Durée', data: 'duration' },
          { title: 'Volume', data: 'distance' }
        ]
      })
    })
  })
};
