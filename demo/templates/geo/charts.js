$(document).ready(function () {
    var base_options = {
        chart: {
            height: 320,
            type: 'donut',
        },
        series: [],
        noData: {
            text: 'Loading...'
        },
        legend: {
            show: true,
            position: 'right',
        },
        dataLabels: {
            enabled: true,
            dropShadow: {
                enabled: false,
            },
        },
        responsive: [{
            breakpoint: 480,
            options: {
                legend: {
                    position: 'bottom'
                }
            }
        }]
    };

    draw_chart = function(options, selector, data_url) {
        var chart = new ApexCharts(
            document.querySelector(selector),
            options
        );
        chart.render();
        $.getJSON(data_url, function(response) {
            chart.updateOptions(response)
        });
    };

    draw_country_chart = function(chart_type, selector, data_url) {
        base_options.chart.type = chart_type
        base_options.tooltip = {
            custom: function({series, seriesIndex, dataPointIndex, w}) {
                return '<div class="arrow_box" style="padding: 3px; background-color: ' + w.config.colors[seriesIndex] + '">' +
                    '<span>' + w.config.labels[seriesIndex] + ': ' + parseInt(series[seriesIndex]).toLocaleString() + '</span></div>'
            }
        }
        draw_chart(base_options, selector, data_url)
    };

    draw_country_cities_chart = function(chart_type, selector, data_url) {
        base_options.chart.type = chart_type
        base_options.plotOptions = {
            bar: {
              horizontal: true
            }
        }
//        base_options.tooltip = {
//            custom: function({series, seriesIndex, dataPointIndex, w}) {
//                return '<div class="arrow_box" style="padding: 3px; background-color: ' + w.config.colors[seriesIndex] + '">' +
//                    '<span>' + w.config.labels[seriesIndex] + ': ' + parseInt(series[seriesIndex]).toLocaleString() + '</span></div>'
//            }
//        }
        draw_chart(base_options, selector, data_url)
    };

})
