document.addEventListener('DOMContentLoaded', function () {
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    function checkAndSetUUID() {
        const sessionUUIDKey = 'sessionUUID';
        let uuid = sessionStorage.getItem(sessionUUIDKey);

        if (!uuid) {
            uuid = generateUUID();
            sessionStorage.setItem(sessionUUIDKey, uuid);
        }
        return uuid;
    }
    const sessionUUID = checkAndSetUUID();

    const search_link_1 = document.getElementById('search_test_1');
    const search_link_2 = document.getElementById('search_test_2');
    let search_href_1 = search_link_1.getAttribute('href');
    search_href_1 += '?gu=' + sessionUUID;
    search_link_1.setAttribute('href', search_href_1);
    let search_href_2 = search_link_2.getAttribute('href');
    search_href_2 += '?gu=' + sessionUUID;
    search_link_2.setAttribute('href', search_href_2);

    console.log(`visitor uuid: ${sessionUUID}`);
});