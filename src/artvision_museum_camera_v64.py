"""ArtVision Museum V64: strictly continuous timed camera return.
Pure deterministic module; no file/network/paid API/renderer side effects.
The former V62 camera resumed a final spline from its start after already finishing
one at starts[9], causing a hard cut (measured 92/255 in a real Socrates visual trial).
"""
import math

def _ease(x):
    x=max(0.0,min(1.0,float(x)))
    return x*x*(3-2*x)

def camera_at(t, duration, beat_starts, poses):
    """Time continuous camera trajectory; poses are (x, y, positive_zoom).

    Beat 9 begins return to the same physical room; no second transition reset
    at the start of beat 10. Final pose equals original gallery entrance pose.
    """
    n=len(poses)
    if n<3 or len(beat_starts)!=n or not duration>0:
        raise ValueError("Museum needs matching timed beats/poses and duration")
    starts=[float(x) for x in beat_starts]
    if starts[0]!=0.0 or any(not 0<=a<b<duration for a,b in zip(starts,starts[1:])):
        raise ValueError("Museum beat starts must strictly increase before duration")
    if any(len(p)!=3 or p[2]<=0 or not all(math.isfinite(float(v)) for v in p) for p in poses):
        raise ValueError("Invalid camera pose")
    t=max(0.,min(float(t),float(duration)))
    def blend(a,b,u):
        u=_ease(u)
        return (a[0]+(b[0]-a[0])*u,
                a[1]+(b[1]-a[1])*u,
                math.exp((1-u)*math.log(a[2])+u*math.log(b[2])))
    # FIRST n-2 segments lead from room through relevant painterly details.
    for i in range(n-2):
        if t <= starts[i+1]:
            return blend(poses[i],poses[i+1],(t-starts[i])/(starts[i+1]-starts[i]))
    # The return begins at START OF PENULTIMATE beat and finishes at END OF VOICE.
    # Never start the same last segment again at starts[-1].
    i=n-2
    return blend(poses[i],poses[i+1],(t-starts[i])/(duration-starts[i]))
