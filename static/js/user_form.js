const dataset = document.currentScript.dataset;

const formsetContainer = document.getElementById("phone-number-formset");
const addFormButton = document.getElementById("add-phone-number-form");


addFormButton.addEventListener("click", e => {
    addNewFormInFormSet()
});


function addNewFormInFormSet() {
    /* Додає до формсету нову форму для ведення номеру телефону користувача. */

    const formCount = document.getElementById('id_phone_numbers-TOTAL_FORMS');
    const currentCount = parseInt(formCount.value, 10);

    const newForm = formsetContainer.lastElementChild.cloneNode(true);

    // очищаємо форму
    newForm.querySelector("label[for=id_number]").textContent = `${dataset.phoneNumberLabel} ${currentCount + 1}`;
    newForm.querySelectorAll("input").forEach(input => input.value = "");

    const errorList = newForm.querySelector(".errorlist");
    if (errorList) {
        newForm.children[0].removeChild(errorList);
    }

    const regex = new RegExp(`-${currentCount - 1}-`, "g");
    newForm.innerHTML = newForm.innerHTML.replace(regex, `-${currentCount}-`);
    newForm.innerHTML = newForm.innerHTML.replace(/-__prefix__-/g, `-${currentCount}-`);

    formsetContainer.appendChild(newForm);

    formCount.value = currentCount + 1;
}