#this will be included at the end of every source file
substitutions = """
.. |env| replace:: :class:`~server.devices.base.BaseEnvironment`
.. |pm| replace:: :class:`~server.forecasting.simulation.devices.storages.SimulatedPowerMeter`
.. |hs| replace:: :class:`~server.forecasting.simulation.devices.storages.SimulatedHeatStorage`
.. |cu| replace:: :class:`~server.forecasting.simulation.devices.producers.SimulatedCogenerationUnit`
.. |plb| replace:: :class:`~server.forecasting.simulation.devices.producers.SimulatedPeakLoadBoiler`
.. |tc| replace:: :class:`~server.forecasting.simulation.devices.consumers.SimulatedThermalConsumer`
.. |ec| replace:: :class:`~server.forecasting.simulation.devices.consumers.SimulatedElectricalConsumer`

.. |SensorValue| replace:: :class:`~server.models.SensorValue`
.. |DeviceConfiguration| replace:: :class:`~server.models.DeviceConfiguration`
"""