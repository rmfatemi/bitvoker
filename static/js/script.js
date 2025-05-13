function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tab-content");
  for (i = 0; i < tabcontent.length; i++) { tabcontent[i].style.display = "none"; }
  tablinks = document.getElementsByClassName("tab-button");
  for (i = 0; i < tablinks.length; i++) { tablinks[i].className = tablinks[i].className.replace(" active", ""); }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
  localStorage.setItem('activeTab', tabName);
  if (tabName === 'dashboard') fetchNotifications();
  if (tabName === 'logs') fetchLogs();
}

function fetchNotifications() {
  const startDate = document.getElementById('startDateFilter').value;
  const endDate = document.getElementById('endDateFilter').value;
  fetch(`/get_notifications?limit=20&startDate=${startDate}&endDate=${endDate}`)
    .then(response => response.json())
    .then(data => {
      const tbody = document.getElementById('notificationsTable').getElementsByTagName('tbody')[0];
      tbody.innerHTML = '';
      data.notifications.forEach(notif => {
        let row = tbody.insertRow();
        row.insertCell().textContent = notif.timestamp;
        row.insertCell().textContent = notif.client;
        row.insertCell().innerHTML = `<pre>${escapeHtml(notif.original)}</pre>`;
        row.insertCell().innerHTML = `<pre>${escapeHtml(notif.ai)}</pre>`;
      });
    });
}

function fetchLogs() {
  fetch('/get_logs')
    .then(response => response.json())
    .then(data => {
      const tbody = document.getElementById('logsTable').getElementsByTagName('tbody')[0];
      tbody.innerHTML = '';
      (data.logs || []).slice().reverse().forEach(log => {
        let row = tbody.insertRow();
        row.insertCell().textContent = log.timestamp;
        let levelCell = row.insertCell();
        levelCell.textContent = log.level;
        levelCell.className = 'log-level-' + log.level;
        row.insertCell().innerHTML = `<pre>${escapeHtml(log.message)}</pre>`;
      });
    });
}

function escapeHtml(unsafe) {
  if (unsafe === null || unsafe === undefined) return '';
  return unsafe.toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

// Function to toggle fields enabled/disabled state based on channel checkbox
function toggleChannelFields(channelId, enabled) {
  const channelCard = document.getElementById(channelId);
  const inputs = channelCard.querySelectorAll('input[type="text"], input[type="password"], textarea');
  const labels = channelCard.querySelectorAll('label:not(:has(input[type="checkbox"]))');

  inputs.forEach(input => {
    input.disabled = !enabled;
    if (!enabled) {
      input.classList.add('disabled-input');
    } else {
      input.classList.remove('disabled-input');
    }
  });

  labels.forEach(label => {
    if (!enabled) {
      label.classList.add('disabled');
    } else {
      label.classList.remove('disabled');
    }
  });
}

document.addEventListener('DOMContentLoaded', function() {
  const themeToggleButton = document.getElementById('themeToggle');
  const currentTheme = localStorage.getItem('theme') || document.getElementById('gui_theme_input').value || 'dark';
  document.body.className = currentTheme === 'light' ? 'light-mode' : '';
  document.getElementById('gui_theme_input').value = currentTheme;

  themeToggleButton.addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
    let theme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
    localStorage.setItem('theme', theme);
    document.getElementById('gui_theme_input').value = theme;
  });

  // Handle AI options enable/disable
  document.getElementById('enable_ai').addEventListener('change', function() {
    const enableAiCheckbox = document.getElementById('enable_ai');
    const showOriginalCheckbox = document.getElementById('show_original');
    const showOriginalLabel = document.getElementById('show_original_label');
    const prepromptTextarea = document.getElementById('preprompt');
    const prepromptLabel = document.getElementById('preprompt_label');

    if (enableAiCheckbox.checked) {
      showOriginalCheckbox.disabled = false;
      showOriginalLabel.classList.remove('disabled');
      prepromptTextarea.disabled = false;
      prepromptLabel.classList.remove('disabled');
    } else {
      showOriginalCheckbox.checked = true;
      showOriginalCheckbox.disabled = true;
      showOriginalLabel.classList.add('disabled');
      prepromptTextarea.disabled = true;
      prepromptLabel.classList.add('disabled');
    }
  });

  // Initialize AI options state
  const enableAiCheckbox = document.getElementById('enable_ai');
  if (!enableAiCheckbox.checked) {
    const showOriginalCheckbox = document.getElementById('show_original');
    const showOriginalLabel = document.getElementById('show_original_label');
    const prepromptTextarea = document.getElementById('preprompt');
    const prepromptLabel = document.getElementById('preprompt_label');

    showOriginalCheckbox.checked = true;
    showOriginalCheckbox.disabled = true;
    showOriginalLabel.classList.add('disabled');
    prepromptTextarea.disabled = true;
    prepromptLabel.classList.add('disabled');
  }

  // Add event listeners for notification channel toggles
  const channelToggles = {
    'telegram-channel': document.querySelector('input[name="channel_telegram_enabled"]'),
    'discord-channel': document.querySelector('input[name="channel_discord_enabled"]'),
    'slack-channel': document.querySelector('input[name="channel_slack_enabled"]'),
    'gotify-channel': document.querySelector('input[name="channel_gotify_enabled"]')
  };

  // Set up event listeners for each channel toggle
  for (const [channelId, toggle] of Object.entries(channelToggles)) {
    if (toggle) {
      // Initialize state
      toggleChannelFields(channelId, toggle.checked);

      // Add change listener
      toggle.addEventListener('change', function() {
        toggleChannelFields(channelId, this.checked);
      });
    }
  }

  // Tab initialization
  const params = new URLSearchParams(window.location.search);
  const activeTabFromUrl = params.get('active');
  const savedTab = localStorage.getItem('activeTab');
  let initialTab = 'dashboard';

  if (window.location.hash) {
    const hashTab = window.location.hash.substring(1);
    if (document.getElementById(hashTab) || document.querySelector(`.tab-button[onclick*="('${hashTab}')"]`)) {
      initialTab = hashTab;
    } else if (document.getElementById('settings-' + hashTab)) {
      initialTab = 'settings';
    }
  } else if (activeTabFromUrl && document.getElementById(activeTabFromUrl)) {
    initialTab = activeTabFromUrl;
  } else if (savedTab && document.getElementById(savedTab)) {
    initialTab = savedTab;
  }

  const tabButtonToClick = document.querySelector(`.tab-button[onclick*="('${initialTab}')"]`);
  if (tabButtonToClick) {
    tabButtonToClick.click();
  } else if (document.querySelector('.tab-button')) {
    document.querySelector('.tab-button').click();
  }

  if (initialTab === 'dashboard') fetchNotifications();
  if (initialTab === 'logs') fetchLogs();

  setInterval(function() {
    if (document.getElementById('logs').style.display === 'block') {
      fetchLogs();
    }
    if (document.getElementById('dashboard').style.display === 'block') {
      fetchNotifications();
    }
}, 5000);

  if (initialTab === 'settings' && window.location.hash) {
    const element = document.getElementById(window.location.hash.substring(1));
    if (element) element.scrollIntoView({behavior: 'smooth'});
  }
});
