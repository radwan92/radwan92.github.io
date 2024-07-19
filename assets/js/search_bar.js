function searchData() {
    let input = document.getElementById('search-bar');
    let filter = input.value.toUpperCase();
    let dataGrid = document.getElementsByClassName('data-grid')[0];
    let dataCells = dataGrid.getElementsByClassName('data-cell');

    for (let i = 0; i < dataCells.length; i++) {
        let dataName = dataCells[i].getAttribute('data-name');
        if (!dataName) {
            continue;
        }

        dataName = dataName.toUpperCase();
        found = dataName.indexOf(filter) >= 0;
        if (found) {
            dataCells[i].style.display = "";
        } else {
            dataCells[i].style.display = "none";
        }
    }
}

function clearSearch() {
    let input = document.getElementById('search-bar');
    input.value = '';
    searchData();
}