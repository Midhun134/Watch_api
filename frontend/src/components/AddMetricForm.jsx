import React, { useState } from 'react'
import api from '../services/api'
import './AddMetricForm.css'

const AddMetricForm = ({ watches, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    watch: '',
    heart_rate: '',
    steps: '0',
    timestamp: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Use current timestamp if not provided
      let timestamp = formData.timestamp
      if (!timestamp) {
        timestamp = Math.floor(Date.now() / 1000)
      } else {
        // Convert date input to epoch timestamp
        timestamp = Math.floor(new Date(timestamp).getTime() / 1000)
      }

      const payload = {
        watch: formData.watch,
        heart_rate: parseInt(formData.heart_rate),
        steps: parseInt(formData.steps) || 0,
        timestamp: timestamp,
      }

      await api.post('/watch-metrics/', payload)
      onSuccess()
    } catch (err) {
      const errorMsg = err.response?.data?.error || 
                      err.response?.data?.heart_rate?.[0] ||
                      err.response?.data?.watch?.[0] ||
                      'Failed to create metric. Please try again.'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Add Watch Metric</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="watch">Watch *</label>
            <select
              id="watch"
              name="watch"
              value={formData.watch}
              onChange={handleChange}
              required
            >
              <option value="">Select a watch</option>
              {watches.map((watch) => (
                <option key={watch.id} value={watch.id}>
                  {watch.name} ({watch.watch_id})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="heart_rate">Heart Rate (BPM) *</label>
            <input
              type="number"
              id="heart_rate"
              name="heart_rate"
              value={formData.heart_rate}
              onChange={handleChange}
              required
              min="1"
              placeholder="e.g., 72"
            />
          </div>

          <div className="form-group">
            <label htmlFor="steps">Steps (optional)</label>
            <input
              type="number"
              id="steps"
              name="steps"
              value={formData.steps}
              onChange={handleChange}
              min="0"
              placeholder="0"
            />
          </div>

          <div className="form-group">
            <label htmlFor="timestamp">Timestamp (optional)</label>
            <input
              type="datetime-local"
              id="timestamp"
              name="timestamp"
              value={formData.timestamp}
              onChange={handleChange}
            />
            <small>Leave empty to use current time</small>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} className="cancel-button">
              Cancel
            </button>
            <button type="submit" disabled={loading || watches.length === 0} className="submit-button">
              {loading ? 'Creating...' : 'Add Metric'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AddMetricForm

