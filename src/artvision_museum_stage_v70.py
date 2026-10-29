"""ArtVision V70 museum geometry planner. Pure planning, no renderer or paid calls."""
import math
from artvision_museum_director_v69 import evaluate

def plan_stage(dossier, canvas_width_px=1080, canvas_height_px=1920):
    review=evaluate(dossier)
    if review["errors"]:
        return {"status":"blocked","errors":review["errors"],"render_authorized":False}
    art=dossier["artwork"]
    width=float(art["width_cm"])
    height=float(art["height_cm"])
    frame=dossier["frame"]
    fw=frame.get("outer_width_cm")
    fh=frame.get("outer_height_cm")
    frame_estimated=fw is None
    if frame_estimated:
        if frame["status"]=="unframed":
            fw,fh=width,height
        else:
            # Artistic planning assumption, never a documented physical measurement.
            border_cm=max(3.0,min(12.0,min(width,height)*0.065))
            fw,fh=width+2*border_cm,height+2*border_cm
    if fw<width or fh<height:
        return {"status":"blocked","errors":["frame smaller than artwork"],"render_authorized":False}
    room_width_cm=max(500.0,fw*1.8)
    room_height_cm=max(300.0,fh*1.6)
    eye_height_cm=160.0
    painting_center_height_cm=max(eye_height_cm,fh/2+40.0)
    # Pixel placement in a vertical composition is only a storyboard projection.
    display_width_px=min(canvas_width_px*0.72,canvas_height_px*0.52*fw/fh)
    display_height_px=display_width_px*fh/fw
    if display_height_px>canvas_height_px*0.62:
        display_height_px=canvas_height_px*0.62
        display_width_px=display_height_px*fw/fh
    return {"status":"stage_plan_ready","render_authorized":False,
      "artwork":{"width_cm":width,"height_cm":height,"aspect_ratio":round(width/height,6)},
      "frame":{"width_cm":round(fw,2),"height_cm":round(fh,2),
               "dimensions_kind":"estimated_scenography" if frame_estimated else "supplied_documented_or_estimated",
               "status":frame["status"],"disclosure":frame.get("disclosure","")},
      "gallery":{"minimum_suggested_width_cm":round(room_width_cm,1),
                 "minimum_suggested_height_cm":round(room_height_cm,1),
                 "dimensions_kind":"creative_planning_not_museum_measurement",
                 "painting_center_height_cm":round(painting_center_height_cm,1),
                 "eye_height_reference_cm":eye_height_cm},
      "storyboard_9_16":{"canvas_px":[canvas_width_px,canvas_height_px],
                         "frame_width_px":round(display_width_px),
                         "frame_height_px":round(display_height_px),
                         "center_x_px":canvas_width_px*dossier["camera"]["painting_center_x"],
                         "center_y_px":canvas_height_px*dossier["camera"]["painting_center_y"]},
      "camera":{"movement_module":"src/artvision_museum_camera_v64.py",
                "continuous_entry_exit":True,"return_same_room":True},
      "variants":["critico_museum","cinema_museum"],
      "warning":"All room and unknown frame dimensions are staging assumptions; visual QA and rights required."}
