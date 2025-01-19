document.getElementById('executeAttack').addEventListener('click', function () {
    const attackType = document.getElementById('attackType').value;
    const targetIP = document.getElementById('targetIP').value;
    const loader = document.getElementById('loader');
    const btnLabel = document.getElementById('btnLabel');
    const resultsDiv = document.getElementById('results');
    const executeAttacks = document.getElementById('executeAttack');

    if (!targetIP) {
        alert("Please enter an IP address or URL of the target.");
        return;
    }

    loader.style.display = 'block';
    btnLabel.style.display = 'none';
    executeAttacks.style.cursor = 'not-allowed';
    resultsDiv.innerHTML = '';

    fetch('/attack', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ attackType, targetIP }),
    })
        .then(response => response.json())
        .then(data => {
            loader.style.display = 'none';
            btnLabel.style.display = 'block';
            executeAttacks.style.cursor = 'pointer';

            if (data.message) {
                resultsDiv.innerHTML = `<strong>Result:</strong> ${data.message}`;

                // Display pop-up with result message
                const resultPopup = document.getElementById('popUp');
                const resultMessage = document.getElementById('results');
                resultMessage.innerHTML = data.message;
                resultPopup.style.display = 'block';
                resultPopup.classList.add('showBounce');
            } else {
                resultsDiv.innerHTML = `<strong>Error:</strong> ${data.error || 'An unknown error occurred.'}`;
            }
        })
        .catch((error) => {
            loader.style.display = 'none';
            btnLabel.style.display = 'block';
            executeAttacks.style.cursor = 'pointer';
            resultsDiv.innerHTML = `<strong>Error:</strong> An error occurred.`;
            console.error(error);
        });
});

// Function to show the popup
function showPopup(message) {
    const filligramme = document.getElementById('filligramme');
    const popUp = document.getElementById('popUp');
    const resultMessage = document.getElementById('results');

    filligramme.style.display = 'block';
    popUp.style.display = 'block';

    resultMessage.innerHTML = `<strong>Attack Result:</strong> ${message}`;

    popUp.classList.add('showBounce');
}


const closeBtn = document.getElementById('closeBtn');
closeBtn.addEventListener('click', function () {
    const filligramme = document.getElementById('filligramme');
    const popUp = document.getElementById('popUp');

    filligramme.style.display = 'none';
    popUp.style.display = 'none';
    popUp.classList.remove('showBounce');
});

// Download report event listener
document.getElementById('downloadReport').addEventListener('click', function () {
    window.location.href = '/attacks';
});
