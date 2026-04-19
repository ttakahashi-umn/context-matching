import { expect, test } from "@playwright/test";

test.describe("talent-interview-profile-poc UI", () => {
  test("人材作成から面談・抽出・プロフィール反映まで通る", async ({ page }) => {
    const suffix = `${Date.now()}`;
    const family = `E2E${suffix}`;
    const display = `${family} 太郎`;

    await page.goto("/talents");
    await page.getByRole("button", { name: "人材を登録" }).click();

    const dialog = page.getByRole("dialog", { name: "人材を登録" });
    await expect(dialog).toBeVisible();

    await dialog.getByPlaceholder("山田").fill(family);
    await dialog.getByPlaceholder("太郎").fill("太郎");
    await dialog.getByPlaceholder("やまだ").fill("いーつーいー");
    await dialog.getByPlaceholder("たろう").fill("たろう");
    await dialog.getByRole("button", { name: "登録" }).click();

    // スライドオーバーは閉じても DOM に残るため、一覧に行が出ることで登録成功を待つ
    const talentLink = page.getByRole("link", { name: display });
    await expect(talentLink).toBeVisible({ timeout: 15_000 });
    await talentLink.click();

    await expect(page.getByRole("heading", { level: 2, name: display })).toBeVisible();
    await expect(page.getByText("まだ反映されていません")).toBeVisible();

    await page.getByRole("button", { name: "面談を追加" }).click();
    await expect(page.getByRole("list", { name: "登録済み面談セッション（新しい順）" })).toBeVisible();

    const templateSelect = page.getByRole("combobox", { name: "テンプレ" });
    await expect(templateSelect).toBeVisible();
    await expect.poll(async () => templateSelect.locator("option").count()).toBeGreaterThan(0);

    await page.getByRole("button", { name: "抽出実行" }).click();
    await expect(page.getByRole("status")).toBeVisible();
    await expect(page.getByRole("status")).toBeHidden({ timeout: 60_000 });

    await expect(page.getByText(/直近の抽出:/)).toContainText("completed", { timeout: 60_000 });

    await page.getByRole("button", { name: "プロフィール反映" }).click();
    await expect(page.getByText("まだ反映されていません")).toBeHidden({ timeout: 30_000 });
    await expect(page.getByText("まだ反映履歴がありません。")).toHaveCount(0);
  });
});
