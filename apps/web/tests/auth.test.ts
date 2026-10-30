import { test } from "node:test";
import assert from "node:assert/strict";
import { verifyBasicAuthorization, readAuthConfig } from "../lib/auth";

const config = { username: "reviewer", password: "very-secure-demo-password" };
const encoded = (value: string) => "Basic " + Buffer.from(value).toString("base64");

test("correct credentials accepted, incorrect ones fail", () => {
  assert.equal(verifyBasicAuthorization(encoded("reviewer:very-secure-demo-password"), config), true);
  assert.equal(verifyBasicAuthorization(encoded("reviewer:wrong"), config), false);
  assert.equal(verifyBasicAuthorization(encoded("wrong:very-secure-demo-password"), config), false);
});

test("missing, invalid and malicious Basic credentials fail closed", () => {
  for (const value of [
    null, undefined, "", "Bearer abc", "Basic !!!",
    "Basic "+Buffer.from("reviewer").toString("base64"),
    "Basic "+Buffer.from("reviewer:").toString("base64"),
    "Basic "+Buffer.from("reviewer:very-secure-demo-password\n").toString("base64"),
  ]) {
    assert.equal(verifyBasicAuthorization(value, config), false);
  }
});

test("authorization supports password with colons and unicode safely", () => {
  const c = {username:"админ", password:"abc:def:ОченьСложныйПароль"};
  assert.equal(verifyBasicAuthorization(encoded("админ:abc:def:ОченьСложныйПароль"), c), true);
});

test("auth configuration demands explicit nonempty high entropy credentials", () => {
  assert.throws(() => readAuthConfig({}), /DASHBOARD_/);
  assert.throws(() => readAuthConfig({DASHBOARD_USERNAME:"x", DASHBOARD_PASSWORD:"123"}), /DASHBOARD_PASSWORD/);
  assert.deepEqual(readAuthConfig({
    DASHBOARD_USERNAME:"admin", DASHBOARD_PASSWORD:"long-password-for-local-demo",
  }), {username:"admin", password:"long-password-for-local-demo"});
});
