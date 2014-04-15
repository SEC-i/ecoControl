var past = ['#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce', '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'];
var future = ['#3895ff', '#153a61', '#a8e329', '#b80000', '#20cef5', '#623896', '#ffa561', '#9ac1ff', '#eb2d2d', '#c6f07f'];
var modified = ['#225999', '#000000', '#5c7d16', '#520000', '#13788f', '#201230', '#b36a32', '#5675a6', '#851919', '#728a49'];

var series_data = [{
        name: 'Cogeneration Unit Workload',
        data: [],
        color: past[0],
        tooltip: {
            valueSuffix: ' %'
        }
}, {
        name: 'Peak Load Boiler Workload',
        data: [],
        color: past[1],
        tooltip: {
            valueSuffix: ' %'
        }
}, {
        name: 'Heat Storage Temperature',
        data: [],
        color: past[2],
        tooltip: {
            valueSuffix: ' °C'
        }
}, {
        name: 'Thermal Consumption',
        data: [],
        color: past[3],
        tooltip: {
            valueSuffix: ' kW'
        }
}, {
        name: 'Warmwater Consumption',
        data: [],
        color: past[4],
        tooltip: {
            valueSuffix: ' kW'
        }
}, {
        name: 'Outside Temperature',
        data: [],
        color: past[5],
        tooltip: {
            valueSuffix: ' °C'
        }
}, {
        name: 'Electrical Consumption',
        data: [],
        color: past[6],
        tooltip: {
            valueSuffix: ' kW'
        }
},
    {
        name: 'Cogeneration Unit Workload (predicted)',
        data: [],
        color: future[0],
        dashStyle: 'shortdash',
        tooltip: {
            valueSuffix: ' %'
        }
}, {
        name: 'Peak Load Boiler Workload (predicted)',
        data: [],
        color: future[1],
        dashStyle: 'shortdash',
        tooltip: {
            valueSuffix: ' %'
        }
}, {
        name: 'Heat Storage Temperature (predicted)',
        data: [],
        color: future[2],
        dashStyle: 'shortdash',
        tooltip: {
            valueSuffix: ' °C'
        }
}, {
        name: 'Thermal Consumption (predicted)',
        data: [],
        color: future[3],
        dashStyle: 'shortdash',
        tooltip: {
            valueSuffix: ' kW'
        }
}, {
        name: 'Warmwater Consumption (predicted)',
        data: [],
        color: future[4],
        tooltip: {
            valueSuffix: ' kW'
        }
}, {
        name: 'Outside Temperature (predicted)',
        data: [],
        color: future[5],
        dashStyle: 'shortdash',
        tooltip: {
            valueSuffix: ' °C'
        }
}, {
        name: 'Electrical Consumption (predicted)',
        data: [],
        color: future[6],
        dashStyle: 'shortdash',
        tooltip: {
            valueSuffix: ' kW'
        }
}, {
        name: 'Cogeneration Unit Workload (not yet applied)',
        data: [],
        color: modified[0],
        visible: false,
        dashStyle: 'longdash',
        tooltip: {
            valueSuffix: ' %'
        }
}, {
        name: 'Peak Load Boiler Workload (not yet applied)',
        data: [],
        color: modified[1],
        visible: false,
        dashStyle: 'longdash',
        tooltip: {
            valueSuffix: ' %'
        }
}, {
        name: 'Heat Storage Temperature (not yet applied)',
        data: [],
        color: modified[2],
        visible: false,
        dashStyle: 'longdash',
        tooltip: {
            valueSuffix: ' °C'
        }
}, {
        name: 'Thermal Consumption (not yet applied)',
        data: [],
        color: modified[3],
        visible: false,
        dashStyle: 'longdash',
        tooltip: {
            valueSuffix: ' kW'
        }
}, {
        name: 'Warmwater Consumption (not yet applied)',
        data: [],
        color: modified[4],
        visible: false,
        dashStyle: 'longdash',
        tooltip: {
            valueSuffix: ' kW'
        }
}, {
        name: 'Outside Temperature (not yet applied)',
        data: [],
        color: modified[5],
        visible: false,
        dashStyle: 'longdash',
        tooltip: {
            valueSuffix: ' °C'
        }
}, {
        name: 'Electrical Consumption (not yet applied)',
        data: [],
        color: modified[6],
        visible: false,
        dashStyle: 'longdash',
        tooltip: {
            valueSuffix: ' kW'
        }
}];