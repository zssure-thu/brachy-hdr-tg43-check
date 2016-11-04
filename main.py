#!/usr/bin/env python
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hdrpackage.parse_omp_rtplan import BrachyPlan, PointComparison
from hdrpackage.pyTG43 import *
from hdrpackage.omp_connect import *
import dicom
from tabulate import tabulate
import os
from numpy import around


def main():
    """ Main function for TG43 dose check """

    print(tabulate([["v0.1 VCC"]], headers=["HDR Brachytherapy Dose Check"]))

    while True:
        patient_id = input("Enter patient ID: ").upper()
        available_cases = get_patient_cases(patient_id)
        if available_cases:
            break
        print("Please enter a valid patient ID")

    print("\n"+patient_id)
    print("\n"+tabulate([[i+1, available_cases[i]] for i in range(len(available_cases))],
                        headers=["#","Available cases"]))

    while True:
        try:
            case_number = int(input("Select case number: "))-1
            case_name = available_cases[case_number]
            available_plans = get_plans_from_case(patient_id, case_name)
            break
        except (ValueError, IndexError):
            print("Please enter a valid case number")

    print("\n"+"Patient ID: %s" % patient_id)
    print("Case name: %s" % case_name)
    print("\n"+tabulate([[i + 1, available_plans[i]] for i in range(len(available_plans))],
                        headers=["#", "Available plans"]))

    while True:
        try:
            plan_number = int(input("Select plan number: "))-1
            plan_name = available_plans[plan_number]
            break
        except IndexError:
            print("Please enter a valid plan number")

    print("Fetching: %s, %s, %s" %(patient_id, case_name, plan_name))

    output_full_path = r'hdrpackage\\data\\rtplan.dcm'
    print("\nGathering data from OMP...")

    rt_plan_blob = get_rtplan(patient_id, case_name, plan_name)     # return RTplan as BLOB

    write_file(rt_plan_blob[0][1], output_full_path)                # save BLOB to dcm
    ds_input = dicom.read_file(output_full_path)                    # read in dcm
    os.remove(output_full_path)
    my_plan = BrachyPlan(ds_input)

    print("RTPlan loaded successfully...")
    my_source_train = make_source_trains(my_plan)
    points_of_interest = my_plan.points

    output_table = []
    for poi in points_of_interest:                                   # for each point
        my_dose = calculate_dose(my_source_train, poi)               # calculate dose
        point_compare = PointComparison(point_name=poi.name,         # and compare to OMP
                        omp_dose=poi.dose,
                        pytg43_dose=my_dose)
        output_table.append([poi.name,                               # display as pretty table
                             around([poi.dose],decimals=2).tolist()[0],
                             around([my_dose],decimals=2).tolist()[0],
                             around([point_compare.percentage_difference],decimals=2).tolist()[0]])

    print("Dose check results for: \n\tPatientID: %s\n\tCase name: %s\n\tPlan name: %s" % (patient_id, case_name, plan_name))
    print("\n" + tabulate(output_table,
                          headers=["Point name", "OMP dose (Gy)", "pyTG43 dose (Gy)", "% difference"]))


if __name__ == '__main__':
    main()