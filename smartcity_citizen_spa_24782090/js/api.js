// js/api.js
const BASE_URL = 'http://103.151.63.88:8007';

async function requestAPI(endpoint, method = 'GET', bodyData = null) {
    const headers = { 'Content-Type': 'application/json' };
    const accessToken = localStorage.getItem('access_token');
    
    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    const options = { method: method, headers: headers };

    if (bodyData && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(bodyData);
    }

    try {
        return await fetch(`${BASE_URL}${endpoint}`, options);
    } catch (error) {
        console.error('Fetch Error:', error);
        throw error;
    }
}