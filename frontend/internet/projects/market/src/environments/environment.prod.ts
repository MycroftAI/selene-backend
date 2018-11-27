export const environment = {
    production: true,
    mycroftUrls: {
        chat: 'https://chat.mycroft.ai',
        forum: 'https://community.mycroft.ai',
        singleSignOn: 'https://sso.mycroft.ai',
        account: 'https://home.mycroft.ai',
        marketplace: 'https://market.mycroft.ai',
        mimic: 'https://mimic.mycroft.ai',
        translate: 'https://translate.mycroft.ai',
        wordpress: 'https://mycroft.ai'
    }
};

document.write(
    '<script async src="https://www.googletagmanager.com/gtag/js?id=UA-101772425-10"></script>'
);
document.write(
    '<script>' +
    'window.dataLayer = window.dataLayer || []; ' +
    'function gtag(){dataLayer.push(arguments);} ' +
    'gtag("js", new Date());' +
    'gtag("config", "UA-101772425-10"); ' +
    '</script>'
);
