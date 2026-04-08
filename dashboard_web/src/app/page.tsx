"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wsUrl, setWsUrl] = useState("");

  useEffect(() => {
    // For local network connections (phone), detect if we're on localhost
    let host = window.location.hostname;

    // If connecting from localhost, use localhost. Otherwise use the actual hostname/IP
    const url = `ws://${host}:8001/ws`;
    setWsUrl(url);

    const socket = new WebSocket(url);

    socket.onopen = () => {
      setConnected(true);
      setError(null);
    };

    socket.onmessage = (event) => {
      const telemetry = JSON.parse(event.data);
      setData(telemetry);
    };

    socket.onerror = (err) => {
      setError("FALHA NA CONEXÃO. VERIFIQUE O FIREWALL DA PORTA 8001.");
      setConnected(false);
    };

    socket.onclose = () => setConnected(false);

    // --- WAKE LOCK API ---
    // Mantém a tela ligada no celular
    let wakeLock: any = null;
    const requestWakeLock = async () => {
      try {
        if ("wakeLock" in navigator) {
          wakeLock = await (navigator as any).wakeLock.request("screen");
        }
      } catch (err: any) {
        console.warn(`WakeLock Error: ${err.name}, ${err.message}`);
      }
    };

    requestWakeLock(); // FIXME [ ]: No meu celular, não está chamando a função, então a tela apaga.

    const handleVisibilityChange = () => {
      if (wakeLock !== null && document.visibilityState === "visible") {
        requestWakeLock();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    // QUESTION [ ]: Este visibilitychange é adaptado para navegadores mobile?

    return () => {
      socket.close();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      if (wakeLock) wakeLock.release();
    };
  }, []);

  if (!data) {
    return (
      <div className="flex flex-col h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-400 font-mono p-4 text-center">
        <div className="mb-4 text-cyan-400 animate-pulse text-3xl font-black drop-shadow-lg">
          ⚡ ARGENTUM DASHBOARD
        </div>
        <div className="text-sm mb-4 text-slate-300">
          {connected ? "AGUARDANDO DADOS..." : "CONECTANDO..."}
        </div>
        {connected && (
          <div className="inline-block w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2 mb-4"></div>
        )}
        <div className="text-[11px] text-slate-500 bg-slate-900 p-3 rounded-lg border border-slate-700 font-semibold max-w-sm">
          WS: {wsUrl}
        </div>
        {error && (
          <div className="mt-6 text-red-400 text-[11px] bg-red-950/30 p-4 border border-red-900/50 rounded-lg max-w-xs">
            ⚠️ {error}
          </div>
        )}
      </div>
    );
  }

  const rpmPct = (data.rpm / data.max_rpm) * 100;
  const steerNorm = (data.steer / 450) * 100;

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-4 md:p-6 font-mono overflow-x-hidden">
      {/* Top Bar - Header Info */}
      <div className="mb-4 md:mb-6 grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-3 md:p-4 rounded-lg shadow-xl">
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1">
            Driver
          </p>
          <p className="text-sm md:text-lg font-black text-cyan-400 truncate">
            {data.pilot}
          </p>
        </div>
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-3 md:p-4 rounded-lg shadow-xl">
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1">
            Car
          </p>
          <p className="text-sm md:text-lg font-black text-purple-400 truncate">
            {data.car}
          </p>
        </div>
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-3 md:p-4 rounded-lg shadow-xl">
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1">
            Source
          </p>
          <p className="text-[10px] md:text-xs font-bold text-emerald-400 truncate">
            {data.source}
          </p>
        </div>
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-3 md:p-4 rounded-lg shadow-xl">
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1">
            Time
          </p>
          <p className="text-xs md:text-sm font-black text-orange-400">
            {data.timestamp}
          </p>
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-12 gap-3 md:gap-4 mb-4 md:mb-6">
        {/* Speed (Large) */}
        <div className="col-span-6 md:col-span-4 bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-cyan-500/50 p-4 md:p-8 rounded-xl shadow-2xl flex flex-col items-center md:items-start justify-center">
          <p className="text-[10px] md:text-xs text-slate-500 uppercase tracking-widest font-bold mb-1 md:mb-3">
            Speed
          </p>
          <div className="flex items-baseline gap-1 md:gap-3">
            <span className="text-4xl md:text-7xl font-black text-cyan-400">
              {data.speed}
            </span>
            <span className="text-xs md:text-xl text-slate-500 font-bold">
              KM/H
            </span>
          </div>
        </div>

        {/* Gear (Large) */}
        <div className="col-span-6 md:col-span-4 bg-gradient-to-br from-slate-800 to-slate-900 border-2 border-purple-500/50 p-4 md:p-8 rounded-xl shadow-2xl flex flex-col items-center justify-center">
          <p className="text-[10px] md:text-xs text-slate-500 uppercase tracking-widest font-bold mb-1 md:mb-4">
            Gear
          </p>
          <span className="text-5xl md:text-8xl font-black text-purple-400">
            {data.gear}
          </span>
        </div>

        {/* Packet Info */}
        <div className="col-span-12 md:col-span-4 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-4 md:p-6 rounded-xl shadow-xl flex flex-col justify-center text-center md:text-left">
          <p className="text-[10px] md:text-xs text-slate-500 uppercase tracking-widest font-bold mb-1 md:mb-2">
            Packet
          </p>
          <p className="text-xl md:text-3xl font-black text-emerald-400">
            {data.packet}
          </p>
        </div>
      </div>

      {/* RPM Section */}
      <div className="mb-4 md:mb-6 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-4 md:p-6 rounded-xl shadow-xl">
        <div className="flex justify-between items-end mb-2 md:mb-4">
          <div>
            <p className="text-[10px] md:text-xs text-slate-500 uppercase tracking-widest font-bold mb-1 md:mb-2">
              RPM
            </p>
            <p className="text-2xl md:text-4xl font-black text-white">
              {data.rpm.toLocaleString()}
            </p>
          </div>
          <div className="text-right">
            <p className="text-[10px] md:text-xs text-slate-500 uppercase tracking-widest font-bold mb-1">
              Max RPM
            </p>
            <p className="text-lg md:text-2xl font-black text-slate-400">
              {data.max_rpm.toLocaleString()}
            </p>
          </div>
        </div>

        {/* RPM Progress Bar */}
        <div className="w-full h-8 md:h-10 bg-slate-700 rounded-lg overflow-hidden border border-slate-600 p-1">
          <div
            className={`h-full rounded transition-all duration-100 font-bold text-[10px] md:text-xs text-white flex items-center justify-center ${
              rpmPct > 95
                ? "bg-gradient-to-r from-red-600 to-red-500 animate-pulse"
                : rpmPct > 85
                  ? "bg-gradient-to-r from-red-600 to-red-500"
                  : rpmPct > 60
                    ? "bg-gradient-to-r from-yellow-600 to-yellow-500"
                    : "bg-gradient-to-r from-green-600 to-green-500"
            }`}
            style={{ width: `${Math.min(rpmPct, 100)}%` }}
          >
            {rpmPct > 10 && `${rpmPct.toFixed(1)}%`}
          </div>
        </div>
      </div>

      {/* Pedals Section */}
      <div className="mb-4 md:mb-6 grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
        <PedalCard
          label="Throttle"
          value={data.throttle}
          color="from-green-600 to-green-500"
          icon="⬆️"
        />
        <PedalCard
          label="Brake"
          value={data.brake}
          color="from-red-600 to-red-500"
          icon="⬇️"
        />
        <PedalCard
          label="Clutch"
          value={data.clutch}
          color="from-orange-600 to-orange-500"
          icon="🔄"
        />
      </div>

      {/* Steering Section */}
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-4 md:p-6 rounded-xl shadow-xl">
        <div className="flex justify-between items-center mb-4">
          <div>
            <p className="text-[10px] md:text-xs text-slate-500 uppercase tracking-widest font-bold mb-1">
              Steering Angle
            </p>
            <p className="text-2xl md:text-4xl font-black text-blue-400">
              {data.steer.toFixed(1)}°
            </p>
          </div>
          <div className="text-right hidden md:block">
            <p className="text-[10px] md:text-xs text-slate-500 uppercase tracking-widest font-bold">
              Range: -450° to +450°
            </p>
          </div>
        </div>

        {/* Steering Visualizer */}
        <div className="relative h-10 md:h-12 bg-slate-700 rounded-lg border border-slate-600 overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center">
            {/* Center line */}
            <div className="absolute w-0.5 h-full bg-slate-500 opacity-50"></div>
            {/* Tick marks */}
            {[-3, -2, -1, 0, 1, 2, 3].map((tick) => (
              <div
                key={tick}
                className="absolute w-0.5 h-1/3 bg-slate-600 opacity-30"
                style={{
                  left: `${50 + (tick * 100) / 6}%`,
                  top: "50%",
                  transform: "translateY(-50%)",
                }}
              />
            ))}
            {/* Indicator */}
            <div
              className="absolute w-1 h-12 md:h-16 bg-blue-500 rounded shadow-lg transition-all duration-75"
              style={{
                left: `${Math.max(0, Math.min(100, 50 + steerNorm / 2))}%`,
                transform: "translateX(-50%)",
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Connection Status Footer */}
      <div className="mt-4 md:mt-6 text-center text-[10px] text-slate-500 border-t border-slate-700 pt-3 md:pt-4">
        <p>
          🟢 Connected <span className="hidden md:inline">| WS @ {wsUrl}</span>
        </p>
        <p className="md:hidden mt-1 truncate opacity-50">WS: {wsUrl}</p>
      </div>
    </main>
  );
}

function PedalCard({
  label,
  value,
  color,
  icon,
}: {
  label: string;
  value: number;
  color: string;
  icon: string;
}) {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 p-4 md:p-6 rounded-xl shadow-xl">
      <div className="flex justify-between items-center mb-2 md:mb-4">
        <div>
          <p className="text-[10px] md:text-xs text-slate-500 uppercase tracking-widest font-bold">
            {label}
          </p>
          <p className="text-xl md:text-3xl font-black text-white mt-1">
            {value.toFixed(1)}
          </p>
        </div>
        <span className="text-2xl md:text-3xl">{icon}</span>
      </div>
      <div className="h-4 md:h-6 bg-slate-700 rounded-lg overflow-hidden border border-slate-600 p-1">
        <div
          className={`h-full rounded bg-gradient-to-r ${color} transition-all duration-75`}
          style={{ width: `${value}%` }}
        />
      </div>
      <p className="text-[9px] md:text-[10px] text-slate-600 mt-1 md:mt-2 text-right font-semibold">
        {value.toFixed(1)}%
      </p>
    </div>
  );
}
