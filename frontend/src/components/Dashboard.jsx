import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'
import AddWatchForm from './AddWatchForm'
import AddMetricForm from './AddMetricForm'
import AddBPForm from './AddBPForm'
import './Dashboard.css'

const Dashboard = () => {
  const { logout } = useAuth()
  const [watches, setWatches] = useState([])
  const [metrics, setMetrics] = useState([])
  const [alerts, setAlerts] = useState([])
  const [bpRecommendation, setBpRecommendation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showAddWatch, setShowAddWatch] = useState(false)
  const [showAddMetric, setShowAddMetric] = useState(false)
  const [showAddBP, setShowAddBP] = useState(false)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError('')

      // Fetch all data in parallel
      const [watchesRes, metricsRes, alertsRes, bpRes] = await Promise.allSettled([
        api.get('/watches/'),
        api.get('/watch-metrics/'),
        api.get('/alerts/'),
        api.get('/best-bp/'),
      ])

      if (watchesRes.status === 'fulfilled') {
        setWatches(watchesRes.value.data)
      }
      if (metricsRes.status === 'fulfilled') {
        setMetrics(metricsRes.value.data)
      }
      if (alertsRes.status === 'fulfilled') {
        setAlerts(alertsRes.value.data)
      }
      if (bpRes.status === 'fulfilled') {
        if (bpRes.value.data.recommended_bp) {
          setBpRecommendation(bpRes.value.data)
        } else {
          setBpRecommendation(null)
        }
      } else {
        setBpRecommendation(null)
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || 'Failed to load dashboard data. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
  }

  const handleAddWatchSuccess = () => {
    setShowAddWatch(false)
    fetchDashboardData()
  }

  const handleAddMetricSuccess = () => {
    setShowAddMetric(false)
    fetchDashboardData()
  }

  const handleAddBPSuccess = () => {
    setShowAddBP(false)
    fetchDashboardData()
  }

  // Group metrics by watch
  const metricsByWatch = {}
  metrics.forEach((metric) => {
    const watchId = metric.watch
    if (!metricsByWatch[watchId]) {
      metricsByWatch[watchId] = []
    }
    metricsByWatch[watchId].push(metric)
  })

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Watch Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {/* Alerts Section - Prominent Display */}
      {alerts.length > 0 && (
        <div className="alerts-section">
          <h2 className="alerts-title">
            ⚠️ Active Alerts ({alerts.length})
          </h2>
          <div className="alerts-grid">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`alert-card ${
                  alert.alert_type === 'HIGH_HEART_RATE' ? 'high' : 'low'
                }`}
              >
                <div className="alert-card-header">
                  <strong>{alert.watch_name}</strong>
                  <span className="alert-type-badge">
                    {alert.alert_type === 'HIGH_HEART_RATE' ? 'HIGH' : 'LOW'} HEART RATE
                  </span>
                </div>
                <div className="alert-card-body">
                  <div className="alert-heart-rate">{alert.heart_rate} BPM</div>
                  <div className="alert-timestamp">
                    {new Date(alert.timestamp_readable).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="action-buttons">
        <button onClick={() => setShowAddWatch(true)} className="action-btn add-watch-btn">
          + Add Watch
        </button>
        <button 
          onClick={() => setShowAddMetric(true)} 
          className="action-btn add-metric-btn"
          disabled={watches.length === 0}
        >
          + Add Metric
        </button>
        <button onClick={() => setShowAddBP(true)} className="action-btn add-bp-btn">
          + Add Blood Pressure
        </button>
      </div>

      {/* Watches and Metrics Table */}
      <div className="watches-section">
        <h2>Your Watches & Metrics</h2>
        {watches.length === 0 ? (
          <div className="empty-state">
            <p>No watches registered yet. Click "Add Watch" to get started.</p>
          </div>
        ) : (
          <div className="watches-table-container">
            {watches.map((watch) => {
              const watchMetrics = metricsByWatch[watch.id] || []
              return (
                <div key={watch.id} className="watch-table-card">
                  <div className="watch-header">
                    <div className="watch-info">
                      <h3>{watch.name}</h3>
                      <span className="watch-id">ID: {watch.watch_id}</span>
                    </div>
                    <div className="watch-thresholds">
                      {watch.high_heart_rate_threshold && (
                        <span>High: {watch.high_heart_rate_threshold} BPM</span>
                      )}
                      {watch.low_heart_rate_threshold && (
                        <span>Low: {watch.low_heart_rate_threshold} BPM</span>
                      )}
                    </div>
                  </div>
                  
                  {watchMetrics.length > 0 ? (
                    <div className="metrics-table-wrapper">
                      <table className="metrics-table">
                        <thead>
                          <tr>
                            <th>Heart Rate (BPM)</th>
                            <th>Steps</th>
                            <th>Timestamp</th>
                          </tr>
                        </thead>
                        <tbody>
                          {watchMetrics.map((metric) => (
                            <tr key={metric.id}>
                              <td className="heart-rate-cell">{metric.heart_rate}</td>
                              <td>{metric.steps}</td>
                              <td className="timestamp-cell">
                                {new Date(metric.timestamp_readable).toLocaleString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="no-metrics">
                      <p>No metrics recorded for this watch yet.</p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Blood Pressure Section */}
      <div className="bp-section">
        <h2>Blood Pressure Recommendation</h2>
        {bpRecommendation ? (
          <div className="bp-card">
            <div className="bp-value-large">{bpRecommendation.recommended_bp}</div>
            <div className="bp-details">
              <p><strong>Age:</strong> {bpRecommendation.age} years</p>
              <p><strong>Systolic:</strong> {bpRecommendation.systolic} mmHg</p>
              <p><strong>Diastolic:</strong> {bpRecommendation.diastolic} mmHg</p>
              <p className="bp-timestamp">
                Created: {new Date(bpRecommendation.timestamp * 1000).toLocaleString()}
              </p>
            </div>
          </div>
        ) : (
          <div className="bp-empty">
            <p>No blood pressure recommendation recorded.</p>
            <p>Click "Add Blood Pressure" to create one.</p>
          </div>
        )}
      </div>

      {/* Modals */}
      {showAddWatch && (
        <AddWatchForm
          onSuccess={handleAddWatchSuccess}
          onCancel={() => setShowAddWatch(false)}
        />
      )}
      {showAddMetric && (
        <AddMetricForm
          watches={watches}
          onSuccess={handleAddMetricSuccess}
          onCancel={() => setShowAddMetric(false)}
        />
      )}
      {showAddBP && (
        <AddBPForm
          onSuccess={handleAddBPSuccess}
          onCancel={() => setShowAddBP(false)}
        />
      )}
    </div>
  )
}

export default Dashboard
