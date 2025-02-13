/*
У цьому файлі знаходиться спільний функціонал для сторінки з 
формою (створення та редагування) обʼєкта нерухомості.
*/

const RealEstateType = Object.freeze({
    APARTMENT: 1,
    COMMERCE: 2,
    HOUSE: 3,
});

const dataset = document.currentScript.dataset;

const btnVerifyAddress = document.getElementById("btn-verify-address");
const btnEditOwner = document.getElementById("btn-edit-owner");
const btnFillAddress = document.getElementById("btn-fill-address");
const localitySelect = document.getElementById("id_locality");
const streetSelect = document.getElementById("id_street");
const houseInput = document.getElementById("id_house");
const apartmentInput = document.getElementById("id_apartment");
const premisesInput = document.getElementById("id_premises");
const housingInput = document.getElementById("id_housing");
const ownerSelect = document.getElementById("id_owner");

document.addEventListener('DOMContentLoaded', () => {
    const formsetContainer = document.getElementById('photo-formset');
    const addFormButton = document.getElementById('add-photo-form');

    addFormButton.addEventListener('click', () => {
        const formCount = document.getElementById('id_images-TOTAL_FORMS');
        console.log(formCount);
        const currentCount = parseInt(formCount.value, 10);
        console.log(currentCount);
        const newForm = formsetContainer.lastElementChild.cloneNode(true);
        console.log(newForm);

        const regex = new RegExp(`-${currentCount - 1}-`, 'g');
        newForm.innerHTML = newForm.innerHTML.replace(regex, `-${currentCount}-`);
        newForm.innerHTML = newForm.innerHTML.replace(/-__prefix__-/g, `-${currentCount}-`);

        newForm.querySelectorAll('input').forEach(input => input.value = '');

        formsetContainer.appendChild(newForm);

        formCount.value = currentCount + 1;
    });

    // передвстановлюємо посилання на сторінку з формою редагування власника квартири
    setOwnerEditFormUrl(ownerSelect.value);
});


btnVerifyAddress.addEventListener("click", async e => {
    verifyRealEstateAddress(parseInt(dataset.realEstateType));
});

ownerSelect.addEventListener("change", async e => {
    setOwnerEditFormUrl(e.target.value);
});

btnFillAddress.addEventListener("click", async e => {
    fillApartmentAddress();
});


function verifyRealEstateAddress(realEstateType) {
    /* 
    Перевіряє, чи існує обʼєкт нерухомості з типом realEstateType за введенною
    адресою (localityId, streetId, house, apartment|premises|housing)
    і виводить отримане повідомлення користувачу.
    Аргументи:
    1) realEstateType - number
    */
    const localityErrorDiv = document.querySelector("#locality-error");
    const streetErrorDiv = document.querySelector("#street-error");
    const houseErrorDiv = document.querySelector("#house-error");
    const apartmentErrorDiv = document.querySelector("#apartment-error")
    const premisesErrorDiv = document.querySelector("#premises-error")
    const housingErrorDiv = document.querySelector("#housing-error")

    // очищуємо поля для повідомлення та помилок
    btnVerifyAddress.nextSibling.textContent = "";
    localityErrorDiv.textContent = "";
    streetErrorDiv.textContent = "";
    houseErrorDiv.textContent = "";

    if (apartmentErrorDiv != null)
        apartmentErrorDiv.textContent = "";
    else if (premisesErrorDiv != null)
        premisesErrorDiv.textContent = "";
    else if (housingErrorDiv != null)
        housingErrorDiv.textContent = "";

    // отримуємо введені дані адреси
    const localityId = localitySelect.value;
    const streetId = streetSelect.value;
    const house = houseInput.value;

    let url =
        dataset.mainUrl +
        `objects/verify-address?type=${realEstateType}&locality=${localityId}&street=${streetId}&house=${house}`

    switch (realEstateType) {
        case RealEstateType.APARTMENT:
            apartment = apartmentInput.value; // квартира
            url += `&apartment=${apartment}`;
            break;
        case RealEstateType.COMMERCE:
            premises = premisesInput.value; // приміщення
            url += `&premises=${premises}`;
            break;
        case RealEstateType.HOUSE:
            housing = housingInput.value; // корпус
            url += `&housing=${housing}`;
            break;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success === true) {
                // виводимо повідомлення
                btnVerifyAddress.nextSibling.textContent = data.message;
                return;
            }
            errors = data.errors;

            // виводимо помилки
            if (errors.locality)
                localityErrorDiv.textContent = errors.locality[0].message;
            if (errors.street)
                streetErrorDiv.textContent = errors.street[0].message;
            if (errors.house)
                houseErrorDiv.textContent = errors.house[0].message;
            if (errors.apartment)
                apartmentErrorDiv.textContent = errors.apartment[0].message;
            if (errors.premises)
                premisesErrorDiv.textContent = errors.premises[0].message;
            if (errors.housing)
                housingErrorDiv.textContent = errors.housing[0].message;
        })
        .catch(error => {
            console.log(error.message);
        });
}

function setOwnerEditFormUrl(ownerId) {
    /* 
    Встановлює значення атрибуту href кнопки btnEditOwner таке, щоб
    воно посилалося на сторінку з формою редагування власника квартири, 
    якого зараз обрали в формі.
    Аргументи:
    1) ownerId - number
    */
    if (ownerId !== "") {
        btnEditOwner.href = dataset.mainUrl + `handbooks/sale/update/client/${ownerId}/`;
        btnEditOwner.style.pointerEvents = "auto";
    } else {
        btnEditOwner.href = "";
        btnEditOwner.style.pointerEvents = "none";
    }
}

function fillApartmentAddress() {
    /* 
    Заповнює інші поля форми для адреси квартири, спираючись на 
    вже заповнені поля адреси. Наприклад, якщо користувач обрав вулицю, 
    то автоматично заповнює поле форми для міста.
    */
    const streetId = streetSelect.value;

    if (!streetId) {
        $("select[name=locality]").selectpicker("val", "");
        return;
    }

    const url = dataset.mainUrl + `objects/fill-address?street=${streetId}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                $("select[name=locality]").selectpicker("val", data.locality.toString());
            }
        })
        .catch(console.error)
}