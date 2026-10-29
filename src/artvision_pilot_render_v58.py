"""Safe entrypoint for 4x1 pilot jobs; existing V16 adapter stays unchanged."""
import argparse
import json
from pathlib import Path

from artvision_pilot_guard_v58 import enforce_pilot_project
from production_adapter_v16 import execute, path

def run(job, out):
    project_file=path(job["project_file"])
    project=json.loads(project_file.read_text(encoding="utf-8"))
    enforce_pilot_project(project)
    return execute(job,out)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--job",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    run(json.loads(Path(args.job).read_text()), args.out)
