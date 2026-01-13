import React, { useState } from 'react'
import api from '../services/api'
import './AddBPForm.css'

const AddBPForm = ({ onSuccess, onCancel }) => {
  const [age, setAge] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await api.post('/best-bp/', { age: parseInt(age) })
      onSuccess()
    } catch (err) {
      const errorMsg = err.response?.data?.error || 
                      err.response?.data?.age?.[0] ||
                      'Failed to create blood pressure recommendation. Please try again.'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2>Add Blood Pressure Recommendation</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="age">Age *</label>
            <input
              type="number"
              id="age"
              name="age"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              required
              min="21"
              max="70"
              placeholder="Enter your age (21-70)"
            />
            <small>Age must be between 21 and 70 years</small>
          </div>

          <div className="form-actions">
            <button type="button" onClick={onCancel} className="cancel-button">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="submit-button">
              {loading ? 'Creating...' : 'Create Recommendation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default AddBPForm

