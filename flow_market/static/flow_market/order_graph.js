class OrderGraph {
    static floDataBids = [
        { x: 0, y: 20 },
        { x: 0, y: 3 }, // maxPrice
        { x: 0, y: 2 }, // minPrice
        { x: 0, y: 0 },
    ];
    static floDataAsks = [
        { x: 0, y: 20 },
        { x: 0, y: 19 }, // maxPrice
        { x: 0, y: 17 }, // minPrice
        { x: 0, y: 0 },
    ];
    static maxPriceIndex = 1;
    static minPriceIndex = 2;
    static bidsIndex = 0;
    static asksIndex = 1;


    get data() {
        return {
            datasets: [{
                label: 'Bids',
                pointRadius: [0, 6, 6, 0],
                pointHitRadius: [0, 25, 25, 0],
                pointStyle: ["", "circle", "rect", ""],
                dragData: true,
                showLine: true,
                backgroundColor: 'rgb(54, 162, 235)',
                borderColor: 'rgba(54, 162, 235, 0.3)',
                data: OrderGraph.floDataBids,
            },
            {
                label: 'Asks',
                pointRadius: [0, 6, 6, 0],
                pointHitRadius: [0, 25, 25, 0],
                pointStyle: ["", "rect", "circle", ""],
                dragData: true,
                showLine: true,
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132, 0.3)',
                data: OrderGraph.floDataAsks,
            }]
        }
    }

    get scales() {
        return {
            x: {
                title: {
                    display: true,
                    text: 'Rate'
                },
                type: 'linear',
                min: 0,
                max: 5,
                position: 'bottom',
                ticks: {
                    stepSize: 1,
                },
            },
            y: {
                title: {
                    display: true,
                    text: 'Price',
                },
                type: 'linear',
                min: 0,
                max: 20,
            }
        }
    }

    get plugins() {
        return {
            dragData: {
                round: 0,
                dragX: true,
                showTooltip: true,
                onDragStart: function (e, datasetIndex, index, value) {
                    if (index == 0 || index == 4) { return false; }
                },
                onDrag: function (e, datasetIndex, index, value) {
                    let maxPriceIndex = OrderGraph.maxPriceIndex;
                    let minPriceIndex = OrderGraph.minPriceIndex;
                    if (datasetIndex == OrderGraph.bidsIndex) {
                        // Dragging bids
                        let data = OrderGraph.floDataBids;
                        if (index == maxPriceIndex) {
                            // Dragging maxPrice
                            if (value.x > 0) {
                                data[maxPriceIndex].x = 0;
                            }
                            if (value.y <= data[minPriceIndex].y) {
                                data[maxPriceIndex].y = data[minPriceIndex].y + 1;
                            }
                        } else {
                            // Dragging minPrice
                            if (value.y >= data[maxPriceIndex].y) {
                                data[minPriceIndex].y = data[maxPriceIndex].y - 1;
                            }
                            data[3].x = value.x;
                        }
                    } else {
                        // Dragging asks
                        let data = OrderGraph.floDataAsks;
                        if (index == minPriceIndex) {
                            // Dragging minPrice
                            if (value.x > 0) {
                                data[minPriceIndex].x = 0;
                            }
                            if (value.y >= data[maxPriceIndex].y) {
                                data[minPriceIndex].y = data[maxPriceIndex].y - 1;
                            }
                        } else {
                            // Dragging maxPrice
                            if (value.y <= data[minPriceIndex].y) {
                                data[maxPriceIndex].y = data[minPriceIndex].y + 1;
                            }
                            data[0].x = value.x;
                        }
                    }

                },
                onDragEnd: function (e, datasetIndex, index, value) {
                },
            }
        }
    }

    get config() {
        return {
            type: 'scatter',
            data: this.data,
            options: {
                scales: this.scales,
                plugins: this.plugins,
            }
        };
    }

    show() {
        var myChart = new Chart(
            document.getElementById("OrderGraph"), this.config);
    }
}