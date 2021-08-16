const submit = document.getElementById("submit-btn")


function addData(data)
{
    for (var key in data) {

    }
}

function fetchData(elem, _)
{
    const form = document.getElementById("masterform")
    const data = new URLSearchParams(new FormData(form));
    console.log("Form is", data)
    fetch('/show', {
        method: 'POST',
        body: data
    })
    .then(response => response.json())
    .then(data => {
        addData(JSON.parse(data))
    })
    .catch(err => console.log(err))
}

submit.addEventListener("click", fetchData)