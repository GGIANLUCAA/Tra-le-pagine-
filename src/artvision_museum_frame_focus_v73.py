"""V73: frame naturally leaves the viewport as a continuous camera moves into details.

Pure planning only. Never erase the authentic frame from source imagery, paint over
the artwork, invent off-canvas pixels, render, or alter prior masters.
"""
from __future__ import annotations
from artvision_museum_camera_v64 import camera_at

def frame_visibility_at(t, duration, beat_starts, poses, *, frame_half_width=0.46,
                        frame_half_height=0.46):
    """Frame edges in normalized artwork coordinates at the current camera pose.

    A 1x viewport has half-width/height 0.5. Zoom > 1 reduces viewport
    half-extents; once inside the physical frame the visible border is absent.
    """
    x,y,zoom=camera_at(t,duration,beat_starts,poses)
    if not (0 < frame_half_width <= .5 and 0 < frame_half_height <= .5):
        raise ValueError("Frame bounds must be normalized and positive")
    left,right=x-.5/zoom,x+.5/zoom
    top,bottom=y-.5/zoom,y+.5/zoom
    inside=(left> .5-frame_half_width and right<.5+frame_half_width
            and top>.5-frame_half_height and bottom<.5+frame_half_height)
    return {"t_seconds":float(t),"camera_zoom":zoom,
            "frame_border_visible":not inside,
            "render_action":"camera_only_no_fake_frame_erasure",
            "source_artwork_immutable":True}

def focus_storyboard(duration,starts,poses):
    samples=[0.,duration*.12,duration*.27,duration*.44,
             duration*.70,duration*.86,duration]
    return [frame_visibility_at(t,duration,starts,poses) for t in samples]
