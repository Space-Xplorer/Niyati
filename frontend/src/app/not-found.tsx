import Link from 'next/link';

export default function NotFound() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center bg-black text-white p-8">
            <div className="text-center space-y-6">
                <h1 className="text-9xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-emerald-500">
                    404
                </h1>
                <h2 className="text-3xl font-bold text-gray-200">Page Not Found</h2>
                <p className="text-gray-400 max-w-md mx-auto">
                    The requested resource could not be found. It might have been moved or deleted.
                </p>
                <div className="pt-8">
                    <Link
                        href="/"
                        className="px-8 py-3 rounded-lg font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors inline-block"
                    >
                        Return Home
                    </Link>
                </div>
            </div>
        </main>
    );
}
