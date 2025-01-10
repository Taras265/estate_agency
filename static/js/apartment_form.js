const dataset = document.currentScript.dataset;

const btnVerifyAddress = document.getElementById("btn-verify-address");
const btnEditOwner = document.getElementById("btn-edit-owner");
const btnFillAddress = document.getElementById("btn-fill-address");
const localitySelect = document.getElementById("id_locality");
const streetSelect = document.getElementById("id_street");
const houseInput = document.getElementById("id_house");
const apartmentInput = document.getElementById("id_apartment");
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
    verifyApartmentAddress();
});

ownerSelect.addEventListener("change", async e => {
    setOwnerEditFormUrl(e.target.value);
});

btnFillAddress.addEventListener("click", async e => {
    fillApartmentAddress();
});


function verifyApartmentAddress() {
    /* Перевіряє, чи існує квартира з введенними даними (localityId, streetId, house, apartment)
    і виводить отримане повідомлення користувачу.
    */
    const localityId = localitySelect.value;
    const streetId = streetSelect.value;
    const house = houseInput.value;
    const apartment = apartmentInput.value;

    const url = dataset.mainUrl + `objects/verify-address?localityId=${localityId}&streetId=${streetId}&house=${house}&apartment=${apartment}`

    fetch(url)
        .then(response => response.json())
        .then(data => {
            btnVerifyAddress.nextSibling.textContent = data.message;
        })
        .catch(console.error);
}

function setOwnerEditFormUrl(ownerId) {
    /* Встановлює значення атрибуту href кнопки btnEditOwner таке, щоб
    воно посилалося на сторінку з формою редагування власника квартири, 
    якого зараз обрали в формі.
    Аргументи:
    1) ownerId - number
    */
    if (ownerId !== "") {
        btnEditOwner.href = dataset.mainUrl + `handbooks/base/update/client/${ownerId}/`;
        btnEditOwner.style.pointerEvents = "auto";
    } else {
        btnEditOwner.href = "";
        btnEditOwner.style.pointerEvents = "none";
    }
}

function fillApartmentAddress() {
    /* Заповнює інші поля форми для адреси квартири, спираючись на 
    вже заповнені поля адреси. Наприклад, якщо користувач обрав вулицю, 
    то автоматично заповнює поле форми для міста.
    */
    const streetId = streetSelect.value;

    if (!streetId) {
        $("select[name=locality]").selectpicker("val", "0");
        return;
    }

    const url = dataset.mainUrl + `objects/fill-address?streetId=${streetId}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.localityId !== -1) {
                $("select[name=locality]").selectpicker("val", data.localityId.toString());
            }
        })
        .catch(console.error)
}