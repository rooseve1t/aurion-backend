// Jarvis whisper mode controls

import React, { useState, useEffect } from 'react';
import { Card, Button, Badge, Switch, Alert } from '@/components/ui';

interface VoiceStatus {
  current_mode: 'normal' | 'whisper' | 'soft' | 'energetic';
  is_night_time: boolean;
  night_hours: string;
  available_modes: string[];
  auto_whisper_enabled: boolean;
  current_hour: number;
}

interface WhisperTestResult {
  text: string;
  should_whisper: boolean;
  current_hour: number;
  contains_trigger: boolean;
}

const JarviSWhisperControl: React.FC = () => {
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus | null>(null);
  const [currentMode, setCurrentMode] = useState<string>('normal');
  const [isLoading, setIsLoading] = useState(false);
  const [testText, setTestText] = useState('');
  const [testResult, setTestResult] = useState<WhisperTestResult | null>(null);
  const [autoWhisper, setAutoWhisper] = useState(true);

  // 🤫 Получаем статус голосовой системы
  useEffect(() => {
    fetchVoiceStatus();
    const interval = setInterval(fetchVoiceStatus, 30000); // Обновляем каждые 30 секунд
    return () => clearInterval(interval);
  }, []);

  const fetchVoiceStatus = async () => {
    try {
      const response = await fetch('/api/v1/voice/jarvis/status');
      const data = await response.json();
      if (data.success) {
        setVoiceStatus(data.data);
        setCurrentMode(data.data.current_mode);
      }
    } catch (error) {
      console.error('Ошибка получения статуса:', error);
    }
  };

  // 🎤 Установить режим голоса
  const setVoiceMode = async (mode: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/voice/jarvis/mode', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode })
      });
      const data = await response.json();
      if (data.success) {
        setCurrentMode(mode);
        setVoiceStatus(prev => prev ? { ...prev, current_mode: mode as any } : null);
      }
    } catch (error) {
      console.error('Ошибка установки режима:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 🤫 Тестировать детектор шепота
  const testWhisper = async () => {
    if (!testText.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/voice/jarvis/test-whisper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: testText })
      });
      const data = await response.json();
      if (data.success) {
        setTestResult(data.data);
      }
    } catch (error) {
      console.error('Ошибка тестирования:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 🎯 Сгенерировать шепот
  const generateWhisper = async (text: string) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/voice/jarvis/whisper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await response.json();
      if (data.success && data.audio_data) {
        // Воспроизводим аудио
        const audio = new Audio(`data:audio/wav;base64,${data.audio_data}`);
        await audio.play();
      }
    } catch (error) {
      console.error('Ошибка генерации шепота:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 🌙 Получить цвет для режима
  const getModeColor = (mode: string) => {
    switch (mode) {
      case 'whisper': return 'bg-purple-500';
      case 'soft': return 'bg-blue-500';
      case 'energetic': return 'bg-orange-500';
      default: return 'bg-green-500';
    }
  };

  // 🌙 Получить иконку режима
  const getModeIcon = (mode: string) => {
    switch (mode) {
      case 'whisper': return '🤫';
      case 'soft': return '🌊';
      case 'energetic': return '⚡';
      default: return '🎤';
    }
  };

  if (!voiceStatus) {
    return (
      <Card className="p-6">
        <div className="animate-pulse text-center">
          <div className="text-lg">Загрузка статуса JARVIS...</div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* 🎯 Заголовок с текущим статусом */}
      <Card className="p-6 bg-gradient-to-r from-purple-900/20 to-blue-900/20 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">
              🤫 JARVIS Whisper Mode
            </h2>
            <p className="text-gray-300">
              Умный голосовой ассистент с эмоциональным интеллектом
            </p>
          </div>
          <div className="text-center">
            <div className={`inline-flex items-center px-4 py-2 rounded-full ${getModeColor(currentMode)} text-white`}>
              <span className="text-2xl mr-2">{getModeIcon(currentMode)}</span>
              <span className="font-bold uppercase">{currentMode}</span>
            </div>
            {voiceStatus.is_night_time && (
              <Badge className="mt-2 bg-indigo-500">
                🌙 Ночной режим активен
              </Badge>
            )}
          </div>
        </div>
      </Card>

      {/* 🎛️ Управление режимами */}
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4 text-white">🎛️ Управление голосом</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {voiceStatus.available_modes.map((mode) => (
            <Button
              key={mode}
              onClick={() => setVoiceMode(mode)}
              disabled={isLoading}
              className={`p-4 h-auto flex flex-col items-center space-y-2 ${
                currentMode === mode ? getModeColor(mode) : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <span className="text-2xl">{getModeIcon(mode)}</span>
              <span className="font-bold">{mode}</span>
            </Button>
          ))}
        </div>

        {/* 🤫 Автоопределение шепота */}
        <div className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
          <div>
            <h4 className="font-bold text-white">🤫 Автоопределение шепота</h4>
            <p className="text-gray-400 text-sm">
              JARVIS автоматически определяет когда говорить шепотом
            </p>
          </div>
          <Switch
            checked={autoWhisper}
            onChange={setAutoWhisper}
            disabled={isLoading}
          />
        </div>
      </Card>

      {/* 🧪 Тестирование детектора */}
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4 text-white">🧪 Тестирование детектора</h3>
        
        <div className="space-y-4">
          <textarea
            value={testText}
            onChange={(e) => setTestText(e.target.value)}
            placeholder="Введите текст для тестирования..."
            className="w-full p-3 bg-gray-800 text-white rounded-lg border border-gray-700 focus:border-purple-500 focus:outline-none"
            rows={3}
          />
          
          <div className="flex space-x-4">
            <Button
              onClick={testWhisper}
              disabled={isLoading || !testText.trim()}
              className="bg-purple-600 hover:bg-purple-700"
            >
              🔍 Тестировать
            </Button>
            
            <Button
              onClick={() => generateWhisper(testText)}
              disabled={isLoading || !testText.trim()}
              className="bg-green-600 hover:bg-green-700"
            >
              🤫 Сгенерировать шепот
            </Button>
          </div>

          {testResult && (
            <Alert className={`p-4 ${
              testResult.should_whisper 
                ? 'bg-purple-900/50 border-purple-500' 
                : 'bg-gray-800 border-gray-700'
            }`}>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">
                    {testResult.should_whisper ? '🤫 Требуется шепот' : '🎤 Обычный режим'}
                  </span>
                  <span className="text-sm text-gray-400">
                    Текущий час: {testResult.current_hour}:00
                  </span>
                </div>
                <div className="text-sm text-gray-300">
                  {testResult.contains_trigger && '📍 Найден триггер шепота'}
                </div>
              </div>
            </Alert>
          )}
        </div>
      </Card>

      {/* 📊 Информация о системе */}
      <Card className="p-6">
        <h3 className="text-xl font-bold mb-4 text-white">📊 Информация о системе</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-800 rounded-lg">
            <h4 className="font-bold text-white mb-2">🌙 Ночные часы</h4>
            <p className="text-gray-300">{voiceStatus.night_hours}</p>
            <p className="text-sm text-gray-400">
              Сейчас {voiceStatus.is_night_time ? 'ночь' : 'день'}
            </p>
          </div>
          
          <div className="p-4 bg-gray-800 rounded-lg">
            <h4 className="font-bold text-white mb-2">🎯 Текущий статус</h4>
            <p className="text-gray-300">Режим: {currentMode}</p>
            <p className="text-sm text-gray-400">
              Автоопределение: {autoWhisper ? 'включено' : 'выключено'}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default JarviSWhisperControl;
