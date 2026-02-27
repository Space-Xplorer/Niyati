import Link from 'next/link';

export default function NotFound() {
    return (
        <main className="min-h-screen flex flex-col items-center justify-center bg-[#f7faf9] text-[#04221f] p-8">
            <div className="text-center space-y-6">
                <h1 className="text-9xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-[#005b52] to-[#dbf226]">
                    404
                </h1>
                <h2 className="text-3xl font-bold text-[#04221f]">Page Not Found</h2>
                <p className="text-[#005b52]/70 max-w-md mx-auto">
                    The requested resource could not be found. It might have been moved or deleted.
                </p>
                <div className="pt-8">
                    <Link
                        href="/"
                        className="px-8 py-3 rounded-lg font-medium text-[#dbf226] bg-[#005b52] hover:bg-[#04221f] transition-colors inline-block shadow-md shadow-[#005b52]/20"
                    >
                        Return Home
                    </Link>
                </div>
            </div>
        </main>
    );
}
