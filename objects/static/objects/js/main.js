const btnVerifyAddress = document.getElementById("btn-verify-address");

btnVerifyAddress.addEventListener("click", async e => {
    const localitySelect = document.getElementById("id_locality");
    const locality = localitySelect.options[localitySelect.selectedIndex].text;

    const streetSelect = document.getElementById("id_street");
    const street = streetSelect.options[streetSelect.selectedIndex].text;

    const house = document.getElementById("id_house").value;
    const apartment = document.getElementById("id_apartment").value;

    const url = `http://localhost:8000/en/objects/verify-address?locality=${locality}&street=${street}&house=${house}&apartment=${apartment}`

    fetch(url)
        .then(response => response.json())
        .then(data => {
            btnVerifyAddress.nextSibling.textContent = data.message;
        })
        .catch(console.error);
});