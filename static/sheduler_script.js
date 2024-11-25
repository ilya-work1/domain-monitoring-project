
document.getElementById("startSchedule").addEventListener("click", () => {
    const scheduleType = document.querySelector('input[name="schedule-type"]:checked').value;
    let data = { scheduleType };

    if (scheduleType === "hourly") {
        const hourlyInterval = document.getElementById("hourlyInterval").value;
        data.interval = parseInt(hourlyInterval, 10);
    } else if (scheduleType === "daily") {
        const dailyTime = document.getElementById("dailyTime").value;
        data.time = dailyTime;
    }

    // Envoyer les données au serveur Flask
    fetch("/start-scheduler", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(result => {
            document.getElementById("nextRunTime").textContent = "Next check: " + result.nextRun;
            document.getElementById("stopSchedule").disabled = false;
        })
        .catch(err => console.error(err));
});

document.getElementById("stopSchedule").addEventListener("click", () => {
    fetch("/stop-scheduler", { method: "POST" })
        .then(() => {
            document.getElementById("nextRunTime").textContent = "Next check: Not scheduled";
            document.getElementById("stopSchedule").disabled = true;
        })
        .catch(err => console.error(err));
});

