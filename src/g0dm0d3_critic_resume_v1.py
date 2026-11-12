#!/usr/bin/env python3
"""Resume ONLY the critic from the 3 genuine free-role replies saved on Actions.

Never replay sceneggiatore/storico/regista; SHA-locked report from GitHub Actions
run 43275046749; use one additional pinned :free Liquid request only.
No TTS/video/publication, no billing, no auto retry.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import g0dm0d3_free_four_roles_v1 as board

SOURCE_SHA256 = "1c634b10557a0c7485c3ffa7413d0d6641d4b0df0eec267ebda5ed0e17fd64a8"
SOURCE_RUN_ID = 43275046749
SOURCE_ARTIFACT = "G0DM0D3_FOUR_REAL_AI_43275046749"
RESUME_MODEL = "liquid/lfm-2.5-2.6b:free"
MAX_CRITIC_OUTPUT_TOKENS = 2500


def original_report(path: Path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise board.FreeOnlyError("Source report does not match verified GitHub run SHA")
    result = json.loads(data)
    if result.get("schema") != "g0dm0d3-free-four-role-pilot-v1":
        raise board.FreeOnlyError("Unrecognized source report schema")
    if (result.get("status") != "incomplete_no_retry"
            or result.get("model_calls") != 4
            or not result.get("failure_reason", "").startswith("No displayable text")):
        raise board.FreeOnlyError("Source was not the verified 3-of-4 partial report")
    if result.get("format") != "giuliano" or "Anticitera" not in result.get("subject", ""):
        raise board.FreeOnlyError("Source not tied to the Antikythera episode")
    replies = result.get("responses")
    if not isinstance(replies, list) or len(replies) != 3:
        raise board.FreeOnlyError("Must have exactly three actual saved replies")
    if result.get("models") != list(board.MODELS):
        raise board.FreeOnlyError("Model whitelist was changed since verified source")
    for row, role, model in zip(replies, board.ROLES[:3], board.MODEL_FOR_ROLE[:3]):
        if (row.get("role") != role or row.get("model") != model
                or not isinstance(row.get("text"), str) or len(row["text"]) < 90
                or not board._zero(row.get("reported_cost_usd"))):
            raise board.FreeOnlyError("Prior genuine role or zero-price proof invalid")
    if result.get("publication_authorized") is not False or result.get("video_rendered") is not False:
        raise board.FreeOnlyError("Source report incorrectly authorizes production")
    return result


def resume(path, key, *, catalogue=None, ask=None):
    original = original_report(Path(path))
    resumed = {**original}
    resumed["schema"] = "g0dm0d3-four-role-resume-critic-v1"
    resumed["source_run_id"] = SOURCE_RUN_ID
    resumed["source_report_sha256"] = SOURCE_SHA256
    resumed["source_successful_eligible_roles"] = 3
    resumed["original_attempts_including_empty_critic"] = 4
    resumed["resumed_attempts"] = 0
    resumed["model_calls"] = 4
    resumed["status"] = "pending_single_critic"
    resumed["failure_reason"] = None
    resumed["paid_fallback"] = False
    resumed["zero_cost_routing_required"] = True
    resumed["no_paid_models"] = True
    resumed["publication_authorized"] = False
    resumed["video_rendered"] = False
    resumed["human_artistic_approval"] = False
    if not key or len(key) > 800 or any(c.isspace() for c in key):
        resumed.update(status="blocked_missing_openrouter_key")
        return resumed
    try:
        price=board.attest_live_free_models(
            catalogue if catalogue is not None
            else board._get_json("https://openrouter.ai/api/v1/models"))
    except board.FreeOnlyError as exc:
        resumed.update(status="blocked_live_zero_price_unverified",failure_reason=str(exc))
        return resumed
    resumed["latest_live_price_attestation"]=price
    prompt=board._prompt("critico", "giuliano", original["subject"],
                         [r["text"] for r in original["responses"]])
    prompt += (
        "\nCRITICA FINALE CONCRETA, 180-300 parole: individua almeno cinque problemi "
        "e una sola priorità. CONFRONTA le bozze con la vera voce: la prima "
        "scena dice 1900, NON 1901; i riferimenti ai raggi X sono verso "
        "50,26–63,32 secondi e le immagini non sono radiografie. "
        "Non aggiungere narrazione immaginaria, non sostituire il film, "
        "non spacciare CGI per reperti autentici."
    )
    if len(prompt) > 6500:
        raise board.FreeOnlyError("Combined critic prompt above allowed size")
    resumed["resumed_attempts"] = 1
    resumed["model_calls"] = 5  # 4 previous *attempts*, plus one focused resumption
    try:
        if ask is None:
            critic=board._request_free(RESUME_MODEL,prompt,key,
                                       max_output_tokens=MAX_CRITIC_OUTPUT_TOKENS)
        else:
            critic=ask(RESUME_MODEL,prompt,key)
        if critic.get("model") != RESUME_MODEL or not isinstance(critic.get("text"),str):
            raise board.FreeOnlyError("New critic response is invalid")
        if not board._zero(critic.get("reported_cost_usd")):
            raise board.FreeOnlyError("New critic charge not verified zero")
        resumed["responses"] = [*original["responses"],{"role":"critico",**critic}]
        resumed["status"] = "four_roles_returned_unapproved"
    except board.FreeOnlyError as exc:
        resumed["status"] = "critic_only_incomplete_no_retry"
        resumed["failure_reason"] = str(exc)
    except Exception:
        resumed["status"] = "critic_only_incomplete_no_retry"
        resumed["failure_reason"] = "Provider unavailable; not retried"
    return resumed


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--source-report",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    if os.environ.get("G0DM0D3_CRITIC_ONE_SHOT") != "1":
        raise board.FreeOnlyError("One-shot approval missing")
    report=resume(a.source_report,os.environ.get("OPENROUTER_API_KEY",""))
    board.save(report,a.out)
    print("G0DM0D3_CRITIC_RESUME",report["status"],"actual_resumed_attempts",
          report["resumed_attempts"],"real_roles",len(report["responses"]))
    return 0 if report["status"] == "four_roles_returned_unapproved" else 2


if __name__=="__main__":
    try:
        sys.exit(main())
    except board.FreeOnlyError as e:
        print("G0DM0D3_CRITIC_FAIL_CLOSED",e)
        sys.exit(2)
