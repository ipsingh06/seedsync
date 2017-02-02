var mapColumnNameToId = {
    'filename' : 0,
    'status' : 1,
    'speed' : 2,
    'size' : 3,
    'transferred' : 4,
    'done' : 5,
    'commands' : 6
};

var drawProgressBar = function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            /* Turn the fifth column -- progress -- into a progressbar with jQuery UI styling */
            progressString = '<div class="progressbar-container"><div class="progressbar-number">'+aData[mapColumnNameToId.done]+'%</div><div class="progressbar"></div></div>';
            $('td:eq('+mapColumnNameToId.done+')', nRow).html(progressString);
            $('td:eq('+mapColumnNameToId.done+')', nRow).children('div').children('div.progressbar').progressbar({value : parseInt(aData[mapColumnNameToId.done])});
            $('td:eq('+mapColumnNameToId.done+')', nRow).children('div').children('div.progressbar').height(20);
            
            /* Truncate the file name */
            fullName = aData[mapColumnNameToId.filename];
            truncatedName = fullName.substring(0,35);
            titleString = '<div class="filename">'+truncatedName+'</div>';
            $('td:eq('+mapColumnNameToId.filename+')', nRow).html(titleString);
            $('td:eq('+mapColumnNameToId.filename+')', nRow).children('div').data('truncatedName',truncatedName);
            $('td:eq('+mapColumnNameToId.filename+')', nRow).children('div').data('fullName',fullName);
            $('td:eq('+mapColumnNameToId.filename+')', nRow).children('div').hover(
                function() { 
                    var $this = $(this); // caching $(this)
                    $this.text($this.data('fullName'));
                },
                function() { 
                    var $this = $(this); // caching $(this)
                    $this.text($this.data('truncatedName'));
                }
            );
            
            /* Generate command links */
            commandHTML = '<div class="commands">';
            commandHTML += '<a title="Add to queue" href="#" onclick=\'command_addToQueue("'+aData[mapColumnNameToId.filename]+'")\'>+</a>';
            commandHTML += '</div>';
            $('td:eq('+mapColumnNameToId.commands+')', nRow).html(commandHTML);
            
            return nRow;
}

$(document).ready( function () {
    $('#topTable').dataTable({
    "sScrollY": "90%",
    "bPaginate": false,
    "bFilter": false,
    "bScrollCollapse": true,
    "bInfo": false,
    "sAjaxSource": "/json/queued",
    "fnRowCallback": drawProgressBar,
    "bAutoWidth": false,
    "bStateSave": true,
    "bJQueryUI": true,
    "aoColumns": [
      { "sWidth": "30%" },
      { "sWidth": "13%" },
      { "sWidth": "12%" },
      { "sWidth": "10%" },
      { "sWidth": "10%" },
      { "sWidth": "20%" },
      { "sWidth": "5%" },
    ]
    });
    
    $('#bottomTable').dataTable({
    "sScrollY": "85%",
    "bPaginate": false,
    "bScrollCollapse": true,
    "bInfo": false,
    "sAjaxSource": "/json/all",
    "fnRowCallback": drawProgressBar,
    "bAutoWidth": false,
    "bDeferRender": true,
    "bStateSave": true,
    "bJQueryUI": true,
    "aoColumns": [
      { "sWidth": "30%" },
      { "sWidth": "13%" },
      { "sWidth": "12%" },
      { "sWidth": "10%" },
      { "sWidth": "10%" },
      { "sWidth": "20%" },
      { "sWidth": "5%" },
    ]
    });
    
    $( "#progressbar" ).progressbar();
    
    setInterval(reloadTopTable, 3000);
    setInterval(reloadBottomTable, 3000);
    $.fn.dataTableExt.sErrMode = 'throw';
} );

function reloadTopTable() {
    $('#topTable').dataTable().fnReloadAjax();
}
function reloadBottomTable() {
    $('#bottomTable').dataTable().fnReloadAjax();
}

function createDialog(title, text) {
    return $("<div class='dialog' title='" + title + "'><p>" + text + "</p></div>")
    .dialog({
        resizable: false,
        height: 250,
        width: 400,
        modal: true,
        buttons: {
            "Ok": function() {
                $( this ).dialog( "close" );
            },
        }
    }).css("font-size", "80%");;
}

function command_addToQueue(filename) {
    $.get('command/add/'+filename, function(data) {
        createDialog("Add to queue", data);
    });
}
