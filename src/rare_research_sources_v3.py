#!/usr/bin/env python3
"""Ten opt-in research adapters: obscure sources, primary records, audio and texts.

Never downloads media, approves copyright, generates video, or spends credits.
No automated bulk research; every invocation requests only one provider.
"""
from __future__ import annotations
import argparse
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROVIDERS={
    "rijks": "artwork", "finna": "archive",
    "getty_museum": "artwork", "getty_provenance": "provenance",
    "wikidata": "reference", "openverse_audio": "sound",
    "librivox": "audio_reference", "openlibrary": "book",
    "gutendex": "public_domain_book", "crossref": "scholarship",
}
HOSTS={
    "data.rijksmuseum.nl","api.finna.fi","data.getty.edu",
    "www.wikidata.org","api.openverse.org","librivox.org",
    "openlibrary.org","gutendex.com","api.crossref.org",
}
AGENT="ArtVision-ArchiveResearch/3.0 (https://github.com/GGIANLUCAA/Tra-le-pagine-)"
MAX_BYTES=1_500_000
UUID=re.compile(r"[a-fA-F0-9]{8}-(?:[a-fA-F0-9]{4}-){3}[a-fA-F0-9]{12}\Z")

class ResearchError(ValueError):
    pass

def text(value):
    if isinstance(value,list):
        value=", ".join(str(v) for v in value[:3])
    if not isinstance(value,(str,int,float)):
        return ""
    return html.unescape(re.sub(r"<[^>]*>","",str(value))).strip()[:250]

def trusted(url, hosts):
    if not isinstance(url,str):
        return ""
    p=urllib.parse.urlsplit(url)
    if p.scheme != "https" or p.hostname not in hosts or p.username or p.password or p.port:
        return ""
    return url[:1100]

def url(base,**fields):
    return base+"?"+urllib.parse.urlencode(fields,doseq=True)

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise ResearchError("Redirect non consentito: controllare host manualmente")

def request_json(uri):
    p=urllib.parse.urlsplit(uri)
    if p.scheme!="https" or p.hostname not in HOSTS or p.username or p.password or p.port:
        raise ResearchError("Host API non consentito")
    request=urllib.request.Request(uri,headers={"User-Agent":AGENT,"Accept":"application/json"})
    try:
        with urllib.request.build_opener(NoRedirect).open(request,timeout=18) as response:
            if int(response.headers.get("Content-Length") or 0)>MAX_BYTES:
                raise ResearchError("Risposta troppo grande")
            raw=response.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:
            raise ResearchError("Risposta troppo grande")
        return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raise ResearchError("HTTP "+str(exc.code)+"; no automatic retries") from None
    except (urllib.error.URLError,TimeoutError,json.JSONDecodeError):
        raise ResearchError("API unavailable or unexpected JSON") from None

def candidate(provider, identifier, name, source_url, *, author="", date="",
              rights="Rights to verify", note="", media_kind="metadata", preview=""):
    return {
        "provider":provider,"id":provider+":"+str(identifier)[:110],
        "title":text(name),"author":text(author),"date":text(date),
        "source_url":source_url,"source_reference":source_url,
        "media_kind":media_kind,"research_category":PROVIDERS[provider],
        "license_claim":text(rights),"preview":preview,
        "rights_review":"pending","authenticity_review":"pending",
        "visual_review":"pending","scene_relevance":"pending",
        "selected":False,"approved":False,"downloaded":False,
        "note":text(note or "Metadata only: verify original source, license and Italian rights."),
    }

def validate(provider,query,limit):
    if provider not in PROVIDERS:
        raise ResearchError("Unknown provider")
    if not isinstance(query,str) or not 3<=len(query.strip())<=120 or re.search(r"[\x00-\x1f\x7f]",query):
        raise ResearchError("Query should have 3-120 printable characters")
    if not isinstance(limit,int) or not 1<=limit<=5:
        raise ResearchError("Up to 5 candidates")
    if provider in ("getty_museum","getty_provenance") and not UUID.fullmatch(query.strip()):
        raise ResearchError("Getty lookup requires an exact official UUID from its catalogue")
    return query.strip()

def search(provider,query,limit=3,fetcher=None):
    query=validate(provider,query,limit)
    fetch=fetcher or request_json
    calls=0
    def get(u):
        nonlocal calls
        calls+=1
        return fetch(u)
    results=[]

    if provider=="rijks":
        data=get(url("https://data.rijksmuseum.nl/search/collection",title=query,imageAvailable="true"))
        for obj in (data.get("orderedItems") or [])[:limit]:
            uri=trusted(obj.get("id"),{"id.rijksmuseum.nl","data.rijksmuseum.nl"})
            if not uri:continue
            results.append(candidate(provider,uri.rsplit("/",1)[-1],query,uri,
                rights="Object metadata only; IIIF image license must be verified",
                media_kind="image_candidate"))

    elif provider=="finna":
        data=get(url("https://api.finna.fi/v1/search",lookfor=query,limit=limit,
                     **{"field[]":["id","title","year","formats","images"]}))
        for obj in (data.get("records") or [])[:limit]:
            ident=obj.get("id")
            if not isinstance(ident,str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{2,150}",ident):
                continue
            page="https://finna.fi/Record/"+urllib.parse.quote(ident,safe=":._-")
            results.append(candidate(provider,ident,obj.get("title") or query,page,
                date=obj.get("year"),rights="Finna institution-specific media rights",
                media_kind="image_candidate"))

    elif provider in ("getty_museum","getty_provenance"):
        stem=("https://data.getty.edu/museum/collection/object/" if provider=="getty_museum"
              else "https://data.getty.edu/provenance/")
        page=stem+query.lower()
        data=get(page)
        if not isinstance(data,dict) or not data.get("id"):data={}
        ident=trusted(data.get("id"),{"data.getty.edu"})
        if ident and ident.startswith(stem):
            names=data.get("identified_by") or []
            title=next((x.get("content") for x in names if isinstance(x,dict) and x.get("content")),query)
            results.append(candidate(provider,query,title,ident,
                rights="Getty metadata CC0; images/descriptions may carry separate rights",
                media_kind="metadata",note="Exact-ID object/provenance lookup, not title search"))

    elif provider=="wikidata":
        data=get(url("https://www.wikidata.org/w/api.php",action="wbsearchentities",
                     search=query,language="en",limit=limit,format="json",type="item"))
        for obj in (data.get("search") or [])[:limit]:
            ident=obj.get("id")
            if not isinstance(ident,str) or not re.fullmatch(r"Q[1-9][0-9]{0,15}",ident):
                continue
            results.append(candidate(provider,ident,obj.get("label"),
                "https://www.wikidata.org/wiki/"+ident,
                note=obj.get("description") or "Community-maintained metadata; cross-check museum"))

    elif provider=="openverse_audio":
        data=get(url("https://api.openverse.org/v1/audio/",q=query,
                     page_size=limit,license="cc0,by",license_type="commercial"))
        for obj in (data.get("results") or [])[:limit]:
            page=trusted(obj.get("foreign_landing_url"),
                        {"freesound.org","commons.wikimedia.org","archive.org",
                         "soundbible.com","www.jamendo.com","openverse.org"})
            if not page:page=trusted(obj.get("detail_url"),{"api.openverse.org"})
            if not page:continue
            results.append(candidate(provider,obj.get("id"),obj.get("title"),page,
                author=obj.get("creator"),rights=obj.get("license") or "Verify each track",
                note="Audio search only; inspect license, attribution and commercial usage",
                media_kind="audio"))

    elif provider=="librivox":
        search_field="author" if query.lower().startswith("author:") else "title"
        term=query.split(":",1)[1].strip() if query.lower().startswith(("author:","title:")) else query
        if len(term)<3:
            raise ResearchError("LibriVox requires a title or author of at least 3 characters")
        data=get(url("https://librivox.org/api/feed/audiobooks/",format="json",
                     limit=limit,**{search_field:term}))
        for obj in (data.get("books") or [])[:limit]:
            ident=str(obj.get("id") or "")
            if not re.fullmatch(r"[0-9]{1,16}",ident):continue
            page=trusted(obj.get("url_librivox"),{"librivox.org"})
            if not page:page="https://librivox.org/search?q="+urllib.parse.quote(query)
            authors=obj.get("authors") or []
            who=" ".join(text(p.get("first_name"))+" "+text(p.get("last_name"))
                         for p in authors[:2] if isinstance(p,dict))
            results.append(candidate(provider,ident,obj.get("title"),page,author=who,
                rights="LibriVox says public domain; check relevant territories",
                media_kind="audio_reference",note="Reference to original reading, no voice generation"))

    elif provider=="openlibrary":
        data=get(url("https://openlibrary.org/search.json",q=query,limit=limit,
                     fields="key,title,author_name,first_publish_year"))
        for obj in (data.get("docs") or [])[:limit]:
            key=obj.get("key")
            if not isinstance(key,str) or not re.fullmatch(r"/works/OL[0-9]+W",key):
                continue
            results.append(candidate(provider,key.rsplit("/",1)[-1],obj.get("title"),
                "https://openlibrary.org"+key,author=obj.get("author_name"),
                date=obj.get("first_publish_year"),
                rights="Bibliographic metadata only, no text rights",
                note="Do not bulk-crawl or use as commercial backend"))

    elif provider=="gutendex":
        data=get(url("https://gutendex.com/books/",search=query))
        for obj in (data.get("results") or [])[:limit]:
            ident=obj.get("id")
            if not isinstance(ident,int) or ident<=0:continue
            authors=obj.get("authors") or []
            who=", ".join(text(a.get("name")) for a in authors[:2] if isinstance(a,dict))
            results.append(candidate(provider,ident,obj.get("title"),
                "https://www.gutenberg.org/ebooks/"+str(ident),
                author=who,rights="Project Gutenberg USA status, verify Italy",
                media_kind="book",note="Bibliographic discovery; no book download"))

    elif provider=="crossref":
        data=get(url("https://api.crossref.org/works",**{
            "query.bibliographic":query,"rows":limit,"select":"DOI,title,author,published"}))
        for obj in ((data.get("message") or {}).get("items") or [])[:limit]:
            doi=obj.get("DOI")
            if not isinstance(doi,str) or len(doi)>180 or not doi.startswith("10."):
                continue
            contributors=obj.get("author") or []
            author=", ".join((text(a.get("given"))+" "+text(a.get("family"))).strip()
                             for a in contributors[:2] if isinstance(a,dict))
            year=((obj.get("published") or {}).get("date-parts") or [[]])[0]
            results.append(candidate(provider,doi,obj.get("title"),
                "https://doi.org/"+urllib.parse.quote(doi,safe="/._;()-"),
                author=author,date=str(year[0]) if year else "",
                rights="Metadata accessible, article content may be copyrighted"))

    return {"schema":"rare-primary-research-v3","provider":provider,"query":query,
            "api_requests":calls,"items":results[:limit],
            "downloaded_files":0,"automatic_selection":False,
            "auto_approved":False,"automatic_publish":False,"paid_calls":False,
            "human_review_required":True}

def render_html(report):
    """Offline mobile view: HTML escaping, no external JavaScript or network."""
    pieces=[]
    for item in report["items"]:
        name=html.escape(item["title"] or item["id"],quote=True)
        page=html.escape(item["source_url"],quote=True)
        who=html.escape(item["author"],quote=True)
        rights=html.escape(item["license_claim"],quote=True)
        pieces.append('<article><h2>'+name+'</h2><p>'+who+'</p><p>'+rights+
                      '</p><p><a href="'+page+'">Consulta la fonte originale</a></p>'+
                      '<small>Da verificare: diritti, autenticita e qualita</small></article>')
    return ('<!doctype html><html lang="it"><head><meta charset="utf-8">'+
            '<meta name="viewport" content="width=device-width,initial-scale=1">'+
            '<title>Ricerca fonti storiche V3</title><style>'+
            'body{font:16px system-ui;margin:auto;padding:18px;max-width:780px;'+
            'line-height:1.5;background:#172232;color:#eee}article{padding:18px;'+
            'margin:14px 0;border:1px solid #65718b;border-radius:14px}'+
            'a{color:#bedaf9}small{color:#d9c9a7}</style></head><body><h1>Fonti da verificare</h1>'+
            '<p>Ricerca: '+html.escape(report["query"],quote=True)+
            ' · '+html.escape(report["provider"],quote=True)+'</p>'+
            ''.join(pieces)+'<p>Nessun media approvato o scaricato.</p></body></html>')


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--provider",choices=sorted(PROVIDERS),required=True)
    p.add_argument("--query",required=True)
    p.add_argument("--limit",type=int,default=3)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    result=search(args.provider,args.query,args.limit)
    dst=Path(args.out)
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    dst.with_suffix(".html").write_text(render_html(result),encoding="utf-8")
    print(json.dumps({"provider":args.provider,"results":len(result["items"]),
                      "api_requests":result["api_requests"],"approved":False}))

if __name__=="__main__":
    main()
