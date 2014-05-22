var lang = {
    apartments: 'Apartments',
    avg_electrical_consumption: 'Avg. Electrical Consumption',
    avg_rooms_per_apartment: 'Avg. Rooms per Apartment',
    avg_thermal_consumption: 'Avg. Thermal Consumption',
    avg_windows_per_room: 'Avg. Windows per Room',
    capacity: 'Capacity',
    critical_temperature: 'Critical Temperature',
    electrical_consumption: 'Electrical Revenues',
    electrical_costs: 'Electrical Costs per kWh',
    electrical_efficiency: 'Electrical Efficiency',
    electrical_infeed: 'Electrical Infeed Revenues',
    electrical_purchase: 'Electrical Purchase',
    feed_in_reward: 'Reward per kWh',
    gas_consumption: 'Gas Costs',
    gas_costs: 'Gas Costs per kWh',
    location: 'Location',
    maintenance_interval_hours: 'Maintenance Interval Hours',
    maintenance_interval_powerons: 'Maintenance Interval Power Ons',
    max_gas_input: 'Maximal Gas Input',
    min_temperature: 'Minimal Temperature',
    minimal_off_time: 'Minimal Time between Power-Ons',
    minimal_workload: 'Minimal Workload',
    purchase_date: 'Date of Purchase',
    purchase_price: 'Purchase Price',
    residents: 'Residents',
    target_temperature: 'Target Temperature',
    thermal_consumption: 'Thermal Revenues',
    thermal_efficiency: 'Thermal Efficiency',
    total_balance: 'Total Balance',
    total_heated_floor: 'Total Heated Floor',
    type_of_housing: 'Type of Housing',
    type_of_residents: 'Type of Residents',
    type_of_windows: 'Type of Windows',
    warmwater_consumption: 'Warmwater Revenues',
    months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
};

function get_text(key) {
    if (key in lang) {
        return lang[key]
    }
    return key;
}