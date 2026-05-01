import React, { useState } from 'react'
import UploadForm from './components/UploadForm.jsx'
import ReportChart from './components/ReportChart.jsx'
import IndividualPerformance from './components/IndividualPerformance.jsx'

function Tiles({ data }) {
  return (
    <div className="tiles">
      <div className="tile">
        <div className="label">Story points delivered</div>
        <div className="value">
          {data.total_story_points_delivered}
          <span className="unit">SP</span>
        </div>
      </div>
      <div className="tile">
        <div className="label">Issues delivered</div>
        <div className="value">{data.total_issues_delivered}</div>
      </div>
      <div className="tile">
        <div className="label">Rows in file</div>
        <div className="value">{data.total_rows ?? '—'}</div>
      </div>
    </div>
  )
}

function SPByAssigneeReport({ rows }) {
  return (
    <section className="report">
      <h2>Story points delivered by team member</h2>
      <p className="caption">
        Sums story points on issues with status in Done / Closed / Resolved, grouped by Assignee.
      </p>
      <div className="report-grid">
        <ReportChart data={rows} xKey="assignee" yKey="story_points" color="#2e5aac" unit="SP" />
        {rows.length === 0 ? (
          <div className="empty-state">No delivered issues with story points.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Assignee</th>
                <th className="num">Issues</th>
                <th className="num">Story points</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.assignee}>
                  <td>{r.assignee}</td>
                  <td className="num">{r.issue_count}</td>
                  <td className="num">{r.story_points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  )
}

function DefectsByAssigneeReport({ rows }) {
  return (
    <section className="report">
      <h2>Defects assigned to each team member</h2>
      <p className="caption">
        Counts every row with Issue Type = Bug or Defect, grouped by Assignee (all statuses).
      </p>
      <div className="report-grid">
        <ReportChart data={rows} xKey="assignee" yKey="defect_count" color="#c23a3a" unit="defects" />
        {rows.length === 0 ? (
          <div className="empty-state">No defects found in the file.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Assignee</th>
                <th className="num">Defects</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.assignee}>
                  <td>{r.assignee}</td>
                  <td className="num">{r.defect_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  )
}

export default function App() {
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [selectedSprint, setSelectedSprint] = useState('__all__')
  const [activeTab, setActiveTab] = useState('sprint')
  const [includeBugs, setIncludeBugs] = useState(true)

  function handleReport(data) {
    setReport(data)
    setSelectedSprint('__all__')
    setActiveTab('sprint')
    setIncludeBugs(true)
  }

  // Pick the right data slice based on sprint selection and bug filter
  const activeData = report
    ? (() => {
        const sprintKey = selectedSprint === '__all__' ? null : selectedSprint
        const sprintSrc = sprintKey
          ? (includeBugs ? report.by_sprint?.[sprintKey] : report.by_sprint_ex_bugs?.[sprintKey])
          : null

        if (sprintSrc) {
          return {
            total_story_points_delivered: sprintSrc.total_story_points_delivered,
            total_issues_delivered: sprintSrc.total_issues_delivered,
            total_rows: undefined,
            story_points_by_assignee: sprintSrc.story_points_by_assignee,
            defects_by_assignee: sprintSrc.defects_by_assignee ?? report.by_sprint?.[sprintKey]?.defects_by_assignee ?? [],
          }
        }

        // "All sprints" view
        return {
          total_story_points_delivered: includeBugs
            ? report.total_story_points_delivered
            : report.total_story_points_delivered_ex_bugs,
          total_issues_delivered: includeBugs
            ? report.total_issues_delivered
            : report.total_issues_delivered_ex_bugs,
          total_rows: report.total_rows,
          story_points_by_assignee: includeBugs
            ? report.story_points_by_assignee
            : report.story_points_by_assignee_ex_bugs,
          defects_by_assignee: report.defects_by_assignee,
        }
      })()
    : null

  const sprintTitle = selectedSprint === '__all__' ? 'All Sprints' : selectedSprint

  return (
    <div className="app">
      <header>
        <h1>QLP Sprint Performance Report</h1>
      </header>

      <UploadForm onReport={handleReport} onError={setError} onLoading={setLoading} />

      {loading && <div className="muted">Analyzing…</div>}
      {error && <div className="error">{error}</div>}

      {report && (
        <>
          {report.warnings?.length > 0 && (
            <div className="warnings">
              <strong>Heads-up on what was assumed:</strong>
              <ul>
                {report.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="filter-bar">
            <span className="filter-label">Filters</span>
            <label className="filter-toggle">
              <input
                type="checkbox"
                checked={includeBugs}
                onChange={(e) => setIncludeBugs(e.target.checked)}
              />
              Include bugs in story points
            </label>
          </div>

          <div className="tabs">
            <button
              className={`tab-btn${activeTab === 'sprint' ? ' active' : ''}`}
              onClick={() => setActiveTab('sprint')}
            >
              Sprint Reports
            </button>
            <button
              className={`tab-btn${activeTab === 'individual' ? ' active' : ''}`}
              onClick={() => setActiveTab('individual')}
            >
              Individual Performance
            </button>
          </div>

          {activeTab === 'sprint' && (
            <>
              {report.sprints?.length > 0 && (
                <div className="sprint-bar">
                  <label htmlFor="sprint-select">Sprint</label>
                  <select
                    id="sprint-select"
                    value={selectedSprint}
                    onChange={(e) => setSelectedSprint(e.target.value)}
                  >
                    <option value="__all__">All Sprints</option>
                    {report.sprints.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                  <h2 className="sprint-title">{sprintTitle}</h2>
                </div>
              )}

              <Tiles data={activeData} />
              <SPByAssigneeReport rows={activeData.story_points_by_assignee} />
              <DefectsByAssigneeReport rows={activeData.defects_by_assignee} />
            </>
          )}

          {activeTab === 'individual' && (
            <IndividualPerformance report={report} includeBugs={includeBugs} />
          )}
        </>
      )}

      {!report && !loading && !error && (
        <p className="muted">
          Upload a Jira extract (.xlsx or .csv) to see the three reports. Required columns:
          Issue Type, Assignee, Status, Story Points. The app will do its best if some are missing.
        </p>
      )}

    </div>
  )
}
