"""Regression: UTC slot stamp must never parse a date separator as an integer."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import engine

class DateSelectionRegression(unittest.TestCase):
    def test_every_hour_and_day(self):
        conf={"allowed_artwork_ids":[436535],"allow_museum_api_search":True,"search_queries":["one","two","three"]}
        old=engine.discovery_ids
        old_valid=engine.fetch_object
        try:
            engine.discovery_ids=lambda q,limit=9: []
            engine.fetch_object=lambda obj: None
            for day in (7,8,9,18,28):
                for hour in range(24):
                    stamp=f"202611{day:02d}T{hour:02d}"
                    try:
                        engine.select_artwork(conf,stamp,[])
                    except RuntimeError as e:
                        self.assertNotIn("invalid literal",str(e))
        finally:
            engine.discovery_ids=old
            engine.fetch_object=old_valid

if __name__=="__main__": unittest.main()
