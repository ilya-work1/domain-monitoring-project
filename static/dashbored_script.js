document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const domainInput = document.getElementById('domainInput');
    const addButton = document.querySelector('.add-button');
    const fileUpload = document.getElementById('file-upload');
    const refreshAllButton = document.querySelector('.refresh-button');
    const tableBody = document.getElementById('domainsTableBody');
    const logoutButton = document.querySelector('.header-nav .logout-button');
    
    // load the domains data on page load
    getDomainsData()
    
    // Logout Button
    logoutButton.addEventListener('click', function() {
        window.location.href = '/logout';
    });

    // Add Domain Button
    addButton.addEventListener('click', function() {
        const domain = domainInput.value.trim();
        if (domain) {
            checkMultipleDomains([domain]);
            domainInput.value = ''; // Clear input after adding
        }
    });

    // Enter key functionality for domain input
    domainInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const domain = this.value.trim();
            if (domain) {
                checkMultipleDomains([domain]);
                this.value = '';
            }
        }
    });

    
    fileUpload.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = async function(e) {
                const domains = e.target.result.split('\n')
                    .map(domain => domain.trim())
                    .filter(domain => domain);
                
                // Basic domain validation regex
                const domainRegex = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
                
                const validDomains = domains.filter(domain => domainRegex.test(domain));
                const invalidDomains = domains.filter(domain => !domainRegex.test(domain));
                
                // Create confirmation message
                let confirmMessage = `Found ${domains.length} domains:\n`;
                confirmMessage += `✓ ${validDomains.length} valid domains\n`;
                confirmMessage += `✗ ${invalidDomains.length} invalid domains\n\n`;
                
                if (invalidDomains.length > 0) {
                    confirmMessage += 'Invalid domains:\n';
                    invalidDomains.forEach(domain => {
                        confirmMessage += `- ${domain}\n`;
                    });
                    confirmMessage += '\n';
                }
                
                confirmMessage += 'Would you like to proceed with checking the valid domains?';
                
                // Show confirmation dialog
                if (validDomains.length > 0 && confirm(confirmMessage)) {
                    // Send only valid domains to be checked
                    checkMultipleDomains(validDomains);
                }
                
                // Reset file input
                fileUpload.value = '';
            };
            reader.readAsText(file);
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
                },
                body: JSON.stringify({ domains: domains })
            });
            
            if (!response.ok) throw new Error(`Failed to check domains. Status: ${response.status}`);
            
            const results = await response.json();
            results.forEach(result => addOrUpdateDomainRow(result));
        } catch (error) {
            console.error('Error:', error);
            alert('Error checking multiple domains. Please try again. Details: ' + error.message);
        }
    }

    // Function to display domains data from database user
    async function getDomainsData(){
        try {
            const response = await fetch('/get_domains', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                
            });
            if (!response.ok) throw new Error(`Failed to check domains. Status: ${response.status}`);
            
            const results = await response.json();
            results.forEach(result => addOrUpdateDomainRow(result));
        } catch (error) {
            console.error('Error:', error);
            alert('Error checking multiple domains. Please try again. Details: ' + error.message);
        }
    }

  

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
            <td class = "domain-name">${result.url}</td>
            <td><span class="status-badge ${result.status_code === 'OK' ? 'active' : 'failed'}">${result.status_code}</span></td>
            <td><span class="ssl-badge ${result.ssl_status}">${result.ssl_status}</span></td>
            <td>${result.expiration_date}</td><td>${result.issuer || 'Unknown'}</td>
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
        checkButton.addEventListener('click', () => checkMultipleDomains([domain]));

        const editButton = row.querySelector('.edit-button');
        editButton.addEventListener('click', function() {
            const newDomain = prompt('Edit domain name:', domain);
            if (newDomain && newDomain.trim() && newDomain !== domain) {
                checkMultipleDomains([newDomain.trim()]);
                row.remove();
            }
        });

        const deleteButton = row.querySelector('.delete-button');
        deleteButton.addEventListener('click', async function() {
            if (confirm('Are you sure you want to delete this domain?')) {
                try {
                    // Envoie une requête au serveur pour supprimer le domaine
                    const domainElement = row.querySelector('.domain-name'); 
                    const domain = encodeURIComponent(domainElement.innerHTML.trim());
                    console.log(domain);
                    const response = await fetch(`/remove_domain?domain=${domain}`, {
                        method: 'DELETE', // DELETE sans body
                    });
        
                    if (response.ok) {
                        // Si la suppression côté serveur réussit, on enlève la ligne de l'interface
                        row.remove();
                        alert('The domain has been successfully deleted.');
                    } else {
                        // Gérer les erreurs renvoyées par le serveur
                        const errorMessage = await response.json();
                        alert(`Failed to delete domain: ${errorMessage}`);
                    }
                } catch (error) {
                    // Gérer les erreurs réseau ou autres
                    console.error('Error:', error);
                    alert('An error occurred while trying to delete the domain.');
                }
            }
        });
        
    }
});