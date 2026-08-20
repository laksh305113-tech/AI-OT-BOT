import { useEffect, useMemo, useRef, useState } from 'react';
import { getPatients } from '../api/patientService.js';
import { getPatientImages, uploadPatientImage } from '../api/imagingService.js';

const defaultUpload = { modality: 'XRAY', description: '' };

export default function MedicalImagingPage() {
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [images, setImages] = useState([]);
  const [selectedImageId, setSelectedImageId] = useState('');
  const [uploadForm, setUploadForm] = useState(defaultUpload);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [brightness, setBrightness] = useState(100);
  const [contrast, setContrast] = useState(100);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isFullscreen, setIsFullscreen] = useState(false);
  const viewerRef = useRef(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError('');
      try {
        const { data } = await getPatients({ archived: 'false' });
        setPatients(data);
        if (data.length > 0) {
          const firstPatientId = String(data[0].id);
          setSelectedPatientId(firstPatientId);
        }
      } catch (requestError) {
        setError(requestError.response?.data?.detail || 'Unable to load patient records.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (!selectedPatientId) {
      setImages([]);
      setSelectedImageId('');
      return;
    }

    (async () => {
      try {
        const { data } = await getPatientImages(selectedPatientId);
        setImages(data);
        setSelectedImageId((current) => data.some((image) => String(image.id) === String(current)) ? current : (data[0]?.id ? String(data[0].id) : ''));
      } catch (requestError) {
        setError(requestError.response?.data?.detail || 'Unable to load patient images.');
      }
    })();
  }, [selectedPatientId]);

  const selectedImage = useMemo(
    () => images.find((image) => String(image.id) === String(selectedImageId)) || null,
    [images, selectedImageId],
  );

  const loadPatientImages = async (patientId) => {
    const { data } = await getPatientImages(patientId);
    setImages(data);
    if (data.length > 0) {
      setSelectedImageId(String(data[0].id));
    } else {
      setSelectedImageId('');
    }
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!selectedPatientId || !file) {
      setError('Select a patient and choose a PNG, JPG, or JPEG image to upload.');
      return;
    }

    const payload = new FormData();
    payload.append('file', file);
    payload.append('modality', uploadForm.modality);
    if (uploadForm.description.trim()) {
      payload.append('description', uploadForm.description.trim());
    }

    try {
      setSaving(true);
      setError('');
      await uploadPatientImage(selectedPatientId, payload);
      setNotice('Image uploaded successfully.');
      setFile(null);
      setUploadForm(defaultUpload);
      event.target.reset();
      await loadPatientImages(selectedPatientId);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || 'Unable to upload the image.');
    } finally {
      setSaving(false);
    }
  };

  const viewerUrl = selectedImage ? `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}${selectedImage.url}` : '';

  const handleFullscreen = async () => {
    if (!viewerRef.current) return;
    if (!document.fullscreenElement) {
      await viewerRef.current.requestFullscreen();
      setIsFullscreen(true);
    } else {
      await document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  return (
    <div className="imaging-page">
      <div className="page-header">
        <div>
          <p className="section-kicker">Medical imaging</p>
          <h1>Imaging workspace</h1>
        </div>
      </div>

      {notice && <div className="status-banner success">{notice}</div>}
      {error && <div className="status-banner error">{error}</div>}
      <div className="imaging-layout">
        <aside className="imaging-panel">
          <div className="panel-header-row">
            <h2>Patient imaging</h2>
          </div>

          <label className="field-label">
            Patient
            <select value={selectedPatientId} onChange={(event) => setSelectedPatientId(event.target.value)}>
              {patients.length === 0 ? <option value="">No patients available</option> : patients.map((patient) => (
                <option key={patient.id} value={patient.id}>{patient.name} ({patient.patient_id})</option>
              ))}
            </select>
          </label>

          <form onSubmit={handleUpload} className="upload-form">
            <label className="field-label">
              Image file
              <input type="file" accept=".png,.jpg,.jpeg,image/png,image/jpeg" onChange={(event) => setFile(event.target.files?.[0] || null)} />
            </label>

            <label className="field-label">
              Modality
              <select value={uploadForm.modality} onChange={(event) => setUploadForm((current) => ({ ...current, modality: event.target.value }))}>
                <option value="XRAY">X-ray</option>
                <option value="CT">CT</option>
                <option value="MRI">MRI</option>
                <option value="US">Ultrasound</option>
                <option value="PHOTO">Photo</option>
              </select>
            </label>

            <label className="field-label">
              Description
              <textarea value={uploadForm.description} onChange={(event) => setUploadForm((current) => ({ ...current, description: event.target.value }))} rows="3" placeholder="Procedure context or image notes" />
            </label>

            <button type="submit" className="primary-button" disabled={saving || !file}>
              {saving ? 'Uploading...' : 'Upload image'}
            </button>
          </form>

          <div className="image-list-panel">
            <h3>Image list</h3>
            {images.length === 0 ? (
              <div className="empty-state compact">No images uploaded for this patient.</div>
            ) : (
              <div className="image-list">
                {images.map((image) => (
                  <button key={image.id} type="button" className={selectedImageId === String(image.id) ? 'image-list-item active' : 'image-list-item'} onClick={() => setSelectedImageId(String(image.id))}>
                    <span className="image-list-title">{image.modality}</span>
                    <span className="image-list-meta">{image.file_name || 'uploaded-image'}</span>
                    <span className="image-list-meta">{image.description || 'No description provided.'}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </aside>

        <section className="viewer-panel">
          <div className="viewer-toolbar">
            <div className="toolbar-group">
              <label>Zoom <input type="range" min="0.5" max="3" step="0.1" value={zoom} onChange={(event) => setZoom(Number(event.target.value))} /></label>
              <label>Rotate <input type="range" min="0" max="360" step="5" value={rotation} onChange={(event) => setRotation(Number(event.target.value))} /></label>
              <label>Brightness <input type="range" min="40" max="180" step="1" value={brightness} onChange={(event) => setBrightness(Number(event.target.value))} /></label>
              <label>Contrast <input type="range" min="40" max="200" step="1" value={contrast} onChange={(event) => setContrast(Number(event.target.value))} /></label>
            </div>
            <button type="button" className="secondary-button" onClick={handleFullscreen}>
              {isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
            </button>
          </div>

          <div className="viewer-frame" ref={viewerRef}>
            {selectedImage && viewerUrl ? (
              <div className="viewer-surface">
                <img
                  src={viewerUrl}
                  alt={selectedImage.description || 'Selected patient image'}
                  style={{
                    transform: `translate(${pan.x}px, ${pan.y}px) rotate(${rotation}deg) scale(${zoom})`,
                    filter: `brightness(${brightness}%) contrast(${contrast}%)`,
                  }}
                  onMouseMove={(event) => {
                    if (event.buttons !== 1) return;
                    setPan((current) => ({ x: current.x + event.movementX, y: current.y + event.movementY }));
                  }}
                />
              </div>
            ) : (
              <div className="empty-state viewer-empty">No image selected. Upload an image to begin review.</div>
            )}
          </div>

          <div className="viewer-controls">
            <button type="button" className="secondary-button" onClick={() => setPan({ x: 0, y: 0 })}>Reset pan</button>
            <button type="button" className="secondary-button" onClick={() => setZoom(1)}>Reset zoom</button>
            <button type="button" className="secondary-button" onClick={() => setRotation(0)}>Reset rotate</button>
            <button type="button" className="secondary-button" onClick={() => setBrightness(100)}>Reset brightness</button>
            <button type="button" className="secondary-button" onClick={() => setContrast(100)}>Reset contrast</button>
          </div>

          <div className="viewer-meta">
            <strong>Prototype image viewer. Images are for demonstration only.</strong>
            <span>{selectedImage ? `${selectedImage.modality} • ${selectedImage.file_name || 'Uploaded image'}` : 'No study loaded'}</span>
          </div>
        </section>
      </div>
    </div>
  );
}
