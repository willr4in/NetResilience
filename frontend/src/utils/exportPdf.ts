import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import type { GraphAnalysisResponse, CascadeResponse } from '../types/metrics'

interface ExportOptions {
  scenarioName: string
  description?: string | null
  district: string
  analysis: GraphAnalysisResponse
  cascade: CascadeResponse | null
  removedCount: number
  addedCount: number
}

const REPORT_WIDTH_PX = 794

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`
}

function buildReportHtml(opts: ExportOptions): string {
  const { scenarioName, description, analysis, cascade, removedCount, addedCount } = opts
  const r = analysis.resilience
  const date = new Date().toLocaleString('ru-RU')

  const topCritical = analysis.metrics.critical_nodes
    .slice(0, 20)
    .map((id, i) => {
      const bc = analysis.metrics.betweenness[id] ?? 0
      return `<tr>
        <td style="padding:4px 8px;border-bottom:1px solid #f1f5f9;width:32px;color:#94a3b8">${i + 1}</td>
        <td style="padding:4px 8px;border-bottom:1px solid #f1f5f9;font-family:monospace;font-size:12px">${escapeHtml(id)}</td>
        <td style="padding:4px 8px;border-bottom:1px solid #f1f5f9;text-align:right;color:#475569">${bc.toFixed(4)}</td>
      </tr>`
    })
    .join('')

  const cascadeRows = cascade && cascade.steps.length
    ? cascade.steps
        .map(
          (s) => `<tr>
        <td style="padding:4px 8px;border-bottom:1px solid #f1f5f9;width:32px;color:#94a3b8">${s.step}</td>
        <td style="padding:4px 8px;border-bottom:1px solid #f1f5f9;font-size:12px">${escapeHtml(s.removed_node_label)}</td>
        <td style="padding:4px 8px;border-bottom:1px solid #f1f5f9;text-align:right">${pct(s.resilience_score)}</td>
        <td style="padding:4px 8px;border-bottom:1px solid #f1f5f9;text-align:right;color:${s.connected ? '#16a34a' : '#dc2626'}">${s.connected ? 'связен' : 'разорван'}</td>
      </tr>`
        )
        .join('')
    : ''

  const comparisonBlock = r.comparison
    ? `<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:8px;padding:10px 12px;background:#f8fafc;border-radius:8px">
        <div><div style="color:#64748b;font-size:11px">До изменений</div><div style="font-weight:600;font-size:14px">${pct(r.comparison.resilience_score_before)}</div></div>
        <div><div style="color:#64748b;font-size:11px">После изменений</div><div style="font-weight:600;font-size:14px">${pct(r.comparison.resilience_score_after)}</div></div>
        <div><div style="color:#64748b;font-size:11px">Дельта</div><div style="font-weight:600;font-size:14px;color:${r.comparison.resilience_delta >= 0 ? '#16a34a' : '#dc2626'}">${r.comparison.resilience_delta >= 0 ? '+' : ''}${pct(r.comparison.resilience_delta)}</div></div>
      </div>`
    : ''

  return `
    <div style="
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
      width: ${REPORT_WIDTH_PX}px;
      padding: 32px;
      background: #ffffff;
      color: #0f172a;
      box-sizing: border-box;
    ">
      <div style="border-bottom:2px solid #0f172a;padding-bottom:12px;margin-bottom:18px">
        <div style="font-size:22px;font-weight:700">NetResilience — отчёт по сценарию</div>
        <div style="display:flex;justify-content:space-between;color:#64748b;font-size:13px;margin-top:6px">
          <span>Сценарий: <b style="color:#0f172a">${escapeHtml(scenarioName)}</b></span>
          <span>${escapeHtml(date)}</span>
        </div>
        ${description ? `<div style="color:#475569;font-size:13px;margin-top:8px;line-height:1.5">${escapeHtml(description)}</div>` : ''}
      </div>

      <div style="margin-bottom:18px">
        <div style="font-size:15px;font-weight:600;margin-bottom:8px;color:#0f172a">Метрики устойчивости</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <div style="padding:10px 12px;background:#f8fafc;border-radius:8px">
            <div style="color:#64748b;font-size:11px">Resilience Score</div>
            <div style="font-weight:700;font-size:20px;color:#1d4ed8">${pct(r.resilience_score)}</div>
          </div>
          <div style="padding:10px 12px;background:#f8fafc;border-radius:8px">
            <div style="color:#64748b;font-size:11px">Граф связен</div>
            <div style="font-weight:600;font-size:14px;color:${r.connected ? '#16a34a' : '#dc2626'}">${r.connected ? 'Да' : 'Нет'}</div>
          </div>
          <div style="padding:10px 12px;background:#f8fafc;border-radius:8px">
            <div style="color:#64748b;font-size:11px">Крупнейшая компонента</div>
            <div style="font-weight:600;font-size:14px">${pct(r.largest_component_ratio)}</div>
          </div>
          <div style="padding:10px 12px;background:#f8fafc;border-radius:8px">
            <div style="color:#64748b;font-size:11px">Концентрация нагрузки</div>
            <div style="font-weight:600;font-size:14px">${pct(r.betweenness_concentration)}</div>
          </div>
          <div style="padding:10px 12px;background:#f8fafc;border-radius:8px">
            <div style="color:#64748b;font-size:11px">Средняя длина пути</div>
            <div style="font-weight:600;font-size:14px">${r.average_shortest_path !== null ? r.average_shortest_path.toFixed(2) : '—'}</div>
          </div>
          <div style="padding:10px 12px;background:#f8fafc;border-radius:8px">
            <div style="color:#64748b;font-size:11px">Изменения сценария</div>
            <div style="font-weight:600;font-size:14px">удалено: ${removedCount} · добавлено: ${addedCount}</div>
          </div>
        </div>
        ${comparisonBlock}
      </div>

      ${topCritical ? `
        <div style="margin-bottom:18px">
          <div style="font-size:15px;font-weight:600;margin-bottom:8px;color:#0f172a">Топ-20 критических узлов</div>
          <table style="width:100%;border-collapse:collapse;font-size:12px">
            <thead>
              <tr style="background:#f1f5f9;color:#475569">
                <th style="padding:6px 8px;text-align:left">#</th>
                <th style="padding:6px 8px;text-align:left">ID узла</th>
                <th style="padding:6px 8px;text-align:right">Betweenness</th>
              </tr>
            </thead>
            <tbody>${topCritical}</tbody>
          </table>
        </div>
      ` : ''}

      ${cascade && cascade.steps.length ? `
        <div style="margin-bottom:8px">
          <div style="font-size:15px;font-weight:600;margin-bottom:8px;color:#0f172a">Каскадный отказ</div>
          <div style="display:flex;justify-content:space-between;font-size:12px;color:#64748b;margin-bottom:6px">
            <span>Начальный score: <b style="color:#0f172a">${pct(cascade.initial_resilience_score)}</b></span>
            <span>Шагов: <b style="color:#0f172a">${cascade.total_steps}</b></span>
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:12px">
            <thead>
              <tr style="background:#f1f5f9;color:#475569">
                <th style="padding:6px 8px;text-align:left">Шаг</th>
                <th style="padding:6px 8px;text-align:left">Удалённый узел</th>
                <th style="padding:6px 8px;text-align:right">Score</th>
                <th style="padding:6px 8px;text-align:right">Связность</th>
              </tr>
            </thead>
            <tbody>${cascadeRows}</tbody>
          </table>
        </div>
      ` : ''}
    </div>
  `
}

async function renderReportToCanvas(html: string): Promise<HTMLCanvasElement> {
  const wrapper = document.createElement('div')
  wrapper.style.cssText = `
    position: fixed;
    left: -10000px;
    top: 0;
    width: ${REPORT_WIDTH_PX}px;
    z-index: -1;
    background: #ffffff;
  `
  wrapper.innerHTML = html
  document.body.appendChild(wrapper)
  try {
    return await html2canvas(wrapper, {
      backgroundColor: '#ffffff',
      logging: false,
      scale: 2,
      useCORS: true,
    })
  } finally {
    document.body.removeChild(wrapper)
  }
}

function canvasToPdf(canvas: HTMLCanvasElement, pdf: jsPDF): void {
  const pageW = pdf.internal.pageSize.getWidth()
  const pageH = pdf.internal.pageSize.getHeight()
  const ratio = pageW / canvas.width
  const totalHeightMm = canvas.height * ratio

  if (totalHeightMm <= pageH) {
    pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 0, 0, pageW, totalHeightMm)
    return
  }

  const slicePxPerPage = pageH / ratio
  let posY = 0
  let first = true
  while (posY < canvas.height) {
    const sliceHeight = Math.min(slicePxPerPage, canvas.height - posY)
    const slice = document.createElement('canvas')
    slice.width = canvas.width
    slice.height = sliceHeight
    const ctx = slice.getContext('2d')
    if (!ctx) return
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, slice.width, slice.height)
    ctx.drawImage(canvas, 0, -posY)
    if (!first) pdf.addPage()
    pdf.addImage(slice.toDataURL('image/png'), 'PNG', 0, 0, pageW, sliceHeight * ratio)
    first = false
    posY += slicePxPerPage
  }
}

export async function exportScenarioPdf(opts: ExportOptions): Promise<void> {
  const html = buildReportHtml(opts)
  const canvas = await renderReportToCanvas(html)
  const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' })
  canvasToPdf(canvas, pdf)
  pdf.save('Отчёт.pdf')
}
