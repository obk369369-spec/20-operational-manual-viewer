"use strict";

const path = require("path");
let raw = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", chunk => raw += chunk);
process.stdin.on("end", () => {
  const tool42Root = path.resolve(process.argv[2]);
  const { branchCustomer } = require(path.join(tool42Root, "scripts", "_customer_branch_internal.js"));
  const packet = JSON.parse(raw);
  process.stdout.write(JSON.stringify(branchCustomer(packet.state, packet.candidates)));
});
