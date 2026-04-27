(function () {
    var STORAGE_KEY = 'iw26-active-venue';
    var TABBED_PAGES = ['program.html', 'map.html', 'usinfo.html'];

    function onReady(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
            return;
        }

        callback();
    }

    function normalizeVenue(value) {
        return (value || '').toString().replace(/^#/, '').replace(/-info$/, '');
    }

    function getStoredVenue() {
        try {
            return normalizeVenue(window.localStorage.getItem(STORAGE_KEY));
        } catch (error) {
            return '';
        }
    }

    function setStoredVenue(venue) {
        if (!venue) {
            return;
        }

        try {
            window.localStorage.setItem(STORAGE_KEY, venue);
        } catch (error) {
            // Some browser privacy modes disable localStorage; the URL hash still works.
        }
    }

    function getTabTarget(tab) {
        return tab.getAttribute('data-target') || '';
    }

    function findVenueTarget(value) {
        var cleanValue = (value || '').toString().replace(/^#/, '');
        var venue = normalizeVenue(cleanValue);
        var candidates = [];
        var tabs = document.querySelectorAll('.venue-tab');
        var i;
        var j;

        if (cleanValue) {
            candidates.push(cleanValue);
        }

        if (venue) {
            candidates.push(venue);
            candidates.push(venue + '-info');
        }

        for (i = 0; i < candidates.length; i++) {
            for (j = 0; j < tabs.length; j++) {
                if (getTabTarget(tabs[j]) === candidates[i] && document.getElementById(candidates[i])) {
                    return candidates[i];
                }
            }
        }

        return '';
    }

    function isTabbedPageHref(href) {
        var path;
        var i;

        if (!href || href.charAt(0) === '#') {
            return false;
        }

        path = href.split('#')[0].split('?')[0];

        for (i = 0; i < TABBED_PAGES.length; i++) {
            if (path === TABBED_PAGES[i] || path.slice(-TABBED_PAGES[i].length - 1) === '/' + TABBED_PAGES[i]) {
                return true;
            }
        }

        return false;
    }

    function updateTabbedPageLinks(venue) {
        var links = document.querySelectorAll('a[href]');
        var suffix = venue ? '#' + venue : '';
        var i;
        var href;

        for (i = 0; i < links.length; i++) {
            href = links[i].getAttribute('href');

            if (isTabbedPageHref(href)) {
                links[i].setAttribute('href', href.split('#')[0] + suffix);
            }
        }
    }

    function updateHash(venue) {
        var nextUrl;

        if (!venue || !window.history || !window.history.replaceState) {
            return;
        }

        if (window.location.hash === '#' + venue) {
            return;
        }

        nextUrl = window.location.href.split('#')[0] + '#' + venue;
        window.history.replaceState(null, '', nextUrl);
    }

    function activateVenueTab(value, shouldUpdateHash) {
        var target = findVenueTarget(value);
        var venue = normalizeVenue(target);
        var tabs;
        var contents;
        var i;

        if (!target) {
            return false;
        }

        tabs = document.querySelectorAll('.venue-tab');
        contents = document.querySelectorAll('.venue-content');

        for (i = 0; i < tabs.length; i++) {
            tabs[i].classList.toggle('active', getTabTarget(tabs[i]) === target);
        }

        for (i = 0; i < contents.length; i++) {
            contents[i].classList.toggle('active', contents[i].id === target);
        }

        setStoredVenue(venue);
        updateTabbedPageLinks(venue);

        if (shouldUpdateHash) {
            updateHash(venue);
        }

        return true;
    }

    function getFallbackTarget() {
        var activeTab = document.querySelector('.venue-tab.active');
        var firstTab = document.querySelector('.venue-tab');

        if (activeTab) {
            return getTabTarget(activeTab);
        }

        if (firstTab) {
            return getTabTarget(firstTab);
        }

        return '';
    }

    function syncVenueTabsFromState() {
        var hashVenue = normalizeVenue(window.location.hash);
        var storedVenue = getStoredVenue();

        if (hashVenue && activateVenueTab(hashVenue, false)) {
            return;
        }

        if (storedVenue && activateVenueTab(storedVenue, true)) {
            return;
        }

        activateVenueTab(getFallbackTarget(), false);
    }

    onReady(function () {
        var tabs = document.querySelectorAll('.venue-tab');
        var i;

        if (!tabs.length) {
            return;
        }

        for (i = 0; i < tabs.length; i++) {
            tabs[i].addEventListener('click', function () {
                activateVenueTab(getTabTarget(this), true);
            });
        }

        syncVenueTabsFromState();

        window.addEventListener('hashchange', function () {
            syncVenueTabsFromState();
        });

        window.addEventListener('pageshow', function () {
            updateTabbedPageLinks(getStoredVenue() || normalizeVenue(getFallbackTarget()));
        });
    });
}());
