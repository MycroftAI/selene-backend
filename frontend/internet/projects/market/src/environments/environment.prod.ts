export const environment = {
    production: true,
    loginUrl: 'https://login.mycroft.ai'
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
