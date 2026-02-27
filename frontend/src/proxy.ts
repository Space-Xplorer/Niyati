import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// This is the new Proxy file convention in Next.js 16!
// It runs before a request is completed to modify responses, headers, or handle redirects.
export function proxy(request: NextRequest) {
    const url = request.nextUrl;

    // Example use case: Check for an auth cookie (if you transition from localStorage to cookies)
    // const token = request.cookies.get('token');
    // if (!token && !url.pathname.startsWith('/login') && !url.pathname.startsWith('/signup')) {
    //   return NextResponse.redirect(new URL('/login', request.url));
    // }

    // Continue standard execution but append a custom security header
    const response = NextResponse.next();
    response.headers.set('X-Niyati-Proxy', 'Active');

    return response;
}

// Ensure the proxy only runs on application pages and skips API/static files
export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
