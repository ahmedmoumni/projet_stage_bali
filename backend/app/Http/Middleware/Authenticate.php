<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Auth\Middleware\Authenticate as Middleware;
use Illuminate\Http\Request;

class Authenticate extends Middleware
{
    /**
     * Get the path the user should be redirected to when they are not authenticated.
     */
    protected function redirectTo(Request $request): ?string
    {
        // For API requests, don't redirect - let unauthenticated() handle it
        if ($request->expectsJson()) {
            return null;
        }

        // For web requests, redirect to login (if login route exists)
        // If not, return null to let exception handler handle it
        try {
            return route('login');
        } catch (\Exception $e) {
            return null;
        }
    }
}
