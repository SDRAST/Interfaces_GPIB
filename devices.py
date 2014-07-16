"""
Compedium of available HPIB devices
"""

# Gateways
gateway = { "addr": {"mod3":    "137.228.236.54",
                     "rarg":    "137.228.236.90",
                     "DSS13-1": "137.228.236.58",  # dss13-gw1
                     "DSS13-2": "137.228.236.62",  # dss13-gw2
                     "DSS13-3": "137.228.236.75"}, # venus-gw3
            "info": {"mod3":     "DSS-14 ModIII area",
                     "rarg":     "DSS-14 pedestal",
                     "DSS13-1":  "Pedestal, controls ellipsoid, etc.",
                     "DSS13-2":  "Pedestal, controls MMSs, etc.",
                     "DSS13-3":  "Control room"}}

# Bus devices
bus = {"mod3":    "lan["+gateway["addr"]["mod3"]+"]:hpib",
       "rarg":    "lan["+gateway["addr"]["rarg"]+"]:hpib",
       "DSS13-1": "lan["+gateway["addr"]["DSS13-1"]+"]:gpib0",
       "DSS13-2": "lan["+gateway["addr"]["DSS13-2"]+"]:hpib2",
       "DSS13-3": "lan["+gateway["addr"]["DSS13-3"]+"]:gpib0"}
       
controller = "lan[128.149.22.44]:gpib0,"

# Power meters
pm = {"14-1": {"addr": bus["rarg"]+",11",
               "type": "437B",
               "info": "HP437B PM K1"},
      "14-2": {"addr": bus["rarg"]+",11",
               "type": "437B",
               "info": "HP437B PM K2"},
      "13-1": {"addr": bus["DSS13-3"]+",16", # tcl p_m(1)
               "type": "438",
               "info": "Spectrometer PM IF1",
               "alive": True},
      "13-2": {"addr": bus["DSS13-3"]+",15", # tcl p_m(2), not working
               "type": "438",
               "info": "Spectrometer PM IF2",
               "alive": False},
      "13-3": {"addr": bus["DSS13-2"]+",26", # tcl p_m(3), not working
               "type": "E4418B",
               "info": "",
               "alive": False},
      "13-4": {"addr": bus["DSS13-3"]+",13", # tcl p_m(4)
               "type": "437B",
               "info": "Radiometer PM IF1",
               "alive": True},
      "13-5": {"addr": bus["DSS13-3"]+",14", # tcl p_m(5)
               "type": "437B",
               "info": "Radiometer PM IF2",
               "alive": True}
      }

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


# =========================== historical names and addresses ==================
synth = controller+str(19)