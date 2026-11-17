import unittest
from validation_helpers import checked_local_date
class AnalysisDateTests(unittest.TestCase):
 def test_taipei_date_crosses_utc_midnight(self):
  self.assertEqual(checked_local_date({"checkedAtUtc":"2026-11-17T23:20:45+00:00","analysisTimeZone":"Asia/Taipei"},""),"2026-11-18")
 def test_utc_default_preserves_existing_reports(self):
  self.assertEqual(checked_local_date({"checkedAtUtc":"2026-11-17T23:20:45Z"},""),"2026-11-17")
if __name__=="__main__":unittest.main()
