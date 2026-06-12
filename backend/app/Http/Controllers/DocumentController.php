<?php

namespace App\Http\Controllers;

use App\Models\DocumentLog;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Validation\ValidationException;

class DocumentController extends Controller
{
    /**
     * Upload and process a document
     * POST /api/documents/upload
     * Protected by Sanctum, admin only
     */
    public function upload(Request $request): JsonResponse
    {
        // Check if user is admin
        if ($request->user()->role !== 'admin') {
            return response()->json([
                'message' => 'Unauthorized. Only admins can upload documents.'
            ], 403);
        }

        // Validate the uploaded file
        try {
            $validated = $request->validate([
                'file' => 'required|file|mimes:pdf,csv,xlsx,xls|max:10240', // 10MB
                'visibility' => 'sometimes|in:public,private'
            ]);
        } catch (ValidationException $e) {
            return response()->json([
                'message' => 'Validation failed',
                'errors' => $e->errors()
            ], 422);
        }

        try {
            $file = $request->file('file');
            $filename = $file->getClientOriginalName();

            // Read file content
            $fileContent = file_get_contents($file->getRealPath());

            // Send to Python Flask Pipeline 0
            $response = Http::timeout(60)
                ->attach('file', $fileContent, $filename)
                ->post(env('PIPELINE0_URL', 'http://localhost:5000') . '/pipeline0/route');

            if (!$response->successful()) {
                return response()->json([
                    'message' => 'Pipeline 0 processing failed',
                    'error' => $response->json()
                ], $response->status());
            }

            $pipelineResponse = $response->json();

            // Save to document_log table
            $documentLog = DocumentLog::create([
                'filename' => $filename,
                'file_type' => $pipelineResponse['file_type'] ?? 'unknown',
                'routing' => $pipelineResponse['routing'] ?? 'rejected',
                'pages' => $pipelineResponse['pages'] ?? 0,
                'rules_extracted' => 0,
                'facts_extracted' => 0,
                'processed_at' => now()
            ]);

            // Return the full Flask response with log
            return response()->json(array_merge(
                $pipelineResponse,
                [
                    'document_id' => $documentLog->id,
                    'visibility' => $validated['visibility'] ?? 'private'
                ]
            ), 200);

        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Error processing document',
                'error' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Get all uploaded documents
     * GET /api/documents
     */
    public function index(): JsonResponse
    {
        $documents = DocumentLog::all();

        return response()->json([
            'data' => $documents
        ], 200);
    }

    /**
     * Get a specific document
     * GET /api/documents/{id}
     */
    public function show(int $id): JsonResponse
    {
        $document = DocumentLog::find($id);

        if (!$document) {
            return response()->json([
                'message' => 'Document not found'
            ], 404);
        }

        return response()->json([
            'data' => $document
        ], 200);
    }
}
