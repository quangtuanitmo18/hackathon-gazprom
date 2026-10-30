import {expect,test,type Browser} from "@playwright/test";

test.skip(process.env.PRODUCTPULSE_AUTH_MODE!=="oidc",
  "Requires actual synthetic Keycloak+PostgreSQL CI environment");

async function login(browser:Browser,username:string,password:string){
  const context=await browser.newContext({ignoreHTTPSErrors:true});
  const page=await context.newPage();
  await page.goto("http://localhost:3000/insights");
  await expect(page.getByRole("heading",{name:"Вход эксперта"})).toBeVisible();
  await page.getByRole("button",{name:/Войти через Keycloak/}).click();
  await page.locator("#username").fill(username);
  await page.locator("#password").fill(password);
  await page.locator("#kc-login").click();
  await expect(page.getByRole("heading",{name:"Предложения продуктовой команде"}))
    .toBeVisible({timeout:30000});
  return {page,context};
}

test("real Keycloak: 2 reviewed tickets become one lead-only proposal then MOCK issue",async({browser})=>{
  const viewer=await login(browser,"reviewer-a","ci-reviewer-A-2026-only");
  await expect(viewer.page.getByRole("button",{name:/Предложение к проверке 1/})).toBeVisible();
  await expect(viewer.page.getByText("Не установлена",{exact:true})).toBeVisible();
  await expect(viewer.page.getByText("Не назначен",{exact:true})).toBeVisible();
  await expect(viewer.page.locator(".insight-evidence .review-ticket")).toHaveCount(2);
  await expect(viewer.page.getByText(/RU-A/).first()).toBeVisible();
  await expect(viewer.page.getByText(/RU-B/).first()).toBeVisible();
  await expect(viewer.page.getByRole("button",{name:"Опубликовать ТОЛЬКО в mock tracker"}))
    .toBeDisabled();
  await viewer.page.getByRole("textbox",{name:"Причина решения ведущего эксперта"})
    .fill("Attempt to approve as ordinary reviewer");
  await viewer.page.getByRole("button",{name:"Одобрить предложение (без публикации)"}).click();
  await expect(viewer.page.getByRole("alert")).toContainText("HTTP 401");
  const data=await viewer.page.evaluate(async()=>await(await fetch("/api/insights")).json());
  expect(data.proposals).toHaveLength(1);
  expect(data.proposals[0].approval_status).toBe("pending");
  expect(data.proposals[0].mock_issue_id).toBeNull();
  expect(data.proposals[0].root_cause_status).toBe("unknown");
  expect(data.proposals[0].owner_team_id).toBeNull();
  expect(JSON.stringify(data)).not.toContain(process.env.PRODUCTPULSE_INTERNAL_TOKEN!);
  await viewer.context.close();

  const lead=await login(browser,"review-lead","ci-review-lead-2026-only");
  const approve=lead.page.getByRole("button",{name:"Одобрить предложение (без публикации)"});
  const publish=lead.page.getByRole("button",{name:"Опубликовать ТОЛЬКО в mock tracker"});
  await expect(publish).toBeDisabled();
  await lead.page.getByRole("textbox",{name:"Причина решения ведущего эксперта"})
    .fill("Checked source-scoped evidence and verified exact Problem revision");
  await approve.click();
  await expect(lead.page.getByText(/одобрил точную ревизию/)).toBeVisible();
  await expect(approve).toBeDisabled();
  await expect(publish).toBeDisabled(); // explicit separate reason required after approval
  await lead.page.getByRole("textbox",{name:"Причина решения ведущего эксперта"})
    .fill("Second explicit action to create internal mock issue only");
  await expect(publish).toBeEnabled();
  await publish.click();
  await expect(lead.page.getByText(/Создан только внутренний MOCK issue/)).toBeVisible();
  await expect(lead.page.getByText(/MOCK-PRB-000001-R2/)).toBeVisible();
  await expect(publish).toBeDisabled();
  const after=await lead.page.evaluate(async()=>await(await fetch("/api/insights")).json());
  expect(after.proposals).toHaveLength(1);
  expect(after.proposals[0].approval_status).toBe("approved");
  expect(after.proposals[0].mock_issue_id).toBe("MOCK-PRB-000001-R2");
  const csrf=await lead.context.request.post("http://localhost:3000/api/insights",{
    headers:{"Origin":"https://evil.example.test","Content-Type":"application/json"},
    data:JSON.stringify({action:"approve",payload:{
      problem_id:"PRB-000001",expected_revision:2,
      evidence_digest:after.proposals[0].evidence_digest,
      reason:"evil",operation_key:"csrf",
    }}),
  });
  expect(csrf.status()).toBe(403);
  const publicSession=await lead.page.evaluate(async()=>await(await fetch("/api/auth/session")).json());
  expect(JSON.stringify(publicSession)).not.toContain("reviewerAccessToken");
  expect(JSON.stringify(publicSession)).not.toContain("access_token");
  await lead.context.close();
});
