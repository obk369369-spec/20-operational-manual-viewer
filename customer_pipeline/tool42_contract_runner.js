"use strict";

const path = require("path");
let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", chunk => raw += chunk);
process.stdin.on("end", () => {
  let packet;
  try {
    packet = JSON.parse(raw);
  } catch (_) {
    process.stdout.write(JSON.stringify({decision: "HOLD", reason: "INVALID_INPUT", send_allowed: false}));
    return;
  }
  const receipt = packet.rule_gate_receipt;
  if (!receipt || receipt.decision !== "ALLOW" || receipt.task_id !== "TOOL042" ||
      !receipt.version || !packet.rule_context ||
      receipt.version !== packet.rule_context.version ||
      packet.rule_context.source_records_verified !== true) {
    process.stdout.write(JSON.stringify({decision: "HOLD", reason: "RULE_GATE_NOT_VERIFIED", send_allowed: false}));
    return;
  }
  const tool42Root = path.resolve(process.argv[2]);
  const { branchCustomer } = require(path.join(tool42Root, "scripts", "_customer_branch_internal.js"));
  process.stdout.write(JSON.stringify(branchCustomer(packet.state, packet.candidates)));
});
