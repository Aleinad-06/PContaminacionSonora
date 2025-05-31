 function getSimulatedDb() {
    return Math.floor(30 + Math.random() * 55);
}

function updateDbCounter() {
    const value = getSimulatedDb();
    document.getElementById('dbValue').textContent = `${value} dB`;
}

setInterval(updateDbCounter, 450);