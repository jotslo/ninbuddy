function updateDashboard() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            const dashboardHeader = document.getElementById('msg');
            dashboardHeader.textContent = `NinBuddy Dashboard - ${data.message}`;
        }
    );
}

setInterval(updateDashboard, 500);