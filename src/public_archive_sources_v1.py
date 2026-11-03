#!/usr/bin/env python3
"""Museum/archive search adapters: candidates only, zero downloads and charges."""
from __future__ import annotations
import html
import json
import re
from urllib.parse import urlencode, quote, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ART={"met","artic","cleveland"}
ARCHIVE={"loc","archive","commons"}
PROVIDERS=ART|ARCHIVE
HOSTS={"collectionapi.metmuseum.org","api.artic.edu",
       "openaccess-api.clevelandart.org","www.loc.gov",
       "archive.org","commons.wikimedia.org"}
AGENT="TraLePagine-Editorial-Research/1.0 (GitHub GGIANLUCAA/Tra-le-pagine-)"
MAX_BYTES=1500000

class ResearchError(ValueError):
    pass

def clean(value):
    if isinstance(value,list):
        value=", ".join(str(x) for x in value[:3])
    return html.unescape(re.sub(r"<[^>]*>","",str(value or ""))).strip()[:300]

def trusted(url, hosts):
    if not isinstance(url,str):
        return ""
    p=urlsplit(url)
    if p.scheme!="https" or p.hostname not in hosts or p.username or p.password or p.port:
        return ""
    return url[:1200]

def fetch_json(url):
    p=urlsplit(url)
    if p.scheme!="https" or p.hostname not in HOSTS or p.username or p.password or p.port:
        raise ResearchError("Host API non consentito")
    req=Request(url,headers={"User-Agent":AGENT,"Accept":"application/json"})
    try:
        with urlopen(req,timeout=18) as res:
            if int(res.headers.get("Content-Length") or 0)>MAX_BYTES:
                raise ResearchError("Risposta troppo grande")
            raw=res.read(MAX_BYTES+1)
            if len(raw)>MAX_BYTES:
                raise ResearchError("Risposta troppo grande")
            return json.loads(raw)
    except HTTPError as e:
        raise ResearchError("HTTP "+str(e.code)+" (senza retry)") from None
    except (URLError,TimeoutError,json.JSONDecodeError):
        raise ResearchError("API non disponibile o JSON non valido") from None

def url(base,**params):
    return base+"?"+urlencode(params)

def candidate(provider,ident,title,page,*,author="",date="",license_claim="",
              preview="",media_kind="image"):
    return {"provider":provider,"id":provider+":"+str(ident)[:100],
            "title":clean(title),"author":clean(author),"date":clean(date),
            "source_url":page,"source_reference":page,"preview":preview,
            "media_kind":media_kind,
            "source_kind":"authentic_artwork" if provider in ART else "verified_archive",
            "license_claim":clean(license_claim) or "UNKNOWN",
            "rights_review":"pending","visual_review":"pending",
            "authenticity_review":"pending","scene_relevance":"pending",
            "selected":False,"review_required":True,
            "note":"Solo candidato: verificare diritti Italia, autenticita, fotogrammi e file originali."}

def search(provider,query,limit=3,fetcher=None):
    if provider not in PROVIDERS:
        raise ResearchError("Provider non supportato")
    if not isinstance(query,str) or not 3<=len(query.strip())<=120 or re.search(r"[\x00-\x1f\x7f]",query):
        raise ResearchError("Query non valida")
    if not isinstance(limit,int) or not 1<=limit<=5:
        raise ResearchError("Limite 1-5")
    get=fetcher or fetch_json
    count=0
    def request(u):
        nonlocal count
        count+=1
        return get(u)
    out=[]
    if provider=="met":
        data=request(url("https://collectionapi.metmuseum.org/public/collection/v1.1/search",
                         q=query,hasImages="true",limit=limit,offset=0))
        for ident in (data.get("objectIDs") or [])[:limit]:
            if not isinstance(ident,int):continue
            x=request("https://collectionapi.metmuseum.org/public/collection/v1/objects/"+str(ident))
            if x.get("isPublicDomain") is not True or not x.get("primaryImageSmall"):continue
            out.append(candidate(provider,ident,x.get("title"),
                "https://www.metmuseum.org/art/collection/search/"+str(ident),
                author=x.get("artistDisplayName"),date=x.get("objectDate"),
                license_claim="Museum open access / public domain, verify record",
                preview=trusted(x.get("primaryImageSmall"),{"images.metmuseum.org"})))
    elif provider=="artic":
        data=request(url("https://api.artic.edu/api/v1/artworks/search",q=query,limit=limit,
            fields="id,title,artist_display,date_display,image_id,is_public_domain",
            **{"query[term][is_public_domain]":"true"}))
        for x in (data.get("data") or [])[:limit]:
            ident=x.get("id"); image_id=str(x.get("image_id") or "")
            if not isinstance(ident,int) or x.get("is_public_domain") is not True:
                continue
            if not re.fullmatch(r"[A-Za-z0-9_-]{5,100}",image_id):continue
            out.append(candidate(provider,ident,x.get("title"),
                "https://www.artic.edu/artworks/"+str(ident),
                author=x.get("artist_display"),date=x.get("date_display"),
                license_claim="Museum record public domain, verify image terms",
                preview="https://www.artic.edu/iiif/2/"+image_id+"/full/843,/0/default.jpg"))
    elif provider=="cleveland":
        data=request(url("https://openaccess-api.clevelandart.org/api/artworks/",
                         q=query,cc0="",has_image=1,limit=limit))
        for x in (data.get("data") or [])[:limit]:
            ident=x.get("id")
            if not isinstance(ident,int):continue
            creator=x.get("creators") or []
            author=creator[0].get("description") if creator and isinstance(creator[0],dict) else ""
            page=trusted(x.get("url"),{"www.clevelandart.org","clevelandart.org"})
            if not page:page="https://www.clevelandart.org/art/"+str(ident)
            preview=trusted((x.get("images") or {}).get("web",{}).get("url"),
                            {"www.clevelandart.org","clevelandart.org"})
            out.append(candidate(provider,ident,x.get("title"),page,
                author=author,date=x.get("creation_date"),
                license_claim=x.get("share_license_status") or "CC0 filter, verify",
                preview=preview))
    elif provider=="loc":
        data=request(url("https://www.loc.gov/search/",q=query,fo="json",c=limit))
        for x in (data.get("results") or [])[:limit]:
            page=trusted(x.get("id"),{"www.loc.gov","loc.gov"})
            if not page:continue
            fmt=clean(x.get("original_format")).lower()
            kind="video" if any(t in fmt for t in ("motion picture","film","video")) else "image"
            images=x.get("image_url") or []
            preview=next((trusted(v,{"www.loc.gov","loc.gov"}) for v in images
                          if trusted(v,{"www.loc.gov","loc.gov"})),"")
            out.append(candidate(provider,x.get("id"),x.get("title"),page,
                author=x.get("contributor"),date=x.get("date"),
                license_claim="Rights and access to verify per record",
                preview=preview,media_kind=kind))
    elif provider=="archive":
        phrase=query.replace("\\"," ").replace('"'," ")
        params=[("q",'title:("'+phrase+'") AND mediatype:(movies)'),
                ("rows",str(limit)),("page","1"),("output","json"),
                ("fl[]","identifier"),("fl[]","title"),("fl[]","year"),
                ("fl[]","creator"),("fl[]","licenseurl")]
        data=request("https://archive.org/advancedsearch.php?"+urlencode(params))
        for x in ((data.get("response") or {}).get("docs") or [])[:limit]:
            ident=x.get("identifier")
            if not isinstance(ident,str) or not re.fullmatch(r"[A-Za-z0-9_.-]{2,120}",ident):
                continue
            out.append(candidate(provider,ident,x.get("title"),
                "https://archive.org/details/"+ident,author=x.get("creator"),
                date=x.get("year"),license_claim=x.get("licenseurl") or "UNKNOWN",
                media_kind="video"))
    elif provider=="commons":
        data=request(url("https://commons.wikimedia.org/w/api.php",action="query",
                         generator="search",gsrsearch=query,gsrnamespace=6,
                         gsrlimit=limit,prop="imageinfo",iiprop="url|size|mime|extmetadata",
                         iiurlwidth=480,format="json",formatversion=2))
        for x in ((data.get("query") or {}).get("pages") or [])[:limit]:
            title=x.get("title")
            if not isinstance(title,str) or not title.startswith("File:"):continue
            info=(x.get("imageinfo") or [{}])[0]
            md=info.get("extmetadata") or {}
            page="https://commons.wikimedia.org/wiki/"+quote(title.replace(" ","_"),safe=":_()-")
            preview=trusted(info.get("thumburl") or info.get("url"),{"upload.wikimedia.org"})
            kind="video" if str(info.get("mime") or "").startswith("video/") else "image"
            out.append(candidate(provider,x.get("pageid",title),title[5:],page,
                author=(md.get("Artist") or {}).get("value"),
                license_claim=(md.get("LicenseShortName") or {}).get("value"),
                preview=preview,media_kind=kind))
    return {"schema":"public-archive-v1","provider":provider,"query":query,
            "api_requests":count,"items":out[:limit],"automatic_download":False,
            "automatic_publish":False,"auto_approved":False,"paid_calls":False}
