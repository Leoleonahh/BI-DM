import React, { useEffect, useState, useRef } from "react";
import CO2Chart from "./CO2Chart";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  // =========================
  // State
  // =========================
  const [countries, setCountries] = useState([]);
  const [country, setCountry] = useState("");
  const [year, setYear] = useState(2025);

  const [history, setHistory] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [chartData, setChartData] = useState([]);

  const [performance, setPerformance] = useState(null);

  const [loadingHistory, setLoadingHistory] = useState(false);
  const [loadingPredict, setLoadingPredict] = useState(false);
  const [loadingPerformance, setLoadingPerformance] = useState(false);

  // =========================
  // PDF Ref
  // =========================
  const pdfRef = useRef();

  // =========================
  // Load countries
  // =========================
  const fetchCountries = async () => {
    try {
      const res = await fetch(`${API_BASE}/countries`);
      const data = await res.json();

      if (data.countries && data.countries.length > 0) {
        setCountries(data.countries);
        setCountry(data.countries[0]);
      }
    } catch (err) {
      console.error("Countries error:", err);
    }
  };

  // =========================
  // Load historical data
  // =========================
  const fetchHistory = async (selectedCountry) => {
    if (!selectedCountry) return;

    setLoadingHistory(true);
    try {
      const res = await fetch(
        `${API_BASE}/history/${selectedCountry}?start_year=2000`
      );
      const data = await res.json();
      setHistory(data.records || []);
    } catch (err) {
      console.error("History error:", err);
    }
    setLoadingHistory(false);
  };

  // =========================
  // Predict CO2
  // =========================
  const fetchPrediction = async () => {
    setLoadingPredict(true);
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ country, year })
      });

      const data = await res.json();
      setPrediction(data.predicted_co2);
    } catch (err) {
      console.error("Prediction error:", err);
    }
    setLoadingPredict(false);
  };

  // =========================
  // Load model performance
  // =========================
  const fetchPerformance = async () => {
    setLoadingPerformance(true);
    try {
      const res = await fetch(`${API_BASE}/model/performance`);
      const data = await res.json();
      setPerformance(data);
    } catch (err) {
      console.error("Performance error:", err);
    }
    setLoadingPerformance(false);
  };

  // =========================
  // Export PDF
  // =========================
  const exportPDF = async () => {
    const element = pdfRef.current;

    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true
    });

    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();

    const imgWidth = pageWidth;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    let heightLeft = imgHeight;
    let position = 0;

    pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    pdf.save(`CO2_Report_${country}_${year}.pdf`);
  };

  // =========================
  // Initial load
  // =========================
  useEffect(() => {
    fetchCountries();
    fetchPerformance();
  }, []);

  // โหลด history เมื่อ country เปลี่ยน
  useEffect(() => {
    if (country) {
      fetchHistory(country);
      setPrediction(null);
    }
  }, [country]);

  // =========================
  // Prepare chart data
  // =========================
  useEffect(() => {
    if (!history.length) return;

    const data = history.map(row => ({
      year: row.year,
      actual: row.co2,
      predicted: null
    }));

    if (prediction !== null) {
      data.push({
        year,
        actual: null,
        predicted: prediction
      });
    }

    setChartData(data);
  }, [history, prediction, year]);

  // =========================
  // Render
  // =========================
  return (
    <div className="container" ref={pdfRef}>

      {/* Header */}
      <header className="header">
        <h1>CO₂ Emissions Forecast Dashboard</h1>
      </header>

      {/* Filters */}
      <section className="filters">
        <select
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          disabled={!countries.length}
        >
          {countries.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>

        <input
          type="number"
          min="1900"
          max="2100"
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
        />

        <button onClick={fetchPrediction} disabled={loadingPredict || !country}>
          {loadingPredict ? "Predicting..." : "Predict"}
        </button>


      </section>

      {/* Chart */}
      <section className="chart-section">
        <h2>CO₂ Emissions: Actual vs Predicted</h2>
        <CO2Chart data={chartData} />
      </section>

      {/* Output + Performance */}
      <section className="middle-section">

        <div className="performance">
          <h3>Model Output</h3>
          <div className="metrics">
            Predicted CO₂ (MtCO₂):{" "}
            <strong>{prediction ?? "-"}</strong>
          </div>
        </div>

        <div className="performance">
          <h3>Model Performance</h3>
          {loadingPerformance ? (
            <p>Loading...</p>
          ) : performance ? (
            <div className="metrics">
              <div>RMSE: <strong>{performance.rmse}</strong></div>
              <div>R²: <strong>{performance.r2}</strong></div>
              <div>Training Rows: <strong>{performance.rows}</strong></div>
            </div>
          ) : (
            <p>No performance data</p>
          )}
        </div>

      </section>

      {/* Table */}
      <section className="table-section">
        <h3>Historical Emissions (MtCO₂)</h3>

        {loadingHistory ? (
          <p>Loading...</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Year</th>
                <th>Actual CO₂</th>
              </tr>
            </thead>
            <tbody>
              {history.slice(-10).map((row, idx) => (
                <tr key={idx}>
                  <td>{row.year}</td>
                  <td>{row.co2}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
      
        <button onClick={exportPDF}>
          📄 Export PDF
        </button>

    </div>
  );
}

export default App;