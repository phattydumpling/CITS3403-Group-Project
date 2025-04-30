document.addEventListener("DOMContentLoaded", function () {
    const calendarDiv = document.getElementById("flatCalendar");

    if (calendarDiv) {
        flatpickr(calendarDiv, {
            inline: true,
            defaultDate: new Date(),
            clickOpens: false
        });
    }
});
