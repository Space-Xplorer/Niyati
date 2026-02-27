'use client';

import { useState } from 'react';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { useAuth } from '@/context/AuthContext';
import Link from 'next/link';
import { login as apiLogin } from '@/lib/api';

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
            const data = await apiLogin(email, password);
            login(data.token, data.user);
        } catch (err: any) {
            setError(err.message || 'Login failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="min-h-screen flex items-center justify-center p-8 bg-[#f7faf9]">
            <div className="w-full max-w-md bg-white border border-[#005b52]/10 rounded-2xl p-10 space-y-6 shadow-xl shadow-black/5">
                <div className="text-center">
                    <h1 className="text-3xl font-bold mb-2 text-[#005b52]">Welcome Back</h1>
                    <p className="text-[#005b52]/70">Log in to continue building</p>
                </div>

                {error && <div className="text-red-700 bg-red-50 border border-red-200 p-3 rounded-lg text-sm">{error}</div>}

                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1 text-[#005b52]">Email</label>
                        <Input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="you@niyati.com"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1 text-[#005b52]">Password</label>
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

                <p className="text-center text-[#005b52]/70 text-sm mt-6">
                    Don't have an account? <Link href="/signup" className="font-bold text-[#005b52] hover:underline hover:text-[#04221f] transition-colors">Sign up</Link>
                </p>
            </div>
        </main>
    );
}
