import React, {useState, useEffect} from 'react';
import {
    Box,
    Typography,
    TextField,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Stack
} from '@mui/material';

function Dashboard({notifications = [], config = {}, onRefresh}) {
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [clientIp, setClientIp] = useState('');
    const [filteredNotifications, setFilteredNotifications] = useState(notifications);

    useEffect(() => {
        setFilteredNotifications(notifications);
    }, [notifications]);

    useEffect(() => {
        const intervalId = setInterval(() => {
            if (onRefresh) onRefresh();
        }, 20000);
        return () => clearInterval(intervalId);
    }, [onRefresh]);

    const handleFilter = () => {
        let filtered = notifications;

        if (startDate && endDate) {
            const start = new Date(`${startDate}T00:00:00`);
            start.setHours(0, 0, 0, 0);
            const end = new Date(`${endDate}T23:59:59.999`);
            filtered = filtered.filter((notif) => {
                const notifDate = new Date(notif.timestamp);
                return notifDate >= start && notifDate <= end;
            });
        }
        if (clientIp) {
            filtered = filtered.filter((notif) =>
                notif.client && notif.client.includes(clientIp)
            );
        }

        setFilteredNotifications(filtered);
    };

    const escapeHtml = (unsafe) => {
        if (unsafe === null || unsafe === undefined) return '';
        return unsafe.toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    };

    return (
        <Box>
            <Stack
                direction="row"
                spacing={2}
                alignItems="flex-end"
                flexWrap="wrap"
                sx={{mb: 2}}
            >
                <Box>
                    <TextField
                        id="startDateFilter"
                        label="From"
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        InputLabelProps={{shrink: true}}
                        size="small"
                        sx={{width: 150}}
                    />
                </Box>

                <Box>
                    <TextField
                        id="endDateFilter"
                        label="To"
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        InputLabelProps={{shrink: true}}
                        size="small"
                        sx={{width: 150}}
                    />
                </Box>

                <Box>
                    <TextField
                        id="clientIpFilter"
                        label="Client IP"
                        placeholder="Filter by IP"
                        value={clientIp}
                        onChange={(e) => setClientIp(e.target.value)}
                        size="small"
                        sx={{width: 150}}
                    />
                </Box>

                <Button
                    variant="contained"
                    onClick={handleFilter}
                    size="medium"
                >
                    Filter
                </Button>
            </Stack>

            <TableContainer
                component={Paper}
                sx={(theme) => ({
                    maxWidth: '100%',
                    overflowX: 'auto',
                    border: `1px solid ${theme.palette.divider}`,
                    boxShadow: theme.shadows[1],
                    '& .MuiTableCell-root': {
                        fontSize: '0.9em',
                        padding: '2px 10px',
                        borderBottom: `1px solid ${theme.palette.divider}`,
                        borderRight: `1px solid ${theme.palette.divider}`
                    },
                    '& .MuiTableCell-root:last-child': {
                        borderRight: 'none'
                    },
                    '& .MuiTableHead-root .MuiTableRow-root': {
                        backgroundColor: theme.palette.background.header,
                        '& .MuiTableCell-root': {
                            fontWeight: 'bold',
                            borderBottom: `2px solid ${theme.palette.divider}`
                        }
                    }
                })}
            >
                <Table id="notificationsTable" size="small">
                    <TableHead>
                        <TableRow>
                            <TableCell>Timestamp</TableCell>
                            <TableCell>Client IP</TableCell>
                            <TableCell>Original Message</TableCell>
                            <TableCell>AI Processed</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {filteredNotifications.map((notif, index) => (
                            <TableRow key={index}>
                                <TableCell sx={{whiteSpace: 'nowrap'}}>{notif.timestamp}</TableCell>
                                <TableCell sx={{whiteSpace: 'nowrap'}}>{notif.client || 'N/A'}</TableCell>
                                <TableCell>
                                    <Box
                                        component="pre"
                                        sx={{
                                            m: 0,
                                            whiteSpace: 'pre-wrap',
                                            wordBreak: 'break-word',
                                            maxHeight: 200,
                                            overflowY: 'auto'
                                        }}
                                        dangerouslySetInnerHTML={{
                                            __html: escapeHtml(notif.original || notif.message)
                                        }}
                                    />
                                </TableCell>
                                <TableCell>
                                    <Box
                                        component="pre"
                                        sx={{
                                            m: 0,
                                            whiteSpace: 'pre-wrap',
                                            wordBreak: 'break-word',
                                            maxHeight: 200,
                                            overflowY: 'auto'
                                        }}
                                        dangerouslySetInnerHTML={{
                                            __html: escapeHtml(notif.ai || '')
                                        }}
                                    />
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Box>
    );
}

export default Dashboard;
