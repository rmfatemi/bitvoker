import React, {useEffect} from 'react';
import {
    Box,
    Paper,
    styled
} from '@mui/material';
import {DataGrid, GridToolbar} from '@mui/x-data-grid';

const WrappedCell = styled('div')({
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    lineHeight: 1.5,
    padding: '8px 0',
    maxHeight: '150px',
    overflowY: 'auto',
    width: '100%',
});

function Dashboard({notifications = [], config = {}, onRefresh}) {

    useEffect(() => {
        const intervalId = setInterval(() => {
            if (onRefresh) onRefresh();
        }, 20000);
        return () => clearInterval(intervalId);
    }, [onRefresh]);

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
            field: 'client',
            headerName: 'Client IP',
            width: 120,
        },
        {
            field: 'original',
            headerName: 'Original Message',
            flex: 1,
            renderCell: (params) => (
                <WrappedCell>{params.value}</WrappedCell>
            )
        },
        {
            field: 'ai',
            headerName: 'AI Processed',
            flex: 1,
            renderCell: (params) => (
                <WrappedCell>{params.value}</WrappedCell>
            )
        },
    ];

    const rows = notifications.map((notif, index) => ({
        id: index,
        timestamp: notif.timestamp,
        client: notif.client || 'N/A',
        original: notif.original || notif.message || '',
        ai: notif.ai || '',
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
                            alignItems: 'flex-start',
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

export default Dashboard;
