from framework import file_opentender

year = [2022]

OT = file_opentender.OPENTENDERfiles(year)
fill_entries = OT.read()
