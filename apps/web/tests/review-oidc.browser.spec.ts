import { expect, test, type Browser, type Page } from "@playwright/test";

test.skip(process.env.PRODUCTPULSE_AUTH_MODE!=="oidc","Runs only against actual Keycloak OIDC CI environment");

async function signInAs(browser:Browser, username:string, password:string){
  const context=await browser.newContext({ignoreHTTPSErrors:true});
  const page=await context.newPage();
  await page.goto("http://localhost:3000/review");
  await expect(page.getByRole("heading",{name:"Вход эксперта"})).toBeVisible();
  await page.getByRole("button",{name:/Войти через Keycloak/}).click();
  await expect(page.locator("#username")).toBeVisible();
  await page.locator("#username").fill(username);
  await page.locator("#password").fill(password);
  await page.locator("#kc-login").click();
  await expect(page.getByRole("heading",{name:"Независимая проверка инцидентов"})).toBeVisible({timeout:30000});
  return {context,page};
}
async function selectPair(page:Page) {
  await page.getByRole("combobox",{name:"Первое обращение"}).selectOption({label:"synthetic: RU-A"});
  await page.getByRole("combobox",{name:"Второе обращение"}).selectOption({label:"synthetic: RU-B"});
}

test("actual Keycloak: reviewer A + reviewer B + independent lead can approve but not merge",async({browser})=>{
  const one=await signInAs(browser,"reviewer-a","ci-reviewer-A-2026-only");
  await selectPair(one.page);
  await one.page.getByText("Одна техническая проблема",{exact:true}).click();
  await one.page.getByRole("textbox",{name:"Обоснование по фактам"}).fill("Same HTTP stack trace, regression version and reproduction steps");
  await one.page.getByRole("button",{name:"Отправить независимую оценку"}).click();
  await expect(one.page.getByText("Ожидается второй эксперт")).toBeVisible();
  // Public Auth.js session cannot leak OAuth access and refresh tokens.
  const session=await one.page.evaluate(async()=>await (await fetch("/api/auth/session")).json());
  expect(JSON.stringify(session)).not.toContain("reviewerAccessToken");
  expect(JSON.stringify(session)).not.toContain("access_token");
  expect(JSON.stringify(session)).not.toContain("refresh_token");
  await one.context.close();

  const two=await signInAs(browser,"reviewer-b","ci-reviewer-B-2026-only");
  await selectPair(two.page);
  await two.page.getByText("Одна техническая проблема",{exact:true}).click();
  await two.page.getByRole("textbox",{name:"Обоснование по фактам"}).fill("Independent reproduction of same error code and version");
  await two.page.getByRole("button",{name:"Отправить независимую оценку"}).click();
  await expect(two.page.getByText("Ожидает ведущего эксперта")).toBeVisible();
  await two.context.close();

  const lead=await signInAs(browser,"review-lead","ci-review-lead-2026-only");
  await selectPair(lead.page);
  await expect(lead.page.getByText("Ожидает ведущего эксперта")).toBeVisible();
  await lead.page.getByRole("textbox",{name:"Причина подтверждения"}).fill("Compared both independent reviews and source evidence");
  await lead.page.getByRole("button",{name:/Подтвердить связь/}).click();
  await expect(lead.page.getByText("Связь подтверждена ведущим экспертом")).toBeVisible();
  await expect(lead.page.getByText(/проблемы не объединены автоматически/)).toBeVisible();
  await lead.context.close();
});
