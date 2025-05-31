#!/usr/bin/env python3
"""
Interactive API Documentation Generator for BDC Backend

This script generates interactive HTML documentation from the OpenAPI specification
and provides a local server to view the documentation.

Usage:
    python generate_interactive_docs.py [--port 8080] [--output docs/]
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
from datetime import datetime

def load_openapi_spec(spec_file):
    """Load OpenAPI specification from YAML file."""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: OpenAPI specification file '{spec_file}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)

def generate_html_documentation(spec, output_dir):
    """Generate interactive HTML documentation."""
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate main HTML file
    html_content = generate_main_html(spec)
    
    # Write HTML file
    html_file = output_dir / 'index.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Generate CSS
    css_content = generate_css()
    css_file = output_dir / 'styles.css'
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # Generate JavaScript
    js_content = generate_javascript()
    js_file = output_dir / 'script.js'
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    # Copy OpenAPI spec as JSON for JavaScript consumption
    spec_file = output_dir / 'openapi.json'
    with open(spec_file, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    print(f"Documentation generated in: {output_dir}")
    return html_file

def generate_main_html(spec):
    """Generate the main HTML document."""
    
    info = spec.get('info', {})
    servers = spec.get('servers', [])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{info.get('title', 'API Documentation')}</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.28.0/themes/prism.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.28.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.28.0/plugins/autoloader/prism-autoloader.min.js"></script>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>{info.get('title', 'API Documentation')}</h1>
            <p class="version">Version: {info.get('version', '1.0.0')}</p>
            <p class="description">{info.get('description', '')}</p>
            
            <div class="servers">
                <h3>Base URLs:</h3>
                <ul>
"""

    for server in servers:
        html += f'                    <li><code>{server.get("url", "")}</code> - {server.get("description", "")}</li>\n'

    html += """                </ul>
            </div>
        </header>

        <nav class="sidebar">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search endpoints...">
            </div>
            
            <div class="filter-buttons">
                <button class="filter-btn active" data-method="all">All</button>
                <button class="filter-btn" data-method="GET">GET</button>
                <button class="filter-btn" data-method="POST">POST</button>
                <button class="filter-btn" data-method="PUT">PUT</button>
                <button class="filter-btn" data-method="DELETE">DELETE</button>
            </div>
            
            <div id="endpoints-nav" class="endpoints-nav">
                <!-- Endpoints will be populated by JavaScript -->
            </div>
        </nav>

        <main class="content">
            <div id="overview" class="section">
                <h2>Overview</h2>
                <div class="overview-stats">
                    <div class="stat-card">
                        <h3 id="total-endpoints">0</h3>
                        <p>Total Endpoints</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="total-tags">0</h3>
                        <p>Categories</p>
                    </div>
                    <div class="stat-card">
                        <h3 id="auth-required">0</h3>
                        <p>Auth Required</p>
                    </div>
                </div>
                
                <div class="quick-start">
                    <h3>Quick Start</h3>
                    <ol>
                        <li>Authenticate using the <code>/auth/login</code> endpoint</li>
                        <li>Include the JWT token in the Authorization header: <code>Bearer &lt;token&gt;</code></li>
                        <li>Make requests to the desired endpoints</li>
                        <li>Handle responses according to the documented schemas</li>
                    </ol>
                </div>
            </div>
            
            <div id="endpoints-content">
                <!-- Endpoint details will be populated by JavaScript -->
            </div>
        </main>
    </div>

    <script src="script.js"></script>
</body>
</html>"""
    
    return html

def generate_css():
    """Generate CSS styles for the documentation."""
    
    return """/* API Documentation Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    display: grid;
    grid-template-columns: 300px 1fr;
    grid-template-rows: auto 1fr;
    grid-template-areas: 
        "header header"
        "sidebar content";
    min-height: 100vh;
}

.header {
    grid-area: header;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
}

.version {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 1rem;
}

.description {
    font-size: 1.1rem;
    opacity: 0.95;
    margin-bottom: 1.5rem;
}

.servers {
    background: rgba(255,255,255,0.1);
    padding: 1rem;
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.servers h3 {
    margin-bottom: 0.5rem;
    font-size: 1.1rem;
}

.servers ul {
    list-style: none;
}

.servers li {
    margin-bottom: 0.5rem;
}

.servers code {
    background: rgba(255,255,255,0.2);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: 'Monaco', 'Consolas', monospace;
}

.sidebar {
    grid-area: sidebar;
    background: white;
    border-right: 1px solid #e9ecef;
    padding: 1.5rem;
    overflow-y: auto;
    max-height: calc(100vh - 200px);
}

.search-box {
    margin-bottom: 1rem;
}

.search-box input {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}

.search-box input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.filter-btn {
    padding: 0.5rem 1rem;
    border: 2px solid #e9ecef;
    background: white;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s ease;
}

.filter-btn:hover {
    border-color: #667eea;
    color: #667eea;
}

.filter-btn.active {
    background: #667eea;
    border-color: #667eea;
    color: white;
}

.endpoints-nav {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.endpoint-link {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    text-decoration: none;
    color: #333;
    transition: all 0.3s ease;
    cursor: pointer;
}

.endpoint-link:hover {
    background: #f8f9fa;
    border-color: #667eea;
    transform: translateX(5px);
}

.method-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 0.75rem;
    min-width: 60px;
    text-align: center;
}

.method-GET { background: #28a745; color: white; }
.method-POST { background: #ffc107; color: #212529; }
.method-PUT { background: #17a2b8; color: white; }
.method-DELETE { background: #dc3545; color: white; }
.method-PATCH { background: #6f42c1; color: white; }

.endpoint-path {
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.9rem;
    flex: 1;
}

.content {
    grid-area: content;
    padding: 2rem;
    overflow-y: auto;
    background: white;
    margin: 1rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.section {
    margin-bottom: 3rem;
}

.section h2 {
    font-size: 2rem;
    margin-bottom: 1.5rem;
    color: #2c3e50;
    border-bottom: 3px solid #667eea;
    padding-bottom: 0.5rem;
}

.overview-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.stat-card h3 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.stat-card p {
    font-size: 1.1rem;
    opacity: 0.9;
}

.quick-start {
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 12px;
    border-left: 5px solid #667eea;
}

.quick-start h3 {
    color: #2c3e50;
    margin-bottom: 1rem;
    font-size: 1.5rem;
}

.quick-start ol {
    padding-left: 1.5rem;
}

.quick-start li {
    margin-bottom: 0.75rem;
    font-size: 1.1rem;
}

.quick-start code {
    background: #e9ecef;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: 'Monaco', 'Consolas', monospace;
    color: #e83e8c;
}

.endpoint-detail {
    margin-bottom: 3rem;
    padding: 2rem;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    background: #fafbfc;
}

.endpoint-header {
    display: flex;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e9ecef;
}

.endpoint-header h3 {
    font-size: 1.5rem;
    margin-left: 1rem;
    color: #2c3e50;
}

.endpoint-description {
    color: #6c757d;
    font-size: 1.1rem;
    margin-bottom: 1.5rem;
    line-height: 1.7;
}

.endpoint-section {
    margin-bottom: 2rem;
}

.endpoint-section h4 {
    font-size: 1.2rem;
    margin-bottom: 1rem;
    color: #495057;
    border-left: 4px solid #667eea;
    padding-left: 1rem;
}

.parameter-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.parameter-table th,
.parameter-table td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
}

.parameter-table th {
    background: #f8f9fa;
    font-weight: 600;
    color: #495057;
}

.parameter-table tbody tr:hover {
    background: #f8f9fa;
}

.required-badge {
    background: #dc3545;
    color: white;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}

.optional-badge {
    background: #6c757d;
    color: white;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}

.code-block {
    background: #2d3748;
    color: #e2e8f0;
    padding: 1.5rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1rem 0;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.9rem;
    line-height: 1.5;
}

.response-section {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    margin-bottom: 1rem;
}

.response-code {
    display: inline-flex;
    align-items: center;
    margin-bottom: 1rem;
}

.status-badge {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    margin-right: 1rem;
}

.status-200 { background: #d4edda; color: #155724; }
.status-201 { background: #d4edda; color: #155724; }
.status-400 { background: #f8d7da; color: #721c24; }
.status-401 { background: #f8d7da; color: #721c24; }
.status-403 { background: #f8d7da; color: #721c24; }
.status-404 { background: #f8d7da; color: #721c24; }
.status-500 { background: #f8d7da; color: #721c24; }

.hidden {
    display: none !important;
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        grid-template-columns: 1fr;
        grid-template-areas: 
            "header"
            "content";
    }
    
    .sidebar {
        display: none;
    }
    
    .header {
        padding: 1rem;
    }
    
    .header h1 {
        font-size: 2rem;
    }
    
    .content {
        margin: 0.5rem;
        padding: 1rem;
    }
    
    .overview-stats {
        grid-template-columns: 1fr;
    }
    
    .filter-buttons {
        justify-content: center;
    }
}

/* Print Styles */
@media print {
    .sidebar,
    .filter-buttons,
    .search-box {
        display: none;
    }
    
    .container {
        grid-template-columns: 1fr;
        grid-template-areas: 
            "header"
            "content";
    }
    
    .content {
        margin: 0;
        box-shadow: none;
    }
}"""

def generate_javascript():
    """Generate JavaScript for interactive functionality."""
    
    return """// API Documentation Interactive Script

let apiSpec = null;
let filteredEndpoints = [];
let currentFilter = 'all';

// Initialize the documentation
document.addEventListener('DOMContentLoaded', function() {
    loadApiSpec();
    setupEventListeners();
});

function loadApiSpec() {
    fetch('openapi.json')
        .then(response => response.json())
        .then(spec => {
            apiSpec = spec;
            processApiSpec();
            renderOverview();
            renderEndpoints();
            setupNavigation();
        })
        .catch(error => {
            console.error('Error loading API specification:', error);
        });
}

function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }

    // Filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(b => b.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            // Apply filter
            currentFilter = this.dataset.method;
            filterEndpoints();
        });
    });
}

function processApiSpec() {
    if (!apiSpec || !apiSpec.paths) return;

    filteredEndpoints = [];
    
    Object.keys(apiSpec.paths).forEach(path => {
        Object.keys(apiSpec.paths[path]).forEach(method => {
            if (method !== 'parameters') {
                const endpoint = apiSpec.paths[path][method];
                filteredEndpoints.push({
                    method: method.toUpperCase(),
                    path: path,
                    summary: endpoint.summary || '',
                    description: endpoint.description || '',
                    tags: endpoint.tags || [],
                    security: endpoint.security || [],
                    parameters: endpoint.parameters || [],
                    requestBody: endpoint.requestBody || null,
                    responses: endpoint.responses || {},
                    operationId: endpoint.operationId || `${method}${path.replace(/[^a-zA-Z0-9]/g, '')}`
                });
            }
        });
    });
}

function renderOverview() {
    // Update stats
    const totalEndpoints = filteredEndpoints.length;
    const totalTags = new Set(filteredEndpoints.flatMap(e => e.tags)).size;
    const authRequired = filteredEndpoints.filter(e => e.security && e.security.length > 0).length;

    document.getElementById('total-endpoints').textContent = totalEndpoints;
    document.getElementById('total-tags').textContent = totalTags;
    document.getElementById('auth-required').textContent = authRequired;
}

function renderEndpoints() {
    const container = document.getElementById('endpoints-content');
    if (!container) return;

    container.innerHTML = '';

    // Group endpoints by tags
    const groupedEndpoints = {};
    filteredEndpoints.forEach(endpoint => {
        if (endpoint.tags && endpoint.tags.length > 0) {
            endpoint.tags.forEach(tag => {
                if (!groupedEndpoints[tag]) {
                    groupedEndpoints[tag] = [];
                }
                groupedEndpoints[tag].push(endpoint);
            });
        } else {
            if (!groupedEndpoints['Other']) {
                groupedEndpoints['Other'] = [];
            }
            groupedEndpoints['Other'].push(endpoint);
        }
    });

    // Render each group
    Object.keys(groupedEndpoints).sort().forEach(tag => {
        const section = document.createElement('div');
        section.className = 'section';
        section.id = `tag-${tag.toLowerCase().replace(/\\s+/g, '-')}`;
        
        const header = document.createElement('h2');
        header.textContent = tag;
        section.appendChild(header);

        groupedEndpoints[tag].forEach(endpoint => {
            const endpointDiv = renderEndpointDetail(endpoint);
            section.appendChild(endpointDiv);
        });

        container.appendChild(section);
    });
}

function renderEndpointDetail(endpoint) {
    const div = document.createElement('div');
    div.className = 'endpoint-detail';
    div.id = `endpoint-${endpoint.operationId}`;
    div.dataset.method = endpoint.method;
    div.dataset.path = endpoint.path;

    let html = `
        <div class="endpoint-header">
            <span class="method-badge method-${endpoint.method}">${endpoint.method}</span>
            <code class="endpoint-path">${endpoint.path}</code>
            <h3>${endpoint.summary}</h3>
        </div>
    `;

    if (endpoint.description) {
        html += `<div class="endpoint-description">${endpoint.description}</div>`;
    }

    // Security/Authentication
    if (endpoint.security && endpoint.security.length > 0) {
        html += `
            <div class="endpoint-section">
                <h4>🔒 Authentication Required</h4>
                <p>This endpoint requires authentication. Include your JWT token in the Authorization header:</p>
                <div class="code-block">Authorization: Bearer &lt;your-jwt-token&gt;</div>
            </div>
        `;
    }

    // Parameters
    if (endpoint.parameters && endpoint.parameters.length > 0) {
        html += renderParameters(endpoint.parameters);
    }

    // Request Body
    if (endpoint.requestBody) {
        html += renderRequestBody(endpoint.requestBody);
    }

    // Responses
    if (endpoint.responses) {
        html += renderResponses(endpoint.responses);
    }

    // Example requests
    html += renderExampleRequests(endpoint);

    div.innerHTML = html;
    return div;
}

function renderParameters(parameters) {
    let html = `
        <div class="endpoint-section">
            <h4>📋 Parameters</h4>
            <table class="parameter-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Location</th>
                        <th>Required</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
    `;

    parameters.forEach(param => {
        const required = param.required ? 
            '<span class="required-badge">Required</span>' : 
            '<span class="optional-badge">Optional</span>';
        
        const type = param.schema ? (param.schema.type || 'string') : 'string';
        
        html += `
            <tr>
                <td><code>${param.name}</code></td>
                <td>${type}</td>
                <td>${param.in}</td>
                <td>${required}</td>
                <td>${param.description || ''}</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    return html;
}

function renderRequestBody(requestBody) {
    let html = `
        <div class="endpoint-section">
            <h4>📤 Request Body</h4>
    `;

    if (requestBody.description) {
        html += `<p>${requestBody.description}</p>`;
    }

    if (requestBody.content) {
        Object.keys(requestBody.content).forEach(contentType => {
            html += `
                <h5>Content-Type: ${contentType}</h5>
                <div class="code-block">${JSON.stringify(requestBody.content[contentType].schema || {}, null, 2)}</div>
            `;
        });
    }

    html += '</div>';
    return html;
}

function renderResponses(responses) {
    let html = `
        <div class="endpoint-section">
            <h4>📨 Responses</h4>
    `;

    Object.keys(responses).forEach(statusCode => {
        const response = responses[statusCode];
        html += `
            <div class="response-section">
                <div class="response-code">
                    <span class="status-badge status-${statusCode}">${statusCode}</span>
                    <span>${response.description || ''}</span>
                </div>
        `;

        if (response.content) {
            Object.keys(response.content).forEach(contentType => {
                const schema = response.content[contentType].schema;
                if (schema) {
                    html += `
                        <h6>Content-Type: ${contentType}</h6>
                        <div class="code-block">${JSON.stringify(schema, null, 2)}</div>
                    `;
                }
            });
        }

        html += '</div>';
    });

    html += '</div>';
    return html;
}

function renderExampleRequests(endpoint) {
    let html = `
        <div class="endpoint-section">
            <h4>💡 Example Request</h4>
    `;

    // Generate curl example
    const baseUrl = apiSpec.servers && apiSpec.servers[0] ? apiSpec.servers[0].url : 'https://api.example.com';
    let curlCommand = `curl -X ${endpoint.method} "${baseUrl}${endpoint.path}"`;

    // Add authentication header if required
    if (endpoint.security && endpoint.security.length > 0) {
        curlCommand += ` \\\\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"`;
    }

    // Add content-type header for POST/PUT requests
    if (['POST', 'PUT', 'PATCH'].includes(endpoint.method)) {
        curlCommand += ` \\\\
  -H "Content-Type: application/json"`;
    }

    // Add example request body
    if (endpoint.requestBody && endpoint.requestBody.content) {
        const jsonContent = endpoint.requestBody.content['application/json'];
        if (jsonContent && jsonContent.schema) {
            curlCommand += ` \\\\
  -d '${JSON.stringify(generateExampleFromSchema(jsonContent.schema), null, 2)}'`;
        }
    }

    html += `<div class="code-block">${curlCommand}</div>`;
    html += '</div>';

    return html;
}

function generateExampleFromSchema(schema) {
    if (!schema) return {};

    const example = {};
    
    if (schema.properties) {
        Object.keys(schema.properties).forEach(prop => {
            const propSchema = schema.properties[prop];
            
            if (propSchema.example !== undefined) {
                example[prop] = propSchema.example;
            } else if (propSchema.type === 'string') {
                example[prop] = propSchema.format === 'email' ? 'user@example.com' : `example_${prop}`;
            } else if (propSchema.type === 'integer') {
                example[prop] = 1;
            } else if (propSchema.type === 'number') {
                example[prop] = 1.0;
            } else if (propSchema.type === 'boolean') {
                example[prop] = true;
            } else if (propSchema.type === 'array') {
                example[prop] = [];
            } else {
                example[prop] = {};
            }
        });
    }

    return example;
}

function setupNavigation() {
    const nav = document.getElementById('endpoints-nav');
    if (!nav) return;

    nav.innerHTML = '';

    filteredEndpoints.forEach(endpoint => {
        const link = document.createElement('div');
        link.className = 'endpoint-link';
        link.dataset.method = endpoint.method;
        link.dataset.operationId = endpoint.operationId;
        
        link.innerHTML = `
            <span class="method-badge method-${endpoint.method}">${endpoint.method}</span>
            <span class="endpoint-path">${endpoint.path}</span>
        `;

        link.addEventListener('click', function() {
            const targetElement = document.getElementById(`endpoint-${endpoint.operationId}`);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });

        nav.appendChild(link);
    });
}

function handleSearch(event) {
    const query = event.target.value.toLowerCase();
    filterEndpoints(query);
}

function filterEndpoints(searchQuery = '') {
    const endpointElements = document.querySelectorAll('.endpoint-detail');
    const navElements = document.querySelectorAll('.endpoint-link');

    endpointElements.forEach((element, index) => {
        const method = element.dataset.method;
        const path = element.dataset.path;
        const matchesFilter = currentFilter === 'all' || method === currentFilter;
        const matchesSearch = !searchQuery || 
            path.toLowerCase().includes(searchQuery) ||
            method.toLowerCase().includes(searchQuery);

        if (matchesFilter && matchesSearch) {
            element.classList.remove('hidden');
            if (navElements[index]) {
                navElements[index].classList.remove('hidden');
            }
        } else {
            element.classList.add('hidden');
            if (navElements[index]) {
                navElements[index].classList.add('hidden');
            }
        }
    });
}

// Utility function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Could show a toast notification here
        console.log('Copied to clipboard');
    });
}

// Add copy functionality to code blocks
document.addEventListener('click', function(event) {
    if (event.target.closest('.code-block')) {
        const codeBlock = event.target.closest('.code-block');
        copyToClipboard(codeBlock.textContent);
        
        // Visual feedback
        const originalBg = codeBlock.style.backgroundColor;
        codeBlock.style.backgroundColor = '#4a5568';
        setTimeout(() => {
            codeBlock.style.backgroundColor = originalBg;
        }, 200);
    }
});"""

def serve_documentation(output_dir, port=8080):
    """Serve the documentation using Python's built-in HTTP server."""
    
    class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=output_dir, **kwargs)
    
    try:
        server = HTTPServer(('localhost', port), CustomHTTPRequestHandler)
        print(f"Starting server at http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Open browser automatically
        webbrowser.open(f'http://localhost:{port}')
        
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down server...")
        server.shutdown()
    except OSError as e:
        if e.errno == 48:  # Port already in use
            print(f"Error: Port {port} is already in use. Try a different port with --port option.")
        else:
            print(f"Error starting server: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate interactive API documentation")
    parser.add_argument('--spec', default='openapi_specification.yaml', 
                       help='Path to OpenAPI specification file (default: openapi_specification.yaml)')
    parser.add_argument('--output', default='docs/', 
                       help='Output directory for generated documentation (default: docs/)')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port for local server (default: 8080)')
    parser.add_argument('--no-serve', action='store_true',
                       help='Generate documentation without starting server')
    
    args = parser.parse_args()
    
    # Check if OpenAPI spec exists
    if not os.path.exists(args.spec):
        print(f"Error: OpenAPI specification file '{args.spec}' not found.")
        print("Make sure you have the openapi_specification.yaml file in the current directory.")
        sys.exit(1)
    
    # Load and validate OpenAPI spec
    spec = load_openapi_spec(args.spec)
    
    # Generate documentation
    html_file = generate_html_documentation(spec, args.output)
    
    print(f"✅ Interactive API documentation generated successfully!")
    print(f"📁 Output directory: {args.output}")
    print(f"📄 Main file: {html_file}")
    
    if not args.no_serve:
        print()
        serve_documentation(args.output, args.port)
    else:
        print(f"\\n🌐 To view the documentation, open {html_file} in your browser")
        print(f"Or run: python -m http.server {args.port} --directory {args.output}")

if __name__ == '__main__':
    main()