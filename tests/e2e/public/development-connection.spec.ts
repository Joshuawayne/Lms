import { expect, test } from '@playwright/test'

test('the Nuxt page can reach FastAPI through the browser', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Check backend' }).click()
  await expect(page.getByText('Connected to jjenga-lms-api.')).toBeVisible()
})
