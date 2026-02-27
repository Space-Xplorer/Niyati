'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

interface User {
    id: number;
    email: string;
    // backend uses strings like 'Admin' or 'Business_Owner', keep open
    role?: string;
}

interface AuthContextType {
    token: string | null;
    login: (token: string, user: User) => void;
    logout: () => void;
    user: User | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [token, setToken] = useState<string | null>(null);
    const [user, setUser] = useState<User | null>(null);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        // Load auth initial state from localStorage
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser) {
            // Validate token is not expired
            try {
                const payload = JSON.parse(atob(storedToken.split('.')[1]));
                const isExpired = payload.exp * 1000 < Date.now();
                
                if (isExpired) {
                    // Token expired, clear storage and redirect to login
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    if (pathname !== '/login' && pathname !== '/signup' && pathname !== '/') {
                        router.push('/login');
                    }
                    return;
                }
                
                setToken(storedToken);
                setUser(JSON.parse(storedUser));
                // Only redirect from login/signup pages, allow landing page access
                if (pathname === '/login' || pathname === '/signup') {
                    router.push('/dashboard');
                }
            } catch (error) {
                // Invalid token format, clear and redirect
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                if (pathname !== '/login' && pathname !== '/signup' && pathname !== '/') {
                    router.push('/login');
                }
            }
        } else if (pathname !== '/login' && pathname !== '/signup' && pathname !== '/') {
            // require authentication for protected routes only (not landing page)
            router.push('/login');
        }
    }, [pathname, router]);

    const login = (newToken: string, newUser: User) => {
        setToken(newToken);
        setUser(newUser);
        localStorage.setItem('token', newToken);
        localStorage.setItem('user', JSON.stringify(newUser));
        router.push('/dashboard');
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        router.push('/login');
    };

    return (
        <AuthContext.Provider value={{ token, login, logout, user }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
