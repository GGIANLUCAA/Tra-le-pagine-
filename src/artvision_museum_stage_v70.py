"""ArtVision Museum scale V72: physical real-size opening shot planner.

Pure offline calculation; no images, rendering, paid calls or museum-authenticity claim.
An artwork stays small when seen from an ordinary gallery viewing distance.
"""
import math
from artvision_museum_director_v69 import evaluate

def plan_stage(dossier, canvas_width_px=1080, canvas_height_px=1920):
    review=evaluate(dossier)
    if review["errors"]:
        return {"status":"blocked","errors":review["errors"],"render_authorized":False}
    if type(canvas_width_px) is not int or type(canvas_height_px) is not int or min(canvas_width_px,canvas_height_px)<100:
        return {"status":"blocked","errors":["invalid output canvas"],"render_authorized":False}
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
            # Never present this border as a documented real frame.
            border_cm=max(3.0,min(12.0,min(width,height)*0.065))
            fw,fh=width+2*border_cm,height+2*border_cm
    if fw<width or fh<height:
        return {"status":"blocked","errors":["frame smaller than artwork"],"render_authorized":False}
    fw=float(fw)
    fh=float(fh)
    camera=dossier["camera"]
    cx=canvas_width_px*camera["painting_center_x"]
    cy=canvas_height_px*camera["painting_center_y"]
    margin_x=canvas_width_px*.10
    margin_y=canvas_height_px*.10
    available_half_width=min(cx-margin_x,canvas_width_px-margin_x-cx)
    available_half_height=min(cy-margin_y,canvas_height_px-margin_y-cy)
    if min(available_half_width,available_half_height)<=0:
        return {"status":"blocked","errors":["frame center outside safe bounds"],"render_authorized":False}
    # A constant real-world camera distance is the key small-artwork safeguard.
    # Optical projection uses a portrait camera's horizontal and vertical FOV.
    horizontal_fov_deg=39.0
    h_slope=math.tan(math.radians(horizontal_fov_deg)/2)
    v_slope=h_slope*(canvas_height_px/canvas_width_px)
    max_width_fraction=min(.72,2*available_half_width/canvas_width_px)
    max_height_fraction=min(.62,2*available_half_height/canvas_height_px)
    distance_cm=max(350.0,
        fw/(2*h_slope*max_width_fraction),
        fh/(2*v_slope*max_height_fraction))
    display_width_px=fw/(2*distance_cm*h_slope)*canvas_width_px
    display_height_px=fh/(2*distance_cm*v_slope)*canvas_height_px
    room_width_cm=max(500.0,fw*1.8)
    room_height_cm=max(300.0,fh*1.6)
    room_depth_cm=max(550.0,distance_cm+150.0)
    eye_height_cm=160.0
    painting_center_height_cm=max(eye_height_cm,fh/2+40.0)
    return {"status":"stage_plan_ready","render_authorized":False,
      "artwork":{"width_cm":width,"height_cm":height,"aspect_ratio":round(width/height,6)},
      "frame":{"width_cm":round(fw,2),"height_cm":round(fh,2),
               "dimensions_kind":"estimated_scenography" if frame_estimated else "supplied_documented_or_estimated",
               "status":frame["status"],"disclosure":frame.get("disclosure",""),
               "height_vs_170cm_person_ratio":round(fh/170.,4)},
      "gallery":{"minimum_suggested_width_cm":round(room_width_cm,1),
                 "minimum_suggested_height_cm":round(room_height_cm,1),
                 "minimum_suggested_depth_cm":round(room_depth_cm,1),
                 "camera_start_distance_cm":round(distance_cm,3),
                 "horizontal_fov_degrees":horizontal_fov_deg,
                 "dimensions_kind":"creative_planning_not_museum_measurement",
                 "painting_center_height_cm":round(painting_center_height_cm,1),
                 "eye_height_reference_cm":eye_height_cm},
      "storyboard_9_16":{"canvas_px":[canvas_width_px,canvas_height_px],
                         "frame_width_px":round(display_width_px),
                         "frame_height_px":round(display_height_px),
                         "center_x_px":cx,
                         "center_y_px":cy,
                         "opening_frame_bounds_px":[round(cx-display_width_px/2,1),
                                                    round(cy-display_height_px/2,1),
                                                    round(cx+display_width_px/2,1),
                                                    round(cy+display_height_px/2,1)],
                         "opening_frame_within_safe_margins":True},
      "camera":{"movement_module":"src/artvision_museum_camera_v64.py",
                "continuous_entry_exit":True,"return_same_room":True},
      "variants":["critico_museum","cinema_museum"],
      "warning":"Physical scale and FOV govern the wide shot. Unknown dimensions, lighting and real gallery remain unverified; full visual QA required."}
