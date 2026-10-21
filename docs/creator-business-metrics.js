/* Shared pure calculations. Missing observations never become zero. */
(function (root) {
  'use strict';
  const valid = n => typeof n === 'number' && Number.isFinite(n) && n >= 0;
  function total(rows, field) {
    return rows.length && rows.every(r => valid(r[field])) ? rows.reduce((s,r)=>s+r[field],0) : null;
  }
  function summary(rows) {
    const revenue=total(rows,'revenue'), cost=total(rows,'cost'), hours=total(rows,'hours');
    const margin=revenue!==null && cost!==null ? revenue-cost : null;
    return {revenue,cost,hours,margin,hourly:margin!==null && hours!==null && hours>0 ? margin/hours : null};
  }
  root.CreatorBusinessMetrics=Object.freeze({summary});
})(globalThis);
