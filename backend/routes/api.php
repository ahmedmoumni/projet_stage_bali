<?php

use App\Http\Controllers\Auth\AuthController;
use App\Http\Controllers\DocumentController;
use App\Http\Controllers\KnowledgeRuleController;
use App\Http\Controllers\KnowledgeFactController;
use Illuminate\Http\Request;
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

    // Knowledge routes
    Route::get('/rules', [KnowledgeRuleController::class, 'index']);
    Route::get('/facts', [KnowledgeFactController::class, 'index']);

    // Pending review routes (admin check in controller)
    Route::get('/pending', [\App\Http\Controllers\PendingReviewController::class, 'index']);
    Route::post('/pending/{type}/{id}/approve', [\App\Http\Controllers\PendingReviewController::class, 'approve']);
    Route::post('/pending/{type}/{id}/reject', [\App\Http\Controllers\PendingReviewController::class, 'reject']);
    Route::put('/pending/{type}/{id}', [\App\Http\Controllers\PendingReviewController::class, 'update']);

    // Document routes (admin only)
    Route::post('/documents/upload', [DocumentController::class, 'upload']);
    Route::get('/documents', [DocumentController::class, 'index']);
    Route::get('/documents/{id}', [DocumentController::class, 'show']);
});
