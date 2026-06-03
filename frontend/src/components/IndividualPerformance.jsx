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
  '#FFDD00', '#FF5555', '#33D17A', '#FF9F43', '#A29BFE',
  '#FD79A8', '#00CEC9', '#B8E994', '#E17055', '#74B9FF',
]

const DARK_TICK = '#888888'
const DARK_GRID = '#2E2E2E'

export default function IndividualPerformance({ report, includeBugs }) {
  const sprints = report.sprints || []

  // Pick the right sprint data source based on the bug filter
  const sprintSource = includeBugs ? report.by_sprint : report.by_sprint_ex_bugs

  // Collect all unique assignees across all sprints (sorted)
  const allAssignees = useMemo(() => {
    const set = new Set()
    for (const sprint of sprints) {
      for (const row of sprintSource?.[sprint]?.story_points_by_assignee || []) {
        set.add(row.assignee)
      }
    }
    return [...set].sort()
  }, [sprintSource, sprints])

  const [selected, setSelected] = useState(() => new Set(allAssignees))

  // Re-sync selection when allAssignees changes (e.g. bug filter changes assignee list)
  const prevAssigneesRef = React.useRef(allAssignees)
  if (prevAssigneesRef.current !== allAssignees) {
    prevAssigneesRef.current = allAssignees
    // Add any newly-appearing assignees; keep existing selections
  }

  // Pivot: [{ sprint: "Sprint 42", Alice: 10, Bob: 5, "Alice__r3": 7.3 }, ...]
  const chartData = useMemo(() => {
    const rows = sprints.map((sprint) => {
      const sprintRows = sprintSource?.[sprint]?.story_points_by_assignee || []
      const row = { sprint }
      for (const assignee of allAssignees) {
        const found = sprintRows.find((r) => r.assignee === assignee)
        row[assignee] = found ? found.story_points : 0
      }
      return row
    })
    // Rolling 3-sprint average per assignee
    rows.forEach((row, i) => {
      for (const assignee of allAssignees) {
        const window = rows.slice(Math.max(0, i - 2), i + 1)
        const avg = window.reduce((sum, r) => sum + (r[assignee] ?? 0), 0) / window.length
        row[`${assignee}__r3`] = Math.round(avg * 10) / 10
      }
    })
    return rows
  }, [sprintSource, sprints, allAssignees])

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
            Story points on Done / Closed / Resolved issues per sprint, per team member
            {!includeBugs && <strong> — bugs excluded</strong>}.
          </p>

          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData} margin={{ top: 8, right: 24, bottom: 8, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={DARK_GRID} />
              <XAxis
                dataKey="sprint"
                tick={{ fill: DARK_TICK, fontSize: 13 }}
                axisLine={{ stroke: DARK_GRID }}
                tickLine={{ stroke: DARK_GRID }}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fill: DARK_TICK, fontSize: 12 }}
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
                formatter={(value, name) => [
                  `${value} SP`,
                  name.endsWith('__r3') ? `${name.replace('__r3', '')} · 3-sp avg` : name,
                ]}
              />
              <Legend
                wrapperStyle={{ color: '#F0F0F0', fontSize: 13, paddingTop: 12 }}
                formatter={(value) =>
                  value.endsWith('__r3') ? `${value.replace('__r3', '')} · 3-sp avg` : value
                }
              />
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
              {selectedList.map((name) => (
                <Line
                  key={`${name}__r3`}
                  type="monotone"
                  dataKey={`${name}__r3`}
                  stroke={colorFor(name)}
                  strokeWidth={1.5}
                  strokeDasharray="6 3"
                  dot={false}
                  activeDot={false}
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
                  const found = sprintSource?.[s]?.story_points_by_assignee?.find(
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
