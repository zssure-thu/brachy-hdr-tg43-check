import dicom
import os
from chardet.universaldetector import UniversalDetector

class BrachyPlan(object):
    def __init__(self, ds):
        self.ds = ds
        self.save_to_txt()
        self.points = self.get_poi()
        self.prescription = float(ds.FractionGroupSequence[0].ReferencedBrachyApplicationSetupSequence[0].BrachyApplicationSetupDose)
        self.treatment_model = ds.TreatmentMachineSequence[0].TreatmentMachineName
        self.ref_air_kerma_rate = float(ds.SourceSequence[0].ReferenceAirKermaRate)
        self.dwells = self.get_dwells()

    def save_to_txt(self):
        with open("data\\output.txt", "w") as f:
            print(self.ds, file=f)

    def get_poi(self):
        points = []
        for p in self.ds.DoseReferenceSequence:
            points.append(self.Point(p))
        return points

    def get_dwells(self):
        dwells = []
        for c in self.ds.ApplicationSetupSequence[0].ChannelSequence:
            for d in c.BrachyControlPointSequence:
                dwells.append(self.Dwell(d))
        return dwells

    class Point(object):
        def __init__(self, ds_sequence):
            self.name = ds_sequence.DoseReferenceDescription
            self.coords = [float(x) for x in ds_sequence.DoseReferencePointCoordinates]
            self.dose = float(ds_sequence.TargetPrescriptionDose)

    class Dwell(object):
        def __init__(self, control_sequence):
            self.coords = [float(x) for x in control_sequence.ControlPoint3DPosition]
            self.time_weight = control_sequence.CumulativeTimeWeight

file_path = r"data\\"
file_name = r'RP.1.3.6.1.4.1.2452.6.2051579269.1225177353.3198701187.1732862112.dcm'

ds_input = dicom.read_file(os.path.join(file_path, file_name))

my_plan = BrachyPlan(ds_input)

with open("data\\decode.txt", "w") as f:
    print(ds_input[0x300f, 0x1000].value, file=f)

print('stop')