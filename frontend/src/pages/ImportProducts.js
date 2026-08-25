import React, { useState } from 'react';
import { productsAPI } from '../services/api';
import { toast } from 'react-toastify';

function ImportProducts() {
  const [file, setFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
  };

  const handleImport = async () => {
    if (!file) {
      toast.warning('Please select a CSV file');
      return;
    }
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await productsAPI.import(formData);
      setResult(response.data);
      toast.success(`Import completed: ${response.data.imported} products imported`);
    } catch (error) {
      console.error('Import failed:', error);
      toast.error('Import failed');
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Import Products</h1>
        <button className="btn btn-secondary" onClick={() => window.history.back()}>Back</button>
      </div>
      <div className="row">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header"><h5 className="mb-0">CSV Import</h5></div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label">Select CSV File</label>
                <input type="file" className="form-control" accept=".csv" onChange={handleFileChange} />
                <div className="form-text">Supported columns: product_number, product_name, product_description, source_category, image_url, materials, product_weight, country_of_origin</div>
              </div>
              <button className="btn btn-primary" onClick={handleImport} disabled={!file || importing}>
                {importing ? (<><span className="spinner-border spinner-border-sm me-2" role="status"></span>Importing...</>) : ('Import Products')}
              </button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card">
            <div className="card-header"><h5 className="mb-0">Import Help</h5></div>
            <div className="card-body">
              <h6>CSV Format</h6>
              <p className="text-muted small">Your CSV file should include headers for each column. The minimum required columns are:</p>
              <ul className="small"><li><strong>product_number</strong> - Unique product identifier</li><li><strong>product_name</strong> - Product name</li><li><strong>source_category</strong> - Current category</li></ul>
              <h6>Optional Columns</h6>
              <ul className="small"><li>product_description</li><li>image_url</li><li>materials</li><li>product_weight</li><li>country_of_origin</li></ul>
            </div>
          </div>
        </div>
      </div>
      {result && (
        <div className="card mt-4">
          <div className="card-header"><h5 className="mb-0">Import Results</h5></div>
          <div className="card-body">
            <div className="row">
              <div className="col-md-3"><div className="text-center"><h3 className="text-success">{result.imported}</h3><p className="text-muted">Products Imported</p></div></div>
              <div className="col-md-3"><div className="text-center"><h3 className="text-warning">{result.skipped}</h3><p className="text-muted">Products Skipped</p></div></div>
              <div className="col-md-3"><div className="text-center"><h3 className="text-danger">{result.failed}</h3><p className="text-muted">Products Failed</p></div></div>
              <div className="col-md-3"><div className="text-center"><h3 className="text-info">{result.total}</h3><p className="text-muted">Total Rows</p></div></div>
            </div>
            {result.errors && result.errors.length > 0 && (<div className="mt-3"><h6>Errors:</h6><div className="alert alert-danger"><ul className="mb-0">{result.errors.map((error, index) => (<li key={index}>{error}</li>))}</ul></div></div>)}
          </div>
        </div>
      )}
    </div>
  );
}

export default ImportProducts;