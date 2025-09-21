import os.path
import sqlite3
import unittest

import pandas as pd
from utils import ConfigTests

from astrafocus.sql.local_gaia_database_query import LocalGaiaDatabaseQuery, QueryInputValidator

CONFIG = ConfigTests().get()


class TestQueryInputValidator(unittest.TestCase):
    def setUp(self):
        self.validator = QueryInputValidator()

    def test_valid_input(self):
        # Valid input within specified ranges
        self.assertIsNone(self.validator.validate_input(10, 20, 30, 40))

    def test_invalid_type(self):
        # Invalid input type (string instead of float)
        with self.assertRaises(TypeError):
            self.validator.validate_input("not_float", 20, 30, 40)

    def test_invalid_range_declination(self):
        # Invalid declination range (below minimum)
        with self.assertRaises(ValueError):
            self.validator.validate_input(-100, 20, 30, 40)

        # Invalid declination range (above maximum)
        with self.assertRaises(ValueError):
            self.validator.validate_input(10, 200, 30, 40)

    def test_invalid_range_ra(self):
        # Invalid right ascension range (below minimum)
        with self.assertRaises(ValueError):
            self.validator.validate_input(10, 20, -10, 40)

        # Invalid right ascension range (above maximum)
        with self.assertRaises(ValueError):
            self.validator.validate_input(10, 20, 30, 400)

    def test_invalid_order_declination(self):
        # Invalid declination order (min greater than max)
        with self.assertRaises(ValueError):
            self.validator.validate_input(30, 20, 30, 40)


class TestLocalGaiaDatabaseQuery(unittest.TestCase):
    def setUp(self):
        config = CONFIG
        self.db_path = config["path_to_gaia_tmass_db"]
        # don't run this if the db path is not set or the file does not exist
        if not self.db_path or not os.path.isfile(self.db_path):
            self.skipTest("No path to Gaia-Tmass database provided in config or file does not exist.")

    def tearDown(self):
        try:
            # Clean up the test database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DROP TABLE IF EXISTS `1_2`")
        except Exception as e:
            print(f"Error during tearDown: {e}")

    def test_determine_relevant_shards(self):
        # Test _determine_relevant_shards method
        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        shards = query_obj._determine_relevant_shards(10, 20)
        self.assertEqual(
            shards,
            {
                "10_11",
                "11_12",
                "12_13",
                "13_14",
                "14_15",
                "15_16",
                "16_17",
                "17_18",
                "18_19",
                "19_20",
            },
        )

    def test_sql_query_of_shard(self):
        # Test _sql_query_of_shard method
        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        query_obj._connect_to_database()
        df = query_obj._sql_query_of_shard("20_21", 20, 21, 23, 23.5)
        query_obj._close_database_connection()
        self.assertIsInstance(df, pd.DataFrame)

    def test_query(self):
        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        df = query_obj(20, 22.2, 23, 23.5)
        self.assertIsInstance(df, pd.DataFrame)

    def test_query_ra_wrap(self):
        # Test query with min_ra > max_ra (RA wrapping)
        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        # This should trigger the RA wrap logic
        df = query_obj(20, 22.2, 355, 5)
        self.assertIsInstance(df, pd.DataFrame)

    def test_weird_ra_ranges(self):
        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        # This should trigger the RA wrap logic
        df = query_obj(20, 22.2, -5, 5)
        self.assertIsInstance(df, pd.DataFrame)

        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        # This should trigger the RA wrap logic
        df = query_obj(20, 22.2, 355, 365)
        self.assertIsInstance(df, pd.DataFrame)

    def test_query_with_magnitude_filters(self):
        # Test query with magnitude filters
        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        df = query_obj(
            20, 22.2, 23, 23.5, min_phot_g_mean_mag=1, max_phot_g_mean_mag=5, min_j_m=1, max_j_m=5
        )
        self.assertIsInstance(df, pd.DataFrame)

    def test_query_all_filters(self):
        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        df = query_obj(20, 22, 23, 23.5, min_phot_g_mean_mag=1, max_phot_g_mean_mag=5, min_j_m=1, max_j_m=5)
        self.assertIsInstance(df, pd.DataFrame)

    def test_query_empty_result(self):
        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        # Use a range that should return no results
        df = query_obj(80, 81, 0, 1, min_phot_g_mean_mag=99, max_phot_g_mean_mag=100)
        self.assertTrue(df.empty)

    def test_invalid_shard(self):
        query_obj = LocalGaiaDatabaseQuery(self.db_path)
        query_obj._connect_to_database()
        with self.assertRaises(Exception):
            query_obj._sql_query_of_shard("invalid_shard", 0, 1, 0, 1)
        query_obj._close_database_connection()


if __name__ == "__main__":
    unittest.main()
