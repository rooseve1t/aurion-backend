import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Zap, Thermometer, Lock, Camera } from 'lucide-react';
import { JarvisHologram3D } from '@/components/Jarvis/Hologram3D';
import { smarthomeService } from '@/services/smarthome';
import { useToast } from '@/hooks/useToast';
import type { Device } from '@/types';
import styles from './ARPage.module.css';

export const ARPage: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    const loadDevices = async () => {
      try {
        const data = await smarthomeService.listDevices();
        setDevices(data);
      } catch {
        toast.error('Не удалось загрузить список устройств');
      } finally {
        setLoading(false);
      }
    };
    loadDevices();
  }, [toast]);

  const toggleDevice = async (device: Device) => {
    const isCurrentlyOn = device.state?.power || false;
    const command = isCurrentlyOn ? 'turn_off' : 'turn_on';
    try {
      await smarthomeService.control(device.id, command);
      setDevices(prev => prev.map(d => 
        d.id === device.id 
          ? { ...d, state: { ...d.state, power: !isCurrentlyOn } }
          : d
      ));
      toast.success(`${device.name} ${!isCurrentlyOn ? 'включен' : 'выключен'}`);
    } catch {
      toast.error('Ошибка управления устройством');
    }
  };

  return (
    <div className={styles.page}>
      <button className={styles.backBtn} onClick={() => navigate(-1)}>
        <ArrowLeft size={14} /> Назад
      </button>

      <div className={styles.hud}>
        <h1 className={styles.title}>AURION OS — AR HUB</h1>
        <p className={styles.subtitle}>WebXR / AR Smart Home Control — THE GOLDEN STANDARD</p>
      </div>

      <div className={styles.deviceStatus}>
        <div style={{ fontSize: '10px', color: 'var(--cyan)', marginBottom: '10px', letterSpacing: '1px' }}>
          УСТРОЙСТВА ОНЛАЙН
        </div>
        {loading ? (
          <div style={{ fontSize: '10px', color: '#555' }}>ЗАГРУЗКА...</div>
        ) : (
          devices.map(device => (
            <div key={device.id} className={styles.deviceItem}>
              <span>{device.name}</span>
              <div className={`${styles.dot} ${device.state?.power ? styles.dotOn : styles.dotOff}`} />
            </div>
          ))
        )}
      </div>

      <div className={styles.arOverlay}>
        {isScanning && (
          <div className={styles.scanLine} style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '2px',
            background: 'var(--cyan)',
            boxShadow: '0 0 15px var(--cyan)',
            zIndex: 10,
            animation: 'scan 2s linear infinite'
          }} />
        )}
        <JarvisHologram3D 
          height="100vh" 
          width="100%" 
          enableAR={true} 
          emotion={devices.some(d => d.state?.power) ? 'happy' : 'neutral'}
        />
      </div>

      <div className={styles.controls}>
        {devices.slice(0, 3).map(device => (
          <button 
            key={device.id}
            className={`btn ${device.state?.power ? 'btn-cyan' : 'btn-ghost'}`}
            style={{ fontSize: '10px', padding: '8px 12px' }}
            onClick={() => toggleDevice(device)}
          >
            {device.device_type === 'light' && <Zap size={14} />}
            {device.device_type === 'thermostat' && <Thermometer size={14} />}
            {device.device_type === 'lock' && <Lock size={14} />}
            <span style={{ marginLeft: '4px' }}>{device.name}</span>
          </button>
        ))}
        <button 
          className={`btn ${isScanning ? 'btn-purple' : 'btn-ghost'}`}
          style={{ fontSize: '10px', padding: '8px 12px' }}
          onClick={() => {
            setIsScanning(!isScanning);
            toast.info(isScanning ? 'Сканирование остановлено' : 'Режим сканирования активен');
          }}
        >
          <Camera size={14} />
          <span style={{ marginLeft: '4px' }}>{isScanning ? 'СТОП' : 'СКАНЕР'}</span>
        </button>
      </div>

      <div style={{ position: 'absolute', bottom: '15px', right: '20px', color: 'rgba(0, 243, 255, 0.3)', fontSize: '8px', fontFamily: 'monospace' }}>
        v2.2.0-AR / STAGE_22
      </div>
    </div>
  );
};
