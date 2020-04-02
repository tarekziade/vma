
var dataPlan;

function fillTable() {
    var speed = getCookie('vma');

    $.getJSON("/api/plan?vma=" + speed, function( data ) {

    var plan = data.plan;
    $.each( plan.weeks, function(key, week) {

        var div = $('#plan').append('<div id="week-' + week.num + '"></div>');
        var title = div.append('<h3 class="ui header"> Semaine ' + week.num + ' / ' + week.type + '</h3>');
        var description = div.append('<p>Description de la semaine</p>')
        var table = div.append("<table class='ui celled table dataTable no-footer' id='tweek-" + week.num + "'></table>");


   var table = $('#tweek-' + week.num).DataTable({
    data: week.sessions,
    paging : false,
    searching : false,
    ordering : false,
    info : false,
       columns: [
        { title: 'Type', data: 'type' },
        { title: 'Description', data: 'description' },
        { title: 'Durée', data: 'duration' },
    ]
} );

    });
  });
};

