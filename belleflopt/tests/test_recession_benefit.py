import logging

from django.test import TestCase

import seaborn
import pandas
from matplotlib import pyplot as plt

from belleflopt import benefit, models, load

log = logging.getLogger('belleflopt.tests.recession')

class TestRecessionBenefit(TestCase):
	def setUp(self):
		self.goodyears_bar = 8058513
		# set up the DB
		load.load_flow_components()
		load.load_flow_metrics()

		gy_segment = models.StreamSegment(com_id=self.goodyears_bar, routed_upstream_area=0, total_upstream_area=0)
		gy_segment.save()
		gy_segment_component = models.SegmentComponent(stream_segment=gy_segment, component=models.FlowComponent.objects.get(ceff_id="SP"))
		gy_segment_component.save()

				# p10, p25, p50, p75, p90
		ffms = {"SP_Tim": [180.5, 214.90625, 232, 241.429166666667, 251.505],
		        "SP_Mag": [1338.26047901366, 1826.36717829523, 2632.40321398374, 4145.2452861466, 6601.86531921443,],
		        "SP_Dur": [46, 55, 67.8625, 89.625, 121.016666666667],
		        "SP_ROC": [0.03845705116239, 0.0486334288519571, 0.0625000000000001, 0.0813201980740652, 0.114111705288176],
		        "DS_Mag_50":[35.5096639009908, 53.7206668057691, 83.012382212525, 122.765691110504, 144.62423838809]
		        }

		# attach the descriptors
		for metric in ffms:
			descriptor = models.SegmentComponentDescriptor(
				flow_metric=models.FlowMetric.objects.get(metric=metric),
				pct_10=ffms[metric][0],
				pct_25=ffms[metric][1],
				pct_50=ffms[metric][2],
				pct_75=ffms[metric][3],
				pct_90=ffms[metric][4],
			)
			descriptor.save()
			descriptor.flow_components.add(gy_segment_component)

		load.build_segment_components(simple_test=False)  # build the segment components so we can use benefit later

		self.x = list(range(1, 366))
		self.goodyears_bar_flows = [111, 111, 112, 146, 146, 133, 127, 122, 118, 118, 118, 116, 114, 112, 112, 112, 111,
		                            111, 111, 110, 110, 111, 111, 111, 111, 111, 111, 110, 110, 110, 110, 109, 109, 108,
		                            108, 108, 108, 108, 109, 109, 109, 110, 110, 110, 111, 112, 112, 112, 112, 112, 111,
		                            134, 322, 492, 600, 315, 200, 165, 261, 587, 500, 388, 385, 220, 172, 169, 160, 153,
		                            151, 150, 148, 146, 145, 143, 143, 148, 157, 297, 218, 189, 177, 239, 252, 212, 420,
		                            604, 346, 275, 235, 217, 209, 196, 179, 180, 176, 172, 182, 251, 401, 349, 630, 807,
		                            511, 397, 339, 306, 334, 1420, 2990, 1530, 1170, 1850, 1890, 1200, 919, 775, 679,
		                            618, 585, 574, 575, 571, 561, 566, 1140, 1290, 1400, 1040, 833, 718, 658, 673, 658,
		                            587, 545, 892, 5610, 3270, 2040, 1550, 1240, 1060, 970, 879, 794, 734, 701, 755,
		                            1760, 2410, 2570, 1780, 1770, 2440, 2570, 2090, 3470, 3620, 2690, 2120, 1750, 1510,
		                            1350, 1210, 1100, 1030, 998, 1010, 1090, 1170, 1340, 1330, 1250, 1300, 1210, 1170,
		                            1360, 1890, 2040, 1680, 1500, 1420, 1440, 2140, 2430, 2210, 2180, 2170, 2280, 3050,
		                            5380, 3510, 2800, 2380, 2170, 2190, 2260, 2120, 1990, 2160, 2600, 2760, 2640, 2570,
		                            2670, 3120, 3520, 3600, 3510, 3320, 3060, 2900, 2470, 2320, 2300, 2240, 2300, 2420,
		                            2690, 2860, 2900, 2800, 2690, 2820, 2960, 2840, 2770, 3330, 2640, 2270, 2210, 1900,
		                            1920, 1850, 1850, 1870, 2050, 2130, 1930, 1970, 2200, 2450, 2630, 2820, 2980, 3230,
		                            3360, 3460, 3470, 3050, 2520, 2300, 2300, 2460, 2450, 2370, 2320, 2250, 2110, 1990,
		                            1920, 1850, 1760, 1580, 1370, 1240, 1190, 1130, 1070, 995, 921, 864, 815, 784, 752,
		                            726, 699, 678, 660, 641, 611, 586, 566, 549, 531, 513, 493, 473, 462, 451, 436, 424,
		                            413, 403, 391, 377, 366, 357, 348, 339, 331, 323, 313, 307, 302, 296, 291, 285, 282,
		                            277, 272, 268, 264, 264, 271, 260, 254, 246, 240, 238, 239, 235, 232, 229, 225, 224,
		                            222, 219, 216, 213, 209, 206, 203, 203, 200, 198, 194, 192, 192, 190, 192, 187, 186,
		                            188, 193, 195, 188, 182, 179, 177, 221, 234, 218, 275, 222, 203, 196, 191, 187, 184,
		                            181, 180, 202, 227, 241]

	def _plot_benefit(self, peak_benefit, base_benefit, segment_component=None, save_path=None):
		base_data = {
			"Days": self.x,
			"Base Benefit": base_benefit,
			"Recession-Adjusted Benefit": peak_benefit
		}
		pd_data = pandas.DataFrame(base_data, columns=base_data.keys())

		seaborn.lineplot("Days", "Base Benefit", data=pd_data, label="Base Benefit")
		seaborn.lineplot("Days", "Recession-Adjusted Benefit", data=pd_data, label="Recession-Adjusted Benefit")

		if segment_component:
			plt.title(
				"Base and recession benefit for {} on segment {}".format(segment_component.component.name, segment_component.stream_segment.com_id))
		plt.ylabel("Benefit")
		plt.xlabel("Day of water year")
		if save_path is not None:
			plt.savefig(save_path)
		plt.show()

	def test_segment_data(self):
		segment_component = models.SegmentComponent.objects.get(component__ceff_id="SP",
		                                                        stream_segment__com_id=self.goodyears_bar)
		segment_component.make_benefit()

		original_benefit, recession_benefit, time_in_recession = segment_component.benefit.get_benefit_for_timeseries(self.goodyears_bar_flows, testing=True)
		log.info("Time in recession at end was: {}".format(time_in_recession))
		self._plot_benefit(recession_benefit, original_benefit, segment_component,
		                   save_path=r"C:\Users\dsx\Dropbox\Graduate\Thesis\figures\recession_benefit_examples\goodyears_recession_benefit.png")
		segment_component.benefit.plot_annual_benefit(screen=False, y_lim=(0, 6000))
		seaborn.lineplot(self.x, self.goodyears_bar_flows)
		plt.savefig(r"C:\Users\dsx\Dropbox\Graduate\Thesis\figures\recession_benefit_examples\goodyears_hydrograph_annual.png")
		plt.show()

