// One-time import: only the exact reviewed GitHub commit/workflow can connect Vidu.
const ISSUER='https://token.actions.githubusercontent.com';
export const AUDIENCE='https://tra-le-pagine-vidu.600led.workers.dev';
const REF='refs/heads/feature/vidu-mobile-panel';
export async function verifyGithub(token,env,now=Date.now()){
 if(!env.IMPORT_COMMIT||!Number.isFinite(Number(env.IMPORT_UNTIL))||now>Number(env.IMPORT_UNTIL))throw Error('disabled');
 if(typeof token!=='string'||token.length>16000)throw Error('token');
 const parts=token.split('.');if(parts.length!==3)throw Error('token');
 const decode=s=>Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/')+'='.repeat((4-s.length%4)%4)),c=>c.charCodeAt(0));
 const head=JSON.parse(new TextDecoder().decode(decode(parts[0]))),claims=JSON.parse(new TextDecoder().decode(decode(parts[1])));
 const second=now/1000;
 if(head.alg!=='RS256'||typeof head.kid!=='string'||claims.iss!==ISSUER||claims.aud!==AUDIENCE||
    !Number.isFinite(claims.exp)||claims.exp<=second||!Number.isFinite(claims.nbf)||claims.nbf>second+30||
    !Number.isFinite(claims.iat)||claims.iat>second+30||second-claims.iat>600||
    claims.repository_id!=='1424142756'||claims.repository_owner_id!=='249835809'||
    claims.repository!=='GGIANLUCAA/Tra-le-pagine-'||claims.ref!==REF||claims.sha!==env.IMPORT_COMMIT||
    claims.event_name!=='push'||claims.workflow_ref!=='GGIANLUCAA/Tra-le-pagine-/.github/workflows/vidu-connect-once.yml@'+REF)throw Error('claims');
 const r=await fetch(ISSUER+'/.well-known/jwks',{redirect:'error',signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error('jwks');
 const jwk=(await r.json()).keys.find(k=>k.kid===head.kid&&k.kty==='RSA'&&k.use==='sig');if(!jwk)throw Error('key');
 const key=await crypto.subtle.importKey('jwk',jwk,{name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'},false,['verify']);
 if(!await crypto.subtle.verify('RSASSA-PKCS1-v1_5',key,decode(parts[2]),new TextEncoder().encode(parts[0]+'.'+parts[1])))throw Error('signature');
 return claims;
}
