var backendUrl = 'https://thanima-backend.herokuapp.com';
// var backendUrl = 'http://localhost:8000';
var submissions = {};

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

if(getCookie('token') == "" || getCookie('token') == 'undefined') {
    window.location.replace(`https://${window.location.host}/`);
  }

function renderContestDiv(event) {
    var output =
        `<div class="card">
        <h2>${event.name}</h2>
        <h3>${event.subname}</h3>`;
    var deadline = new Date(event.deadline);
    output +=
        `${event.rules}<br><br>
        ${event.judging_criteria}<div class="date-submit">
        <div class="left"><span class="status-title">Last day for submission</span>
            <h2>${deadline.toLocaleDateString("en-IN")}</h2></div>`;
        if(deadline < Date.now()) {
            output += `<div class="right"><span class="status-title">Submissions</span>
            <h2 class="closed">CLOSED</h2></div></div>`; 
        } else {
            output += `<div class="right"><span class="status-title">Submissions</span>
            <h2 class="open">OPEN</h2></div></div>`;
        }
    if (submissions[event.id]) {//already submitted
        output += `<div class="submission" id="upload-${event.id}">
                    <a href="${submissions[event.id].file}" target="_blank">VIEW YOUR SUBMISSION</a>
                </div>`;
    } else if(deadline >= Date.now()){//can submit
        if (event.file_submission) {
            output +=
                `<div class="submission" id="upload-${event.id}">
                    <input type="file" name="file" id="file-${event.id}">
                    <button type="button" onclick="submitFile(${event.id})">Submit</button>
                </div>`;
        } else {
            output +=
                `<div class="submit-alert submission" >Upload your video in Google Drive (without any restriction -
                    Edit the permission to "Anyone with the link can view") and paste the link below. Only the first
                    link uploaded will be considered. So please be careful while uploading.</div>
                <div class="submission" id="upload-${event.id}">
                    <input type="text" name="file" id="file-${event.id}" placeholder="File Hosted Link">
                    <button type="button" onclick="submitLink(${event.id})">Submit</button>
                </div>`;
        }
    }
    output += `</div>`;
    return output;
}

function submitLink(eventId) {
    var link = document.getElementById(`file-${eventId}`).value;
    const submitRequest = {
        'file': link,
        'event_id': eventId
    };
    fetch(`${backendUrl}/api/events/submit/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${getCookie('token')}`
        },
        'body': JSON.stringify(submitRequest)
    })
        .then((response) => response.json())
        .then((result) => {
            console.log(result);
            if (result.status == 200) {
                swal({
                title: "Submitted Successfully!",
                icon: "success",
                buttons: true,
                dangerMode: true,
              })
              .then((release) => {
                location.reload();
              });
            } else {
                swal({
                title: "Error while submitting!",
                text: result.message,
                icon: "warning",
                dangerMode: true,
              })
              .then((release) => {
                location.reload();
              });
            }
        })
        .catch((err) => console.error(err));
}

function submitFile(eventId) {
    var file = document.getElementById(`file-${eventId}`).files[0];
    let formData = new FormData();
    formData.append("file", file);
    formData.append("event_id", eventId);

    fetch(`${backendUrl}/api/events/submit/`, {
        method: 'POST',
        headers: {
            'Authorization': `Token ${getCookie('token')}`
        },
        'body': formData
    })
        .then((response) => response.json())
        .then((result) => {
            console.log(result);
            if (result.status == 200) {
                swal({
                    title: "Uploaded Successfully!",
                    icon: "success"
                  })
                  .then((release) => {
                    location.reload();
                  });
                // location.reload();
            } else {
                swal({
                title: "Error while uploading!",
                text: result.message,
                icon: "warning",
                dangerMode: true,
              })
              .then((release) => {
                location.reload();
              });
            }
        }).catch((err) => {
            swal({
                title: "Client error while submitting!",
                text: err,
                icon: "warning",
                dangerMode: true,
              })
              .then((release) => {
                location.reload();
              });
        });

}

function loadProfile() {
    fetch(`${backendUrl}/api/events/profile/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${getCookie('token')}`
        }
    })
        .then((response) => response.json())
        .then((response) => {
            console.log(response);
            for (const submission of response.data.submissions) {
                submissions[submission.event] = submission;
            }
            for (const event of response.data.events) {
                var element = renderContestDiv(event);
                var contestsElement = document.getElementById('contests');
                contestsElement.innerHTML += element;
            }
            document.getElementById('username').innerHTML = `${response.data.profile.name.toUpperCase()}, ${response.data.profile.reg_no.toUpperCase()}`;
        })
        .catch((err) => {
            console.error(err);
        })
}

function deleteCookie(name) {
    document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function logout() {
    deleteCookie('token');
    window.location.replace(backendUrl);
}

loadProfile();