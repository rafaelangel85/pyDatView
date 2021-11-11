# - *- coding: utf- 8 - *-
from __future__ import unicode_literals, print_function

import unittest

import numpy as np
import pandas as pd

from pydatview.common import filter_list
from pydatview.common import has_chinese_char
from pydatview.common import rectangleOverlap
from pydatview.common import unit, no_unit, ellude_common, getDt, find_leftstop


class TestCommon(unittest.TestCase):
    def assertEqual(self, first, second, msg=None):
        # print('>',first,'<',' >',second,'<')
        super(TestCommon, self).assertEqual(first, second, msg)

    def test_unit(self):
        self.assertEqual(unit('speed [m/s]'), 'm/s')
        self.assertEqual(unit('speed [m/s'), 'm/s')  # ...
        self.assertEqual(no_unit('speed [m/s]'), 'speed')

    def test_date(self):
        def test_dt(datestr, dt_ref):
            def myassert(x):
                if np.isnan(dt_ref):
                    self.assertTrue(np.isnan(getDt(x)))
                else:
                    self.assertEqual(getDt(x), dt_ref)

            # Type: Numpy array  - Elements: datetime64
            if isinstance(datestr[0], int):
                x = np.array(datestr, dtype='datetime64[s]')
                myassert(x)

                x = np.array(datestr)
                myassert(x)
            elif isinstance(datestr[0], float):
                x = np.array(datestr)
                myassert(x)
            else:
                x = np.array(datestr, dtype='datetime64')
                myassert(x)
            # Type: Pandas DatetimeIndex - Elements: TimeSamp
            df = pd.DataFrame(data=datestr)
            x = pd.to_datetime(df.iloc[:, 0].values)
            myassert(x)
            # Type: Numpy array  - Elements: datetime.datetime
            df = pd.DataFrame(data=datestr)
            x = pd.to_datetime(df.iloc[:, 0].values).to_pydatetime()
            myassert(x)

        test_dt(['2008-01-01', '2009-01-01'], 24 * 366 * 3600);  # year
        test_dt(['2008-01-01', '2008-02-01'], 24 * 3600 * 31);  # month
        test_dt(['2000-10-15 01:00:00', '2000-10-15 02:00:00'], 3600);  # hour
        test_dt(['2000-10-15 00:00:05.000001', '2000-10-15 00:00:05.000002'], 0.000001);  # mu s
        test_dt([np.datetime64('NaT'), '2000-10-15 00:00:05.000001'], np.nan);
        test_dt([np.datetime64('NaT'), '2000-10-15 00:00:05.000001', '2000-10-15 00:00:05.000002'], 0.000001)
        test_dt([0], np.nan)
        test_dt([0.0], np.nan)
        #         test_dt([0,1],1) # TODO
        #         test_dt([0.0,1.0],1.0) # TODO
        self.assertEqual(getDt([0.0, 0.1]), 0.1)
        self.assertEqual(getDt(np.array([0.0, 0.1])), 0.1)
        self.assertEqual(getDt([0, 1]), 1)
        self.assertEqual(getDt(np.array([0, 1])), 1)

    def test_leftstop(self):
        self.assertEqual(find_leftstop('A'), 'A')
        self.assertEqual(find_leftstop('_'), '')
        self.assertEqual(find_leftstop('A_'), 'A')
        self.assertEqual(find_leftstop('_B'), '')
        self.assertEqual(find_leftstop('ABC'), 'ABC')
        self.assertEqual(find_leftstop('AB_D'), 'AB')
        self.assertEqual(find_leftstop('AB.D'), 'AB')

    def test_ellude(self):
        print('')
        print('')
        self.assertListEqual(ellude_common(['>AA', '>AB']), ['AA', 'AB'])
        self.assertListEqual(ellude_common(['AAA', 'AAA_raw']), ['AAA', 'AAA_raw'])
        self.assertListEqual(ellude_common(['A_.txt', 'A.txt']), ['A_', 'A'])
        self.assertListEqual(ellude_common(['A_', 'A']), ['A_', 'A'])
        self.assertListEqual(ellude_common(['ABCDA_', 'ABCDAA']), ['ABCDA_', 'ABCDAA'])
        S = ['C:|A_BD', 'C:|A_BD_bld|DC', 'C:|A_BD_bld|BP']
        self.assertListEqual(ellude_common(S), ['BD', 'BD_bld|DC', 'BD_bld|BP'])
        self.assertListEqual(ellude_common(['C|FO', 'C|FO_HD']), ['FO', 'FO_HD'])
        self.assertListEqual(ellude_common(['CT_0.11', 'CT_0.22']), ['11', '22'])  # Unfortunate
        self.assertListEqual(ellude_common(['CT_0.1', 'CT_0.9']), ['0.1', '0.9'])
        self.assertListEqual(ellude_common(['CT=0.1', 'CT=0.9']), ['CT=0.1', 'CT=0.9'])
        self.assertListEqual(ellude_common(['AAA', 'ABA'], minLength=-1), ['A', 'B'])
        # print(ellude_common(['Farm.ifw.T1','Farm.ifw.T2'],minLength=2))
        # print('')
        # print('')

    def test_chinese_char(self):
        self.assertEqual(has_chinese_char(''), False)
        self.assertEqual(has_chinese_char('aaaa'), False)
        self.assertEqual(has_chinese_char('aa时'), True)
        self.assertEqual(has_chinese_char('a时a'), True)

    def test_filter(self):
        L = ['RotTrq_[kNm]', 'B1RootMy_[kNm]', 'B2RootMy_[kNm]', 'Power_[kW]']
        Lf, If = filter_list(L, 'Root')
        self.assertEqual(If, [1, 2])
        Lf, If = filter_list(L, 'ro')
        self.assertEqual(If, [0, 1, 2])
        self.assertEqual(Lf[0], 'RotTrq_[kNm]')
        Lf, If = filter_list(L, 'Kro')
        self.assertEqual(len(If), 0)
        self.assertEqual(len(Lf), 0)

    def test_rectangleOverlap(self):
        self.assertEqual(rectangleOverlap(0, 0, 1, 1, 0, 0, 2, 2), True)  # rect1 contained
        self.assertEqual(rectangleOverlap(-2, -2, 1, 1, 0, 0, 1, 1), True)  # rect2 contained
        self.assertEqual(rectangleOverlap(-2, -2, 1, 1, 0, 0, 2, 2), True)  # overlap corner2 in
        self.assertEqual(rectangleOverlap(-2, -2, 1, 1, -3, 0, 2, 2), True)  # overlap
        self.assertEqual(rectangleOverlap(-2, -2, -1, -1, 0, 0, 1, 1), False)


if __name__ == '__main__':
    unittest.main()
