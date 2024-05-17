document.addEventListener("DOMContentLoaded", function() {
    const pathname = window.location.pathname;
    const selectRoles = document.querySelector('#rolesSelect');
    const selectMembers = document.querySelector('#membersSelect');
    const searchForm = document.querySelector('#searchForm');
    const searchInput = document.querySelector('#searchInput');
    const urlParams = new URLSearchParams(window.location.search);
    const searchInputValue = urlParams.get('search_input');
    if (searchInputValue) {
        searchInput.value = searchInputValue;
    }

    if (selectRoles) {
        selectRoles.addEventListener("change", function(e) {
            redirectToUrl();
        });
    }
    
    if (selectMembers) {
        selectMembers.addEventListener("change", function(e) {
            redirectToUrl();
        });
    }
    
    if (searchForm) {
        searchForm.addEventListener("submit", function(e) {
            e.preventDefault();
            redirectToUrl();
        });
    }

    function redirectToUrl() {
        const params = {};
        const searchValue = searchInput.value.trim();
        if (searchValue) {
            params["search_input"] = searchValue;
        }
        if (selectRoles && selectRoles.value) {
            params["dep"] = selectRoles.value; 
        }
        if (selectMembers && selectMembers.value) {
            params["member"] = selectMembers.value;
        }

        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? pathname + "?" + queryString : pathname;
        window.location.replace(url);
    }
});