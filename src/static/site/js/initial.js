var langMap = {
   'en' : 'English',
   'es-ES' : 'Spanish',
}

function getLanguage() {
    var lang = navigator.language || navigator.userLanguage;
    return '//cdn.datatables.net/plug-ins/1.10.19/i18n/'+langMap[lang]+'.json'
}