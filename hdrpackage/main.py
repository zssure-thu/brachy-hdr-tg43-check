from hdrpackage.parse_omp_rtplan import BrachyPlan, PointComparison
from hdrpackage.pyTG43 import *
from hdrpackage.omp_connect import *
import dicom


patID = 'V107489W'
case_name = 'Gynae Brachy Ins 1'
plan_name = 'Post Ins 1'
output_path = r'data\\rtplan.dcm'
rt_plan_blob = get_rtplan('V107489W', 'Gynae Brachy Ins 1', 'Post Ins 1')
write_file(rt_plan_blob[0][1], output_path)

ds_input = dicom.read_file(output_path)
my_plan = BrachyPlan(ds_input)

my_source_train = make_source_trains(my_plan)
points_of_interest = my_plan.points
for poi in points_of_interest:
    my_dose = calculate_dose(my_source_train, poi)
    point_compare = PointComparison(point_name=poi.name,
                    omp_dose=poi.dose,
                    pytg43_dose=my_dose)
    print("Percentage difference = %.2f"%point_compare.percentage_difference)
