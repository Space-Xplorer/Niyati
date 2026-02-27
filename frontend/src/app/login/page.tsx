'use client';

import { useState } from 'react';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const url = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
            const response = await fetch(`${url}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'Login failed');
            }

            login(data.token, data.user);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="min-h-screen flex items-center justify-center p-8" style={{ backgroundColor: '#efefef' }}>
            <div className="w-full max-w-md bg-white border border-gray-300 rounded-xl p-8 space-y-6 shadow-lg">
                <div className="text-center">
                    <h1 className="text-3xl font-bold mb-2" style={{ color: '#005b52' }}>Welcome Back</h1>
                    <p className="text-gray-600">Log in to continue building</p>
                </div>

                {error && <div className="text-red-700 bg-red-100 border border-red-300 p-3 rounded">{error}</div>}

                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1" style={{ color: '#005b52' }}>Email</label>
                        <Input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="you@niyati.com"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1" style={{ color: '#005b52' }}>Password</label>
                        <Input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                        />
                    </div>
                    <Button type="submit" className="w-full" isLoading={isLoading}>Log In</Button>
                </form>

                <p className="text-center text-gray-600 text-sm mt-4">
                    Don't have an account? <Link href="/signup" className="font-medium hover:underline" style={{ color: '#005b52' }}>Sign up</Link>
                </p>
            </div>
        </main>
    );
}
