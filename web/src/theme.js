import { createTheme } from '@mui/material/styles';
import { blue, indigo, grey, red, amber, lightBlue, green } from '@mui/material/colors';

export const getAppTheme = (mode) => {
  return createTheme({
    palette: {
      mode,
      ...(mode === 'light'
        ? {
            // Light theme
            primary: blue,
            secondary: {
              main: grey[600],
            },
            background: {
              default: grey[100],
              paper: grey[50],
              card: grey[50],
              header: grey[200],
              tab: grey[50],
              tabHover: grey[300],
              input: '#fff',
              disabled: grey[200],
            },
            text: {
              primary: grey[900],
              secondary: grey[700],
              disabled: grey[500],
            },
            divider: grey[300],
            action: {
              disabled: grey[300],
            },
            error: {
              main: red[700],
            },
            warning: {
              main: amber[700],
            },
            info: {
              main: lightBlue[700],
            },
            success: {
              main: green[700],
            },
            logoBackground: grey[300],
            logoText: grey[900],
          }
        : {
            // Dark theme
            primary: indigo,
            secondary: {
              main: grey[500],
            },
            background: {
              default: grey[900],
              paper: grey[800],
              card: grey[800],
              header: grey[900],
              tab: grey[850],
              tabHover: grey[700],
              input: grey[800],
              disabled: grey[850],
            },
            text: {
              primary: grey[200],
              secondary: grey[500],
              disabled: grey[700],
            },
            divider: grey[700],
            action: {
              disabled: grey[700],
            },
            error: {
              main: red[500],
            },
            warning: {
              main: amber[500],
            },
            info: {
              main: lightBlue[400],
            },
            success: {
              main: green[500],
            },
            logoBackground: grey[800],
            logoText: grey[100],
          }),
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
            lineHeight: 1.6,
            transition: 'background-color 0.3s, color 0.3s',
          },
          a: mode === 'light'
            ? {
                color: blue[700],
                textDecoration: 'none',
                transition: 'color 0.2s ease',
                '&:hover': {
                  color: blue[900],
                  textDecoration: 'underline',
                },
                '&:visited': {
                  color: indigo[700],
                },
                '&:active': {
                  color: blue[800],
                }
              }
            : {
                color: blue[300],
                textDecoration: 'none',
                transition: 'color 0.2s ease',
                '&:hover': {
                  color: blue[200],
                  textDecoration: 'underline',
                },
                '&:visited': {
                  color: indigo[300],
                },
                '&:active': {
                  color: blue[100],
                }
              },
          pre: {
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            backgroundColor: mode === 'light' ? grey[50] : grey[800],
            padding: '10px',
            borderRadius: '4px',
            fontSize: '0.9em',
            maxHeight: '200px',
            overflowY: 'auto',
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
          },
        },
        variants: [
          {
            props: { variant: 'action' },
            style: {
              fontSize: '0.8em',
              padding: '4px 8px',
              marginLeft: '5px',
              backgroundColor: mode === 'light' ? grey[200] : grey[700],
              color: mode === 'light' ? grey[900] : grey[100],
              border: `1px solid ${mode === 'light' ? grey[300] : grey[600]}`,
              '&:hover': {
                backgroundColor: mode === 'light' ? blue[700] : blue[800],
                color: '#fff',
              },
            },
          },
        ],
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            borderColor: mode === 'light' ? grey[300] : grey[700],
            padding: '10px',
            fontSize: '0.9em',
          },
          head: {
            backgroundColor: mode === 'light' ? grey[200] : grey[900],
            fontWeight: 'bold',
          },
        },
      },
      MuiInputBase: {
        styleOverrides: {
          root: {
            backgroundColor: mode === 'light' ? '#fff' : grey[800],
            '&.Mui-disabled': {
              backgroundColor: mode === 'light' ? grey[100] : grey[900],
              color: mode === 'light' ? grey[500] : grey[600],
            },
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundColor: mode === 'light' ? grey[50] : grey[800],
          },
        },
      },
    },
    typography: {
      h1: {
        fontSize: '1.8em',
        margin: 0,
      },
      h4: {
        marginBottom: '1rem',
      },
    },
  });
};
