import React, { useState, useEffect } from 'react';
import { Card, Button, Badge, Switch, Progress } from '@/components/ui';
import { Shield, Lock, Unlock, Eye } from 'lucide-react';

interface VPNStatus {
  status: 'disconnected' | 'connecting' | 'connected' | 'reconnecting' | 'error';
  connected: boolean;
  connection_id?: string;
  server?: {
    name: string;
    country: string;
    city: string;
  };
  protocol?: string;
  ip_address?: string;
  obfuscation_level?: string;
  stealth_mode?: boolean;
  kill_switch?: boolean;
  metrics?: {
    latency_ms: number;
    download_speed_mbps: number;
    upload_speed_mbps: number;
    packet_loss: number;
    jitter_ms: number;
    quality_score: number;
  };
  uptime?: number;
  bytes_sent?: number;
  bytes_received?: number;
}

interface VPNServer {
  id: string;
  name: string;
  country: string;
  city: string;
  ip_address: string;
  protocol: string;
  status: string;
  load: number;
  speed_mbps: number;
  latency_ms: number;
  obfuscation_support: boolean;
  stealth_support: boolean;
  is_dedicated: boolean;
  is_residential: boolean;
  is_mobile: boolean;
}

interface BlockadeDetection {
  blockade_type: string;
  confidence_score: number;
  blocked_protocols: string[];
  working_protocols: string[];
  recommended_protocol: string;
  detection_time: string;
  target_host: string;
}

const AurionShieldVPN: React.FC = () => {
  const [status, setStatus] = useState<VPNStatus | null>(null);
  const [servers, setServers] = useState<VPNServer[]>([]);
  const [selectedServer, setSelectedServer] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [blockadeDetection, setBlockadeDetection] = useState<BlockadeDetection | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [autoProtocolSwitch, setAutoProtocolSwitch] = useState(true);
  const [killSwitch, setKillSwitch] = useState(true);
  const [dnsProtection, setDnsProtection] = useState(true);
  const [ipv6Protection, setIpv6Protection] = useState(true);

  // 🛡️ Получение статуса VPN
  useEffect(() => {
    fetchVPNStatus();
    fetchServers();
    const interval = setInterval(fetchVPNStatus, 5000); // Обновляем каждые 5 секунд
    return () => clearInterval(interval);
  }, []);

  const fetchVPNStatus = async () => {
    try {
      const response = await fetch('/api/v1/vpn/status');
      const data = await response.json();
      if (data.success) {
        setStatus(data.data);
      }
    } catch (error) {
      console.error('Ошибка получения статуса VPN:', error);
    }
  };

  const fetchServers = async () => {
    try {
      const response = await fetch('/api/v1/vpn/servers');
      const data = await response.json();
      if (data.success) {
        setServers(data.data.servers);
      }
    } catch (error) {
      console.error('Ошибка получения серверов:', error);
    }
  };

  // 🚀 Подключение к VPN
  const handleConnect = async (serverId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/vpn/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          server_id: serverId,
          protocol: 'auto',
          obfuscation: 'auto',
          stealth: true
        })
      });
      const data = await response.json();
      if (data.success) {
        await fetchVPNStatus();
      } else {
        alert('Ошибка подключения: ' + (data.error || 'Неизвестная ошибка'));
      }
    } catch (error) {
      console.error('Ошибка подключения:', error);
      alert('Ошибка подключения к VPN');
    } finally {
      setIsLoading(false);
    }
  };

  // 🔌 Отключение от VPN
  const handleDisconnect = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/vpn/disconnect', {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        await fetchVPNStatus();
      }
    } catch (error) {
      console.error('Ошибка отключения:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 🔍 Детекция блокировок
  const handleBlockadeDetection = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/vpn/detect-blockade', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_host: 'google.com',
          deep_scan: true
        })
      });
      const data = await response.json();
      if (data.success) {
        setBlockadeDetection(data.data);
      }
    } catch (error) {
      console.error('Ошибка детекции:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 🔄 Переключение протокола
  const handleProtocolSwitch = async (protocol: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/vpn/switch-protocol', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          protocol: protocol,
          reason: 'manual'
        })
      });
      const data = await response.json();
      if (data.success) {
        await fetchVPNStatus();
      }
    } catch (error) {
      console.error('Ошибка переключения:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 🎨 Получение цвета для статуса
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500';
      case 'reconnecting': return 'bg-orange-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  // 🎨 Получение иконки для страны
  const getCountryFlag = (country: string) => {
    const flags: { [key: string]: string } = {
      'US': '🇺🇸',
      'DE': '🇩🇪',
      'CH': '🇨🇭',
      'SE': '🇸🇪',
      'JP': '🇯🇵',
      'SG': '🇸🇬'
    };
    return flags[country] || '🌍';
  };

  // 🎨 Форматирование байтов
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 🎨 Форматирование времени
  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}ч ${minutes}м`;
  };

  if (!status) {
    return (
      <Card className="p-6">
        <div className="animate-pulse text-center">
          <Shield className="w-12 h-12 mx-auto mb-4 text-purple-500" />
          <div className="text-lg">Загрузка статуса Aurion Shield VPN...</div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* 🎯 Заголовок с главным статусом */}
      <Card className="p-6 bg-gradient-to-r from-green-900/20 to-blue-900/20 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2 flex items-center">
              <Shield className="w-8 h-8 mr-3 text-green-400" />
              Aurion Shield VPN
            </h2>
            <p className="text-gray-300">
              Интеллектуальная система обхода блокировок с AI-детектором
            </p>
          </div>
          <div className="text-center">
            <div className={`inline-flex items-center px-6 py-3 rounded-full ${getStatusColor(status.status)} text-white font-bold`}>
              {status.connected ? <Lock className="w-5 h-5 mr-2" /> : <Unlock className="w-5 h-5 mr-2" />}
              {status.status === 'connected' ? 'ЗАЩИЩЕН' : status.status.toUpperCase()}
            </div>
            {status.connected && status.ip_address && (
              <div className="mt-2 text-sm text-gray-300">
                IP: {status.ip_address}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* 🎛️ Быстрые действия */}
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4 text-white">🎛️ Быстрые действия</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Подключение/Отключение */}
          <div className="space-y-2">
            <label className="text-sm text-gray-400">Основное управление</label>
            {status.connected ? (
              <Button
                onClick={handleDisconnect}
                disabled={isLoading}
                className="w-full bg-red-600 hover:bg-red-700"
              >
                <Unlock className="w-4 h-4 mr-2" />
                Отключиться
              </Button>
            ) : (
              <div className="space-y-2">
                <select
                  value={selectedServer}
                  onChange={(e) => setSelectedServer(e.target.value)}
                  className="w-full p-2 bg-gray-800 text-white rounded border border-gray-700"
                >
                  <option value="">Выберите сервер</option>
                  {servers.map((server) => (
                    <option key={server.id} value={server.id}>
                      {getCountryFlag(server.country)} {server.name}
                    </option>
                  ))}
                </select>
                <Button
                  onClick={() => selectedServer && handleConnect(selectedServer)}
                  disabled={isLoading || !selectedServer}
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  <Lock className="w-4 h-4 mr-2" />
                  Подключиться
                </Button>
              </div>
            )}
          </div>

          {/* Детекция блокировок */}
          <div className="space-y-2">
            <label className="text-sm text-gray-400">Безопасность</label>
            <Button
              onClick={handleBlockadeDetection}
              disabled={isLoading}
              className="w-full bg-purple-600 hover:bg-purple-700"
            >
              <Eye className="w-4 h-4 mr-2" />
              Проверить блокировки
            </Button>
            {blockadeDetection && (
              <div className="text-xs text-gray-400 p-2 bg-gray-800 rounded">
                {blockadeDetection.blockade_type === 'none' ? '✅ Блокировок нет' : '⚠️ Обнаружены блокировки'}
              </div>
            )}
          </div>

          {/* Автопереключение */}
          <div className="space-y-2">
            <label className="text-sm text-gray-400">Автоматизация</label>
            <div className="flex items-center justify-between p-2 bg-gray-800 rounded">
              <span className="text-white">Автопереключение</span>
              <Switch
                checked={autoProtocolSwitch}
                onChange={setAutoProtocolSwitch}
                disabled={isLoading}
              />
            </div>
          </div>
        </div>
      </Card>

      {/* 📊 Метрики соединения */}
      {status.connected && status.metrics && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4 text-white">📊 Качество соединения</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-green-400">
                {status.metrics.latency_ms.toFixed(0)}ms
              </div>
              <div className="text-sm text-gray-400">Задержка</div>
            </div>
            
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-blue-400">
                {status.metrics.download_speed_mbps.toFixed(1)}Mbps
              </div>
              <div className="text-sm text-gray-400">Скорость загрузки</div>
            </div>
            
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">
                {status.metrics.quality_score.toFixed(2)}
              </div>
              <div className="text-sm text-gray-400">Качество</div>
            </div>
            
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-orange-400">
                {(status.metrics.packet_loss * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-400">Потеря пакетов</div>
            </div>
          </div>

          {/* Прогресс качества */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-400 mb-1">
              <span>Качество соединения</span>
              <span>{(status.metrics.quality_score * 100).toFixed(0)}%</span>
            </div>
            <Progress 
              value={status.metrics.quality_score * 100} 
              className="h-2"
            />
          </div>
        </Card>
      )}

      {/* 🌍 Список серверов */}
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4 text-white">🌍 Серверы Aurion Shield</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {servers.map((server) => (
            <div
              key={server.id}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                status.server?.name === server.name
                  ? 'bg-green-900/50 border-green-500'
                  : 'bg-gray-800 border-gray-700 hover:bg-gray-700'
              }`}
              onClick={() => !status.connected && setSelectedServer(server.id)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center">
                  <span className="text-2xl mr-2">{getCountryFlag(server.country)}</span>
                  <div>
                    <div className="font-bold text-white">{server.name}</div>
                    <div className="text-sm text-gray-400">{server.city}</div>
                  </div>
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  server.status === 'active' ? 'bg-green-500' : 'bg-red-500'
                }`} />
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                <div>⚡ {server.speed_mbps}Mbps</div>
                <div>📍 {server.latency_ms}ms</div>
                <div>📊 {server.load}% нагрузка</div>
                <div className="flex items-center">
                  {server.stealth_support && <Shield className="w-3 h-3 mr-1 text-purple-400" />}
                  {server.obfuscation_support && <Eye className="w-3 h-3 mr-1 text-blue-400" />}
                </div>
              </div>

              {server.is_residential && (
                <Badge className="mt-2 bg-blue-500 text-xs">Residential</Badge>
              )}
              {server.is_dedicated && (
                <Badge className="mt-2 bg-purple-500 text-xs">Dedicated</Badge>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* 🚨 Результаты детекции блокировок */}
      {blockadeDetection && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4 text-white">🔍 Результаты анализа</h3>
          
          <div className={`p-4 rounded-lg ${
            blockadeDetection.blockade_type === 'none'
              ? 'bg-green-900/50 border border-green-500'
              : 'bg-red-900/50 border border-red-500'
          }`}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-bold text-white mb-2">Тип блокировки</h4>
                <p className="text-gray-300">
                  {blockadeDetection.blockade_type === 'none' 
                    ? 'Блокировки не обнаружены' 
                    : `Обнаружена: ${blockadeDetection.blockade_type}`}
                </p>
                <p className="text-sm text-gray-400 mt-1">
                  Уверенность: {(blockadeDetection.confidence_score * 100).toFixed(0)}%
                </p>
              </div>
              
              <div>
                <h4 className="font-bold text-white mb-2">Рекомендации</h4>
                <p className="text-gray-300">
                  Рекомендуемый протокол: <span className="text-purple-400">{blockadeDetection.recommended_protocol}</span>
                </p>
                <Button
                  onClick={() => handleProtocolSwitch(blockadeDetection.recommended_protocol)}
                  disabled={isLoading}
                  className="mt-2 bg-purple-600 hover:bg-purple-700"
                >
                  Применить рекомендацию
                </Button>
              </div>
            </div>
            
            {blockadeDetection.blocked_protocols.length > 0 && (
              <div className="mt-4">
                <h4 className="font-bold text-white mb-2">Заблокированные протоколы</h4>
                <div className="flex flex-wrap gap-2">
                  {blockadeDetection.blocked_protocols.map((protocol) => (
                    <Badge key={protocol} className="bg-red-500">
                      {protocol}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* ⚙️ Расширенные настройки */}
      {showAdvanced && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4 text-white">⚙️ Расширенные настройки</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-bold text-white">Kill Switch</h4>
                <p className="text-sm text-gray-400">Блокировка интернета при отключении VPN</p>
              </div>
              <Switch checked={killSwitch} onChange={setKillSwitch} />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-bold text-white">Защита DNS</h4>
                <p className="text-sm text-gray-400">Предотвращение утечек DNS</p>
              </div>
              <Switch checked={dnsProtection} onChange={setDnsProtection} />
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-bold text-white">Защита IPv6</h4>
                <p className="text-sm text-gray-400">Отключение IPv6 для предотвращения утечек</p>
              </div>
              <Switch checked={ipv6Protection} onChange={setIpv6Protection} />
            </div>
          </div>
        </Card>
      )}

      {/* 📊 Статистика сессии */}
      {status.connected && status.uptime && (
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4 text-white">📊 Статистика сессии</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-green-400">
                {formatUptime(status.uptime)}
              </div>
              <div className="text-sm text-gray-400">Время работы</div>
            </div>
            
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-blue-400">
                {formatBytes(status.bytes_sent || 0)}
              </div>
              <div className="text-sm text-gray-400">Отправлено</div>
            </div>
            
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-purple-400">
                {formatBytes(status.bytes_received || 0)}
              </div>
              <div className="text-sm text-gray-400">Получено</div>
            </div>
            
            <div className="text-center p-4 bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-orange-400">
                {status.protocol?.toUpperCase() || 'UNKNOWN'}
              </div>
              <div className="text-sm text-gray-400">Протокол</div>
            </div>
          </div>
        </Card>
      )}

      {/* 🎛️ Кнопка показа расширенных настроек */}
      <div className="text-center">
        <Button
          onClick={() => setShowAdvanced(!showAdvanced)}
          variant="outline"
          className="bg-gray-800 hover:bg-gray-700"
        >
          {showAdvanced ? 'Скрыть' : 'Показать'} расширенные настройки
        </Button>
      </div>
    </div>
  );
};

export default AurionShieldVPN;
