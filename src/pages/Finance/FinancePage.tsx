import { useState } from 'react'
import './FinancePage.css'

// Страница финансов и криптовалют
export function FinancePage() {
  const [activeTab, setActiveTab] = useState('wallet')

  // Демо-данные кошелька
  const walletData = {
    total: 12547.50,
    currencies: [
      { code: 'BTC', name: 'Bitcoin', balance: 0.45, value: 18900.00, change: +5.2 },
      { code: 'ETH', name: 'Ethereum', balance: 4.2, value: 8400.00, change: +3.8 },
      { code: 'USDT', name: 'Tether', balance: 2500.00, value: 2500.00, change: 0.0 },
      { code: 'AUR', name: 'Aurion', balance: 15000.00, value: 3750.00, change: +12.5 },
    ]
  }

  // Демо-данные транзакций
  const transactions = [
    { id: 1, type: 'receive', amount: 0.1, currency: 'BTC', from: '0x1234...5678', date: '2024-03-28', status: 'completed' },
    { id: 2, type: 'send', amount: 500, currency: 'USDT', to: '0x8765...4321', date: '2024-03-27', status: 'completed' },
    { id: 3, type: 'receive', amount: 1000, currency: 'AUR', from: 'staking', date: '2024-03-26', status: 'completed' },
  ]

  return (
    <div className="finance-page">
      <h1 className="page-title">💰 Финансы</h1>
      <p className="page-subtitle">Управление криптовалютным портфелем</p>

      {/* Вкладки */}
      <div className="finance-tabs">
        <button 
          className={activeTab === 'wallet' ? 'active' : ''}
          onClick={() => setActiveTab('wallet')}
        >
          Кошелек
        </button>
        <button 
          className={activeTab === 'transactions' ? 'active' : ''}
          onClick={() => setActiveTab('transactions')}
        >
          Транзакции
        </button>
        <button 
          className={activeTab === 'send' ? 'active' : ''}
          onClick={() => setActiveTab('send')}
        >
          Отправить
        </button>
      </div>

      {/* Содержимое вкладок */}
      {activeTab === 'wallet' && (
        <div className="wallet-section">
          {/* Общий баланс */}
          <div className="total-balance">
            <span className="balance-label">Общий баланс</span>
            <span className="balance-value">${walletData.total.toLocaleString()}</span>
            <span className="balance-change positive">+8.4%</span>
          </div>

          {/* Список валют */}
          <div className="currencies-list">
            {walletData.currencies.map(currency => (
              <div key={currency.code} className="currency-card">
                <div className="currency-info">
                  <div className="currency-icon">{currency.code[0]}</div>
                  <div className="currency-details">
                    <span className="currency-name">{currency.name}</span>
                    <span className="currency-code">{currency.code}</span>
                  </div>
                </div>
                <div className="currency-values">
                  <span className="currency-balance">{currency.balance} {currency.code}</span>
                  <span className="currency-usd">${currency.value.toLocaleString()}</span>
                  <span className={`currency-change ${currency.change >= 0 ? 'positive' : 'negative'}`}>
                    {currency.change >= 0 ? '+' : ''}{currency.change}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'transactions' && (
        <div className="transactions-section">
          <div className="transactions-list">
            {transactions.map(tx => (
              <div key={tx.id} className={`transaction-item ${tx.type}`}>
                <div className="tx-icon">
                  {tx.type === 'receive' ? '↓' : '↑'}
                </div>
                <div className="tx-details">
                  <span className="tx-type">
                    {tx.type === 'receive' ? 'Получено' : 'Отправлено'}
                  </span>
                  <span className="tx-address">
                    {tx.type === 'receive' ? `От: ${tx.from}` : `Кому: ${tx.to}`}
                  </span>
                  <span className="tx-date">{tx.date}</span>
                </div>
                <div className="tx-amount">
                  <span className={`amount-value ${tx.type}`}>
                    {tx.type === 'receive' ? '+' : '-'}{tx.amount} {tx.currency}
                  </span>
                  <span className="tx-status">{tx.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'send' && (
        <div className="send-section">
          <div className="send-form">
            <div className="form-group">
              <label>Адрес получателя:</label>
              <input type="text" placeholder="0x... или адрес кошелька" />
            </div>
            <div className="form-group">
              <label>Сумма:</label>
              <div className="amount-input">
                <input type="number" placeholder="0.00" />
                <select>
                  <option>BTC</option>
                  <option>ETH</option>
                  <option>USDT</option>
                  <option>AUR</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label>Примечание (опционально):</label>
              <input type="text" placeholder="Сообщение для получателя" />
            </div>
            <button className="send-button">Отправить</button>
          </div>
        </div>
      )}
    </div>
  )
}
