import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { productsAPI, classificationsAPI } from '../services/api';
import { toast } from 'react-toastify';

function ProductDetail() {
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProduct();
  }, [id]);

  const fetchProduct = async () => {
    try {
      const response = await productsAPI.getById(id);
      setProduct(response.data);
    } catch (error) {
      console.error('Failed to fetch product:', error);
      toast.error('Failed to fetch product');
    } finally {
      setLoading(false);
    }
  };

  const handleClassify = async () => {
    try {
      await classificationsAPI.classify({ product_id: parseInt(id) });
      toast.success('Classification started');
      fetchProduct();
    } catch (error) {
      console.error('Classification failed:', error);
      toast.error('Classification failed');
    }
  };

  const handleApprove = async () => {
    try {
      await classificationsAPI.approve(product.classification.id, { reviewed_by: 'user', notes: 'Approved from product detail' });
      toast.success('Classification approved');
      fetchProduct();
    } catch (error) {
      console.error('Approval failed:', error);
      toast.error('Approval failed');
    }
  };

  const handleReject = async () => {
    try {
      await classificationsAPI.reject(product.classification.id, { reviewed_by: 'user', notes: 'Rejected from product detail' });
      toast.success('Classification rejected');
      fetchProduct();
    } catch (error) {
      console.error('Rejection failed:', error);
      toast.error('Rejection failed');
    }
  };

  if (loading) {
    return (<div className="container mt-5"><div className="text-center"><div className="spinner-border" role="status"><span className="visually-hidden">Loading...</span></div></div></div>);
  }

  if (!product) {
    return (<div className="container mt-5"><div className="alert alert-danger">Product not found</div></div>);
  }

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Product Details</h1>
        <Link to="/products" className="btn btn-secondary">Back to Products</Link>
      </div>
      <div className="row">
        <div className="col-md-8">
          <div className="card mb-4">
            <div className="card-header"><h5 className="mb-0">Product Information</h5></div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <p><strong>Product Number:</strong> {product.product_number}</p>
                  <p><strong>Name:</strong> {product.product_name}</p>
                  <p><strong>Category:</strong> {product.source_category}</p>
                  <p><strong>Materials:</strong> {product.materials || 'N/A'}</p>
                </div>
                <div className="col-md-6">
                  <p><strong>Weight:</strong> {product.product_weight ? `${product.product_weight} lbs` : 'N/A'}</p>
                  <p><strong>Country of Origin:</strong> {product.country_of_origin || 'N/A'}</p>
                  <p><strong>Status:</strong> <span className={`badge bg-${product.status === 'completed' ? 'success' : product.status === 'processing' ? 'warning' : product.status === 'failed' ? 'danger' : 'secondary'} ms-2`}>{product.status}</span></p>
                </div>
              </div>
              <hr />
              <p><strong>Description:</strong></p>
              <p className="text-muted">{product.product_description || 'No description available'}</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card mb-4">
            <div className="card-header"><h5 className="mb-0">Product Image</h5></div>
            <div className="card-body text-center">
              {product.image_url ? (<img src={product.image_url} alt={product.product_name} className="img-fluid rounded" style={{ maxHeight: '300px' }} />) : (<div className="bg-light p-5 rounded"><p className="text-muted mb-0">No image available</p></div>)}
            </div>
          </div>
        </div>
      </div>
      <div className="card mb-4">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Classification</h5>
          <div>
            <button className="btn btn-primary me-2" onClick={handleClassify}>Classify Product</button>
            {product.classification && (<><button className="btn btn-success me-2" onClick={handleApprove}>Approve</button><button className="btn btn-danger" onClick={handleReject}>Reject</button></>)}
          </div>
        </div>
        <div className="card-body">
          {product.classification ? (
            <div className="row">
              <div className="col-md-6">
                <p><strong>Predicted Category:</strong></p>
                <p className="text-primary fw-bold">{product.classification.predicted_category_path}</p>
                <p><strong>Confidence:</strong></p>
                <div className="progress mb-2" style={{ height: '20px' }}><div className={`progress-bar bg-${product.classification.confidence >= 0.7 ? 'success' : product.classification.confidence >= 0.5 ? 'warning' : 'danger'}`} role="progressbar" style={{ width: `${product.classification.confidence * 100}%` }}>{(product.classification.confidence * 100).toFixed(1)}%</div></div>
                <p><strong>Status:</strong> <span className={`badge bg-${product.classification.status === 'approved' ? 'success' : product.classification.status === 'needs_review' ? 'warning' : 'secondary'} ms-2`}>{product.classification.status}</span></p>
              </div>
              <div className="col-md-6">
                <p><strong>Classification Method:</strong> {product.classification.classification_method}</p>
                <p><strong>Requires Review:</strong> <span className={`badge bg-${product.classification.requires_manual_review ? 'warning' : 'success'} ms-2`}>{product.classification.requires_manual_review ? 'Yes' : 'No'}</span></p>
                {product.classification.review_reason && (<p><strong>Review Reason:</strong> {product.classification.review_reason}</p>)}
              </div>
            </div>
          ) : (<div className="text-center py-4"><p className="text-muted mb-3">No classification yet</p><button className="btn btn-primary" onClick={handleClassify}>Classify Now</button></div>)}
        </div>
      </div>
      {product.classification?.alternative_categories?.length > 0 && (
        <div className="card mb-4">
          <div className="card-header"><h5 className="mb-0">Alternative Categories</h5></div>
          <div className="card-body">
            <table className="table table-sm"><thead><tr><th>Rank</th><th>Category</th><th>Confidence</th></tr></thead><tbody>{product.classification.alternative_categories.map((alt, index) => (<tr key={index}><td>{alt.rank}</td><td>{alt.category_path}</td><td>{(alt.confidence * 100).toFixed(1)}%</td></tr>))}</tbody></table>
          </div>
        </div>
      )}
      {product.classification?.attributes?.length > 0 && (
        <div className="card">
          <div className="card-header"><h5 className="mb-0">Extracted Attributes</h5></div>
          <div className="card-body">
            <table className="table table-sm"><thead><tr><th>Attribute</th><th>Value</th><th>Confidence</th></tr></thead><tbody>{product.classification.attributes.map((attr, index) => (<tr key={index}><td>{attr.attribute_name}</td><td>{attr.attribute_value}</td><td>{(attr.confidence * 100).toFixed(1)}%</td></tr>))}</tbody></table>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProductDetail;