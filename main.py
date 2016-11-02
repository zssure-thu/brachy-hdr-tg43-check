import dicom
import os
from itertools import starmap


class BrachyPlan(object):
    def __init__(self, ds):
        self.ds = ds
        self.applicator = self.ds.ApplicationSetupSequence[0][0x300b, 0x100f].value.decode('utf-8')
        self.save_to_txt()
        self.points = self.get_poi()
        self.channel_numbers = self.get_channel_numbers()
        self.prescription = float(
            ds.FractionGroupSequence[0].ReferencedBrachyApplicationSetupSequence[0].BrachyApplicationSetupDose)
        self.treatment_model = ds.TreatmentMachineSequence[0].TreatmentMachineName
        self.ref_air_kerma_rate = float(ds.SourceSequence[0].ReferenceAirKermaRate)
        self.channels = self.get_channel_dwell_times()

    def save_to_txt(self):
        with open("data\\output.txt", "w") as f:
            print(self.ds, file=f)

    def get_channel_numbers(self):
        return [int(x.SourceApplicatorID) for x in self.ds.ApplicationSetupSequence[0].ChannelSequence]

    def get_poi(self):
        points = []
        for p in self.ds.DoseReferenceSequence:
            points.append(self.Point(p))
        return points

    def get_channel_dwell_times(self):
        channel_dwells = []
        for c in range(len(self.ds.ApplicationSetupSequence[0].ChannelSequence)):
            total_channel_time = float(self.ds.ApplicationSetupSequence[0].ChannelSequence[c].ChannelTotalTime)
            total_time_weight = float(self.ds.ApplicationSetupSequence[0].ChannelSequence[c].FinalCumulativeTimeWeight)
            dwell_weights = []
            dwells_list = []
            number_of_dwells = int(self.ds.ApplicationSetupSequence[0].ChannelSequence[c].NumberOfControlPoints / 2)
            for i in range(0, len(self.ds.ApplicationSetupSequence[0].ChannelSequence[c].BrachyControlPointSequence), 2):
                d1 = float(
                    self.ds.ApplicationSetupSequence[0].ChannelSequence[c].BrachyControlPointSequence[
                        i].CumulativeTimeWeight)
                d2 = float(
                    self.ds.ApplicationSetupSequence[0].ChannelSequence[c].BrachyControlPointSequence[
                        i + 1].CumulativeTimeWeight)
                dwell_weights.append(d2 - d1)
                dwells_list.append(self.ds.ApplicationSetupSequence[0].ChannelSequence[c].BrachyControlPointSequence[
                        i])
            dwell_times = [(total_channel_time / number_of_dwells) * x for x in dwell_weights]
            dwells = []
            for i in range(len(dwells_list)):
                dwells.append(self.Dwell(dwells_list[i],dwell_times[i],dwell_weights[i]))
            channel_dwells.append(dwells)
        return channel_dwells

    class Point(object):
        def __init__(self, ds_sequence):
            self.name = ds_sequence.DoseReferenceDescription
            self.coords = [float(x) for x in ds_sequence.DoseReferencePointCoordinates]
            self.dose = float(ds_sequence.TargetPrescriptionDose)

    class Dwell(object):
        def __init__(self, control_sequence, d_time, d_weight):
            self.coords = [float(x) for x in control_sequence.ControlPoint3DPosition]
            self.time_weight = d_weight
            self.dwell_time = d_time


file_path = r"data//"
file_name = r'RP.1.3.6.1.4.1.2452.6.2051579269.1225177353.3198701187.1732862112.dcm'

ds_input = dicom.read_file(os.path.join(file_path, file_name))

my_plan = BrachyPlan(ds_input)


