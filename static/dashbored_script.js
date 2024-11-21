document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const domainInput = document.getElementById('domainInput');
    const addButton = document.querySelector('.add-button');
    const fileUpload = document.getElementById('file-upload');
    const refreshAllButton = document.querySelector('.refresh-button');
    const tableBody = document.getElementById('domainsTableBody');
    const logoutButton = document.querySelector('.header-nav .logout-button');

    // Logout Button
    logoutButton.addEventListener('click', function() {
        window.location.href = '/logout';
    });

    // Add Domain Button
    addButton.addEventListener('click', function() {
        const domain = domainInput.value.trim();
        if (domain) {
            checkAndAddDomain(domain);
            domainInput.value = ''; // Clear input after adding
        }
    });

    // Enter key functionality for domain input
    domainInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const domain = this.value.trim();
            if (domain) {
                checkAndAddDomain(domain);
                this.value = '';
            }
        }
    });

    // File Upload
    fileUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const domains = e.target.result.split('\n')
                    .map(domain => domain.trim())
                    .filter(domain => domain);
                
                // Send all domains to be checked
                checkMultipleDomains(domains);
            };
            reader.readAsText(file);
            fileUpload.value = ''; // Reset file input
        }
    });

    // Refresh All Button
    refreshAllButton.addEventListener('click', function() {
        const rows = tableBody.getElementsByTagName('tr');
        const domains = Array.from(rows).map(row => row.cells[0].textContent);
        checkMultipleDomains(domains);
    });

    // Function to check multiple domains
    async function checkMultipleDomains(domains) {
        try {
            const response = await fetch('/check_domains', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) throw new Error(`Failed to check domains. Status: ${response.status}`);
            
            const results = await response.json();
            results.forEach(result => updateDomainRow(result));
        } catch (error) {
            console.error('Error:', error);
            alert('Error checking multiple domains. Please try again. Details: ' + error.message);
        }
    }

    // Function to check and add a single domain
    async function checkAndAddDomain(domain) {
        try {
            const response = await fetch('/add_domains', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ domains: [domain] })
            });
            
            if (!response.ok) throw new Error(`Failed to check domain. Status: ${response.status}`);
            
            const responseData = await response.json();
            const result = responseData.results[0];
            addOrUpdateDomainRow(result);
        } catch (error) {
            console.error('Error:', error);
            alert(`Error checking domain "${domain}": ${error.message}`);
        }
    }

    // New function to fetch and display domains
    async function fetchAndDisplayDomains() {
        try {
            const response = await fetch('/check_domains', {
                method: 'POST'
            });
            
            if (!response.ok) throw new Error(`Failed to load domains. Status: ${response.status}`);
            
            const results = await response.json();
            results.forEach(result => addOrUpdateDomainRow(result));
        } catch (error) {
            console.error('Error loading domains:', error);
        }
    }
    fetchAndDisplayDomains();


    // Function to add or update domain row
    function addOrUpdateDomainRow(result) {
        const existingRow = Array.from(tableBody.getElementsByTagName('tr'))
            .find(row => row.cells[0].textContent === result.url);

        if (existingRow) {
            updateDomainRow(result);
        } else {
            const tr = document.createElement('tr');
            tr.innerHTML = createRowHTML(result);
            addRowEventListeners(tr);
            tableBody.appendChild(tr);
        }
    }

    // Function to update existing domain row
    function updateDomainRow(result) {
        const rows = tableBody.getElementsByTagName('tr');
        for (let row of rows) {
            if (row.cells[0].textContent === result.url) {
                row.innerHTML = createRowHTML(result);
                addRowEventListeners(row);
                break;
            }
        }
    }

    

    // Function to create row HTML
    function createRowHTML(result) {
        return `
            <td>${result.url}</td>
            <td><span class="status-badge ${result.status_code === 'OK' ? 'active' : 'failed'}">${result.status_code}</span></td>
            <td><span class="ssl-badge ${result.ssl_status}">${result.ssl_status}</span></td>
            <td>${result.expiration_date}</td><td>${result.issuer || 'Unknown'}</td>
            <td>${(result.last_checked)}</td>
            <td class="actions-cell">
                <button class="button action-button check-button" data-tooltip="Check Status">
                    <span class="icon">⟳</span>
                </button>
                <button class="button action-button edit-button" data-tooltip="Edit Domain">
                    <span class="icon">✎</span>
                </button>
                <button class="button action-button delete-button" data-tooltip="Delete Domain">
                    <span class="icon">×</span>
                </button>
            </td>
        `;
    }

    // Function to add event listeners to row buttons
    function addRowEventListeners(row) {
        const domain = row.cells[0].textContent;
        
        const checkButton = row.querySelector('.check-button');
        checkButton.addEventListener('click', () => checkAndAddDomain(domain));

        const editButton = row.querySelector('.edit-button');
        editButton.addEventListener('click', function() {
            const newDomain = prompt('Edit domain name:', domain);
            if (newDomain && newDomain.trim() && newDomain !== domain) {
                checkAndAddDomain(newDomain.trim());
                row.remove();
            }
        });

        const deleteButton = row.querySelector('.delete-button');
        deleteButton.addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this domain?')) {
                row.remove();
            }
        });
    }
});