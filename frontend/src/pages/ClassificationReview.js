import React, { useState, useEffect } from 'react';
import { classificationsAPI } from '../services/api';
import { toast } from 'react-toastify';

function ClassificationReview() {
  const [classifications, setClassifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('needs_review');
  const [selectedItems, setSelectedItems] = useState([]);

  useEffect(() => {
    fetchClassifications();
  }, [filter]);

  const fetchClassifications = async () => {
    try {
      const params = {};
      if (filter === 'needs_review') params.requires_manual_review = true;
      if (filter === 'approved') params.status = 'approved';
      if (filter === 'rejected') params.status = 'rejected';
      const response = await classificationsAPI.getAll(params);
      setClassifications(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch classifications:', error);
      toast.error('Failed to fetch classifications');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id) => {
    try {
      await classificationsAPI.approve(id, { reviewed_by: 'user', notes: 'Approved from review page' });
      toast.success('Classification approved');
      fetchClassifications();
    } catch (error) {
      console.error('Approval failed:', error);
      toast.error('Approval failed');
    }
  };

  const handleReject = async (id) => {
    try {
      await classificationsAPI.reject(id, { reviewed_by: 'user', notes: 'Rejected from review page' });
      toast.success('Classification rejected');
      fetchClassifications();
    } catch (error) {
      console.error('Rejection failed:', error);
      toast.error('Rejection failed');
    }
  };

  const handleBatchApprove = async () => {
    if (selectedItems.length === 0) {
      toast.warning('Please select items to approve');
      return;
    }
    try {
      await classificationsAPI.batchApprove({ classification_ids: selectedItems, reviewed_by: 'user' });
      toast.success(`Approved ${selectedItems.length} classifications`);
      setSelectedItems([]);
      fetchClassifications();
    } catch (error) {
      console.error('Batch approval failed:', error);
      toast.error('Batch approval failed');
    }
  };

  const handleSelectItem = (id) => {
    setSelectedItems(prev => prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]);
  };

  const handleSelectAll = () => {
    if (selectedItems.length === classifications.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(classifications.map(c => c.id));
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return 'success';
    if (confidence >= 0.5) return 'warning';
    return 'danger';
  };

  if (loading) {
    return (<div className="container mt-5"><div className="text-center"><div className="spinner-border" role="status"><span className="visually-hidden">Loading...</span></div></div></div>);
  }

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Classification Review</h1>
        <button className="btn btn-success" onClick={handleBatchApprove} disabled={selectedItems.length === 0}>Batch Approve ({selectedItems.length})</button>
      </div>
      <div className="row mb-4">
        <div className="col-md-4">
          <select className="form-select" value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="needs_review">Needs Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="all">All</option>
          </select>
        </div>
      </div>
      <div className="card">
        <div className="card-body">
          <table className="table table-hover">
            <thead>
              <tr>
                <th><input type="checkbox" checked={selectedItems.length === classifications.length} onChange={handleSelectAll} /></th>
                <th>Product</th>
                <th>Predicted Category</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Method</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {classifications.map((classification) => (
                <tr key={classification.id}>
                  <td><input type="checkbox" checked={selectedItems.includes(classification.id)} onChange={() => handleSelectItem(classification.id)} /></td>
                  <td><div><strong>{classification.product_name}</strong><br /><small className="text-muted">{classification.product_number}</small></div></td>
                  <td>{classification.predicted_category_path}</td>
                  <td><span className={`badge bg-${getConfidenceColor(classification.confidence)}`}>{(classification.confidence * 100).toFixed(1)}%</span></td>
                  <td><span className={`badge bg-${classification.status === 'approved' ? 'success' : classification.status === 'needs_review' ? 'warning' : classification.status === 'rejected' ? 'danger' : 'secondary'}`}>{classification.status}</span></td>
                  <td>{classification.classification_method}</td>
                  <td><button className="btn btn-sm btn-success me-1" onClick={() => handleApprove(classification.id)}>Approve</button><button className="btn btn-sm btn-danger" onClick={() => handleReject(classification.id)}>Reject</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {classifications.length === 0 && (<div className="text-center py-4"><p className="text-muted">No classifications found</p></div>)}
        </div>
      </div>
    </div>
  );
}

export default ClassificationReview;