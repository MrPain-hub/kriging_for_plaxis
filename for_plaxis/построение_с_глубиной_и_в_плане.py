from plxscripting.easy import *

import pandas as pd
import numpy as np

PORT_i = 10000
PORT_o = 10001
PASSWORD = "qwerty123"

#s_o, g_o = new_server('localhost', port=PORT_o, password=PASSWORD)
s_i, g_i = new_server('localhost', port=PORT_i, password=PASSWORD)

coor_space = (12.5, 12.5, 0)
size_space = (50, 50, 20)
H_plate = 1

df_soils = pd.read_excel("data/soil_plaxis_K+SVR_1m.xlsx")


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


df_sectors = pd.read_excel("data/E_uk_3d.xlsx").sort_values(by=["zi", "yi", "xi"])
x_coord = np.linspace(0, 25, 13)
y_coord = np.linspace(0, 25, 14)

for i in range(len(x_coord)):
        point1 = [x_coord[i], y_coord[0], -2]
        point2 = [x_coord[i], y_coord[-1], -2]
        point3 = [x_coord[i], y_coord[-1], -11]
        point4 = [x_coord[i], y_coord[0], -11]
        g_i.surface(point1, point2, point3, point4)

for i in range(len(y_coord)):
        point1 = [x_coord[0], y_coord[i], -2]
        point2 = [x_coord[-1], y_coord[i], -2]
        point3 = [x_coord[-1], y_coord[i], -11]
        point4 = [x_coord[0], y_coord[i], -11]
        g_i.surface(point1, point2, point3, point4)



g_i.gotomesh()
#g_i.mesh("Coarseness", 1)
g_i.mesh()

g_i.gotostages()

phase0_s = g_i.Phases[0]

len_df_sectors = df_sectors.shape[0]
h_depth = 0
print(len_df_sectors)


for i in range(len_df_sectors):

        if i % 156 == 0:
            print(f"Глубина {h_depth}", i % 156, i)
            h_depth += 2

        row = df_sectors.iloc[i]
        params = [f"h={h_depth}_i={i % 156}",
                  row["E0"]*1e3,
                  0,
                  -2
                  ]

        material_now = g_i.soilmat("Comments", "",
                                       "Identification", params[0],
                                       "SoilModel", 1,  # 1 - Linear Elastic; 2 - Mohr-Coulomb.
                                       #"ERef", params[1],
                                       #"Eoed", params[1],
                                       "Gref", params[1] / (2 * (1 + 0.3)),
                                       "Vs", 0,
                                       "Vp", 0,
                                       #"Einc", params[2],
                                       #"verticalRef", params[3],
                                       "gammaUnsat", 2,
                                       "gammaSat", 2,
                                       'nu', 0.3
                                       )

        volumes = []
        if i % 156 < 78:
            exec(f"volumes.append(g_i.BoreholeVolume_{h_depth}_{(i % 156) + 1})")
            if h_depth < 8:
                exec(f"volumes.append(g_i.BoreholeVolume_{h_depth+1}_{(i % 156) + 1})")
        else:
            exec(f"volumes.append(g_i.BoreholeVolume_{h_depth}_{(i % 156) + 2})")
            if h_depth < 8:
                exec(f"volumes.append(g_i.BoreholeVolume_{h_depth+1}_{(i % 156) + 2})")

        g_i.setmaterial(volumes, phase0_s, material_now)

        percent = 100 / len_df_sectors * (i + 1)
        if i % 20 == 0:
            print("Выполнено", round(percent, 1), "%")



phase1_1_s = g_i.phase(phase0_s)
g_i.Plates.activate(phase1_1_s)

phase1_2_s = g_i.phase(phase1_1_s)
g_i.SurfaceLoads.activate(phase1_2_s)

g_i.calculate()
g_i.view(phase1_2_s)
