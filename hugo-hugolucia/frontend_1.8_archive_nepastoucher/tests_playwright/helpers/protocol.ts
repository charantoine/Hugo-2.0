import type { Page, Response } from '@playwright/test'
import { expect } from '@playwright/test'
import { apiPath, type ApiCallRecord } from './demo-env'

export function trackApi(page: Page) {
  const calls: ApiCallRecord[] = []

  const handler = async (response: Response) => {
    const url = response.url()
    if (!url.includes('/api/') && !url.includes(':8000/')) return
    calls.push({
      method: response.request().method(),
      url,
      status: response.status(),
      path: apiPath(url),
    })
  }

  page.on('response', handler)

  return {
    calls,
    clear: () => {
      calls.length = 0
    },
    find: (pathFragment: string, method?: string) =>
      calls.filter(
        (c) => c.path.includes(pathFragment) && (!method || c.method === method),
      ),
    waitFor: async (pathFragment: string, method?: string, timeout = 15_000) => {
      const start = Date.now()
      while (Date.now() - start < timeout) {
        const hit = calls.find(
          (c) => c.path.includes(pathFragment) && (!method || c.method === method),
        )
        if (hit) return hit
        await page.waitForTimeout(200)
      }
      throw new Error(`API call not captured: ${method || '*'} ${pathFragment}`)
    },
  }
}

export async function expectOrgBanner(page: Page, orgName: string) {
  await expect(page.locator('main').getByText(/Organisation active\s*:/)).toBeVisible()
  await expect(page.locator('main').getByText(orgName, { exact: false })).toBeVisible()
}

export async function collectConsoleErrors(page: Page) {
  const errors: string[] = []
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text())
  })
  return errors
}

export type LabelWireResult = {
  label: string
  ok: boolean
  layer: 'visible' | 'network' | 'metier'
  detail?: string
}

export function recordLabelCheck(
  results: LabelWireResult[],
  label: string,
  ok: boolean,
  layer: LabelWireResult['layer'],
  detail?: string,
) {
  results.push({ label, ok, layer, detail })
}
