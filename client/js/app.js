const form = document.getElementById("master_form")
const submit_btn = document.getElementById("submit_btn")
const statusLabel = document.getElementById("status")
const content = document.getElementById("content")
const masterKey = document.getElementById("master_key")


function insertUserRow(user) {
    const table = document.getElementById("table_view")
    html =
        `<tr id="entry">
        <th>${user.id}</th>
        <th><input value="${user.name}" onfocusout="updateUser(event, ${user.id}, 'name', this);"></input></th>
        <th><input value="${user.email}" onfocusout="updateUser(event, ${user.id}, 'email', this);"></input></th>
        <th>...${user.key.slice(220, 256)}</th>
        <th><input value="${user.suspended}" onfocusout="updateUser(event, ${user.id}, 'suspended', this);"></input></th>
        <th>${user.creation_date}</th>
        <th>
            <button onclick="deleteUser(event,${user.id});">DELETE</button><br>
        </th>
    </tr>`
    table.innerHTML += html
}

function insertTokenRow(token) {
    const table = document.getElementById("table_view")
    html =
        `<tr id="entry">
        <th>${token.id}</th>
        <th>...${token.token.slice(1000, 1024)}</th>
        <th>${token.creation_date}</th>
        <th>
            <button onclick="deleteToken(event,${token.id});">DELETE</button>
        </th>
    </tr>`
    table.innerHTML += html
}

function addUserTable() {
    content.innerHTML =
        `<table id="table_view">
        <tr id="entry">
            <th>id</th>
            <th>name</th>
            <th>email</th>
            <th>key</th>
            <th>suspended</th>
            <th>creation date</th>
            <th>Manage</th>
        </tr>
    </table>`
}

function addTokenTable() {
    content.innerHTML =
        `<table id="table_view">
        <tr id="entry">
            <th>id</th>
            <th>token</th>
            <th>creation date</th>
            <th>Manage</th>
        </tr>
    </table>`
}

function resetTable() {
    content.innerHTML = ''
}

function addData(data, action) {
    if (action === "showusers")
        addUserTable()
    else if (action === "showtokens")
        addTokenTable()

    for (i in data) {
        obj = data[i]
        if (action === "showusers")
            insertUserRow(obj)
        else if (action === "showtokens")
            insertTokenRow(obj)
    }
}

function requestDeleteUser(userid) {
    fetch(`http://localhost:31563/api/user/${userid}/delete`, {
        method: 'POST',
        body: JSON.stringify({
            "master_key": masterKey.value
        })
    })
        .then(response => {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response.json();
        }).then(response => {
            alert(response["status"])

        }).catch(error => {
            console.log('Error is', error);
        });
}

function flashText(element) {
    console.log(element.style.color)
    if (element.style.color == "rgb(39, 174, 96)") {
        element.style.color = "black";
    }else {
        console.log("here1")
        element.style.color = "rgb(39, 174, 96)";
    }
}

function updateUser(event, userid, field_type, element) {
    event.preventDefault()

    data = {
        "master_key": masterKey.value,
    }
    data[field_type] = element.value
    console.log(data)
    fetch(`http://localhost:31563/api/user/${userid}`, {
        method: 'PATCH',
        body: JSON.stringify(data)
    })
        .then(response => {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response.json();
        }).then(response => {
            flashText(element)
            setTimeout(flashText, 700, element)

        }).catch(error => {
                console.log('Error is', error);
            });
}

function generateToken() {
    fetch(`http://localhost:31563/api/token`, {
        method: 'POST',
        body: JSON.stringify({
            "master_key": masterKey.value
        })
    })
        .then(response => {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response.json();
        }).then(response => {
            // alert(response["status"])
            uriContent = "data:application/octet-stream," + encodeURIComponent(response["token"]);
            newWindow = window.open(uriContent, 'temp.key');
        }).catch(error => {
            console.log('Error is', error);
        });
}

function deleteToken(event, tokenid) {
    event.preventDefault()
    fetch(`http://localhost:31563/api/token/${tokenid}/delete`, {
        method: 'POST',
        body: JSON.stringify({
            "master_key": masterKey.value
        })
    })
        .then(response => {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response.json();
        }).then(response => {
            alert(response["status"])
        }).catch(error => {
            console.log('Error is', error);
        });
}

function deleteUser(event, user_id) {
    event.preventDefault();
    if (window.confirm(`Delete user?`)) {
        requestDeleteUser(user_id)
    }
}

function disableSubmitButton() {
    submit_btn.disabled = true;
    submit_btn.innerHTML = "Processing ...";

}

function enableSubmitButton() {
    submit_btn.disabled = false;
    submit_btn.innerHTML = "Show";
}

function setOkStatus(status) {
    statusLabel.innerHTML = `<b style="color: #2ecc71">${status}</b>`
}

function setFailStatus(status) {
    statusLabel.innerHTML = `<b style="color: #e74c3c">${status}</b>`
}

function fetchData() {
    disableSubmitButton()
    resetTable()

    const data = new FormData(form);
    const action = data.get('action')

    if (action === "generatetoken") {
        generateToken()
        enableSubmitButton()
        return
    }

    fetch("http://localhost:31563/show", {
        method: 'POST',
        mode: 'cors',
        body: data,
    })
        .then(response => {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response.json();
        }).then(response => {
            if (response["status"] === "request failed") {
                setFailStatus("Request failed")
            } else if (response["status"] === "success") {
                setOkStatus("Success")
                addData(response["data"], action)
            } else {
                setFailStatus("Undefined response")
            }
        }).catch(error => {
            console.log('Error is', error);
        });

    enableSubmitButton()
}

form.addEventListener("submit", (event) => {
    event.preventDefault()
    fetchData()
})

