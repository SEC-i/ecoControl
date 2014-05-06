var lang = {
    apartments: 'Apartments',
    avg_electrical_consumption: 'Avg. Electrical Consumption',
    avg_rooms_per_apartment: 'Avg. Rooms per Apartment',
    avg_thermal_consumption: 'Avg. Thermal Consumption',
    avg_windows_per_room: 'Avg. Windows per Room',
    capacity: 'Capacity',
    critical_temperature: 'Critical Temperature',
    electrical_costs: 'Electrical Costs per kWh',
    electrical_efficiency: 'Electrical Efficiency',
    feed_in_reward: 'Reward per kWh',
    gas_costs: 'Gas Costs per kWh',
    location: 'Location',
    maintenance_interval_hours: 'Maintenance Interval Hours',
    maintenance_interval_powerons: 'Maintenance Interval Power Ons',
    max_gas_input: 'Maximal Gas Input',
    min_temperature: 'Minimal Temperature',
    minimal_workload: 'Minimal Workload',
    purchase_date: 'Date of Purchase',
    purchase_price: 'Purchase Price',
    residents: 'Residents',
    target_temperature: 'Target Temperature',
    thermal_efficiency: 'Thermal Efficiency',
    total_heated_floor: 'Total Heated Floor',
    type_of_housing: 'Type of Housing',
    type_of_residents: 'Type of Residents',
    type_of_windows: 'Type of Windows',
};

function get_text(key) {
    if (key in lang) {
        return lang[key]
    }
    return key;
}