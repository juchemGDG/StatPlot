'use strict';
// Regressionstest: stats.js gegen die Python-Originale aus NIT_Code.
//   node tests/test_stats.js
// Die Referenzwerte (fixtures.json) erzeugt tests/make_fixtures.py.
const path = require('path');
const fs = require('fs');
const S = require(path.join(__dirname, '..', 'web', 'static', 'stats.js'));
const FX = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures.json'), 'utf8'));

let pass = 0, fail = 0;
function check(ok, what) {
  if (ok) { pass++; return; }
  fail++;
  console.log('✗ ' + what);
}

// Zahlen vergleichen: Summen werden in Python 3.12 kompensiert addiert,
// deshalb kleine Abweichungen in den letzten Stellen zulassen.
function close(a, b, tol) {
  if (tol === undefined) tol = 1e-9;
  if (typeof b === 'string' && /^(nan|inf|-inf)$/.test(b)) return String(a) === ({ nan: 'NaN', inf: 'Infinity', '-inf': '-Infinity' })[b];
  if (a === null || b === null || typeof a !== 'number' || typeof b !== 'number') return a === b;
  return Math.abs(a - b) <= tol * Math.max(1, Math.abs(a), Math.abs(b));
}
function deepClose(a, b, tol) {
  if (Array.isArray(b)) return Array.isArray(a) && a.length === b.length && b.every((x, i) => deepClose(a[i], x, tol));
  if (b && typeof b === 'object') return a && typeof a === 'object' && Object.keys(b).every(k => deepClose(a[k], b[k], tol));
  return close(a, b, tol);
}
const show = v => JSON.stringify(v);

for (const [v, d, want] of FX.fmt_num) {
  const got = S.fmtNum(v, d);
  check(got === want, `fmtNum(${v}, ${d}) = ${got}, erwartet ${want}`);
}
for (const [d, want] of FX.describe) {
  const got = S.describe(d);
  check(deepClose(got, want), `describe(${show(d)}) = ${show(got)}, erwartet ${show(want)}`);
}
for (const [d, want] of FX.quartiles) check(deepClose(S.quartiles(d), want), `quartiles(${show(d)})`);
for (const [d, want] of FX.whiskers) {
  const [q1, , q3] = S.quartiles(d);
  check(deepClose(S.tukeyWhiskers(d, q1, q3), want), `tukeyWhiskers(${show(d)})`);
}
for (const [d, w, want] of FX.histogram) {
  const got = S.histogramBins(d, w);
  check(deepClose(got, want, 0), `histogramBins(${show(d)}, ${w}) = ${show(got)}, erwartet ${show(want)}`);
}
for (const [lo, hi, cnt, pad, want] of FX.nice_ticks) {
  const got = S.niceTicks(lo, hi, cnt, pad);
  check(deepClose(got, want, 1e-12), `niceTicks(${lo}, ${hi}) = ${show(got)}, erwartet ${show(want)}`);
}
for (const [xs, ys, want, text] of FX.regression) {
  const got = S.linearRegression(xs, ys);
  check(deepClose(got, want), `linearRegression(${show(xs)})`);
  const gotText = S.regressionText(...got);
  check(gotText === text, `regressionText = ${gotText}, erwartet ${text}`);
}
for (const [pairs, want] of FX.cumulate) check(deepClose(S.cumulate(pairs), want), 'cumulate');
for (const [t, df, want] of FX.t_cdf) check(close(S.tCdf(t, df), want, 1e-11), `tCdf(${t}, ${df}) = ${S.tCdf(t, df)}, erwartet ${want}`);
for (const [p, df, want] of FX.t_ppf) check(close(S.tPpf(p, df), want, 1e-9), `tPpf(${p}, ${df}) = ${S.tPpf(p, df)}, erwartet ${want}`);
for (const [n, k, p0, alt, alpha, want] of FX.binomial) {
  const got = S.binomialTest(n, k, p0, alt, alpha);
  check(deepClose(got, want, 1e-9), `binomialTest(${n}, ${k}, ${p0}, ${alt}, ${alpha}) = ${show(got)}, erwartet ${show(want)}`);
}
for (const [d, mu0, alt, alpha, want] of FX.one_t) {
  const got = S.oneSampleT(d, mu0, alt, alpha);
  check(deepClose(got, want, 1e-9), `oneSampleT(${alt}) = ${show(got)}, erwartet ${show(want)}`);
}
for (const [a, b, eq, alt, alpha, want] of FX.two_t) {
  const got = S.twoSampleT(a, b, eq, alt, alpha);
  check(deepClose(got, want, 1e-9), `twoSampleT(${eq}, ${alt}) = ${show(got)}, erwartet ${show(want)}`);
}
for (const [a, b, alt, alpha, want] of FX.paired_t) {
  const got = S.pairedT(a, b, alt, alpha);
  check(deepClose(got, want, 1e-9), `pairedT(${alt}) = ${show(got)}, erwartet ${show(want)}`);
}
// Bewusste Verbesserungen gegenüber Pythons csv.Sniffer, der hier danebenliegt:
// deutsches Dezimalkomma ohne Kopfzeile und Tab-Dateien mit kürzerer letzter Zeile.
const BETTER_THAN_PYTHON = {
  '1;2,5;3\n4;5,5;6\n': { headers: ['Spalte 1', 'Spalte 2', 'Spalte 3'], rows: [['1', '2,5', '3'], ['4', '5,5', '6']], info: { delimiter: ';', header: false } },
  'a\tb\tc\n1\t2\t3\n4\t5\n': { headers: ['a', 'b', 'c'], rows: [['1', '2', '3'], ['4', '5', '']], info: { delimiter: '\t', header: true } },
};
for (const [text, headers, rows, info] of FX.read_csv) {
  if (BETTER_THAN_PYTHON[text]) {
    check(deepClose(S.parseCSV(text), BETTER_THAN_PYTHON[text], 0), `parseCSV(${show(text)}) (Verbesserung)`);
    continue;
  }
  const got = S.parseCSV(text);
  check(deepClose(got, { headers, rows, info }, 0), `parseCSV(${show(text)}) = ${show(got)}, erwartet ${show({ headers, rows, info })}`);
}
for (const [spec, want] of FX.codegen) {
  const got = S.generateCode(Object.assign({ nit: true }, spec));
  if (got !== want) {
    const a = got.split('\n'), b = want.split('\n');
    const i = a.findIndex((l, j) => l !== b[j]);
    check(false, `generateCode(${spec.chart_type}, cat=${spec.cat_col}, val=${spec.value_col}) Zeile ${i + 1}:\n    js: ${a[i]}\n    py: ${b[i]}`);
  } else check(true);
}

// Ohne NIT_Code: allgemeine Hinweise statt NIT-Menü
const plain = S.generateCode(Object.assign({}, FX.codegen[0][0], { nit: false }));
check(plain.includes('erzeugt mit StatPlot') && plain.includes('pip install matplotlib') && !plain.includes('NIT_Code'),
  'generateCode ohne nit erwähnt NIT_Code nicht');

// Fehlerfälle der Tests
const throws = f => { try { f(); return false; } catch (e) { return e instanceof S.TestError; } };
check(throws(() => S.binomialTest(10, 11, 0.5)), 'binomialTest k > n wirft');
check(throws(() => S.oneSampleT([1], 0)), 'oneSampleT n < 2 wirft');
check(throws(() => S.oneSampleT([2, 2, 2], 0)), 'oneSampleT s = 0 wirft');
check(throws(() => S.pairedT([1, 2], [1])), 'pairedT ungleich lang wirft');

console.log(`${pass} bestanden, ${fail} fehlgeschlagen`);
process.exit(fail ? 1 : 0);
