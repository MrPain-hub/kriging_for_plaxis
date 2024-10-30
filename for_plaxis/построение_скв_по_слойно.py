from plxscripting.easy import *

import pandas as pd

PORT_i = 10000
PORT_o = 10001
PASSWORD = "qwerty123"

#s_o, g_o = new_server('localhost', port=PORT_o, password=PASSWORD)
s_i, g_i = new_server('localhost', port=PORT_i, password=PASSWORD)


coor_space = (12.5, 12.5, 0)
size_space = (50, 50, 20)
H_plate = 1

df_soils = pd.read_excel("data/soil_plaxis_poly2_1m.xlsx")


try:
    s_i.new()
except Exception as ex:
    print(ex)

g_i.setproperties("Title", "example_1",
                  "Company", "niiosp"
                  )
"""
Создание space
"""
g_i.SoilContour.initializerectangular(coor_space[0] - size_space[0]/2, coor_space[0] - size_space[0]/2,
                                      coor_space[0] + size_space[0]/2, coor_space[1] + size_space[1]/2
                                      )


platemat = g_i.platemat("Identification", "plate",
                        "MaterialType", "Elastic",
                        "Gamma", 18,
                        "E1", 25e6,
                        "d", H_plate,
                        )

"""
"""
g_i.gotosoil()
borehole = g_i.borehole(0, 0)
g_soilmat = g_i.soilmat("Identification", f"ige_0",
                        "SoilModel", 1,
                        "nu", .3,
                        "ERef", 1.18e4,
                        "gammaUnsat", 10.8,
                        "gammaSat", 10.8,
                        )
g_soil = g_i.soillayer(borehole, 2)
g_soil.Soil.Material = g_soilmat
g_soil.PorePressure.Conditions = "Dry"  # сухой грунт

for row in range(df_soils.shape[0]):
    df_row = df_soils.iloc[row]
    name = df_row["soil"]
    dz = df_row["z"]
    gamma = df_row["gamma"]
    E_now = df_row["E"]
    print(name, dz, gamma, E_now)
    g_soilmat = g_i.soilmat("Identification", f"ige_{int(name)}",
                            "SoilModel", 1,
                            "nu", .3,
                            "ERef", E_now * 1e3,
                            "gammaUnsat", gamma,
                            "gammaSat", gamma,
                            )
    g_soil = g_i.soillayer(borehole, dz)
    soil_now = g_soil[-1]
    soil_now.Soil.Material = g_soilmat
    soil_now.PorePressure.Conditions = "Dry"  # сухой грунт

g_soilmat = g_i.soilmat("Identification", f"sand",
                        "SoilModel", 1,
                        "nu", .3,
                        "ERef", 1.18e4,
                        "gammaUnsat", 19.8,
                        "gammaSat", 19.8,
                        )
g_soil = g_i.soillayer(borehole, 3)
g_soil[-1].Soil.Material = g_soilmat
g_soil[-1].PorePressure.Conditions = "Dry"  # сухой грунт
"""
"""
g_i.gotostructures()
surf_g, plate_g = g_i.plate((0, 0, 0),
                              (25, 0, 0),
                              (25, 25, 0),
                              (0, 25, 0)
                              )
plate_g.Material = platemat
load_plate = g_i.surfload(surf_g,
                          "sigz",
                          -200
                          )  # Приложение нагрузки


g_i.gotomesh()
g_i.mesh()


g_i.gotostages()

phase0_s = g_i.Phases[0]

phase1_1_s = g_i.phase(phase0_s)
g_i.Plates.activate(phase1_1_s)

phase1_2_s = g_i.phase(phase1_1_s)
g_i.SurfaceLoads.activate(phase1_2_s)

g_i.calculate()
g_i.view(phase1_2_s)
