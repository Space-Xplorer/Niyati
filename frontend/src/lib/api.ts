/**
 * API utility functions for making authenticated requests to the backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';

export interface ApiError {
    message: string;
    status: number;
}

/**
 * Make an authenticated API request
 */
export async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const token = localStorage.getItem('token');
    
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
    };
    
    // Merge with any provided headers
    if (options.headers) {
        Object.assign(headers, options.headers);
    }
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Request failed' }));
        throw {
            message: error.message || `HTTP ${response.status}`,
            status: response.status,
        } as ApiError;
    }
    
    return response.json();
}

/**
 * Login user
 */
export async function login(email: string, password: string) {
    return apiRequest<{
        message: string;
        token: string;
        user: {
            id: number;
            email: string;
            role: string;
            gstin?: string;
        };
    }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });
}

/**
 * Register new user
 */
export async function signup(
    email: string,
    password: string,
    role: string,
    gstin?: string
) {
    return apiRequest<{ message: string }>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password, role, gstin }),
    });
}

/**
 * Get dashboard data
 */
export async function getDashboard() {
    return apiRequest<{
        health_score: number;
        risk_level: string;
        risk_probability: number;
        top_drivers: Array<{
            feature: string;
            contribution: number;
            direction: string;
        }>;
        vendor_risks: Array<any>;
        patterns: {
            circular_trade: number;
            ghost_invoices: number;
            spider_web_involvement: boolean;
        };
    }>('/dashboard');
}

/**
 * Check if token is expired
 */
export function isTokenExpired(token: string): boolean {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp * 1000 < Date.now();
    } catch {
        return true;
    }
}
