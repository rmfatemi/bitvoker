import React from 'react';

function NotificationTable({notifications, showOriginal}) {
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
            <table id="notificationsTable">
                <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Client IP</th>
                    {showOriginal && <th>Original Message</th>}
                    <th>AI Summary</th>
                </tr>
                </thead>
                <tbody>
                {notifications.map((notification, index) => (
                    <tr key={index}>
                        <td>{notification.timestamp}</td>
                        <td>{notification.client_ip || 'N/A'}</td>
                        {showOriginal && (
                            <td>
                                <pre dangerouslySetInnerHTML={{__html: escapeHtml(notification.original_message)}}/>
                            </td>
                        )}
                        <td>
                            {notification.ai_message ? (
                                <pre dangerouslySetInnerHTML={{__html: escapeHtml(notification.ai_message)}}/>
                            ) : (
                                <span className="ai-disabled-notice">AI processing disabled</span>
                            )}
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
            {notifications.length === 0 && <p>No notifications found in selected date range.</p>}
        </div>
    );
}

export default NotificationTable;
