document.addEventListener("DOMContentLoaded", function () {
    const calendarDiv = document.getElementById("flatCalendar");

    if (calendarDiv) {
        flatpickr(calendarDiv, {
            inline: true,
            defaultDate: new Date(),
            clickOpens: false
        });
    }
    
    // Hardcoded data for the pie chart for units studied
    new Chart(document.getElementById("donutChart"), {
        type: "doughnut",
        data: {
            labels: ["CITS3403", "CITS3002", "CITS2007", "CITS2401"],
            datasets: [{
                data: [30, 25, 20, 25],
                backgroundColor: [
                    "#6366f1", // indigo
                    "#f59e0b", // amber
                    "#10b981", // emerald
                    "#ef4444"  // red
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "70%",
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#6b7280', // text-gray-500
                        padding: 10,
                        boxWidth: 12
                    }
                }
            }
        }
    });

});
