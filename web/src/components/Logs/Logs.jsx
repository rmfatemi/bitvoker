import React, {useEffect, useState, useRef} from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Box,
    Paper
} from '@mui/material';

function Logs({logs = [], onRefresh}) {
    const [logEntries, setLogEntries] = useState(logs);
    const logsContainerRef = useRef(null);

    useEffect(() => {
        setLogEntries(logs);
    }, [logs]);

    useEffect(() => {
        const intervalId = setInterval(() => {
            if (onRefresh) onRefresh();
        }, 20000);

        return () => clearInterval(intervalId);
    }, [onRefresh]);

    useEffect(() => {
        if (logsContainerRef.current) {
            logsContainerRef.current.scrollTop = logsContainerRef.current.scrollHeight;
        }
    }, [logEntries]);

    const escapeHtml = (unsafe) => {
        if (unsafe === null || unsafe === undefined) return '';
        return unsafe.toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    };

    const getLogLevelStyle = (level) => {
        switch (level) {
            case 'DEBUG':
                return {color: '#888'};
            case 'INFO':
                return {color: '#4CAF50'};
            case 'WARNING':
                return {color: '#FFC107'};
            case 'ERROR':
                return {color: '#F44336'};
            case 'CRITICAL':
                return {color: '#F44336', fontWeight: 'bold'};
            default:
                return {};
        }
    };

    return (
        <TableContainer
            component={Paper}
            ref={logsContainerRef}
            sx={{
                maxHeight: '75vh',
                overflowY: 'auto',
                '& .MuiTableCell-root': {
                    fontSize: '0.9em',
                    padding: '2px 10px',
                    borderBottom: '1px solid rgba(120, 120, 120, 0.4)',
                    borderRight: '1px solid rgba(120, 120, 120, 0.3)'
                },
                // Remove border from last column
                '& .MuiTableCell-root:last-child': {
                    borderRight: 'none'
                }
            }}
        >
            <Table stickyHeader size="small" id="logsTable">
                <TableHead>
                    <TableRow>
                        <TableCell sx={{width: '1%', whiteSpace: 'nowrap'}}>Timestamp</TableCell>
                        <TableCell sx={{width: '1%', whiteSpace: 'nowrap'}}>Level</TableCell>
                        <TableCell>Message</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {logEntries.map((log, index) => (
                        <TableRow key={index}>
                            <TableCell sx={{width: '1%', whiteSpace: 'nowrap'}}>
                                {log.timestamp}
                            </TableCell>
                            <TableCell
                                sx={{
                                    width: '1%',
                                    whiteSpace: 'nowrap',
                                    ...getLogLevelStyle(log.level)
                                }}
                            >
                                {log.level}
                            </TableCell>
                            <TableCell>
                                <Box
                                    component="pre"
                                    sx={{
                                        m: 0,
                                        p: '5px',
                                        whiteSpace: 'pre-wrap',
                                        wordBreak: 'break-word',
                                        maxHeight: '200px',
                                        overflowY: 'auto',
                                        background: 'transparent',
                                        borderRadius: 0,
                                        fontSize: '1em'
                                    }}
                                    dangerouslySetInnerHTML={{__html: escapeHtml(log.message)}}
                                />
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

export default Logs;
