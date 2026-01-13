import React, { useState } from 'react'
import api from '../services/api'
import './AddWatchForm.css'

const AddWatchForm = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    watch_id: '',
    name: '',
    high_heart_rate_threshold: '',
    low_heart_rate_threshold: '',
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
      const payload = {
        watch_id: formData.watch_id,
        name: formData.name,
      }

      // Only include thresholds if provided
      if (formData.high_heart_rate_threshold) {
        payload.high_heart_rate_threshold = parseInt(formData.high_heart_rate_threshold)
      }
      if (formData.low_heart_rate_threshold) {
        payload.low_heart_rate_threshold = parseInt(formData.low_heart_rate_threshold)
      }

      await api.post('/watches/', payload)
      onSuccess()
    } catch (err) {
      const errorMsg = err.response?.data?.error || 
                      err.response?.data?.watch_id?.[0] ||
                      err.response?.data?.name?.[0] ||
                      'Failed to create watch. Please try again.'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Add New Watch</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="watch_id">Watch ID *</label>
            <input
              type="text"
              id="watch_id"
              name="watch_id"
              value={formData.watch_id}
              onChange={handleChange}
              required
              placeholder="Unique watch identifier"
              maxLength={64}
            />
          </div>

          <div className="form-group">
            <label htmlFor="name">Watch Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="e.g., Apple Watch Series 9"
              maxLength={100}
            />
          </div>

          <div className="form-group">
            <label htmlFor="high_heart_rate_threshold">High Heart Rate Threshold (optional)</label>
            <input
              type="number"
              id="high_heart_rate_threshold"
              name="high_heart_rate_threshold"
              value={formData.high_heart_rate_threshold}
              onChange={handleChange}
              min="1"
              max="300"
              placeholder="Default: 98 BPM"
            />
          </div>

          <div className="form-group">
            <label htmlFor="low_heart_rate_threshold">Low Heart Rate Threshold (optional)</label>
            <input
              type="number"
              id="low_heart_rate_threshold"
              name="low_heart_rate_threshold"
              value={formData.low_heart_rate_threshold}
              onChange={handleChange}
              min="1"
              max="200"
              placeholder="Default: 25 BPM"
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} className="cancel-button">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Creating...' : 'Create Watch'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AddWatchForm

