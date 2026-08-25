import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { statsAPI } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await statsAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <h1 className="mb-4">Shopify Taxonomy Super Classifier</h1>
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <h5 className="card-title">Total Products</h5>
              <h2 className="card-text">{stats?.total_products || 0}</h2>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body">
              <h5 className="card-title">Classified</h5>
              <h2 className="card-text">{stats?.classified || 0}</h2>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body">
              <h5 className="card-title">Needs Review</h5>
              <h2 className="card-text">{stats?.needs_review || 0}</h2>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body">
              <h5 className="card-title">Avg Confidence</h5>
              <h2 className="card-text">{((stats?.average_confidence || 0) * 100).toFixed(1)}%</h2>
            </div>
          </div>
        </div>
      </div>
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Quick Actions</h5>
            </div>
            <div className="card-body">
              <Link to="/import" className="btn btn-primary me-2">Import Products</Link>
              <Link to="/products" className="btn btn-secondary me-2">View Products</Link>
              <Link to="/review" className="btn btn-warning me-2">Review Classifications</Link>
              <Link to="/statistics" className="btn btn-info">View Statistics</Link>
            </div>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Status Breakdown</h5>
            </div>
            <div className="card-body">
              {stats?.status_counts && Object.entries(stats.status_counts).map(([status, count]) => (
                <div key={status} className="d-flex justify-content-between mb-2">
                  <span className="text-capitalize">{status.replace('_', ' ')}</span>
                  <span className="badge bg-secondary">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">Classification Methods</h5>
            </div>
            <div className="card-body">
              <p className="mb-2"><strong>Hybrid:</strong> Combines lexical, semantic, and image signals</p>
              <p className="mb-2"><strong>LLM:</strong> Uses Groq/Gemini for advanced classification</p>
              <p className="mb-0"><strong>Semantic:</strong> SentenceTransformers for fast matching</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;