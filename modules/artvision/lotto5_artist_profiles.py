from batch5_lotto4_v6 import studio
studio.ROOT = __import__('pathlib').Path('output/artvision-lotto5')
studio.P.clear()
studio.P.update({'friedrich':{'name':'Caspar David Friedrich','duration':125,'hero':'Caspar David Friedrich - Wanderer above the Sea of Fog.jpg','key':['wanderer','sea of fog','moonrise','monk','abbey','landscape'],'find':['Caspar David Friedrich paintings','Caspar David Friedrich landscapes'],'act':['The wanderer','Moonlight','Silence','The sea','Return'],'track':'calmant'}})
studio.suitable_filename=lambda name,slug: 'friedrich' in name.casefold() and name.casefold().endswith(('.jpg','.jpeg','.png'))
if __name__ == '__main__': studio.make('friedrich')
