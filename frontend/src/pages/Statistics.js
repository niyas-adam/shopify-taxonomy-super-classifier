import React, { useState, useEffect } from 'react';
import { classificationsAPI } from '../services/api';
import { toast } from 'react-toastify';

function Statistics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      const response = await classificationsAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
      toast.error('Failed to fetch statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (<div className="container mt-5"><div className="text-center"><div className="spinner-border" role="status"><span className="visually-hidden">Loading...</span></div></div></div>);
  }

  if (!stats) {
    return (<div className="container mt-5"><div className="alert alert-danger">Failed to load statistics</div></div>);
  }

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Classification Statistics</h1>
        <button className="btn btn-secondary" onClick={() => window.history.back()}>Back</button>
      </div>
      <div className="row mb-4">
        <div className="col-md-3"><div className="card bg-primary text-white"><div className="card-body"><h6 className="card-title">Total Classifications</h6><h2 className="mb-0">{stats.total_classifications}</h2></div></div></div>
        <div className="col-md-3"><div className="card bg-success text-white"><div className="card-body"><h6 className="card-title">Average Confidence</h6><h2 className="mb-0">{(stats.average_confidence * 100).toFixed(1)}%</h2></div></div></div>
        <div className="col-md-3"><div className="card bg-warning text-white"><div className="card-body"><h6 className="card-title">Pending Review</h6><h2 className="mb-0">{stats.pending_review}</h2></div></div></div>
        <div className="col-md-3"><div className="card bg-info text-white"><div className="card-body"><h6 className="card-title">Success Rate</h6><h2 className="mb-0">{stats.total_classifications > 0 ? ((stats.approved_count / stats.total_classifications) * 100).toFixed(1) : 0}%</h2></div></div></div>
      </div>
      <div className="row mb-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header"><h5 className="mb-0">Status Distribution</h5></div>
            <div className="card-body">
              <table className="table"><thead><tr><th>Status</th><th>Count</th><th>Percentage</th></tr></thead><tbody>
                <tr><td><span className="badge bg-success">Approved</span></td><td>{stats.approved_count}</td><td>{stats.total_classifications > 0 ? ((stats.approved_count / stats.total_classifications) * 100).toFixed(1) : 0}%</td></tr>
                <tr><td><span className="badge bg-warning">Pending Review</span></td><td>{stats.needs_review_count}</td><td>{stats.total_classifications > 0 ? ((stats.needs_review_count / stats.total_classifications) * 100).toFixed(1) : 0}%</td></tr>
                <tr><td><span className="badge bg-secondary">Processing</span></td><td>{stats.processing_count}</td><td>{stats.total_classifications > 0 ? ((stats.processing_count / stats.total_classifications) * 100).toFixed(1) : 0}%</td></tr>
                <tr><td><span className="badge bg-danger">Failed</span></td><td>{stats.failed_count}</td><td>{stats.total_classifications > 0 ? ((stats.failed_count / stats.total_classifications) * 100).toFixed(1) : 0}%</td></tr>
              </tbody></table>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header"><h5 className="mb-0">Method Distribution</h5></div>
            <div className="card-body">
              <table className="table"><thead><tr><th>Method</th><th>Count</th><th>Percentage</th></tr></thead><tbody>
                {Object.entries(stats.method_distribution).map(([method, count]) => (
                  <tr key={method}><td className="text-capitalize">{method}</td><td>{count}</td><td>{stats.total_classifications > 0 ? ((count / stats.total_classifications) * 100).toFixed(1) : 0}%</td></tr>
                ))}
              </tbody></table>
            </div>
          </div>
        </div>
      </div>
      <div className="card mb-4">
        <div className="card-header"><h5 className="mb-0">Confidence Distribution</h5></div>
        <div className="card-body">
          <div className="row">
            {Object.entries(stats.confidence_distribution).map(([range, count]) => (
              <div key={range} className="col-md-2"><div className="text-center"><div className="h4 mb-1">{count}</div><small className="text-muted">{range}</small></div></div>
            ))}
          </div>
        </div>
      </div>
      <div className="card">
        <div className="card-header"><h5 className="mb-0">Top Categories</h5></div>
        <div className="card-body">
          <table className="table"><thead><tr><th>Category</th><th>Count</th><th>Avg Confidence</th></tr></thead><tbody>
            {stats.top_categories.map((item, index) => (
              <tr key={index}><td>{item.category}</td><td>{item.count}</td><td>{(item.avg_confidence * 100).toFixed(1)}%</td></tr>
            ))}
          </tbody></table>
        </div>
      </div>
    </div>
  );
}

export default Statistics;