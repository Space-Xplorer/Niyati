'use client';

import { useState } from 'react';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function SignupPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setSuccess('');

        try {
            const url = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';
            const response = await fetch(`${url}/api/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, role: isAdmin ? 'admin' : 'user' }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'Signup failed');
            }

            setSuccess('Registration successful! Redirecting to login...');
            setTimeout(() => router.push('/login'), 2000);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="min-h-screen flex items-center justify-center bg-black text-white p-8">
            <div className="w-full max-w-md bg-gray-900 border border-gray-800 rounded-xl p-8 space-y-6">
                <div className="text-center">
                    <h1 className="text-3xl font-bold mb-2 text-emerald-400">Join Niyati</h1>
                    <p className="text-gray-400">Create a secure account to sync your bots</p>
                </div>

                {error && <div className="text-red-400 bg-red-950 p-3 rounded">{error}</div>}
                {success && <div className="text-emerald-400 bg-emerald-950 p-3 rounded">{success}</div>}

                <form onSubmit={handleSignup} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1">Email</label>
                        <Input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="you@niyati.com"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1">Password</label>
                        <Input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                        />
                    </div>
                    <div className="flex items-center space-x-2">
                        <input
                            type="checkbox"
                            id="isAdmin"
                            checked={isAdmin}
                            onChange={(e) => setIsAdmin(e.target.checked)}
                            className="w-4 h-4 bg-gray-900 border-gray-700 rounded text-emerald-500 focus:ring-emerald-500"
                        />
                        <label htmlFor="isAdmin" className="text-sm font-medium text-gray-300">
                            Register as Admin (For testing purposes)
                        </label>
                    </div>
                    <Button type="submit" className="w-full" isLoading={isLoading}>Sign Up</Button>
                </form>

                <p className="text-center text-gray-500 text-sm mt-4">
                    Already have an account? <Link href="/login" className="text-emerald-400 hover:text-emerald-300 transition-colors">Log in</Link>
                </p>
            </div>
        </main>
    );
}
