const dataset = document.currentScript.dataset;

const localityDistrictSelect = $("#id_locality_district");
const streetSelect = $("#id_street");

localityDistrictSelect.on("changed.bs.select", function (e, clickedIndex, isSelected, prevVal) {
    const selectedIds = localityDistrictSelect.selectpicker("val");
    console.log(selectedIds);
    const queryString = selectedIds.map(districtId => `locality_district=${districtId}`).join("&")

    // заповнення випадаючого списку з вулицями міст лише тими вулицями,
    // які належать обраним районам міст
    const streetsURL = `${dataset.mainUrl}handbooks/load_streets/?${queryString}`;
    fetch(streetsURL)
        .then(response => response.json())
        .then(data => {
            if (data.success === true) {
                const options = data.streets.map(item => $("<option>", {
                    value: item.id, text: item.street
                }));
                setSelectBoxOptions(streetSelect, options);
            }
        });
});

function setSelectBoxOptions(selectBox, options) {
    /* Знищує <selectBox>, потім ініціалізує та заповнює елементами з <options>  */
    selectBox.empty();
    selectBox.selectpicker("destroy");
    selectBox.selectpicker();
    options.forEach(option => selectBox.append(option))
    selectBox.selectpicker("refresh");
}
