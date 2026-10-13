"use strict";
const assert = require("node:assert/strict");
const { FACTORS, HISTORICAL_RATES, calculate } = require("./app.js");
assert.equal(FACTORS.length, 9);
assert.equal(calculate({}).score, 0);
assert.equal(calculate({}).annual_bleeding_risk, 1.13);
assert.throws(() => calculate({ renal: 1 }), TypeError);
assert.throws(() => calculate(null), TypeError);
for (let mask = 0; mask < (1 << 9); mask++) {
  const flags = {};
  let expected = 0;
  for (let i = 0; i < FACTORS.length; i++) {
    flags[FACTORS[i][0]] = Boolean(mask & (1 << i));
    if (flags[FACTORS[i][0]]) expected++;
  }
  const result = calculate(flags);
  assert.equal(result.score, expected, "mask=" + mask);
  assert.equal(result.factors_present.length, expected);
  assert.equal(result.modifiable.length + result.non_modifiable.length, expected);
  assert.equal(result.annual_bleeding_risk, HISTORICAL_RATES[expected]);
  assert.equal(result.risk_level, expected <= 1 ? "Low" : expected === 2 ? "Moderate" : "High");
}
console.log("512 browser scoring combinations passed");
