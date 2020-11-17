import unittest
import numpy as np
from risk_adjusted_ic import mean_var_opt, adjusted_return


class RiskAdjustedICTestCase(unittest.TestCase):
    def get_test_data(self):
        f = np.asarray([0.5, 0, -0.5])
        beta = np.asarray([[0.9], [1.1], [1]])
        r = np.asarray([-0.05, 0.15, 0])
        specific_risk_mat = np.diag([0.2, 0.2, 0.2])

        return f, beta, r, specific_risk_mat

    def test_adjusted_forecast(self):
        f, beta, r, specific_risk_mat = self.get_test_data()
        w = mean_var_opt(f, specific_risk_mat, beta).flatten()

        self.assertEqual((w[0]-1.25) < 0.0000001, True)
        self.assertEqual((w[1]-1.25) < 0.0000001, True)
        self.assertEqual((w[2]+2.5) < 0.000001, True)

    def test_adjusted_return(self):
        f, beta, r, specific_risk_mat = self.get_test_data()

        adj_ret = adjusted_return(r, specific_risk_mat, beta)

        self.assertEqual((adj_ret[0] - 0.08333333) < 0.00001, True)
        self.assertEqual((adj_ret[1] - 0.08333333) < 0.00001, True)
        self.assertEqual((adj_ret[2] + 0.16666667) < 0.00001, True)



if __name__ == '__main__':
    unittest.main()
