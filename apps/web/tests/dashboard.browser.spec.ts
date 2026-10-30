import { expect, test } from "@playwright/test";

test("real Problem Inbox renders a PostgreSQL-backed seeded ticket and detail navigation",async ({page})=>{
  await page.goto("/");
  await expect(page.getByRole("heading",{name:"Обзор проблем"})).toBeVisible();
  const first=page.getByRole("link",{name:/PRB-000001/});
  await expect(first).toBeVisible();
  await page.getByRole("searchbox",{name:"Поиск по реестру"}).fill("not-existing-problem-zz");
  await expect(page.getByText("По вашему запросу ничего не найдено")).toBeVisible();
  await page.getByRole("searchbox",{name:"Поиск по реестру"}).fill("PRB-000001");
  await expect(first).toBeVisible();
  await first.click();
  await expect(page).toHaveURL(/\/problems\/PRB-000001$/);
  await expect(page.getByRole("heading",{name:"PRB-000001"})).toBeVisible();
  await expect(page.getByText(/RU-401/)).toBeVisible();
});

test("audit navigation displays the actual ticket registered event",async ({page})=>{
  await page.goto("/");
  await page.getByRole("link",{name:/Аудит/}).click();
  await expect(page).toHaveURL(/\/audit$/);
  await expect(page.getByRole("heading",{name:"Журнал изменений"})).toBeVisible();
  await expect(page.getByText("ticket_registered")).toBeVisible();
});

test("browser does not receive the FastAPI service token",async ({page})=>{
  const token=process.env.PRODUCTPULSE_INTERNAL_TOKEN;
  if(!token) throw new Error("browser smoke requires PRODUCTPULSE_INTERNAL_TOKEN");
  await page.goto("/");
  const text=await page.content();
  expect(text).not.toContain(token);
  const scripts=await page.locator("script").allTextContents();
  for(const script of scripts) expect(script).not.toContain(token);
});
