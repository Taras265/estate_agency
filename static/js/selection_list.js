const localitySelect = $("#id_locality");
const localityDistrictSelect = $("#id_locality_district");


localitySelect.on("changed.bs.select", function (e, clickedIndex, isSelected, prevVal) {
    const selectedIds = localitySelect.selectpicker("val");
    const queryString = selectedIds.map(localityId => `locality=${localityId}`).join("&");

    // заповнення випадаючого списку з районами міст лише тими районами,
    // які належать обраним містам
    const localityDistrictsURL = `/en/load_locality_districts/?${queryString}`;
    fetch(localityDistrictsURL)
        .then(response => response.json())
        .then(data => {
            if (data.success === true) {
                const options = data.districts.map(item => $("<option>", {
                    value: item.id, text: item.district
                }));
                setSelectBoxOptions(localityDistrictSelect, options);
            }
        })

    // заповнення випадаючого списку з вулицями міст лише тими вулицями,
    // які належать обраним містам
    const streetsURL = `/en/load_streets/?${queryString}`;
    fetch(streetsURL)
        .then(response => response.json())
        .then(data => {
            if (data.success === true) {
                const options = data.streets.map(item => $("<option>", {
                    value: item.id, text: item.street
                }));
                setSelectBoxOptions($("#id_street"), options);
            }
        })
})

localityDistrictSelect.on("changed.bs.select", function (e, clickedIndex, isSelected, prevVal) {
    const selectedIds = localityDistrictSelect.selectpicker("val");
    const queryString = selectedIds.map(districtId => `locality_district=${districtId}`).join("&")

    // заповнення випадаючого списку з вулицями міст лише тими вулицями,
    // які належать обраним районам міст
    const streetsURL = `/en/load_streets/?${queryString}`;
    fetch(streetsURL)
        .then(response => response.json())
        .then(data => {
            if (data.success === true) {
                const options = data.streets.map(item => $("<option>", {
                    value: item.id, text: item.street
                }));
                setSelectBoxOptions($("#id_street"), options);
            }
        })
})


function setSelectBoxOptions(selectBox, options) {
    /* Знищує <selectBox>, потім ініціалізує та заповнює елементами з <options>  */
    selectBox.empty();
    selectBox.selectpicker("destroy");
    selectBox.selectpicker();
    options.forEach(option => selectBox.append(option))
    selectBox.selectpicker("refresh");
}