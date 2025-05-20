import React, { useEffect, useState, useRef } from 'react';

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

    return (
        <div
            className="table-responsive"
            ref={logsContainerRef}
            style={{ maxHeight: '75vh', overflowY: 'auto' }}
        >
            <table id="logsTable">
                <thead style={{ position: 'sticky', top: 0, zIndex: 1, backgroundColor: 'var(--bg-color)' }}>
                <tr>
                    <th>Timestamp</th>
                    <th>Level</th>
                    <th>Message</th>
                </tr>
                </thead>
                <tbody>
                {logEntries.map((log, index) => (
                    <tr key={index}>
                        <td>{log.timestamp}</td>
                        <td className={`log-level-${log.level}`}>{log.level}</td>
                        <td>
                            <pre dangerouslySetInnerHTML={{__html: escapeHtml(log.message)}}/>
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}

export default Logs;
