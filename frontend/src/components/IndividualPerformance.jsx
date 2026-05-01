import React, { useMemo, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const COLORS = [
  '#2e5aac', '#c23a3a', '#2ea87e', '#e08c2f', '#7c3aed',
  '#db2777', '#0891b2', '#65a30d', '#9f1239', '#b45309',
]

export default function IndividualPerformance({ report }) {
  const sprints = report.sprints || []

  // Collect all unique assignees across all sprints (sorted)
  const allAssignees = useMemo(() => {
    const set = new Set()
    for (const sprint of sprints) {
      const sprintData = report.by_sprint?.[sprint]
      for (const row of sprintData?.story_points_by_assignee || []) {
        set.add(row.assignee)
      }
    }
    return [...set].sort()
  }, [report, sprints])

  const [selected, setSelected] = useState(() => new Set(allAssignees))

  // Pivot: [{ sprint: "Sprint 42", Alice: 10, Bob: 5 }, ...]
  const chartData = useMemo(() => {
    return sprints.map((sprint) => {
      const sprintRows = report.by_sprint?.[sprint]?.story_points_by_assignee || []
      const row = { sprint }
      for (const assignee of allAssignees) {
        const found = sprintRows.find((r) => r.assignee === assignee)
        row[assignee] = found ? found.story_points : 0
      }
      return row
    })
  }, [report, sprints, allAssignees])

  const selectedList = allAssignees.filter((a) => selected.has(a))
  const allChecked = selected.size === allAssignees.length
  const someChecked = selected.size > 0 && selected.size < allAssignees.length

  function toggleAll(checked) {
    setSelected(checked ? new Set(allAssignees) : new Set())
  }

  function toggleOne(name, checked) {
    setSelected((prev) => {
      const next = new Set(prev)
      if (checked) next.add(name)
      else next.delete(name)
      return next
    })
  }

  function colorFor(name) {
    return COLORS[allAssignees.indexOf(name) % COLORS.length]
  }

  if (!sprints.length) {
    return (
      <div className="empty-state" style={{ margin: '32px 0' }}>
        No sprint data found in this file. Add a Sprint column to use this view.
      </div>
    )
  }

  return (
    <div>
      <section className="report">
        <h2>Team members</h2>
        <p className="caption">Select the members you want to compare across sprints.</p>
        <div className="member-checkboxes">
          <label className="member-check member-check--all">
            <input
              type="checkbox"
              checked={allChecked}
              ref={(el) => { if (el) el.indeterminate = someChecked }}
              onChange={(e) => toggleAll(e.target.checked)}
            />
            <span>All members</span>
          </label>
          {allAssignees.map((name) => (
            <label key={name} className="member-check">
              <input
                type="checkbox"
                checked={selected.has(name)}
                onChange={(e) => toggleOne(name, e.target.checked)}
              />
              <span className="member-dot" style={{ background: colorFor(name) }} />
              <span>{name}</span>
            </label>
          ))}
        </div>
      </section>

      {selectedList.length === 0 ? (
        <div className="empty-state">Select at least one team member to see their performance.</div>
      ) : (
        <section className="report">
          <h2>Story points delivered per sprint</h2>
          <p className="caption">
            Story points on Done / Closed / Resolved issues per sprint, per team member.
          </p>

          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData} margin={{ top: 8, right: 24, bottom: 8, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="sprint" tick={{ fontSize: 13 }} />
              <YAxis allowDecimals={false} />
              <Tooltip formatter={(value, name) => [`${value} SP`, name]} />
              <Legend />
              {selectedList.map((name) => (
                <Line
                  key={name}
                  type="monotone"
                  dataKey={name}
                  stroke={colorFor(name)}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>

          <table style={{ marginTop: 28 }}>
            <thead>
              <tr>
                <th>Member</th>
                {sprints.map((s) => (
                  <th key={s} className="num">{s}</th>
                ))}
                <th className="num">Total</th>
              </tr>
            </thead>
            <tbody>
              {selectedList.map((name) => {
                const sprintSPs = sprints.map((s) => {
                  const found = report.by_sprint?.[s]?.story_points_by_assignee?.find(
                    (r) => r.assignee === name
                  )
                  return found ? found.story_points : null
                })
                const total = sprintSPs.reduce((acc, v) => acc + (v ?? 0), 0)
                return (
                  <tr key={name}>
                    <td>
                      <span className="member-dot" style={{ background: colorFor(name) }} />
                      {name}
                    </td>
                    {sprintSPs.map((sp, j) => (
                      <td key={j} className="num">
                        {sp != null ? sp : <span className="muted">—</span>}
                      </td>
                    ))}
                    <td className="num">
                      <strong>{Math.round(total * 100) / 100}</strong>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </section>
      )}
    </div>
  )
}
