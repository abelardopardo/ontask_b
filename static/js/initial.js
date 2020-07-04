var langMap = {
   'en' : 'English',
   'es-ES' : 'Spanish',
   'es' : 'Spanish',
   'zh-CN' : 'Chinese',
   'zh' : 'Chinese',
   'fi' : 'Finnish',
}

function getLanguage() {
    var lang = navigator.language || navigator.userLanguage;
    if (!(lang in langMap)) {
      lang = 'en';
    }
    return '//cdn.datatables.net/plug-ins/1.10.21/i18n/'+langMap[lang]+'.json'
}
