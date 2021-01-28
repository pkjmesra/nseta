import unittest
from nseta.common.symbols import get_symbol_list, get_index_constituents_list
from baseUnitTest import baseUnitTest

class TestSymbols(baseUnitTest):
    def setUp(self, redirect_logs=True):
        super().setUp()

    def test_symbol_list(self):
        df = get_symbol_list()
        # Check popular names are in the list
        _ril = df["SYMBOL"] == "RELIANCE"
        # Expect 1 row
        self.assertEqual(df[_ril].shape[0], 1)
        _sbi = df["SYMBOL"] == "SBIN"
        # Check company matches the expected value
        self.assertEqual(df[_sbi].iloc[0].get(
            'NAME OF COMPANY'), "State Bank of India")

    def test_index_constituents_list(self):
        df = get_index_constituents_list("NIFTY50")
        # Check for 50 items
        self.assertEqual(df.shape[0], 50)

        # Check popular names are in the list
        _sbi = df["Symbol"] == "SBIN"
        # Check company matches the expected value
        self.assertEqual(df[_sbi].iloc[0].get(
            'Company Name'), "State Bank of India")
        self.assertEqual(df[_sbi].iloc[0].get(
            'Industry'), "FINANCIAL SERVICES")

        df = get_index_constituents_list("NIFTYCPSE")
        # Check popular names are in the list
        _oil = df["Symbol"] == "OIL"
        # Check company matches the expected value
        self.assertEqual(df[_oil].iloc[0].get('ISIN Code'), "INE274J01014")

    def tearDown(self):
        super().tearDown()

if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(TestSymbols)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if six.PY2:
        if result.wasSuccessful():
            print("tests OK")
        for (test, error) in result.errors:
            print("=========Error in: %s===========" % test)
            print(error)
            print("======================================")

        for (test, failures) in result.failures:
            print("=========Error in: %s===========" % test)
            print(failures)
            print("======================================")
