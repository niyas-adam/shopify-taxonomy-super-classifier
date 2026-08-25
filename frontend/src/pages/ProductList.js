import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { productsAPI, classificationsAPI } from '../services/api';
import { toast } from 'react-toastify';

function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedProducts, setSelectedProducts] = useState([]);

  useEffect(() => {
    fetchProducts();
  }, [statusFilter]);

  const fetchProducts = async () => {
    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (searchTerm) params.search = searchTerm;
      const response = await productsAPI.getAll(params);
      setProducts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
      toast.error('Failed to fetch products');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchProducts();
  };

  const handleClassify = async (productId) => {
    try {
      await classificationsAPI.classify({ product_id: productId });
      toast.success('Classification started');
      fetchProducts();
    } catch (error) {
      console.error('Classification failed:', error);
      toast.error('Classification failed');
    }
  };

  const handleBatchClassify = async () => {
    if (selectedProducts.length === 0) {
      toast.warning('Please select products to classify');
      return;
    }
    try {
      await classificationsAPI.batchClassify({ product_ids: selectedProducts });
      toast.success(`Batch classification started for ${selectedProducts.length} products`);
      setSelectedProducts([]);
      fetchProducts();
    } catch (error) {
      console.error('Batch classification failed:', error);
      toast.error('Batch classification failed');
    }
  };

  const handleSelectProduct = (productId) => {
    setSelectedProducts(prev => 
      prev.includes(productId) 
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  };

  const handleSelectAll = () => {
    if (selectedProducts.length === products.length) {
      setSelectedProducts([]);
    } else {
      setSelectedProducts(products.map(p => p.id));
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return 'success';
    if (confidence >= 0.5) return 'warning';
    return 'danger';
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
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Products</h1>
        <Link to="/" className="btn btn-secondary">Back to Dashboard</Link>
      </div>
      <div className="row mb-4">
        <div className="col-md-6">
          <form onSubmit={handleSearch}>
            <div className="input-group">
              <input type="text" className="form-control" placeholder="Search products..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
              <button className="btn btn-outline-primary" type="submit">Search</button>
            </div>
          </form>
        </div>
        <div className="col-md-3">
          <select className="form-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
        <div className="col-md-3">
          <button className="btn btn-primary" onClick={handleBatchClassify} disabled={selectedProducts.length === 0}>Batch Classify ({selectedProducts.length})</button>
        </div>
      </div>
      <div className="card">
        <div className="card-body">
          <table className="table table-hover">
            <thead>
              <tr>
                <th><input type="checkbox" checked={selectedProducts.length === products.length} onChange={handleSelectAll} /></th>
                <th>Image</th>
                <th>Product Number</th>
                <th>Name</th>
                <th>Category</th>
                <th>Status</th>
                <th>Confidence</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td><input type="checkbox" checked={selectedProducts.includes(product.id)} onChange={() => handleSelectProduct(product.id)} /></td>
                  <td>{product.image_url ? (<img src={product.image_url} alt={product.product_name} style={{ width: '50px', height: '50px', objectFit: 'cover' }} />) : (<div className="bg-light d-flex align-items-center justify-content-center" style={{ width: '50px', height: '50px' }}><span className="text-muted">No Image</span></div>)}</td>
                  <td>{product.product_number}</td>
                  <td><Link to={`/products/${product.id}`}>{product.product_name}</Link></td>
                  <td>{product.source_category}</td>
                  <td><span className={`badge bg-${product.status === 'completed' ? 'success' : product.status === 'processing' ? 'warning' : product.status === 'failed' ? 'danger' : 'secondary'}`}>{product.status}</span></td>
                  <td>{product.classification && (<span className={`badge bg-${getConfidenceColor(product.classification.confidence)}`}>{(product.classification.confidence * 100).toFixed(1)}%</span>)}</td>
                  <td><button className="btn btn-sm btn-primary me-1" onClick={() => handleClassify(product.id)}>Classify</button><Link to={`/products/${product.id}`} className="btn btn-sm btn-outline-secondary">View</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
          {products.length === 0 && (
            <div className="text-center py-4">
              <p className="text-muted">No products found</p>
              <Link to="/import" className="btn btn-primary">Import Products</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProductList;