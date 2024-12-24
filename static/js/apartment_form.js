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

    const btnVerifyAddress = document.getElementById("btn-verify-address");

    btnVerifyAddress.addEventListener("click", async e => {
        const localitySelect = document.getElementById("id_locality");
        const locality = localitySelect.options[localitySelect.selectedIndex].text;

        const streetSelect = document.getElementById("id_street");
        const street = streetSelect.options[streetSelect.selectedIndex].text;

        const house = document.getElementById("id_house").value;
        const apartment = document.getElementById("id_apartment").value;

        const url = `/en/objects/verify-address?locality=${locality}&street=${street}&house=${house}&apartment=${apartment}`

        fetch(url)
            .then(response => response.json())
            .then(data => {
                btnVerifyAddress.nextSibling.textContent = data.message;
            })
            .catch(console.error);
    });
});