from pathlib import Path
import argparse
import batch5_lotto4_v6 as prior
studio=prior.studio
studio.ROOT=Path("output/artvision-lotto5")
studio.P.clear()
studio.P.update({
"gentileschi":{"name":"Artemisia Gentileschi","duration":119,"hero":"Artemisia Gentileschi - Self-Portrait as the Allegory of Painting.jpg","key":["self portrait","saint catherine","magdalene","allegory","portrait","cleopatra"],"find":["Artemisia Gentileschi paintings","Artemisia Gentileschi self portrait","Artemisia Gentileschi museum artworks"],"act":["The artist's gaze","Light and shadow","The painter's figures","A dramatic vision","Return to the portrait"],"track":"darkest_child"},
"friedrich":{"name":"Caspar David Friedrich","duration":125,"hero":"Caspar David Friedrich - Wanderer above the Sea of Fog.jpg","key":["wanderer","sea of fog","monk","abbey","moonrise","ice sea","landscape"],"find":["Caspar David Friedrich paintings","Caspar David Friedrich landscape museum","Caspar David Friedrich Wanderer paintings"],"act":["A figure above the clouds","The sea","Ruins and moonlight","Northern landscapes","The wanderer returns"],"track":"dreams_become_real"},
"bruegel":{"name":"Pieter Bruegel the Elder","duration":132,"hero":"Pieter Bruegel the Elder - The Tower of Babel (Vienna) - Google Art Project.jpg","key":["tower of babel","hunters in the snow","wedding","proverbs","children's games","harvesters","winter"],"find":["Pieter Bruegel the Elder paintings","Pieter Bruegel the Elder Tower of Babel","Pieter Bruegel the Elder landscape paintings"],"act":["The tower","Tiny human stories","Winter villages","The world below","The tower returns"],"track":"evening_fall_piano"},
"seurat":{"name":"Georges Seurat","duration":110,"hero":"Georges Seurat - A Sunday Afternoon on the Island of La Grande Jatte - Google Art Project.jpg","key":["grande jatte","bathers","asnieres","circus","seine","pointillism"],"find":["Georges Seurat paintings","Georges Seurat pointillism museum","Georges Seurat Grande Jatte paintings"],"act":["Tiny dots","Summer by the river","Figures and rhythm","Colour","Sunday returns"],"track":"calmant"}
})
ALLOW={"gentileschi":["gentileschi"],"friedrich":["friedrich"],"bruegel":["bruegel","brueghel"],"seurat":["seurat"]}
studio.suitable_filename=lambda name,slug: name.casefold().endswith((".jpg",".jpeg",".png",".webp",".tif",".tiff")) and any(v in name.casefold() for v in ALLOW[slug])
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--artist",required=True,choices=sorted(studio.P))
 studio.make(p.parse_args().artist)
