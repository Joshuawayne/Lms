/**
 * Captures real, verified multi-viewport screenshots of the Jjenga Code public website.
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from '@playwright/test'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const OUT_DIR = path.join(ROOT, 'docs', 'evidence', 'screenshots')

if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true })
}

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 375, height: 812 },
]

const PAGES = [
  { name: 'homepage', path: '/' },
  { name: 'catalogue', path: '/programs' },
  { name: 'program-detail', path: '/programs/coding-robotics-camp-nov-2026' },
  { name: 'application-form', path: '/programs/coding-robotics-camp-nov-2026/apply' },
]

async function run() {
  console.log('Launching browser (msedge)...')
  const browser = await chromium.launch({ channel: 'msedge' })

  for (const vp of VIEWPORTS) {
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: 2,
    })
    const page = await context.newPage()

    for (const p of PAGES) {
      const url = `http://127.0.0.1:3000${p.path}`
      console.log(`Capturing ${p.name} [${vp.name}] at ${url}...`)
      await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 })
      await page.waitForTimeout(500) // let animations settle

      const outPath = path.join(OUT_DIR, `${p.name}-${vp.name}.png`)
      await page.screenshot({ path: outPath, fullPage: true })
      console.log(`Saved ${outPath}`)
    }

    // Special state 1: Interactive building demo on homepage
    if (vp.name === 'desktop') {
      console.log('Capturing interactive sequence builder in execution state...')
      await page.goto('http://127.0.0.1:3000/#interactive-demo', { waitUntil: 'networkidle' })
      const runBtn = page.getByRole('button', { name: /Run Sequence/i })
      if (await runBtn.isVisible()) {
        await runBtn.click()
        await page.waitForTimeout(700) // mid-sequence step
        const outPath = path.join(OUT_DIR, 'interactive-demo-executing-desktop.png')
        await page.screenshot({ path: outPath })
        console.log(`Saved ${outPath}`)
      }
    }

    // Special state 2: Application form accessible error validation state
    if (vp.name === 'desktop') {
      console.log('Capturing accessible error summary on application page...')
      await page.goto('http://127.0.0.1:3000/programs/coding-robotics-camp-nov-2026/apply', { waitUntil: 'networkidle' })
      const submitBtn = page.getByRole('button', { name: /Submit application/i })
      if (await submitBtn.isVisible()) {
        await submitBtn.click()
        await page.waitForTimeout(400)
        const outPath = path.join(OUT_DIR, 'application-validation-errors-desktop.png')
        await page.screenshot({ path: outPath })
        console.log(`Saved ${outPath}`)
      }
    }

    await context.close()
  }

  await browser.close()
  console.log('All screenshots captured successfully.')
}

run().catch((err) => {
  console.error('Screenshot capture failed:', err)
  process.exit(1)
})
