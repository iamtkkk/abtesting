window.addEventListener('load', function () {
    document.body.classList.add('loaded');
});



function handleButtonClick(page, button) {
    const data = {
        page: page,
        button: button
    };

    fetch('api/save-click-action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            if (response.ok) {
                //alert(button + ' action has been saved.');
            } else {
                alert('Failed to ' + button + 'buy action.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again later.');
        });
}


function increaseValue(target_id) {
    var value = parseInt(document.getElementById(target_id).value, 10);
    value = isNaN(value) ? 0 : value;
    value+=100;
    document.getElementById(target_id).value = value;
}

function decreaseValue(target_id) {
    var value = parseInt(document.getElementById(target_id).value, 10);
    value = isNaN(value) ? 0 : value;
    value-=100;
    document.getElementById(target_id).value = value;
}