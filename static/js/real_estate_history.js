const myOrOthersRealEstateSelect = $("#id_whose_real_estate");
const realtorSelect = $("#id_realtor");
const minDateCalendar = document.querySelector("#id_history_date_min");
const maxDateCalendar = document.querySelector("#id_history_date_max");

document.addEventListener("DOMContentLoaded", function () {
    // робимо неактивним поле "Рієлтор",
    // тому що поле "Чия нерухомість" має значення "Моя" за замовчуванням
    if (myOrOthersRealEstateSelect.selectpicker("val") == "my") {
        realtorSelect.prop("disabled", true);
        realtorSelect.selectpicker("refresh");
    }
});

myOrOthersRealEstateSelect.on("changed.bs.select", function (e, clickedIndex, isSelected, prevVal) {
    // робить активним чи неактивним поле "Рієлтор"
    // в залежності від обраного значення у полі "Чия нерухомість"
    const value = myOrOthersRealEstateSelect.selectpicker("val");
    if (value === "my") {
        realtorSelect.selectpicker("deselectAll");
        realtorSelect.prop("disabled", true);
    } else {
        realtorSelect.prop("disabled", false);
    }
    realtorSelect.selectpicker("refresh");
});

minDateCalendar.addEventListener("input", function (e) {
    maxDateCalendar.min = minDateCalendar.value;
});

maxDateCalendar.addEventListener("input", function (e) {
    minDateCalendar.max = maxDateCalendar.value;
});