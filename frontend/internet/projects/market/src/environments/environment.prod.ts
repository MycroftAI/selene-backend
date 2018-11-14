export const environment = {
    chatUrl: 'https://chat.mycroft.ai',
    forumUrl: 'https://forum.mycroft.ai',
    singleSignOnUrl: 'https://sso.mycroft.ai',
    accountUrl: 'https://home.mycroft.ai',
    marketplaceUrl: 'https://market.mycroft.ai',
    translateUrl: 'https://translate.mycroft.ai',
    wordpressUrl: 'https://test.mycroft.ai'
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
