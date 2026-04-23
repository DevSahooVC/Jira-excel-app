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

/** Generic horizontal-friendly bar chart — works for SP or defect counts. */
export default function ReportChart({ data, xKey, yKey, color = '#2e5aac', unit }) {
  if (!data || data.length === 0) {
    return <div className="empty-state">No data to chart.</div>
  }
  return (
    <ResponsiveContainer width="100%" height={Math.max(220, data.length * 40)}>
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" allowDecimals={false} />
        <YAxis type="category" dataKey={xKey} width={120} />
        <Tooltip
          formatter={(value) => [`${value} ${unit || ''}`.trim(), undefined]}
          cursor={{ fill: 'rgba(46, 90, 172, 0.08)' }}
        />
        <Bar dataKey={yKey} fill={color} radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
