import React from 'react'
import { useLocation } from 'react-router-dom'

export default function Congrats() {
  const location = useLocation()
  const team = location.state?.team || sessionStorage.getItem('team')
  const completed_time = location.state?.completed_time
  const total_time = location.state?.total_time

  return (
    <div className="container">
      <h1>Congratulations!</h1>
      <p className="small-muted">Well done, detective{team ? ` — ${team}` : ''}.</p>

      {completed_time && (
        <div style={{ marginTop: 12 }}>
          <div>Completed time: <strong>{completed_time}</strong></div>
          <div>Total time: <strong>{total_time}</strong></div>
        </div>
      )}

      <div style={{ marginTop: 16 }}>
        <p className="small-muted">Thanks for participating. The host can view all results via the Results page.</p>
      </div>
    </div>
  )
}
