ace.define('ace/snippets/python', ['require', 'exports', 'module'], function(require, exports, module) {


    exports.snippetText = "snippet env.get_hour_of_day()\n\
	env.get_hour_of_day()\n\
snippet env.get_min_of_hour()\n\
	env.get_min_of_hour()\n\
snippet env.get_day_of_year()\n\
	env.get_day_of_year()\n\
snippet env.log()\n\
	env.log('msg')\n\
snippet env.measurement_interval\n\
	env.measurement_interval\n\
snippet env.steps_per_measurement\n\
	env.steps_per_measurement\n\
snippet env.step_size\n\
	env.step_size\n\
snippet cu.start()\n\
	cu.start()\n\
snippet cu.stop()\n\
	cu.stop()\n\
snippet cu.get_operating_costs()\n\
	cu.get_operating_costs()\n\
snippet cu.running\n\
	cu.running\n\
snippet cu.workload\n\
	cu.workload\n\
snippet cu.current_gas_consumption\n\
	cu.current_gas_consumption\n\
snippet cu.current_thermal_production\n\
	cu.current_thermal_production\n\
snippet cu.total_gas_consumption\n\
	cu.total_gas_consumption\n\
snippet cu.total_thermal_production\n\
	cu.total_thermal_production\n\
snippet cu.total_hours_of_operation\n\
	cu.total_hours_of_operation\n\
snippet cu.power_on_count\n\
	cu.power_on_count\n\
snippet cu.max_gas_input\n\
	cu.max_gas_input\n\
snippet cu.electrical_efficiency\n\
	cu.electrical_efficiency\n\
snippet cu.thermal_efficiency\n\
	cu.thermal_efficiency\n\
snippet cu.max_efficiency_loss\n\
	cu.max_efficiency_loss\n\
snippet cu.maintenance_interval\n\
	cu.maintenance_interval\n\
snippet cu.minimal_workload\n\
	cu.minimal_workload\n\
snippet cu.minimal_off_time\n\
	cu.minimal_off_time\n\
snippet cu.total_electrical_production\n\
	cu.total_electrical_production\n\
snippet cu.thermal_driven\n\
	cu.thermal_driven\n\
snippet cu.electrical_driven_overproduction\n\
	cu.electrical_driven_overproduction\n\
snippet cu.overwrite_workload\n\
	cu.overwrite_workload\n\
snippet plb.start()\n\
	plb.start()\n\
snippet plb.stop()\n\
	plb.stop()\n\
snippet plb.get_operating_costs()\n\
	plb.get_operating_costs()\n\
snippet plb.running\n\
	plb.running\n\
snippet plb.workload\n\
	plb.workload\n\
snippet plb.plbrrent_gas_consumption\n\
	plb.plbrrent_gas_consumption\n\
snippet plb.plbrrent_thermal_production\n\
	plb.plbrrent_thermal_production\n\
snippet plb.total_gas_consumption\n\
	plb.total_gas_consumption\n\
snippet plb.total_thermal_production\n\
	plb.total_thermal_production\n\
snippet plb.total_hours_of_operation\n\
	plb.total_hours_of_operation\n\
snippet plb.power_on_count\n\
	plb.power_on_count\n\
snippet plb.max_gas_input\n\
	plb.max_gas_input\n\
snippet plb.thermal_efficiency\n\
	plb.thermal_efficiency\n\
snippet plb.overwrite_workload\n\
	plb.overwrite_workload\n\
snippet heat_storage.capacity\n\
	heat_storage.capacity\n\
snippet heat_storage.min_temperature\n\
	heat_storage.min_temperature\n\
snippet heat_storage.max_temperature\n\
	heat_storage.max_temperature\n\
snippet heat_storage.input_energy\n\
	heat_storage.input_energy\n\
snippet heat_storage.output_energy\n\
	heat_storage.output_energy\n\
snippet heat_storage.empty_count\n\
	heat_storage.empty_count\n\
snippet heat_storage.energy_stored()\n\
	heat_storage.energy_stored()\n\
snippet heat_storage.get_target_energy()\n\
	heat_storage.get_target_energy()\n\
snippet heat_storage.get_temperature()\n\
	heat_storage.get_temperature()\n\
snippet power_meter.electrical_reward_per_kwh\n\
	power_meter.electrical_reward_per_kwh\n\
snippet power_meter.electrical_costs_per_kwh\n\
	power_meter.electrical_costs_per_kwh\n\
snippet power_meter.total_fed_in_electricity\n\
	power_meter.total_fed_in_electricity\n\
snippet power_meter.total_purchased\n\
	power_meter.total_purchased\n\
snippet power_meter.get_reward()\n\
	power_meter.get_reward()\n\
snippet power_meter.get_costs()\n\
	power_meter.get_costs()\n\
snippet thermal_consumer.target_temperature\n\
	thermal_consumer.target_temperature\n\
snippet thermal_consumer.total_consumption\n\
	thermal_consumer.total_consumptionn\n\
snippet thermal_consumer.max_power\n\
	thermal_consumer.max_power\n\
snippet thermal_consumer.get_consumption_power()\n\
	thermal_consumer.get_consumption_power()\n\
snippet thermal_consumer.get_consumption_energy()\n\
	thermal_consumer.get_consumption_energy()\n\
snippet thermal_consumer.get_outside_temperature()\n\
	thermal_consumer.get_outside_temperature()\n\
snippet thermal_consumer.get_outside_temperature(offset=1)\n\
	thermal_consumer.get_outside_temperature(offset=1)\n\
snippet electrical_consumer.total_consumption\n\
	electrical_consumer.total_consumption\n\
snippet electrical_consumer.get_consumption_power()\n\
	electrical_consumer.get_consumption_power()\n\
snippet electrical_consumer.get_consumption_energy()\n\
	electrical_consumer.get_consumption_energy()\n\
snippet electrical_consumer.get_electrical_demand()\n\
	electrical_consumer.get_electrical_demand()\n\
snippet #!\n\
	#!/usr/bin/env python\n\
snippet imp\n\
	import ${1:module}\n\
snippet from\n\
	from ${1:package} import ${2:module}\n\
# Module Docstring\n\
snippet docs\n\
	'''\n\
	File: ${1:`Filename('$1.py', 'foo.py')`}\n\
	Author: ${2:`g:snips_author`}\n\
	Description: ${3}\n\
	'''\n\
snippet wh\n\
	while ${1:condition}:\n\
		${2:# TODO: write code...}\n\
# dowh - does the same as do...while in other languages\n\
snippet dowh\n\
	while True:\n\
		${1:# TODO: write code...}\n\
		if ${2:condition}:\n\
			break\n\
snippet with\n\
	with ${1:expr} as ${2:var}:\n\
		${3:# TODO: write code...}\n\
# New Class\n\
snippet cl\n\
	class ${1:ClassName}(${2:object}):\n\
		\"\"\"${3:docstring for $1}\"\"\"\n\
		def __init__(self, ${4:arg}):\n\
			${5:super($1, self).__init__()}\n\
			self.$4 = $4\n\
			${6}\n\
# New Function\n\
snippet def\n\
	def ${1:fname}(${2:`indent('.') ? 'self' : ''`}):\n\
		\"\"\"${3:docstring for $1}\"\"\"\n\
		${4:# TODO: write code...}\n\
snippet deff\n\
	def ${1:fname}(${2:`indent('.') ? 'self' : ''`}):\n\
		${3:# TODO: write code...}\n\
# New Method\n\
snippet defs\n\
	def ${1:mname}(self, ${2:arg}):\n\
		${3:# TODO: write code...}\n\
# New Property\n\
snippet property\n\
	def ${1:foo}():\n\
		doc = \"${2:The $1 property.}\"\n\
		def fget(self):\n\
			${3:return self._$1}\n\
		def fset(self, value):\n\
			${4:self._$1 = value}\n\
# Ifs\n\
snippet if\n\
	if ${1:condition}:\n\
		${2:# TODO: write code...}\n\
snippet el\n\
	else:\n\
		${1:# TODO: write code...}\n\
snippet ei\n\
	elif ${1:condition}:\n\
		${2:# TODO: write code...}\n\
# For\n\
snippet for\n\
	for ${1:item} in ${2:items}:\n\
		${3:# TODO: write code...}\n\
# Encodes\n\
snippet cutf8\n\
	# -*- coding: utf-8 -*-\n\
snippet clatin1\n\
	# -*- coding: latin-1 -*-\n\
snippet cascii\n\
	# -*- coding: ascii -*-\n\
# Lambda\n\
snippet ld\n\
	${1:var} = lambda ${2:vars} : ${3:action}\n\
snippet .\n\
	self.\n\
snippet try Try/Except\n\
	try:\n\
		${1:# TODO: write code...}\n\
	except ${2:Exception}, ${3:e}:\n\
		${4:raise $3}\n\
snippet try Try/Except/Else\n\
	try:\n\
		${1:# TODO: write code...}\n\
	except ${2:Exception}, ${3:e}:\n\
		${4:raise $3}\n\
	else:\n\
		${5:# TODO: write code...}\n\
snippet try Try/Except/Finally\n\
	try:\n\
		${1:# TODO: write code...}\n\
	except ${2:Exception}, ${3:e}:\n\
		${4:raise $3}\n\
	finally:\n\
		${5:# TODO: write code...}\n\
snippet try Try/Except/Else/Finally\n\
	try:\n\
		${1:# TODO: write code...}\n\
	except ${2:Exception}, ${3:e}:\n\
		${4:raise $3}\n\
	else:\n\
		${5:# TODO: write code...}\n\
	finally:\n\
		${6:# TODO: write code...}\n\
# if __name__ == '__main__':\n\
snippet ifmain\n\
	if __name__ == '__main__':\n\
		${1:main()}\n\
# __magic__\n\
snippet _\n\
	__${1:init}__${2}\n\
# python debugger (pdb)\n\
snippet pdb\n\
	import pdb; pdb.set_trace()\n\
# ipython debugger (ipdb)\n\
snippet ipdb\n\
	import ipdb; ipdb.set_trace()\n\
# ipython debugger (pdbbb)\n\
snippet pdbbb\n\
	import pdbpp; pdbpp.set_trace()\n\
snippet pprint\n\
	import pprint; pprint.pprint(${1})${2}\n\
snippet \"\n\
	\"\"\"\n\
	${1:doc}\n\
	\"\"\"\n\
# test function/method\n\
snippet test\n\
	def test_${1:description}(${2:`indent('.') ? 'self' : ''`}):\n\
		${3:# TODO: write code...}\n\
# test case\n\
snippet testcase\n\
	class ${1:ExampleCase}(unittest.TestCase):\n\
		\n\
		def test_${2:description}(self):\n\
			${3:# TODO: write code...}\n\
snippet fut\n\
	from __future__ import ${1}\n\
#getopt\n\
snippet getopt\n\
	try:\n\
		# Short option syntax: \"hv:\"\n\
		# Long option syntax: \"help\" or \"verbose=\"\n\
		opts, args = getopt.getopt(sys.argv[1:], \"${1:short_options}\", [${2:long_options}])\n\
	\n\
	except getopt.GetoptError, err:\n\
		# Print debug info\n\
		print str(err)\n\
		${3:error_action}\n\
\n\
	for option, argument in opts:\n\
		if option in (\"-h\", \"--help\"):\n\
			${4}\n\
		elif option in (\"-v\", \"--verbose\"):\n\
			verbose = argument\n\
";
    exports.scope = "python";

});