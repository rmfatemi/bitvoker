import React, {useEffect, useState} from 'react';

function Logs({logs = []}) {
    const [logEntries, setLogEntries] = useState(logs);

    useEffect(() => {
        setLogEntries(logs);
    }, [logs]);

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
        <div className="table-responsive">
            <table id="logsTable">
                <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Level</th>
                    <th>Message</th>
                </tr>
                </thead>
                <tbody>
                {[...logEntries].reverse().map((log, index) => (
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
