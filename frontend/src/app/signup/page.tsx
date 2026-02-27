'use client';

import { useState } from 'react';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { signup as apiSignup } from '@/lib/api';

export default function SignupPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [gstin, setGstin] = useState('');
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
            const role = isAdmin ? 'Admin' : 'Business_Owner';
            await apiSignup(email, password, role, isAdmin ? undefined : gstin);
            
            setSuccess('Registration successful! Redirecting to login...');
            setTimeout(() => router.push('/login'), 2000);
        } catch (err: any) {
            setError(err.message || 'Signup failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <main className="min-h-screen flex items-center justify-center p-8" style={{ backgroundColor: '#efefef' }}>
            <div className="w-full max-w-md bg-white border border-gray-300 rounded-xl p-8 space-y-6 shadow-lg">
                <div className="text-center">
                    <h1 className="text-3xl font-bold mb-2" style={{ color: '#005b52' }}>Join Niyati</h1>
                    <p className="text-gray-600">Create a secure account to sync your bots</p>
                </div>

                {error && <div className="text-red-700 bg-red-100 border border-red-300 p-3 rounded">{error}</div>}
                {success && <div className="text-green-700 bg-green-100 border border-green-300 p-3 rounded">{success}</div>}

                <form onSubmit={handleSignup} className="space-y-4">
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
                    {!isAdmin && (
                        <div>
                            <label className="block text-sm font-medium mb-1" style={{ color: '#005b52' }}>GSTIN</label>
                            <Input
                                type="text"
                                value={gstin}
                                onChange={(e) => setGstin(e.target.value)}
                                required
                                placeholder="15‑character GSTIN"
                            />
                        </div>
                    )}

                    <div className="flex items-center space-x-2">
                        <input
                            type="checkbox"
                            id="isAdmin"
                            checked={isAdmin}
                            onChange={(e) => setIsAdmin(e.target.checked)}
                            className="w-4 h-4 border-gray-400 rounded focus:ring-2"
                            style={{ accentColor: '#dbf226' }}
                        />
                        <label htmlFor="isAdmin" className="text-sm font-medium text-gray-700">
                            Register as Admin (For testing purposes)
                        </label>
                    </div>
                    <Button type="submit" className="w-full" isLoading={isLoading}>Sign Up</Button>
                </form>

                <p className="text-center text-gray-600 text-sm mt-4">
                    Already have an account? <Link href="/login" className="font-medium hover:underline" style={{ color: '#005b52' }}>Log in</Link>
                </p>
            </div>
        </main>
    );
}
