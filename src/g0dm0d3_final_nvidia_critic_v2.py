#!/usr/bin/env python3
"""Single FREE NVIDIA critic on pre-existing 3 genuine model responses.

Previous 4-role attempt (3 genuine answers, 1 empty): run 43275046749.
Focused Liquid retry (also empty): run 43276334272.
This stage verifies and reuses the *existing* three answers, sending just ONE
new, explicitly no-charge NVIDIA critic prompt with no retry or fallback.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import g0dm0d3_free_four_roles_v1 as board

PREVIOUS_RUN = 43276334272
PREVIOUS_REPORT_SHA256 = "28b118a9c42c947f9028f3f6dbcb0ffa5786c489ea7e96f6c55c73c3215e78f6"
PREVIOUS_ORIGINAL_RUN = 43275046749
PREVIOUS_ORIGINAL_SHA256 = "1c634b10557a0c7485c3ffa7413d0d6641d4b0df0eec267ebda5ed0e17fd64a8"
CRITIC_MODEL = "nvidia/nemotron-3.5-lightning:free"


def verify_prior(path):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PREVIOUS_REPORT_SHA256:
        raise board.FreeOnlyError("Previous failed-critic report SHA mismatch")
    data=json.loads(raw)
    if (data.get("schema")!="g0dm0d3-four-role-resume-critic-v1"
            or data.get("status")!="critic_only_incomplete_no_retry"
            or data.get("source_run_id")!=PREVIOUS_ORIGINAL_RUN
            or data.get("source_report_sha256")!=PREVIOUS_ORIGINAL_SHA256
            or data.get("model_calls")!=5
            or data.get("resumed_attempts")!=1):
        raise board.FreeOnlyError("Previous result was not the single verified Liquid failure")
    if not str(data.get("failure_reason","")).startswith("No displayable text"):
        raise board.FreeOnlyError("Previous failure type unexpected")
    if data.get("models")!=list(board.MODELS) or data.get("format")!="giuliano":
        raise board.FreeOnlyError("Prior pinned models or format mismatch")
    responses=data.get("responses")
    if not isinstance(responses,list) or len(responses)!=3:
        raise board.FreeOnlyError("Need three genuine saved responses")
    for row,role,model in zip(responses,board.ROLES[:3],board.MODEL_FOR_ROLE[:3]):
        if (not isinstance(row,dict) or row.get("role")!=role
                or row.get("model")!=model or
                not isinstance(row.get("text"),str) or len(row["text"])<90
                or not board._zero(row.get("reported_cost_usd"))):
            raise board.FreeOnlyError("Prior model / user-visible text / cost proof invalid")
    if data.get("publication_authorized") is not False or data.get("video_rendered") is not False:
        raise board.FreeOnlyError("Previous output wrongly approved a video")
    return data


def complete(source,token,*,catalogue=None,ask=None):
    original=verify_prior(source)
    report=dict(original)
    report["schema"]="g0dm0d3-final-critic-nvidia-v2"
    report["status"]="pending_final_critic_only"
    report["source_run_id"]=PREVIOUS_RUN
    report["source_report_sha256"]=PREVIOUS_REPORT_SHA256
    report["original_run_id"]=PREVIOUS_ORIGINAL_RUN
    report["successful_roles_carried_forward"]=3
    report["previous_actual_model_attempts"]=5
    report["new_actual_model_attempts"]=0
    report["model_calls"]=5
    report["failure_reason"]=None
    report["critic_model"]=CRITIC_MODEL
    report["four_roles_two_distinct_models"]=True
    report["critic_uses_same_model_as_screenwriter_and_director"]=True
    report["no_auto_retry"]=True
    report["video_rendered"]=False
    report["publication_authorized"]=False
    report["human_artistic_approval"]=False
    if not isinstance(token,str) or not token or len(token)>800 or any(c.isspace() for c in token):
        report["status"]="blocked_missing_key"
        return report
    try:
        report["current_zero_price_verification"]=board.attest_live_free_models(
            catalogue if catalogue is not None
            else board._get_json("https://openrouter.ai/api/v1/models"))
    except board.FreeOnlyError as exc:
        report["status"]="blocked_zero_price_unverified"
        report["failure_reason"]=str(exc)
        return report
    prompt=board._prompt("critico","giuliano",original["subject"],
                          [x["text"] for x in original["responses"]])
    prompt += (
        "\nRISPOSTA BREVE IN ITALIANO, MASSIMO 220 PAROLE. Prima individua "
        "due inesattezze riscontrabili nel master originale (1900 vs 1901, "
        "riferimenti ai raggi X dal secondo 50), poi le ripetizioni dei frame "
        "o delle CGI (63-75s e 75-96s). Formula 3 correzioni con timecode "
        "che conservino la voce Gacrux e non inventino nuove foto o fonti. "
        "Nessuna frase generica, nessun finale filosofico. Non fingere di "
        "aver visionato l'intero video: hai soltanto lo shotmap verificato."
    )
    if len(prompt)>6500:
        raise board.FreeOnlyError("Critic prompt unexpectedly long")
    report["new_actual_model_attempts"]=1
    report["model_calls"]=6  # 4 first trial, one failed Liquid continuation, this single NVIDIA critic
    try:
        outcome=(ask or (lambda m,p,k: board._request_free(
            m,p,k,max_output_tokens=1600)))(CRITIC_MODEL,prompt,token)
        if (not isinstance(outcome,dict) or outcome.get("model")!=CRITIC_MODEL
                or not isinstance(outcome.get("text"),str) or len(outcome["text"])<80
                or not board._zero(outcome.get("reported_cost_usd"))):
            raise board.FreeOnlyError("NVIDIA critic output/model/zero-cost unverifiable")
        report["responses"]=[*original["responses"],{"role":"critico",**outcome}]
        report["status"]="four_real_roles_two_free_models_unapproved"
    except board.FreeOnlyError as exc:
        report["status"]="final_critic_failed_no_retry"
        report["failure_reason"]=str(exc)
    except Exception:
        report["status"]="final_critic_failed_no_retry"
        report["failure_reason"]="Provider unavailable without retry"
    return report


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-report",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    opts=parser.parse_args(argv)
    if os.environ.get("G0DM0D3_NVIDIA_CRITIC_FINAL_ONE_SHOT")!="1":
        raise board.FreeOnlyError("Explicit one-shot approval missing")
    result=complete(opts.source_report,os.environ.get("OPENROUTER_API_KEY",""))
    board.save(result,opts.out)
    print("G0DM0D3_FINAL_CRITIC",result["status"],
          "fresh_attempts",result["new_actual_model_attempts"],
          "saved_real_roles",len(result["responses"]))
    return 0 if result["status"]=="four_real_roles_two_free_models_unapproved" else 2


if __name__=="__main__":
    try:
        sys.exit(main())
    except board.FreeOnlyError as exc:
        print("G0DM0D3_NVIDIA_CRITIC_BLOCKED",exc)
        sys.exit(2)
