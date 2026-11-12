'use strict';
// Korrelationstest nach Pearson: stats.js gegen scipy.stats.pearsonr (scipy 1.18).
//   node tests/test_korrelation.js
const path = require('path');
const S = require(path.join(__dirname, '..', 'web', 'static', 'stats.js'));

const CASES = [
  { x: [1, 2, 3, 4, 5, 6], y: [2, 1, 4, 3, 7, 8],
    r: 0.9014600868406593,
    p: { 'two-sided': 0.014086754809093853, less: 0.992956622595453, greater: 0.007043377404546926 },
    ci: [0.3349310458848851, 0.9892764833634093] },
  { x: [10, 12, 15, 19, 23, 28, 31, 40], y: [5.1, 4.2, 6.6, 6.0, 8.8, 7.9, 11.0, 12.5],
    r: 0.9478748156758001,
    p: { 'two-sided': 0.00034036738385421117, less: 0.9998298163080729, greater: 0.00017018369192710558 },
    ci: [0.7324072413333408, 0.990770673916992] },
  { x: [150, 160, 170, 180, 175, 165, 155], y: [35, 38, 42, 45, 44, 40, 36],
    r: 0.9960238411119946,
    p: { 'two-sided': 1.910677784395542e-06, less: 0.9999990446611078, greater: 9.55338892197771e-07 },
    ci: [0.9721111290075648, 0.9994389460681056] },
];

let pass = 0, fail = 0;
const close = (a, b, tol) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(b));
function check(ok, what) { if (ok) pass++; else { fail++; console.log('✗ ' + what); } }

CASES.forEach((c, i) => {
  for (const alt of ['two-sided', 'less', 'greater']) {
    const res = S.correlationTest(c.x, c.y, alt, 0.05);
    check(close(res.r, c.r, 1e-12), `Fall ${i}: r`);
    check(Math.abs(res.p - c.p[alt]) <= 1e-9 * Math.max(1e-3, c.p[alt]) + 1e-15, `Fall ${i} ${alt}: p = ${res.p}, erwartet ${c.p[alt]}`);
  }
  const res = S.correlationTest(c.x, c.y);
  check(close(res.ci[0], c.ci[0], 1e-8) && close(res.ci[1], c.ci[1], 1e-8), `Fall ${i}: Konfidenzintervall ${res.ci}`);
  check(close(res.r2, c.r * c.r, 1e-12), `Fall ${i}: R²`);
});

// negativer Zusammenhang und kein Zusammenhang
const neg = S.correlationTest([1, 2, 3, 4, 5], [10, 8, 7, 4, 2]);
check(neg.r < -0.98 && neg.reject, 'negative Korrelation');
const none = S.correlationTest([1, 2, 3, 4, 5, 6], [3, 1, 4, 1, 5, 2]);
check(!none.reject && Math.abs(none.r) < 0.5, 'keine Korrelation');
// perfekte Korrelation: kein NaN
const perf = S.correlationTest([1, 2, 3, 4], [2, 4, 6, 8]);
check(perf.r === 1 && perf.p === 0 && perf.reject, 'perfekte Korrelation');

const throws = f => { try { f(); return false; } catch (e) { return e instanceof S.TestError; } };
check(throws(() => S.correlationTest([1, 2], [1, 2])), 'n < 3 wirft');
check(throws(() => S.correlationTest([1, 1, 1], [1, 2, 3])), 'konstante Reihe wirft');
check(throws(() => S.correlationTest([1, 2, 3], [1, 2])), 'ungleich lang wirft');
check(close(S.normPpf(0.975), 1.959963984540054, 1e-8), 'normPpf(0,975)');

console.log(`${pass} bestanden, ${fail} fehlgeschlagen`);
process.exit(fail ? 1 : 0);
