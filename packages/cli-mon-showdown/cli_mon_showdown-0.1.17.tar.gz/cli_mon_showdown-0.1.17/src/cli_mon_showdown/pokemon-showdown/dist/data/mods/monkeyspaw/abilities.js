"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var abilities_exports = {};
__export(abilities_exports, {
  Abilities: () => Abilities
});
module.exports = __toCommonJS(abilities_exports);
const Abilities = {
  slowstart: {
    inherit: true,
    condition: {
      duration: 5,
      durationCallback(target, source, effect) {
        if (target.m.revivedByMonkeysPaw) return 0;
        return 5;
      },
      onResidualOrder: 28,
      onResidualSubOrder: 2,
      onStart(target, source, effect) {
        if (target.m.revivedByMonkeysPaw) this.effectState.duration = 0;
        this.add("-start", target, "ability: Slow Start");
      },
      onModifyAtkPriority: 5,
      onModifyAtk(atk, pokemon) {
        return this.chainModify(0.5);
      },
      onModifySpe(spe, pokemon) {
        return this.chainModify(0.5);
      },
      onEnd(target) {
        this.add("-end", target, "Slow Start");
      }
    }
  }
};
//# sourceMappingURL=abilities.js.map
