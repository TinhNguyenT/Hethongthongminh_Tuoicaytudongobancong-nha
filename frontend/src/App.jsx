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
  Activity
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
            <h3>Điều khiển máy bơm</h3>
            <div className={`pump-disk ${current.pump_status ? 'running' : ''}`}>
              <Power size={32} />
              <div className="glow"></div>
            </div>
            <div className="pump-info">
              <span className="status-label">{current.pump_status ? 'ĐANG BẬT' : 'ĐANG TẮT'}</span>
              <p className="reason">{current.pump_status ? "Đã kích hoạt tưới nước" : "Độ ẩm đất tối ưu"}</p>
            </div>
            <div className="manual-switch">
              <span>Chế độ thủ công</span>
              <button
                className={`toggle ${manualMode ? 'on' : ''}`}
                onClick={() => setManualMode(!manualMode)}
              >
                <div className="ball"></div>
              </button>
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
          grid-template-columns: repeat(4, 1fr);
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
