<?php

use App\Http\Controllers\Auth\AuthController;
use App\Http\Controllers\DocumentController;
use App\Http\Controllers\KnowledgeRuleController;
use App\Http\Controllers\KnowledgeFactController;
use App\Http\Controllers\AnalyticsController;
use App\Http\Controllers\DashboardController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Route;

// Public auth routes
Route::post('/login', [AuthController::class, 'login']);
Route::post('/register', [AuthController::class, 'register']);

// Protected auth routes
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/me', [AuthController::class, 'me']);
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::get('/user', function (Request $request) {
        return $request->user();
    });

    // Dashboard route
    Route::get('/dashboard', [DashboardController::class, 'index']);

    // Analytics routes (admin-only)
    Route::get('/analytics/monthly', [AnalyticsController::class, 'monthly']);
    Route::get('/analytics/methods', [AnalyticsController::class, 'methods']);
    Route::get('/analytics/documents', [AnalyticsController::class, 'documents']);

    // Knowledge routes
    Route::get('/rules', [KnowledgeRuleController::class, 'index']);
    Route::get('/facts', [KnowledgeFactController::class, 'index']);

    // Pending review routes (admin check in controller)
    Route::get('/pending', [\App\Http\Controllers\PendingReviewController::class, 'index']);
    Route::post('/pending/{type}/{id}/approve', [\App\Http\Controllers\PendingReviewController::class, 'approve']);
    Route::post('/pending/{type}/{id}/reject', [\App\Http\Controllers\PendingReviewController::class, 'reject']);
    Route::put('/pending/{type}/{id}', [\App\Http\Controllers\PendingReviewController::class, 'update']);

    Route::post('/pipeline3/discover', function (Request $request) {
        $user = $request->user();
        if (!$user || $user->role !== 'admin') {
            return response()->json(['message' => 'Unauthorized. Admin access required.'], 403);
        }

        $validated = $request->validate([
            'file' => ['required', 'file', 'mimes:csv,txt', 'max:5120'],
            'subject_column' => ['required', 'string'],
            'target_column' => ['required', 'string'],
            'feature_columns' => ['required', 'string'],
        ]);

        $file = $request->file('file');
        $response = Http::timeout(300)
            ->asMultipart()
            ->post( env('ML_SERVICE_URL', 'http://127.0.0.1:5000') . '/pipeline3/discover', [
                [
                    'name' => 'file',
                    'contents' => file_get_contents($file->getRealPath()),
                    'filename' => $file->getClientOriginalName(),
                ],
                ['name' => 'subject_column', 'contents' => $validated['subject_column']],
                ['name' => 'target_column', 'contents' => $validated['target_column']],
                ['name' => 'feature_columns', 'contents' => $validated['feature_columns']],
            ]);

        return response()->json($response->json(), $response->status());
    });

    // Document routes (admin only)
    Route::post('/documents/upload', [DocumentController::class, 'upload']);
    Route::get('/documents', [DocumentController::class, 'index']);
    Route::get('/documents/{id}', [DocumentController::class, 'show']);
});
