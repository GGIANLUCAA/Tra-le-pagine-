#!/usr/bin/env python3
"""Safe read-only check of consumer Vidu token from vidu.com; NEVER submit."""
import json
import os
import subprocess
import sys

def call(name, args):
    try:
        p=subprocess.run(args, capture_output=True, text=True, timeout=45, check=False)
        try:
            data=json.loads(p.stdout)
        except (ValueError, TypeError):
            print(f"{name}: invalid/non-JSON CLI response; exit={p.returncode}; no generation")
            return False
        if not isinstance(data,dict) or data.get("ok") is not True or p.returncode:
            error=data.get("error",{}) if isinstance(data,dict) else {}
            if not isinstance(error,dict):
                error={}
            safe_type=str(error.get("type","unknown"))[:60]
            safe_code=str(error.get("code","unknown"))[:60]
            status=error.get("http_status")
            if type(status) is not int:
                status="unknown"
            print(f"{name}: refused; type={safe_type} code={safe_code} http_status={status} exit={p.returncode}; no generation")
            return False
        if name.endswith("quote_NOT_Q2_PRO_FAST"):
            cost=data.get("cost_credits")
            if type(cost) is int:
                print(f"{name}: verified; 8_credit_ceiling={cost<=8}; can_submit={data.get('can_submit') is True}; no generation")
            else:
                print(f"{name}: verified with no interpretable price; no generation")
        else:
            print(f"{name}: confirmed; account quota numbers hidden from public logs")
        return True
    except (OSError,subprocess.TimeoutExpired,ValueError):
        print(f"{name}: unavailable or invalid output; no generation")
        return False

def main():
    if not os.getenv("VIDU_TOKEN","").strip():
        print("MISSING_CONSUMER_TOKEN: retrieve from vidu.com avatar > Vidu Token")
        return 2
    if os.getenv("VIDU_BASE_URL")!="https://service.vidu.com":
        print("BLOCKED: consumer Vidu overseas endpoint required")
        return 3
    print("READ ONLY: no generation, no uploads, no purchases, no retries")
    success=True
    for name,cmd in [
        ("consumer_subscription_pass",["vidu-cli","quota","pass"]),
        ("consumer_included_credits",["vidu-cli","quota","credit"]),
        ("Q2_legacy_exploratory_quote_NOT_Q2_PRO_FAST",[
            "vidu-cli","task","cost","--type","img2video",
            "--model-version","3.1","--duration","5","--resolution","1080p",
            "--transition","pro","--schedule-mode","nopeak"]),
        ("EXACT_APPROVED_Q2_PRO_FAST_720P_READ_ONLY",[
            "vidu-cli","task","cost","--type","img2video",
            "--model-version","viduq2-pro-fast","--duration","5","--resolution","720p",
            "--transition","pro","--schedule-mode","nopeak"])]:
        success=call(name,cmd) and success
    print("ZERO tasks submitted. Never treat exploratory Q2 quote as approval of Q2 Pro Fast.")
    return 0 if success else 4

if __name__=="__main__":
    sys.exit(main())
