#!/usr/bin/env python3
"""V2: five more keyless catalogues. Discovery-only; no media is imported.

All result entries remain pending for rights, authenticity and visual review.
Never turn a source API result into an approved publication automatically.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import public_archive_sources_v1 as old

ART = old.ART | {"vam", "smk", "wellcome"}
ARCHIVE = old.ARCHIVE | {"nasa", "gallica", "wellcome"}
PROVIDERS = ART | ARCHIVE
EXTRA_HOSTS = {"api.vam.ac.uk", "api.smk.dk",
               "api.wellcomecollection.org", "images-api.nasa.gov",
               "gallica.bnf.fr"}
MAX_BYTES = old.MAX_BYTES

def fetch_json(url):
    return _fetch(url, "json")

def fetch_xml(url):
    return _fetch(url, "xml")

def _fetch(url, mode):
    p=old.urlsplit(url)
    if p.scheme!="https" or p.hostname not in EXTRA_HOSTS or p.username or p.password or p.port:
        raise old.ResearchError("Host non consentito V2")
    req=Request(url,headers={"User-Agent":old.AGENT,
                             "Accept":"application/json" if mode=="json" else "application/xml"})
    try:
        with urlopen(req,timeout=18) as response:
            if int(response.headers.get("Content-Length") or 0)>MAX_BYTES:
                raise old.ResearchError("Risposta API troppo grande")
            raw=response.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:
            raise old.ResearchError("Risposta API troppo grande")
        return json.loads(raw) if mode=="json" else raw
    except HTTPError as exc:
        raise old.ResearchError("HTTP "+str(exc.code)+"; nessun retry automatico") from None
    except (URLError, TimeoutError, ValueError, ET.ParseError):
        raise old.ResearchError("Risposta API non disponibile o non valida") from None

def _name(entry):
    if isinstance(entry,dict):
        return entry.get("name") or entry.get("title") or entry.get("label") or ""
    if isinstance(entry,list):
        return _name(entry[0]) if entry else ""
    return entry or ""

def _gallica(xml_source,limit):
    if not isinstance(xml_source,(bytes,str)) or len(xml_source)>MAX_BYTES:
        raise old.ResearchError("Gallica response missing or too long")
    # stdlib ElementTree does not resolve external XML entities.
    try:
        root=ET.fromstring(xml_source)
    except ET.ParseError:
        raise old.ResearchError("Gallica XML invalid") from None
    local=lambda element: element.tag.split("}")[-1].lower() if isinstance(element.tag,str) else ""
    records=[x for x in root.iter() if local(x)=="record"]
    results=[]
    for rec in records[:limit]:
        props={}
        for elem in rec.iter():
            name=local(elem)
            if name in ("identifier","title","creator","date","rights","type") and elem.text:
                props.setdefault(name,[]).append(elem.text.strip())
        ark=next((v for v in props.get("identifier",[])
                  if v.startswith("https://gallica.bnf.fr/ark:/12148/")),"")
        if not ark:continue
        code=ark.removeprefix("https://gallica.bnf.fr/ark:/12148/").split("/")[0].split("?")[0]
        if not re.fullmatch(r"[A-Za-z0-9]{4,80}",code):continue
        kind="image"  # Gallica catalogue results are documentary items, not confirmed motion pictures.
        results.append(old.candidate("gallica",code,_name(props.get("title")),ark,
             author=_name(props.get("creator")),date=_name(props.get("date")),
             license_claim="Gallica rights notice requires review",
             media_kind=kind))
    return results

def search(provider,query,limit=3,fetcher=None):
    if provider in old.PROVIDERS:
        return old.search(provider,query,limit,fetcher)
    if provider not in PROVIDERS:
        raise old.ResearchError("Provider V2 non supportato")
    if not isinstance(query,str) or not 3<=len(query.strip())<=120 or re.search(r"[\x00-\x1f\x7f]",query):
        raise old.ResearchError("Query non valida")
    if not isinstance(limit,int) or not 1<=limit<=5:
        raise old.ResearchError("Limit 1-5")
    get=fetcher or (fetch_xml if provider=="gallica" else fetch_json)
    count=0
    def request(url):
        nonlocal count
        count+=1
        return get(url)
    results=[]
    if provider=="vam":
        data=request(old.url("https://api.vam.ac.uk/v2/objects/search",
                             q=query,page_size=limit,images_exist=1))
        for obj in (data.get("records") or [])[:limit]:
            ident=obj.get("systemNumber")
            if not isinstance(ident,str) or not re.fullmatch(r"O[0-9]{3,16}",ident):
                continue
            images=obj.get("_images") or {}
            preview=old.trusted(images.get("_primary_thumbnail"),{"framemark.vam.ac.uk"})
            if not preview:continue
            maker=obj.get("_primaryMaker") or {}
            results.append(old.candidate(provider,ident,
                obj.get("_primaryTitle") or obj.get("objectType"),
                "https://collections.vam.ac.uk/item/"+ident+"/",
                author=_name(maker),date=obj.get("_primaryDate"),
                license_claim="V&A collections image; reuse terms must be checked",
                preview=preview))
    elif provider=="smk":
        data=request(old.url("https://api.smk.dk/api/v1/art/search/",
                         keys=query,filters="[public_domain:true],[has_image:true]",
                         offset=0,rows=limit))
        for obj in (data.get("items") or [])[:limit]:
            ident=str(obj.get("object_number") or obj.get("id") or "")
            if not re.fullmatch(r"[A-Za-z0-9_.-]{2,100}",ident):continue
            # The API search filter is public domain; still needs item-level verification.
            preview=old.trusted(obj.get("image_thumbnail"),
                {"iip-thumb.smk.dk","api.smk.dk","open.smk.dk"})
            titles=obj.get("titles")
            name=obj.get("title") or _name(titles) or ident
            results.append(old.candidate(provider,ident,name,
                "https://open.smk.dk/en/artwork/image/"+ident,
                author=_name(obj.get("artist")) or _name(obj.get("artists")),
                date=obj.get("production_date") or obj.get("dating"),
                license_claim="SMK public-domain search filter, verify specific record",
                preview=preview))
    elif provider=="wellcome":
        data=request(old.url("https://api.wellcomecollection.org/catalogue/v2/works",
                             query=query,include="images,contributors,production",pageSize=limit,page=1))
        for obj in (data.get("results") or [])[:limit]:
            ident=obj.get("id")
            if not isinstance(ident,str) or not re.fullmatch(r"[a-zA-Z0-9]{4,50}",ident):
                continue
            contributors=obj.get("contributors") or []
            agent=contributors[0].get("agent") if contributors and isinstance(contributors[0],dict) else {}
            author=_name(agent)
            results.append(old.candidate(provider,ident,obj.get("title"),
                "https://wellcomecollection.org/works/"+ident,
                author=author,license_claim="Work metadata; image license varies by item"))
    elif provider=="nasa":
        data=request(old.url("https://images-api.nasa.gov/search",
                             q=query,media_type="image,video",page_size=limit))
        for obj in ((data.get("collection") or {}).get("items") or [])[:limit]:
            metadata=obj.get("data") or []
            if not metadata or not isinstance(metadata[0],dict):continue
            d=metadata[0]
            ident=d.get("nasa_id")
            if not isinstance(ident,str) or not re.fullmatch(r"[A-Za-z0-9_.-]{2,120}",ident):
                continue
            links=obj.get("links") or []
            preview=next((old.trusted(link.get("href"),{"images-assets.nasa.gov","images.nasa.gov"})
                         for link in links if isinstance(link,dict) and
                         old.trusted(link.get("href"),{"images-assets.nasa.gov","images.nasa.gov"})),"")
            media_kind=d.get("media_type")
            if media_kind not in ("video","image"):continue
            results.append(old.candidate(provider,ident,d.get("title"),
                "https://images.nasa.gov/details/"+ident,
                author=_name(d.get("photographer")) or "NASA",
                date=d.get("date_created"),license_claim="NASA media guidelines and third-party rights",
                preview=preview,media_kind=media_kind))
    elif provider=="gallica":
        phrase=query.replace("\\"," ").replace('"'," ")
        query_cql='(gallica all "'+phrase+'")'
        data=request(old.url("https://gallica.bnf.fr/SRU",version="1.2",
                     operation="searchRetrieve",query=query_cql,
                     maximumRecords=limit,startRecord=1))
        results=_gallica(data,limit)
    return {"schema":"public-archive-v2","provider":provider,"query":query,
            "api_requests":count,"items":results[:limit],"automatic_download":False,
            "automatic_publish":False,"auto_approved":False,"paid_calls":False}
