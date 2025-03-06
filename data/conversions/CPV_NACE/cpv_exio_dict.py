import json
import os

dump_path = os.path.join(os.path.abspath('..'), "CPV_NACE/cpv_exio_dict.json")

cpv_exio_dict = {
    "15811100": "Processing of Food products nec",
    "15000000": "Processing of Food products nec",
    "15894700": "Processing of Food products nec",
    "39000000": "Manufacture of furniture; manufacturing n.e.c. (36)",
    "33772000": "Paper",
    "03220000": "Cultivation of vegetables, fruit, nuts",
    "15800000": "Processing of Food products nec",
    "15221000": "Manufacture of fish products",
    "15100000": "Production of meat products nec",
    "03200000": "Processing of Food products nec",
    "15300000": "Processing of Food products nec",
    "15811000": "Processing of Food products nec",
    "15220000": "Manufacture of fish products",
    "50000000": "Retail trade, except of motor vehicles and motorcycles; repair of personal and household goods (52)",
    "39711000": "Manufacture of electrical machinery and apparatus n.e.c. (31)",
    "44612100": "Manufacture of gas; distribution of gaseous fuels through mains"
}

with open(dump_path, 'w') as json_file:
    json.dump(cpv_exio_dict, json_file)
