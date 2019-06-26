window.globals.append_resource_link_id = function(url){
    if (!url.match(/resource_link_id/)) {
        var url_separator = (url.match(/\?/)) ? '&' : '?';
        return url + url_separator + 'resource_link_id=' + window.globals.RESOURCE_LINK_ID;
    }
    return url;
};

$(document).ajaxSend(function(event, jqxhr, settings){
    settings.url = window.globals.append_resource_link_id(settings.url);
});
