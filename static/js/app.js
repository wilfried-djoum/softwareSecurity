document.getElementById('executeAttack').addEventListener('click', function () {
    const attackType = document.getElementById('attackType').value;
    const targetIP = document.getElementById('targetIP').value;
    const loader = document.getElementById('loader');
    const btnLabel = document.getElementById('btnLabel')
    const resultsDiv = document.getElementById('results');
    const executeAttacks = document.getElementById('executeAttack')

    if (!targetIP) {
        alert("Please enter an IP address or URL of the target.");
        return;
    }
    // cursor: not-allowed;
    // pointer-events: none;
    loader.style.display = 'block';
    btnLabel.style.display = 'none'

    executeAttacks.style.cursor = 'not-allowed'
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
            btnLabel.style.display = 'block'
            executeAttacks.style.cursor = 'pointer'
            filligramme.style.display = 'block'
            popUp.style.display = 'block'
            popUp.classList.add('showBounce');
            resultsDiv.innerHTML = `<strong>Résultat:</strong> ${data.Messages}`;
        })
        .catch((error) => {
            loader.style.display = 'none';
            btnLabel.style.display = 'block'
            executeAttacks.style.cursor = 'pointer'
            filligramme.style.display = 'block'
            popUp.style.display = 'block'
            popUp.classList.add('showBounce');
            resultsDiv.innerHTML = `<strong>Résultat:</strong> ${data.Messages}`;
        });
});


const closeBtn = document.getElementById('closeBtn')
const filligramme = document.getElementById('filligramme')
const popUp = document.getElementById('popUp')

filligramme.style.display = 'none'
popUp.style.display = 'none'

closeBtn.addEventListener('click', function () {
    filligramme.style.display = 'none'
    popUp.style.display = 'none'
    popUp.classList.remove('showBounce'); // Réinitialiser l'animation
})

document.getElementById('downloadReport').addEventListener('click', function () {
    window.location.href = '/attacks';
});
