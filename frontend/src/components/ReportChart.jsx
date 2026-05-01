import React from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const DARK_TICK  = '#888888'
const DARK_GRID  = '#2E2E2E'
const DARK_BG    = '#1A1A1A'
const DARK_LABEL = '#F0F0F0'

/** Generic horizontal-friendly bar chart — works for SP or defect counts. */
export default function ReportChart({ data, xKey, yKey, color = '#FFDD00', unit }) {
  if (!data || data.length === 0) {
    return <div className="empty-state">No data to chart.</div>
  }
  return (
    <ResponsiveContainer width="100%" height={Math.max(220, data.length * 44)}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={DARK_GRID} />
        <XAxis
          type="number"
          allowDecimals={false}
          tick={{ fill: DARK_TICK, fontSize: 12 }}
          axisLine={{ stroke: DARK_GRID }}
          tickLine={{ stroke: DARK_GRID }}
        />
        <YAxis
          type="category"
          dataKey={xKey}
          width={130}
          tick={{ fill: DARK_LABEL, fontSize: 13 }}
          axisLine={{ stroke: DARK_GRID }}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{
            background: '#222222',
            border: '1px solid #3A3A3A',
            borderRadius: 8,
            color: '#F0F0F0',
            fontSize: 13,
          }}
          itemStyle={{ color: '#F0F0F0' }}
          labelStyle={{ color: '#FFDD00', fontWeight: 600 }}
          formatter={(value) => [`${value} ${unit || ''}`.trim(), undefined]}
          cursor={{ fill: 'rgba(255, 221, 0, 0.06)' }}
        />
        <Bar dataKey={yKey} fill={color} radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
