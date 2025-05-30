import React, {useEffect} from 'react';
import {
    Box,
    Paper,
    styled,
    Typography
} from '@mui/material';
import {DataGrid, GridToolbar} from '@mui/x-data-grid';

const WrappedCell = styled('div')({
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    lineHeight: 1,
    padding: '2px 0',
});

function Logs({logs = [], onRefresh}) {

    useEffect(() => {
        const intervalId = setInterval(() => {
            if (onRefresh) onRefresh();
        }, 20000);
        return () => clearInterval(intervalId);
    }, [onRefresh]);

    const getLogLevelStyle = (level, theme) => {
        switch (level) {
            case 'DEBUG':
                return {color: theme.palette.text.secondary};
            case 'INFO':
                return {color: theme.palette.success.main};
            case 'WARNING':
                return {color: theme.palette.warning.main};
            case 'ERROR':
                return {color: theme.palette.error.main};
            case 'CRITICAL':
                return {color: theme.palette.error.main, fontWeight: 'bold'};
            default:
                return {};
        }
    };

    const columns = [
        {
            field: 'timestamp',
            headerName: 'Timestamp',
            width: 180,
            type: 'dateTime',
            valueGetter: (params) => {
                if (typeof params.value === 'string' && params.value) {
                    const isoString = params.value.replace(' ', 'T');
                    const date = new Date(isoString);
                    return !isNaN(date.getTime()) ? date : null;
                }
                return null;
            },
        },
        {
            field: 'level',
            headerName: 'Level',
            width: 120,
            renderCell: (params) => (
                <Typography variant="body2" sx={(theme) => getLogLevelStyle(params.value, theme)}>
                    {params.value}
                </Typography>
            )
        },
        {
            field: 'message',
            headerName: 'Message',
            flex: 1,
            renderCell: (params) => (
                <WrappedCell>{params.value}</WrappedCell>
            )
        },
    ];

    const rows = logs.map((log, index) => ({
        id: index,
        ...log
    }));

    return (
        <Box>
            <Paper sx={{
                height: '75vh',
                width: '100%',
                border: (theme) => `1px solid ${theme.palette.divider}`
            }}>
                <DataGrid
                    rows={rows}
                    columns={columns}
                    getRowHeight={() => 'auto'}
                    disableRowSelectionOnClick
                    slots={{
                        toolbar: GridToolbar,
                    }}
                    initialState={{
                        sorting: {
                            sortModel: [{field: 'timestamp', sort: 'desc'}],
                        },
                    }}
                    sx={{
                        '&.MuiDataGrid-root': {
                            border: 'none',
                        },
                        '& .MuiDataGrid-columnHeader, & .MuiDataGrid-cell': {
                            borderRight: (theme) => `1px solid ${theme.palette.divider}`,
                        },
                        '& .MuiDataGrid-columnHeader:last-of-type, & .MuiDataGrid-cell:last-of-type': {
                            borderRight: 'none',
                        },
                        '& .MuiDataGrid-cell': {
                            borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
                            backgroundColor: (theme) => theme.palette.background.paper,
                            display: 'flex',
                            alignItems: 'center',
                            py: 1,
                        },
                        '& .MuiDataGrid-columnHeaders': {
                            backgroundColor: (theme) => theme.palette.background.default,
                            borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
                        },
                        '& .MuiDataGrid-toolbarContainer': {
                            borderBottom: (theme) => `1px solid ${theme.palette.divider}`,
                        },
                        '& .MuiDataGrid-virtualScroller': {
                            '&::-webkit-scrollbar': {
                                width: '0.4em',
                                height: '0.4em',
                            },
                            '&::-webkit-scrollbar-track': {
                                background: (theme) => theme.palette.background.paper,
                            },
                            '&::-webkit-scrollbar-thumb': {
                                backgroundColor: (theme) => theme.palette.divider,
                                borderRadius: '2px',
                            },
                            '&::-webkit-scrollbar-thumb:hover': {
                                background: (theme) => theme.palette.secondary.main,
                            },
                        },
                    }}
                />
            </Paper>
        </Box>
    );
}

export default Logs;
