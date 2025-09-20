/**
 * PlotX Enterprise JavaScript/Node.js SDK Example
 * ===============================================
 *
 * Comprehensive examples for using PlotX Enterprise API
 * in JavaScript/Node.js applications.
 */

const axios = require('axios');

/**
 * PlotX Enterprise JavaScript Client
 */
class PlotXEnterpriseClient {
    constructor(baseUrl = 'http://localhost:8888', options = {}) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.token = null;
        this.axios = axios.create({
            baseURL: this.baseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Add request interceptor for authentication
        this.axios.interceptors.request.use(config => {
            if (this.token) {
                config.headers.Authorization = `Bearer ${this.token}`;
            }
            return config;
        });

        // Add response interceptor for error handling
        this.axios.interceptors.response.use(
            response => response,
            error => {
                const errorResponse = {
                    success: false,
                    error: error.response?.data?.error || error.message,
                    status_code: error.response?.status || 500,
                    data: null
                };
                return Promise.reject(errorResponse);
            }
        );
    }

    /**
     * Authenticate with username and password
     */
    async authenticate(username, password) {
        try {
            const response = await this.axios.post('/api/auth/login', {
                username,
                password
            });

            this.token = response.data.token;
            return {
                success: true,
                data: response.data,
                status_code: response.status
            };
        } catch (error) {
            return error;
        }
    }

    /**
     * Check server health
     */
    async healthCheck() {
        try {
            const response = await this.axios.get('/health');
            return {
                success: true,
                data: response.data,
                status_code: response.status
            };
        } catch (error) {
            return error;
        }
    }

    /**
     * Get system metrics
     */
    async getMetrics() {
        try {
            const response = await this.axios.get('/metrics');
            return {
                success: true,
                data: response.data,
                status_code: response.status
            };
        } catch (error) {
            return error;
        }
    }

    /**
     * Create enterprise chart
     */
    async createChart(chartConfig) {
        try {
            const response = await this.axios.post('/api/charts', chartConfig);
            return {
                success: true,
                data: response.data,
                status_code: response.status
            };
        } catch (error) {
            return error;
        }
    }

    /**
     * Get chart by ID
     */
    async getChart(chartId) {
        try {
            const response = await this.axios.get(`/api/charts/${chartId}`);
            return {
                success: true,
                data: response.data,
                status_code: response.status
            };
        } catch (error) {
            return error;
        }
    }

    /**
     * List all charts
     */
    async listCharts() {
        try {
            const response = await this.axios.get('/api/charts');
            return {
                success: true,
                data: response.data,
                status_code: response.status
            };
        } catch (error) {
            return error;
        }
    }

    /**
     * List users (admin only)
     */
    async listUsers() {
        try {
            const response = await this.axios.get('/api/users');
            return {
                success: true,
                data: response.data,
                status_code: response.status
            };
        } catch (error) {
            return error;
        }
    }
}

/**
 * Example: Basic usage
 */
async function basicUsageExample() {
    console.log('📘 Basic Usage Example');
    console.log('-'.repeat(30));

    const client = new PlotXEnterpriseClient('http://localhost:8888');

    // Authenticate
    const authResult = await client.authenticate('admin@company.com', 'password123');
    if (!authResult.success) {
        console.log('❌ Authentication failed:', authResult.error);
        return;
    }

    console.log('✅ Authentication successful');
    console.log(`   User ID: ${authResult.data.user_id}`);
    console.log(`   Roles: ${authResult.data.roles.join(', ')}`);

    // Health check
    const health = await client.healthCheck();
    if (health.success) {
        console.log(`✅ Server healthy: ${health.data.status}`);
        console.log(`   Version: ${health.data.version}`);
    }

    console.log();
}

/**
 * Example: Executive dashboard creation
 */
async function executiveDashboardExample() {
    console.log('📊 Executive Dashboard Example');
    console.log('-'.repeat(30));

    const client = new PlotXEnterpriseClient();
    await client.authenticate('admin@company.com', 'password123');

    const dashboardConfig = {
        type: 'executive_dashboard',
        title: 'Q4 2024 Executive Dashboard',
        security_level: 'confidential',
        compliance_tags: ['Executive Reporting', 'Board Review'],
        kpis: {
            'Revenue Growth': {
                value: 15.7,
                target: 15.0,
                status: 'good'
            },
            'Customer Acquisition': {
                value: 1250,
                target: 1500,
                status: 'warning'
            },
            'Market Share': {
                value: 23.4,
                target: 25.0,
                status: 'warning'
            },
            'Employee Satisfaction': {
                value: 8.2,
                target: 8.5,
                status: 'good'
            }
        }
    };

    const result = await client.createChart(dashboardConfig);
    if (result.success) {
        console.log('✅ Executive dashboard created!');
        console.log(`   Chart ID: ${result.data.id}`);
        console.log(`   Security Level: ${result.data.security_level}`);
        console.log(`   Compliance Tags: ${result.data.compliance_tags.join(', ')}`);
    } else {
        console.log('❌ Dashboard creation failed:', result.error);
    }

    console.log();
}

/**
 * Example: Financial analytics
 */
async function financialAnalyticsExample() {
    console.log('💰 Financial Analytics Example');
    console.log('-'.repeat(30));

    const client = new PlotXEnterpriseClient();
    await client.authenticate('admin@company.com', 'password123');

    const financialConfig = {
        type: 'financial_analytics',
        title: '2024 Revenue Waterfall Analysis',
        security_level: 'confidential',
        compliance_tags: ['SOX', 'Financial Reporting'],
        categories: ['Q1 Base', 'Q2 Growth', 'Q3 Investments', 'Q4 Returns', 'Year End'],
        values: [10000000, 2500000, -1800000, 3200000, 13900000]
    };

    const result = await client.createChart(financialConfig);
    if (result.success) {
        console.log('✅ Financial chart created!');
        console.log(`   Chart ID: ${result.data.id}`);
        console.log(`   SOX Compliant: ${result.data.compliance_tags.includes('SOX')}`);
    } else {
        console.log('❌ Financial chart failed:', result.error);
    }

    console.log();
}

/**
 * Example: Batch operations with Promise.all
 */
async function batchOperationsExample() {
    console.log('📦 Batch Operations Example');
    console.log('-'.repeat(30));

    const client = new PlotXEnterpriseClient();
    await client.authenticate('admin@company.com', 'password123');

    const chartsToCreate = [
        {
            type: 'executive_dashboard',
            title: 'Sales Performance Dashboard',
            security_level: 'internal',
            kpis: {
                'Monthly Sales': { value: 850000, target: 800000, status: 'good' },
                'New Customers': { value: 127, target: 150, status: 'warning' }
            }
        },
        {
            type: 'compliance',
            title: 'Security Compliance Check',
            security_level: 'internal',
            metrics: {
                'Data Security': { score: 94, threshold_good: 90 },
                'Access Control': { score: 87, threshold_good: 85 }
            }
        },
        {
            type: 'risk_analysis',
            title: 'Monthly Risk Assessment',
            security_level: 'confidential',
            risks: [
                { name: 'Cyber Risk', probability: 65, impact: 80, category: 'Technology' },
                { name: 'Market Risk', probability: 45, impact: 70, category: 'Financial' }
            ]
        }
    ];

    console.log(`Creating ${chartsToCreate.length} charts concurrently...`);

    try {
        const results = await Promise.all(
            chartsToCreate.map(config => client.createChart(config))
        );

        const successful = results.filter(r => r.success);
        console.log(`✅ Created ${successful.length}/${results.length} charts`);

        successful.forEach((result, index) => {
            console.log(`   ${chartsToCreate[index].title}: ${result.data.id}`);
        });

        const failed = results.filter(r => !r.success);
        if (failed.length > 0) {
            console.log('❌ Failed charts:');
            failed.forEach((result, index) => {
                const failedIndex = results.findIndex(r => r === result);
                console.log(`   ${chartsToCreate[failedIndex].title}: ${result.error}`);
            });
        }
    } catch (error) {
        console.log('❌ Batch operation failed:', error);
    }

    console.log();
}

/**
 * Example: Real-time monitoring with intervals
 */
async function realTimeMonitoringExample() {
    console.log('⚡ Real-time Monitoring Example');
    console.log('-'.repeat(30));

    const client = new PlotXEnterpriseClient();
    await client.authenticate('admin@company.com', 'password123');

    let monitoringCount = 0;
    const maxChecks = 5;

    console.log('Starting real-time monitoring...');

    const interval = setInterval(async () => {
        try {
            const metrics = await client.getMetrics();
            if (metrics.success) {
                const data = metrics.data;
                console.log(`[${new Date().toISOString()}] System Status:`);
                console.log(`   CPU: ${data.cpu_usage}%`);
                console.log(`   Memory: ${data.memory_usage}%`);
                console.log(`   Active Sessions: ${data.active_sessions}`);
                console.log(`   Total Users: ${data.total_users}`);
            }

            monitoringCount++;
            if (monitoringCount >= maxChecks) {
                clearInterval(interval);
                console.log('✅ Monitoring completed');
            }
        } catch (error) {
            console.log('❌ Monitoring error:', error);
            clearInterval(interval);
        }
    }, 2000); // Check every 2 seconds

    // Return a promise that resolves when monitoring is done
    return new Promise(resolve => {
        setTimeout(resolve, maxChecks * 2000 + 1000);
    });
}

/**
 * Example: Error handling and retry logic
 */
async function errorHandlingExample() {
    console.log('🛡️ Error Handling Example');
    console.log('-'.repeat(30));

    const client = new PlotXEnterpriseClient();
    await client.authenticate('admin@company.com', 'password123');

    /**
     * Retry function with exponential backoff
     */
    async function createChartWithRetry(config, maxRetries = 3) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const result = await client.createChart(config);
                if (result.success) {
                    return result;
                }

                if (attempt === maxRetries) {
                    return result; // Return the final failed result
                }

                console.log(`   Attempt ${attempt} failed: ${result.error}`);
                const delay = Math.pow(2, attempt - 1) * 1000; // Exponential backoff
                console.log(`   Retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            } catch (error) {
                if (attempt === maxRetries) {
                    return error;
                }
                console.log(`   Attempt ${attempt} failed: ${error.error}`);
            }
        }
    }

    // Test error scenarios
    const errorTests = [
        {
            name: 'Invalid Chart Type',
            config: {
                type: 'invalid_type',
                title: 'Test Chart'
            }
        },
        {
            name: 'Empty Title',
            config: {
                type: 'executive_dashboard',
                title: ''
            }
        }
    ];

    for (const test of errorTests) {
        console.log(`Testing: ${test.name}`);
        const result = await createChartWithRetry(test.config);

        if (result.success) {
            console.log('   ⚠️ Unexpected success - should have failed');
        } else {
            console.log(`   ✅ Correctly failed: ${result.error}`);
        }
    }

    console.log();
}

/**
 * Example: Integration with Express.js web framework
 */
function expressIntegrationExample() {
    console.log('🌐 Express.js Integration Example');
    console.log('-'.repeat(30));

    // This is a conceptual example - requires Express.js to be installed
    const expressCode = `
const express = require('express');
const { PlotXEnterpriseClient } = require('./plotx-enterprise-client');

const app = express();
app.use(express.json());

// Initialize PlotX client
const plotxClient = new PlotXEnterpriseClient(
    process.env.PLOTX_API_URL || 'http://localhost:8888'
);

// Middleware to authenticate PlotX client
app.use(async (req, res, next) => {
    if (!plotxClient.token) {
        await plotxClient.authenticate(
            process.env.PLOTX_USERNAME,
            process.env.PLOTX_PASSWORD
        );
    }
    next();
});

// API endpoint to create dashboard
app.post('/api/dashboard', async (req, res) => {
    try {
        const { title, kpis, securityLevel } = req.body;

        const result = await plotxClient.createChart({
            type: 'executive_dashboard',
            title,
            kpis,
            security_level: securityLevel || 'internal'
        });

        if (result.success) {
            res.json({
                success: true,
                chartId: result.data.id,
                message: 'Dashboard created successfully'
            });
        } else {
            res.status(400).json({
                success: false,
                error: result.error
            });
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// API endpoint to get system status
app.get('/api/status', async (req, res) => {
    try {
        const [health, metrics] = await Promise.all([
            plotxClient.healthCheck(),
            plotxClient.getMetrics()
        ]);

        res.json({
            server_health: health.success ? health.data : null,
            system_metrics: metrics.success ? metrics.data : null
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => {
    console.log('Express server running on port 3000');
});
`;

    console.log('Express.js integration code example:');
    console.log(expressCode);
    console.log();
}

/**
 * Main function to run all examples
 */
async function main() {
    console.log('🚀 PlotX Enterprise JavaScript SDK Examples');
    console.log('='.repeat(50));

    try {
        await basicUsageExample();
        await executiveDashboardExample();
        await financialAnalyticsExample();
        await batchOperationsExample();
        await realTimeMonitoringExample();
        await errorHandlingExample();
        expressIntegrationExample();

        console.log('🎉 All JavaScript examples completed!');
        console.log('\n📚 Next Steps:');
        console.log('• Install the SDK: npm install plotx-enterprise-client');
        console.log('• Review the API documentation');
        console.log('• Integrate into your Node.js applications');
        console.log('• Use with React, Vue, or other frontend frameworks');

    } catch (error) {
        console.log('❌ Examples failed:', error);
        console.log('\nTroubleshooting:');
        console.log('• Ensure PlotX Enterprise server is running');
        console.log('• Check your authentication credentials');
        console.log('• Verify network connectivity');
        console.log('• Install required dependencies: npm install axios');
    }
}

// Export for use as module
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        PlotXEnterpriseClient,
        basicUsageExample,
        executiveDashboardExample,
        financialAnalyticsExample,
        batchOperationsExample,
        realTimeMonitoringExample,
        errorHandlingExample
    };
}

// Run examples if called directly
if (require.main === module) {
    main();
}