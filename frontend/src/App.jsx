import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Thermometer,
  Droplets,
  CloudRain,
  Cpu,
  Power,
  Timer,
  History,
  CircleGauge,
  Activity,
  Waves,
  AlertTriangle,
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
  Legend
);

const API_URL = 'http://localhost:5000/api/stats';

function App() {
  const [data, setData] = useState(null);
  const [manualMode, setManualMode] = useState(false);
  const [localTime, setLocalTime] = useState(new Date());

  useEffect(() => {
    // 1. Đồng hồ thời gian thực (nhảy từng giây)
    const clockInterval = setInterval(() => {
      setLocalTime(new Date());
    }, 1000);

    // 2. Lấy dữ liệu từ Backend (5s/lần)
    const fetchData = async () => {
      try {
        const res = await axios.get(API_URL);
        setData(res.data);
      } catch (err) {
        console.error("Fetch error:", err);
      }
    };

    fetchData();
    const dataInterval = setInterval(fetchData, 5000);

    return () => {
      clearInterval(clockInterval);
      clearInterval(dataInterval);
    };
  }, []);

  if (!data) return <div className="loading">Đang kết nối Bộ não AI...</div>;

  const { current, history } = data;

  // Logic xác định trạng thái đất
  const getSoilStatus = (moisture) => {
    const val = moisture * 100;
    if (val < 25) return { label: 'KHÔ ĐÉT', class: 'danger' };
    if (val < 45) return { label: 'KHÔ', class: 'danger' };
    if (val > 80) return { label: 'ẨM', class: 'info' };
    return { label: 'TỐI ƯU', class: 'success' };
  };

  const soilStatus = getSoilStatus(current.soil_moisture);

  // Logic xác định trạng thái nước
  const getWaterStatus = (level) => {
    if (level < 15) return { label: 'SẮP CẠN', class: 'danger' };
    if (level < 40) return { label: 'THẤP', class: 'warning' };
    return { label: 'ĐẦY', class: 'success' };
  };

  const waterStatus = getWaterStatus(current.water_level ?? 100);

  // Format thời gian hiển thị tiếng Việt
  const timeStr = localTime.toLocaleTimeString('vi-VN', { hour12: false });
  const dateStr = localTime.toLocaleDateString('vi-VN', {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric'
  }).toUpperCase();

  const chartData = {
    labels: history.map(h => h.timestamp),
    datasets: [
      {
        fill: true,
        label: 'Độ ẩm đất',
        data: history.map(h => h.soil_moisture * 100),
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.05)',
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#10b981',
        pointBorderColor: '#0a0a0c',
        pointBorderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: '#1e293b',
        titleFont: { family: 'Inter' },
        bodyFont: { family: 'Inter' }
      }
    },
    scales: {
      y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#64748b' } },
      x: { grid: { display: false }, ticks: { display: false } }
    }
  };

  return (
    <div className="layout">
      {/* Header */}
      <header className="header">
        <div className="brand">
          <div className="icon-box"><Cpu size={24} color="#3b82f6" /></div>
          <div>
            <h1>Hệ Thống Tưới Cây <span className="ai-badge">AI MLP</span></h1>
            <p>Trí tuệ nhân tạo bảo vệ cây trồng</p>
          </div>
        </div>
        <div className="time-box">
          <h2>{timeStr}</h2>
          <p>{dateStr}</p>
        </div>
      </header>

      {/* Main Grid */}
      <main className="grid">
        {/* Sensors Area */}
        <div className="sensor-grid">
          <Card
            title="Nhiệt độ"
            value={current.air_temp}
            unit="°C"
            icon={<Thermometer color="#f43f5e" size={20} />}
          />
          <Card
            title="Độ ẩm khí"
            value={current.air_humidity}
            unit="%"
            icon={<Droplets color="#3b82f6" size={20} />}
          />
          <Card
            title="Lượng mưa"
            value={current.rain_mm}
            unit=" mm"
            icon={<CloudRain color="#94a3b8" size={20} />}
          />
          <Card
            title="Độ ẩm đất"
            value={(current.soil_moisture * 100).toFixed(1)}
            unit="%"
            icon={<Activity color="#10b981" size={20} />}
            status={soilStatus}
            isAlert={current.soil_moisture * 100 < 45}
          />
        </div>

        {/* Control Area */}
        <div className="controls">
          <div className="pump-panel">
            {/* Visual Tank Background */}
            <div 
              className="tank-background" 
              style={{ height: `${current.water_level ?? 100}%` }}
            >
              <div className="water-wave"></div>
            </div>

            <div className="pump-content">
              <div className="pump-header">
                <h3>Điều khiển máy bơm</h3>
                <div className="water-badge">
                  <Waves size={14} />
                  <span>{Math.round(current.water_level ?? 100)}%</span>
                </div>
              </div>

              <div className={`pump-disk ${current.pump_status ? 'running' : ''}`}>
                <Power size={32} />
                <div className="glow"></div>
              </div>

              <div className="pump-info">
                <span className="status-label">{current.pump_status ? 'ĐANG BẬT' : 'ĐANG TẮT'}</span>
                {(current.water_level ?? 100) < 10 ? (
                  <p className="reason warning-text">
                    <AlertTriangle size={12} style={{display:'inline', marginRight:'4px'}}/>
                    Hết nước - Đã ngắt bơm
                  </p>
                ) : (current.source || '').includes('CHÂM') ? (
                  <p className="reason" style={{color:'#3b82f6'}}>Đang nạp nước vào bồn...</p>
                ) : (
                  <p className="reason">{current.pump_status ? "Đang tưới cây..." : "Trạng thái ổn định"}</p>
                )}
              </div>

              <div className="manual-switch">
                <span>Tham số AI</span>
                <button
                  className={`toggle ${manualMode ? 'on' : ''}`}
                  onClick={() => setManualMode(!manualMode)}
                >
                  <div className="ball"></div>
                </button>
              </div>
            </div>
          </div>

          {/* Chart Area */}
          <div className="chart-panel">
            <div className="chart-header">
              <History size={18} />
              <h3>Lịch sử độ ẩm đất (Real-time)</h3>
            </div>
            <div className="chart-wrapper">
              <Line data={chartData} options={chartOptions} />
            </div>
          </div>
        </div>
      </main>

      <style jsx="true">{`
        .layout {
          height: 100vh;
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 20px;
          max-width: 1400px;
          margin: 0 auto;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px 0;
        }

        .brand { display: flex; gap: 15px; align-items: center; }
        .icon-box { background: #1a1a1e; padding: 12px; border-radius: 12px; border: 1px solid #242428; }
        h1 { font-size: 1.4rem; font-weight: 700; display: flex; align-items: center; gap: 10px; }
        .ai-badge { font-size: 0.7rem; background: #3b82f633; color: #3b82f6; padding: 2px 8px; border-radius: 4px; border: 1px solid #3b82f655; }
        p { color: #64748b; font-size: 0.85rem; }

        .time-box { text-align: right; }
        .time-box h2 { font-size: 1.8rem; font-weight: 700; }

        .grid {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 20px;
          min-height: 0;
        }

        .sensor-grid {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 20px;
        }

        .controls {
          flex: 1;
          display: grid;
          grid-template-columns: 350px 1fr;
          gap: 20px;
          min-height: 0;
        }

        .card-component {
          background: var(--bg-card);
          padding: 20px;
          border-radius: 16px;
          border: 1px solid var(--border-subtle);
          display: flex;
          gap: 15px;
          align-items: center;
          position: relative;
          transition: all 0.3s;
        }
        
        .card-component.alert-danger {
          border-color: #f43f5e;
          background: rgba(244, 63, 94, 0.03);
          animation: simple-flash 0.8s infinite alternate;
        }

        @keyframes simple-flash {
          0% { border-color: #f43f5e; box-shadow: 0 0 0px transparent; }
          100% { border-color: #f43f5e; box-shadow: 0 0 15px rgba(244, 63, 94, 0.4); }
        }

        .card-status {
          position: absolute;
          top: 15px;
          right: 15px;
          font-size: 0.65rem;
          font-weight: 700;
          padding: 3px 8px;
          border-radius: 10px;
        }
        .card-status.danger { background: #f43f5e22; color: #f43f5e; }
        .card-status.warning { background: #f59e0b22; color: #f59e0b; }
        .card-status.info { background: #3b82f622; color: #3b82f6; }
        .card-status.success { background: #10b98122; color: #10b981; }

        .pump-panel {
          background: var(--bg-card);
          border-radius: 16px;
          border: 1px solid var(--border-subtle);
          padding: 24px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
        }

        .pump-disk {
          width: 120px;
          height: 120px;
          background: #1a1a1e;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #334155;
          position: relative;
          transition: all 0.5s;
        }
        .pump-disk.running { color: #3b82f6; box-shadow: 0 0 30px #3b82f633; }
        .pump-disk.running::before {
          content: ''; position: absolute; width: 100%; height: 100%;
          border-radius: 50%; border: 2px solid #3b82f6;
          animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
        }

        @keyframes ping { 75%, 100% { transform: scale(1.6); opacity: 0; } }

        .pump-info { text-align: center; }
        .status-label { font-weight: 700; font-size: 1.1rem; }
        .reason { font-size: 0.8rem; color: #64748b; margin-top: 5px; }

        .chart-panel {
          background: var(--bg-card);
          border-radius: 16px;
          border: 1px solid var(--border-subtle);
          padding: 24px;
          display: flex;
          flex-direction: column;
        }
        .chart-header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; color: #64748b; }
        .chart-wrapper { flex: 1; min-height: 0; }

        .manual-switch { 
          width: 100%; margin-top: auto; 
          background: #0a0a0c88; padding: 15px; border-radius: 12px;
          display: flex; justify-content: space-between; align-items: center;
        }

        .toggle { width: 50px; height: 26px; border-radius: 15px; background: #334155; border: none; cursor: pointer; position: relative; transition: 0.3s; }
        .toggle.on { background: #3b82f6; }
        .ball { width: 20px; height: 20px; background: white; border-radius: 50%; position: absolute; left: 3px; top: 3px; transition: 0.3s; }
        .toggle.on .ball { left: 27px; }

        .warning-text { color: #f59e0b !important; }

        /* ===================== PUMP PANEL AS TANK ===================== */
        .pump-panel {
          background: #0a0a0c;
          border-radius: 24px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          position: relative;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          min-height: 420px;
          box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.5);
        }

        .tank-background {
          position: absolute;
          bottom: 0;
          left: 0;
          width: 100%;
          background: linear-gradient(180deg, #1d4ed8 0%, #1e3a8a 100%);
          transition: height 1.5s cubic-bezier(0.19, 1, 0.22, 1);
          z-index: 1;
          box-shadow: 0 -4px 15px rgba(59, 130, 246, 0.5);
        }

        /* Nắp bồn hoặc viền trên */
        .tank-background::after {
          content: "";
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 4px;
          background: rgba(255, 255, 255, 0.4);
          box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
        }

        .water-wave {
          position: absolute;
          top: -20px;
          left: 0;
          width: 200%;
          height: 25px;
          background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none"><path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5,73.84-4.36,147.54,16.88,218.2,35.26,69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113,14.29,1200,52.47V0Z" fill="%231d4ed8" opacity="0.6"></path></svg>');
          animation: wave-slide 4s linear infinite;
        }

        @keyframes wave-slide {
          from { transform: translateX(0); }
          to { transform: translateX(-50%); }
        }

        .pump-content {
          position: relative;
          z-index: 2;
          padding: 24px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
          height: 100%;
          background: linear-gradient(180deg, rgba(10, 10, 12, 0) 0%, rgba(10, 10, 12, 0.6) 100%);
          backdrop-filter: blur(1px); /* Nhìn xuyên qua nước */
        }

        .pump-header {
          width: 100%;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .water-badge {
          display: flex;
          align-items: center;
          gap: 6px;
          background: rgba(255, 255, 255, 0.1);
          padding: 6px 12px;
          border-radius: 12px;
          color: #fff;
          font-weight: 700;
          font-size: 0.9rem;
          border: 1px solid rgba(255, 255, 255, 0.2);
          backdrop-filter: blur(4px);
        }

        .pump-disk {
          width: 140px;
          height: 140px;
          background: rgba(15, 15, 20, 0.9);
          border: 3px solid rgba(255, 255, 255, 0.05);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #475569;
          position: relative;
          transition: all 0.5s;
          margin: 10px 0;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        }
        .pump-disk.running { color: #3b82f6; box-shadow: 0 0 40px rgba(59, 130, 246, 0.4); border-color: #3b82f6; }

        .loading { height: 100vh; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 500; color: #3b82f6; }
      `}</style>
    </div>
  );
}


function Card({ title, value, unit, icon, status, isAlert }) {
  return (
    <div className={`card-component ${isAlert ? 'alert-danger' : ''}`}>
      {status && <span className={`card-status ${status.class}`}>{status.label}</span>}
      <div className="icon-box" style={{ padding: '10px' }}>{icon}</div>
      <div>
        <p>{title}</p>
        <div style={{ fontSize: '1.6rem', fontWeight: 700 }}>
          {value}<span style={{ fontSize: '0.9rem', color: '#64748b', marginLeft: '4px' }}>{unit}</span>
        </div>
      </div>
    </div>
  );
}

export default App;
