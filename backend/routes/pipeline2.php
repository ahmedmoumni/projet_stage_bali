<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\PipelineController;

// Pipeline 2: Domain Classification (Admin only)
Route::middleware(['auth:sanctum', 'admin'])->group(function () {
    
    // Train classifiers
    Route::post('/pipeline2/train', function () {
        try {
            $response = Http::timeout(300)  // 5 minute timeout for training
                ->post('http://localhost:5000/pipeline2/train');
            
            return response()->json([
                'status' => 'success',
                'message' => 'Training initiated',
                'data' => $response->json()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to train classifiers: ' . $e->getMessage()
            ], 500);
        }
    });
    
    // Classify unclassified items from database
    Route::post('/pipeline2/classify', function () {
        try {
            $response = Http::timeout(120)
                ->post('http://localhost:5000/pipeline2/classify');
            
            return response()->json([
                'status' => 'success',
                'message' => 'Classification completed',
                'data' => $response->json()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to classify items: ' . $e->getMessage()
            ], 500);
        }
    });
    
    // Classify from CSV/Excel file
    Route::post('/pipeline2/classify-file', function (Illuminate\Http\Request $request) {
        try {
            if (!$request->hasFile('file')) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'No file provided'
                ], 400);
            }
            
            $file = $request->file('file');
            $textColumn = $request->input('text_column', 'text');
            
            $response = Http::timeout(60)
                ->attach('file', $file->getContent(), $file->getClientOriginalName())
                ->post('http://localhost:5000/pipeline2/classify-file', [
                    'text_column' => $textColumn
                ]);
            
            return response()->json([
                'status' => 'success',
                'message' => 'File classified successfully',
                'data' => $response->json()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to classify file: ' . $e->getMessage()
            ], 500);
        }
    });
    
    // Get classification statistics
    Route::get('/pipeline2/stats', function () {
        try {
            $response = Http::get('http://localhost:5000/pipeline2/stats');
            
            return response()->json([
                'status' => 'success',
                'data' => $response->json()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to get statistics: ' . $e->getMessage()
            ], 500);
        }
    });
    
    // Get evaluation results
    Route::get('/pipeline2/evaluate', function () {
        try {
            $response = Http::get('http://localhost:5000/pipeline2/evaluate');
            
            return response()->json([
                'status' => 'success',
                'data' => $response->json()
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Failed to get evaluation results: ' . $e->getMessage()
            ], 500);
        }
    });
});

// Public endpoints for testing (remove in production)
Route::post('/pipeline2/test-train', function () {
    try {
        $response = Http::timeout(300)
            ->post('http://localhost:5000/pipeline2/train');
        
        return response()->json($response->json());
    } catch (\Exception $e) {
        return response()->json(['error' => $e->getMessage()], 500);
    }
});

Route::post('/pipeline2/test-classify', function () {
    try {
        $response = Http::timeout(120)
            ->post('http://localhost:5000/pipeline2/classify');
        
        return response()->json($response->json());
    } catch (\Exception $e) {
        return response()->json(['error' => $e->getMessage()], 500);
    }
});
