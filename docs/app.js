"use strict";

/* Pure client-side implementation of the standard nine-item HAS-BLED sum.
 * There are no requests, trackers, or saved patient data.
 */
(function (root) {
  const FACTORS = [
    ["hypertension", "Uncontrolled hypertension", "Systolic BP >160 mmHg", true],
    ["renal", "Abnormal renal function", "Dialysis, transplant, or creatinine >200 µmol/L", true],
    ["liver", "Abnormal liver function", "Cirrhosis or bilirubin >2× ULN with enzymes >3× ULN", true],
    ["stroke", "History of stroke", "Prior stroke; assess TIA history clinically", false],
    ["bleeding", "Bleeding history or predisposition", "Prior major bleeding or predisposition", false],
    ["labile_inr", "Labile INR", "Unstable INR or time in therapeutic range <60% (VKA only)", true],
    ["elderly", "Age over 65 years", "Age >65 years", false],
    ["drugs", "Antiplatelet or NSAID use", "Concomitant drugs increasing bleeding risk", true],
    ["alcohol", "Alcohol excess", "At least 8 alcohol units per week", true]
  ];
  const HISTORICAL_RATES = [1.13, 1.02, 1.88, 3.74, 8.70, 12.50, null, null, null, null];

  function calculate(flags) {
    if (flags === null || typeof flags !== "object") {
      throw new TypeError("Risk factors must be an object");
    }
    const present = [];
    const modifiable = [];
    const non_modifiable = [];
    for (const [key, title, , isModifiable] of FACTORS) {
      const active = flags[key] === undefined ? false : flags[key];
      if (typeof active !== "boolean") {
        throw new TypeError(key + " must be a boolean");
      }
      if (active) {
        present.push(title);
        (isModifiable ? modifiable : non_modifiable).push(title);
      }
    }
    const score = present.length;
    return {
      score,
      risk_level: score <= 1 ? "Low" : score === 2 ? "Moderate" : "High",
      annual_bleeding_risk: HISTORICAL_RATES[score],
      factors_present: present,
      modifiable,
      non_modifiable
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { FACTORS, HISTORICAL_RATES, calculate };
  }
  if (!root.document) return;

  const container = root.document.getElementById("factors");
  const form = root.document.getElementById("calculator");
  const scoreBox = root.document.getElementById("score");
  const levelBox = root.document.getElementById("level");
  const rateBox = root.document.getElementById("rate");
  const presentBox = root.document.getElementById("selected");
  const modifiableBox = root.document.getElementById("modifiable");
  if (!container || !form || !scoreBox || !levelBox || !rateBox || !presentBox ||
      !modifiableBox) return;

  for (const [key, title, description] of FACTORS) {
    const label = root.document.createElement("label");
    label.className = "factor";
    const checkbox = root.document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.name = key;
    checkbox.value = "yes";
    const content = root.document.createElement("span");
    const heading = root.document.createElement("strong");
    heading.textContent = title;
    const desc = root.document.createElement("small");
    desc.textContent = description;
    content.append(heading, desc);
    label.append(checkbox, content);
    container.append(label);
  }

  function render() {
    const flags = {};
    for (const [key] of FACTORS) {
      flags[key] = form.elements.namedItem(key).checked;
    }
    const r = calculate(flags);
    scoreBox.textContent = String(r.score) + " / 9";
    levelBox.textContent = r.risk_level + " bleeding-risk category";
    rateBox.textContent = r.annual_bleeding_risk === null
      ? "Not estimable (insufficient observations for scores 6–9)"
      : r.annual_bleeding_risk.toFixed(2) + " major bleeds per 100 patient-years";
    presentBox.textContent = r.factors_present.length
      ? r.factors_present.join("; ") : "None selected";
    modifiableBox.textContent = r.modifiable.length
      ? r.modifiable.join("; ") : "None selected";
  }

  form.addEventListener("change", render);
  form.addEventListener("reset", () => root.requestAnimationFrame(render));
  render();
})(typeof window !== "undefined" ? window : globalThis);
