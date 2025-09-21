import unittest

from utils import ConfigTests

from astrafocus.autofocuser import NonParametricResponseAutofocuser
from astrafocus.extremum_estimators import LOWESSExtremumEstimator
from astrafocus.focus_measure_operators import (
    FFTFocusMeasureTan2022,
    NormalizedVarianceFocusMeasure,
)
from astrafocus.interface.simulation import ObservationBasedDeviceSimulator

CONFIG = ConfigTests().get()


class TestNonParametricResponseAutofocuser(unittest.TestCase):
    def setUp(self):
        config = CONFIG
        path_to_fits = config["path_to_fits"]
        if path_to_fits is None:
            self.skipTest("No path to fits files provided in config.")
        self.TELESCOPE_INTERFACE = ObservationBasedDeviceSimulator(fits_path=path_to_fits)

    def test_non_parametric_response_autofocuser(self):
        NPRAF = NonParametricResponseAutofocuser(
            autofocus_device_manager=self.TELESCOPE_INTERFACE,
            exposure_time=3.0,
            focus_measure_operator=FFTFocusMeasureTan2022(),
            n_steps=(20, 5),
            n_exposures=(1, 2),
            decrease_search_range=True,
            keep_images=True,
            extremum_estimator=LOWESSExtremumEstimator(frac=0.5, it=3),
            secondary_focus_measure_operators={"normalized_variance": NormalizedVarianceFocusMeasure()},
        )

        NPRAF.run()
        df = NPRAF.focus_record

        # Add assertions based on your expectations
        self.assertIsNotNone(df)
        # You can add more specific assertions based on your requirements


if __name__ == "__main__":
    unittest.main()
