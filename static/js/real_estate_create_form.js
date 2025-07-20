/*
У цьому файлі знаходиться функціонал для сторінки з 
формою створення обʼєкта нерухомості.
*/

const realEstateTypeSelect = document.getElementById("real-estate-type-select");


// передвстановлюємо значення для випадаючого списку з типами нерухості
setSelectedRealEstateType(dataset.realEstateType);


realEstateTypeSelect.addEventListener("change", async e => {
    /* 
    Перенаправляє користувача на сторінку з формою створення 
    нового обʼєкту нерухомості в залежності від обраного значення
    з випадаючого списку realEstateTypeSelect.
    */
    const realEstateType = parseInt(e.target.value);
    let url = dataset.mainUrl;

    switch (realEstateType) {
        case RealEstateType.APARTMENT:
            url += "objects/base/create/apartment"
            break;
        case RealEstateType.COMMERCE:
            url += "objects/base/create/commerce"
            break;
        case RealEstateType.HOUSE:
            url += "objects/base/create/house"
            break;
        case RealEstateType.LAND:
            url += "objects/base/create/land"
            break;
        default:
            return;
    }
    window.location.href = url;
});


function setSelectedRealEstateType(type) {
    /*
    Встановлює значення для випадаючого списку з типами нерухості 
    в залежності від значення query параметра "type".
    Аргументи:
    1) type - number
    */
    $("select[name=real-estate-type]").selectpicker("val", type.toString());
}