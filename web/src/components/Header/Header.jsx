import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Button
} from '@mui/material';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import LogoutIcon from '@mui/icons-material/Logout';
import bitvokerLogo from '../../assets/bitvoker.png';

function Header({ toggleTheme, theme, onLogout }) {
  return (
    <AppBar
      position="static"
      color="default"
      elevation={1}
      sx={{ bgcolor: theme => theme.palette.background.default }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <img
            src={bitvokerLogo}
            alt="bitvoker"
            width="32"
            height="32"
            style={{ marginRight: '10px' }}
          />
          <Typography variant="h6" component="h1">
            bitvoker
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton
            onClick={toggleTheme}
            color="inherit"
            aria-label="toggle theme"
          >
            {theme === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
          {onLogout && (
            <Button
              onClick={onLogout}
              color="inherit"
              size="small"
              startIcon={<LogoutIcon />}
            >
              logout
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
