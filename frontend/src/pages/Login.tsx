import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import axios from 'axios'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const setAuth = useAuthStore((s) => s.setAuth)
  const navigate = useNavigate()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await axios.post('/api/auth/login', { username, password })
      setAuth(res.data.token, res.data.user)
      navigate(`/${res.data.user.role}`)
    } catch (err: any) {
      setError(err.response?.data?.message_zh || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', background: '#f0f2f5' }}>
      <form onSubmit={handleLogin} style={{ background: '#fff', padding: 40, borderRadius: 8, width: 360, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <h1 style={{ textAlign: 'center', marginBottom: 24 }}>MedAgent 登录</h1>
        {error && <div style={{ color: '#ff4d4f', marginBottom: 16, textAlign: 'center' }}>{error}</div>}
        <input
          type="text"
          placeholder="用户名"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ width: '100%', padding: '8px 12px', marginBottom: 16, border: '1px solid #d9d9d9', borderRadius: 6, fontSize: 14 }}
          required
        />
        <input
          type="password"
          placeholder="密码"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ width: '100%', padding: '8px 12px', marginBottom: 16, border: '1px solid #d9d9d9', borderRadius: 6, fontSize: 14 }}
          required
        />
        <button
          type="submit"
          disabled={loading}
          style={{ width: '100%', padding: '10px 0', background: '#1677ff', color: '#fff', border: 'none', borderRadius: 6, fontSize: 16, cursor: 'pointer' }}
        >
          {loading ? '登录中...' : '登录'}
        </button>
      </form>
    </div>
  )
}
