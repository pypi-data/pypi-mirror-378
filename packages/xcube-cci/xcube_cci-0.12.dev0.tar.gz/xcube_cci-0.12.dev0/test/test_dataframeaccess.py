import pandas as pd
import unittest

from xcube_cci.cciodp import CciOdp
from xcube_cci.dataframeaccess import DataFrameAccessor

GHG_DS_ID = "esacci.GHG.satellite-orbit-frequency.L2.CH4.SCIAMACHY.Envisat.IMAP.v7-2.r1"

class DataFrameAccessTest(unittest.TestCase):

    def setUp(self) -> None:
        ccicdc = CciOdp(data_type='geodataframe')
        self._dfa = DataFrameAccessor(ccicdc, GHG_DS_ID, {})

    def test_get_geodataframe(self):
        gdf = self._dfa.get_geodataframe()
        self.assertIsNotNone(gdf)

    def test_get_geodataframe_for_dataset(self):
        gdf = self._dfa._get_features_from_cci_cdc(
            GHG_DS_ID,
            (pd.Timestamp('2003-01-08 00:00:00'), pd.Timestamp('2003-01-08 23:59:59'))
        )
        self.assertIsNotNone(gdf)
