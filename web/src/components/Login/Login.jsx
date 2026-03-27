import React, { useState } from 'react';
import {
    Box, TextField, Button, Typography, Alert, Paper
} from '@mui/material';
import bitvokerLogo from '../../assets/bitvoker.png';

function Login({ onLogin }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            if (!response.ok) {
                setError('invalid credentials');
                return;
            }
            const data = await response.json();
            onLogin(data.token);
        } catch {
            setError('failed to connect to server');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '100vh',
            bgcolor: 'background.default'
        }}>
            <Paper sx={{ p: 4, maxWidth: 360, width: '100%' }}>
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <img src={bitvokerLogo} alt="bitvoker" width="48" height="48" />
                    <Typography variant="h5" sx={{ mt: 1 }}>bitvoker</Typography>
                </Box>
                <Box component="form" onSubmit={handleSubmit}>
                    {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
                    <TextField
                        fullWidth
                        label="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        sx={{ mb: 2 }}
                        autoFocus
                    />
                    <TextField
                        fullWidth
                        label="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                    <Button
                        fullWidth
                        variant="contained"
                        type="submit"
                        disabled={loading || !username || !password}
                    >
                        {loading ? 'logging in...' : 'login'}
                    </Button>
                </Box>
            </Paper>
        </Box>
    );
}

export default Login;
