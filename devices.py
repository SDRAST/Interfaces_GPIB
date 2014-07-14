"""
Compedium of available HPIB devices
"""

# Gateways
gateway = { "addr": {"mod3":    "137.228.236.54",
                     "rarg":    "137.228.236.90",
                     "DSS13-1": "137.228.236.58",
                     "DSS13-2": "137.228.236.62",
                     "DSS13-3": "137.228.236.75"},
            "info": {"mod3":     "DSS-14 ModIII area",
                     "rarg":     "DSS-14 pedestal"}}

# Bus devices
bus = {"mod3":    "lan["+gateway["addr"]["mod3"]+"]:hpib",
       "rarg":    "lan["+gateway["addr"]["rarg"]+"]:hpib",
       "DSS13-3": "lan["+gateway["addr"]["DSS13-3"]+"]:hpib3"}
       
controller = "lan[128.149.22.44]:gpib0,"

# Power meters
pm = {"14-1": {"addr": bus["rarg"]+",11",
               "info": "HP437B PM K1"},
      "14-2": {"addr": bus["rarg"]+",11",
               "info": "HP437B PM K2"},
      "13-1": {"addr": bus["DSS13-3"]+",16",
               "info": "DSS-13 Spectrometer IF #1 power meter"}}

# MMS receivers
mms_display = {"14-1": {"addr": bus["mod3"]+",4",
                        "info": "DSS14 cone MMS1 display"},
               "14-2": {"addr": bus["mod3"]+",6",
                        "info": "DSS14 cone MMS2 display"}}
mms = {"14-1": {"addr": bus["mod3"]+",18",
                "info": "DSS14 cone MMS1 mainframe"},
       "14-2": {"addr": bus["mod3"]+",22",
                "info": "DSS14 cone MMS2 mainframe"}}

# temperature sensors
thermometer = {"ls_14": {"addr": bus["mod3"]+",27",
                         "info": "Lakeshore 208 Thermometer in DSS-14 cone"},
               "si_14": {"addr": bus["mod3"]+",29",
                         "info": "SI 9300 Thermometer for K-band"}}

# controllers
control = {"K_14": {"addr": bus["mod3"]+",28",
                    "info": "Agilent controller for K-band"}}


synth = controller+str(19)