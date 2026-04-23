import React, { useState } from 'react'
import UploadForm from './components/UploadForm.jsx'
import ReportChart from './components/ReportChart.jsx'

function Tiles({ report }) {
  return (
    <div className="tiles">
      <div className="tile">
        <div className="label">Story points delivered</div>
        <div className="value">
          {report.total_story_points_delivered}
          <span className="unit">SP</span>
        </div>
      </div>
      <div className="tile">
        <div className="label">Issues delivered</div>
        <div className="value">{report.total_issues_delivered}</div>
      </div>
      <div className="tile">
        <div className="label">Rows in file</div>
        <div className="value">{report.total_rows}</div>
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

  return (
    <div className="app">
      <header>
        <h1>
          Jira Excel Reporter <span className="sub">v0.1</span>
        </h1>
      </header>

      <UploadForm onReport={setReport} onError={setError} onLoading={setLoading} />

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
          <Tiles report={report} />
          <SPByAssigneeReport rows={report.story_points_by_assignee} />
          <DefectsByAssigneeReport rows={report.defects_by_assignee} />
        </>
      )}

      {!report && !loading && !error && (
        <p className="muted">
          Upload a Jira extract (.xlsx or .csv) to see the three reports. Required columns:
          Issue Type, Assignee, Status, Story Points. The app will do its best if some are missing.
        </p>
      )}

      <footer>FastAPI + React — story-points &amp; defect reports from an Excel/CSV extract.</footer>
    </div>
  )
}
