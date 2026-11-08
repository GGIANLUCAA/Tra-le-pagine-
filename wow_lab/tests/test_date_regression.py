"""Regression: UTC slot stamp must never parse a date separator as an integer."""
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import engine

class DateSelectionRegression(unittest.TestCase):
    def test_every_hour_and_day(self):
        conf={"allowed_artwork_ids":[436535],"allow_museum_api_search":True,"search_queries":["one","two","three"]}
        old=engine.discovery_ids
        old_get=engine.get_json
        try:
            engine.discovery_ids=lambda q,limit=9: []
            engine.get_json=lambda url: {'objectID':436535,'isPublicDomain':True,'objectName':'Painting','primaryImage':'https://images.metmuseum.org/example.jpg','title':'Mock artwork'}
            for day in (7,8,9,18,28):
                for hour in range(24):
                    stamp=f"202611{day:02d}T{hour:02d}"
                    try:
                        engine.select_artwork(conf,stamp,[])
                    except RuntimeError as e:
                        self.assertNotIn("invalid literal",str(e))
        finally:
            engine.discovery_ids=old
            engine.get_json=old_get

if __name__=="__main__": unittest.main()
