function renderChart_1() {
    var ctx = document.getElementById("chart_1").getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels: ["19:12", "19:13", "19:14"],
            datasets: [{
                label: "Length",
                data: [3000, 3200, 3400],
                borderColor: "rgba(75, 192, 192, 1)",
                backgroundColor: "rgba(75, 192, 192, 0.2)",
                fill: true,
                tension: 0.2
            }]
        }
    });
}
