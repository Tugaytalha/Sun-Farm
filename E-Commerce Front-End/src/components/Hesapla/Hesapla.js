import React, { useState, useEffect } from 'react';
import './ProductionForm.css'; // Stil dosyanız

const ProductionForm = () => {
  const [formData, setFormData] = useState({
    latitude: '',
    longitude: '',
    panel_area: '',
    panel_efficiency: '',
    panel_wattage: '',
    kwh_price: '',
  });

  const [calculationResult, setCalculationResult] = useState(null); // Sonucu saklamak için state
  const [message, setMessage] = useState('');

  // Geolocation API to get latitude and longitude
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData((prevData) => ({
            ...prevData,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          }));
        },
        (error) => {
          alert(`Error getting location: ${error.message}`);
        }
      );
    } else {
      alert('Geolocation is not supported by your browser');
    }
  }, []);

  // Form submission handler
  const handleSubmit = (event) => {
    event.preventDefault(); // Prevent page refresh

    const postData = {
      latitude: parseFloat(formData.latitude),
      longitude: parseFloat(formData.longitude),
      panel_area: parseFloat(formData.panel_area),
      panel_efficiency: formData.panel_efficiency ? parseFloat(formData.panel_efficiency) / 100 : null,
      panel_wattage: formData.panel_wattage ? parseFloat(formData.panel_wattage) : null,
      kwh_price: parseFloat(formData.kwh_price),
    };

    fetch('http://192.168.234.167:5000/predict_energy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        setCalculationResult(data); // Hesaplama sonucunu state'e kaydet
        setMessage('Hesaplama başarıyla tamamlandı!');
      })
      .catch((error) => {
        alert('Form gönderilirken bir hata oluştu!');
        console.error('Error:', error);
      });
  };

  // Form input change handler
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  return (
    <div className="production-form-container">
      <h2>Enerji Hesaplama</h2>
      <form onSubmit={handleSubmit}>
        <label htmlFor="latitude">Enlem:</label>
        <input
          type="text"
          id="latitude"
          name="latitude"
          value={formData.latitude}
          readOnly
        />

        <label htmlFor="longitude">Boylam:</label>
        <input
          type="text"
          id="longitude"
          name="longitude"
          value={formData.longitude}
          readOnly
        />

        <label htmlFor="panel_area">Panel Alanı (m²):</label>
        <input
          type="number"
          id="panel_area"
          name="panel_area"
          placeholder="Panel alanı gir"
          value={formData.panel_area}
          onChange={handleInputChange}
          required
        />

        <label htmlFor="panel_efficiency">Panel Verimliliği (%):</label>
        <input
          type="number"
          id="panel_efficiency"
          name="panel_efficiency"
          placeholder="Panel verimliliği gir"
          value={formData.panel_efficiency}
          onChange={handleInputChange}
        />

        <label htmlFor="panel_wattage">Panel Watt Gücü (Opsiyonel):</label>
        <input
          type="number"
          id="panel_wattage"
          name="panel_wattage"
          placeholder="Panel watt gücü gir (opsiyonel)"
          value={formData.panel_wattage}
          onChange={handleInputChange}
        />

        <label htmlFor="kwh_price">kWh Fiyatı:</label>
        <input
          type="number"
          id="kwh_price"
          name="kwh_price"
          placeholder="kWh fiyatı gir"
          value={formData.kwh_price}
          onChange={handleInputChange}
          required
        />

        <button type="submit">Hesapla</button>
      </form>

      {message && <p>{message}</p>}
      {calculationResult && (
        <div className="calculation-result">
          <h3>Hesaplama Sonuçları:</h3>
          <p>Aylık Enerji Üretimi: {calculationResult.monthly_energy_output_kWh} kWh</p>
          <p>Aylık Kar: {calculationResult.monthly_profit} TL</p>
          <p>Yıllık Kar: {calculationResult.yearly_profit} TL</p>
          <p>Amorti Süresi (Ay): {calculationResult.break_even_month} Ay</p>
          <p>Amorti Süresi (Yıl): {calculationResult.break_even_year} Yıl</p>
          {/* Display chart if present */}
          {calculationResult.chart && (
            <div className="chart-container">
              <h4>Maliyet Analizi</h4>
              <div dangerouslySetInnerHTML={{ __html: calculationResult.chart }} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ProductionForm;
