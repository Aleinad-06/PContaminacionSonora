
        function getSimulatedDb() {
            return Math.floor(30 + Math.random() * 55);
        }

        function updateDbCounter() {
            const value = getSimulatedDb();
            const dbElement = document.getElementById('dbValue');
            dbElement.textContent = `${value} dB`;

            if (value < 50) {
                dbElement.style.color = "green";
            } else if (value < 70) {
                dbElement.style.color = "orange";
            } else {
                dbElement.style.color = "red";
            }
        }

        setInterval(updateDbCounter, 450);