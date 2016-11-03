from hdrpackage.omp_plan import BrachyPlan, PointComparison
from hdrpackage.pyTG43 import *
import dicom
import os

file_path = r"data//"
file_name = r'RP.1.3.6.1.4.1.2452.6.2051579269.1225177353.3198701187.1732862112.dcm'

ds_input = dicom.read_file(os.path.join(file_path, file_name))

my_plan = BrachyPlan(ds_input)

my_source_train = make_source_trains(my_plan)

points_of_interest = my_plan.points

for poi in points_of_interest:
    my_dose = calculate_dose(my_source_train, poi)
    point_compare = PointComparison(point_name=poi.name,
                    omp_dose=poi.dose,
                    pytg43_dose=my_dose)
    print("Percentage difference = %.2f"%point_compare.percentage_difference)

print('here')

