import unittest
from finb.utils.common import cafef_company_url


class CommonTestCase(unittest.TestCase):
    def test_cafef_company_url(self):
        ret = cafef_company_url("PNJ")
        self.assertEqual(ret, "cong-ty-co-phan-vang-bac-da-quy-phu-nhuan")

        ret = cafef_company_url("HPG")
        self.assertEqual(ret, "cong-ty-co-phan-tap-doan-hoa-phat")

        ret = cafef_company_url("DTD")
        self.assertEqual(ret, "cong-ty-co-phan-dau-tu-phat-trien-thanh-dat")


if __name__ == '__main__':
    unittest.main()
