import React, {useState, useEffect} from 'react';

function Dashboard({notifications = [], config = {}}) {
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [filteredNotifications, setFilteredNotifications] = useState(notifications);

    useEffect(() => {
        setFilteredNotifications(notifications);
    }, [notifications]);

    const handleFilter = () => {
        if (!startDate || !endDate) {
            setFilteredNotifications(notifications);
            return;
        }
        const start = new Date(`${startDate}T00:00:00`);
        start.setHours(0, 0, 0, 0);
        const end = new Date(`${endDate}T23:59:59.999`);
        const filtered = notifications.filter((notif) => {
            const notifDate = new Date(notif.timestamp);
            return notifDate >= start && notifDate <= end;
        });

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
        <div>
            <h2>Recent Notifications</h2>
            <div className="date-filter-group">
                <label htmlFor="startDateFilter">From:</label>
                <input
                    type="date"
                    id="startDateFilter"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                />
                <label htmlFor="endDateFilter">To:</label>
                <input
                    type="date"
                    id="endDateFilter"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                />
                <button onClick={handleFilter} className="button" type="button">
                    Filter
                </button>
            </div>
            <div className="table-responsive">
                <table id="notificationsTable">
                    <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Client IP</th>
                        <th>Original Message</th>
                        <th>AI Summary</th>
                    </tr>
                    </thead>
                    <tbody>
                    {filteredNotifications.map((notif, index) => (
                        <tr key={index}>
                            <td>{notif.timestamp}</td>
                            <td>{notif.client || 'N/A'}</td>
                            <td>
                  <pre
                      dangerouslySetInnerHTML={{
                          __html: escapeHtml(notif.original || notif.message),
                      }}
                  />
                            </td>
                            <td>
                  <pre
                      dangerouslySetInnerHTML={{
                          __html: escapeHtml(notif.ai || ''),
                      }}
                  />
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default Dashboard;
