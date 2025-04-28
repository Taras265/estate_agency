/*
У цьому файлі знаходиться функціонал для сторінки з списком (таблицею)
обʼєктів нерухомості.
*/
const RealEstateType = Object.freeze({
    APARTMENT: 1,
    COMMERCE: 2,
    HOUSE: 3,
});

const dataset = document.currentScript.dataset;

const setStatusSoldBtns = document.querySelectorAll(".btn-set-status-sold");


setStatusSoldBtns.forEach(btn => {
    btn.addEventListener("click", e => {
        const realEstateId = e.currentTarget.dataset.id;
        const url = `${dataset.mainUrl}objects/set-status-sold/${realEstateId}?type=${dataset.realEstateType}`;

        fetch(url, {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            mode: "same-origin",
            body: {},
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    btn.nextElementSibling.classList.remove("d-none");
                    btn.classList.add("d-none");
                }
            })
            .catch(error => {
                console.log(error.message);
            });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}