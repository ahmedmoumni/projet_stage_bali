<?php

namespace App\Http\Controllers;

use App\Models\DocumentLog;
use App\Models\KnowledgeFact;
use App\Models\FactValue;
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
                'file' => 'required|file|mimes:pdf,csv,xlsx,xls|max:51200', // 50MB
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
            $visibility = $validated['visibility'] ?? 'private';

            \Log::info('File received', [
                'name' => $filename,
                'size' => $file->getSize(),
                'real_path' => $file->getRealPath(),
                'mime' => $file->getMimeType()
            ]);

            // STEP 1: Send to Pipeline 0 for routing decision
            $pipeline0Url = env('PIPELINE0_URL', 'http://localhost:5000');
            $pipeline0Response = Http::timeout(120)
                ->attach('file', $file->get(), $filename)
                ->post($pipeline0Url . '/pipeline0/route');

            if (!$pipeline0Response->successful()) {
                return response()->json([
                    'message' => 'Pipeline 0 failed',
                    'error' => $pipeline0Response->json(),
                    'debug_url' => $pipeline0Url . '/pipeline0/route'
                ], $pipeline0Response->status());
            }

            $pipeline0Result = $pipeline0Response->json();
            $routing = $pipeline0Result['routing'] ?? 'rejected';
            $fileType = $pipeline0Result['file_type'] ?? 'unknown';
            $pages = $pipeline0Result['pages'] ?? 0;

            \Log::info('Pipeline0 result received', [
                'routing' => $routing,
                'file_type' => $fileType,
                'has_data' => isset($pipeline0Result['data']),
                'data_count' => count($pipeline0Result['data'] ?? []),
                'data_sample' => array_slice($pipeline0Result['data'] ?? [], 0, 2)
            ]);

            $combinedResponse = [
                'pipeline0_result' => $pipeline0Result,
                'pipeline1_result' => null,
                'pipeline2_result' => null
            ];

            $rulesExtracted = 0;
            $factsExtracted = 0;

            // STEP 2: Route to appropriate pipeline(s)
            if ($routing === 'rejected') {
                // Document rejected: insufficient content
                $combinedResponse['message'] = 'Document rejected: insufficient content';
                
            } elseif ($routing === 'pipeline1' || $routing === 'ocr_then_pipeline1') {
                // Text extracted by Pipeline 0 → Pass to Pipeline 1 for rule/fact extraction
                $textOrData = $pipeline0Result['text'] ?? '';
                $pipeline1Url = env('PIPELINE1_URL', 'http://localhost:5000');

                $pipeline1Response = Http::timeout(120)
                    ->post($pipeline1Url . '/api/pipeline/extract', [
                        'text' => $textOrData,
                        'document_id' => null
                    ]);

                if ($pipeline1Response->successful()) {
                    $pipeline1Result = $pipeline1Response->json();
                    $combinedResponse['pipeline1_result'] = $pipeline1Result;
                    $rulesExtracted = $pipeline1Result['rules_extracted'] ?? 0;
                    $factsExtracted = $pipeline1Result['facts_extracted'] ?? 0;

                    // STEP 3: Pass extracted data to Pipeline 2 for automatic classification
                    if ($rulesExtracted > 0 || $factsExtracted > 0) {
                        $pipeline2Url = env('PIPELINE2_URL', 'http://localhost:5000');
                        $pipeline2Response = Http::timeout(120)
                            ->post($pipeline2Url . '/pipeline2/classify');

                        if ($pipeline2Response->successful()) {
                            $pipeline2Result = $pipeline2Response->json();
                            $combinedResponse['pipeline2_result'] = $pipeline2Result;
                        }
                    }
                }

            } elseif ($routing === 'pipeline2_direct') {
                // Structured data detected (CSV/Excel) → Pass directly to Pipeline 2
                $structuredData = $pipeline0Result['data'] ?? [];

                    // New structure: headers + rows + semantic info
                $headers = $structuredData['headers'] ?? [];
                $rows = $structuredData['rows'] ?? [];
                $subjectColumn = $structuredData['subject_column'] ?? ($headers[0] ?? null);
                $relationColumns = $structuredData['relation_columns'] ?? array_slice($headers, 1);

                \Log::info('Pipeline2_direct: structured data received', [
                    'headers' => $headers,
                    'subject_column' => $subjectColumn,
                    'relation_columns' => $relationColumns,
                    'rows_count' => count($rows)
                ]);

                if (!empty($headers) && !empty($rows)) {
                    // Call Pipeline 2 to classify CSV/Excel data with new structure
                        $pipeline2Url = env('PIPELINE2_URL', 'http://localhost:5000');
                    
                    try {
                        $pipeline2Response = Http::timeout(120)
                            ->post($pipeline2Url . '/pipeline2/classify', [
                                'data' => [
                                    'headers' => $headers,
                                    'rows' => $rows,
                                    'subject_column' => $subjectColumn,
                                    'relation_columns' => $relationColumns
                                ],
                                'source' => 'pipeline0_direct'
                            ]);

                        if ($pipeline2Response->successful()) {
                            $pipeline2Result = $pipeline2Response->json();
                            $combinedResponse['pipeline2_result'] = $pipeline2Result;
                            $factsExtracted = count($pipeline2Result['predictions'] ?? []);
                            $rulesExtracted = 0;

                            // Save classified facts to database
                            // Now EACH prediction is ONE FACT with ONE relation
                            if (isset($pipeline2Result['predictions']) && is_array($pipeline2Result['predictions'])) {
                                foreach ($pipeline2Result['predictions'] as $prediction) {
                                    $subject = $prediction['subject'] ?? 'unknown';
                                    $tfidfText = $prediction['text'] ?? '';
                                    $domain = $prediction['domain'] ?? 'unknown';
                                    $confidence = $prediction['confidence'] ?? 0;
                                    $relation = $prediction['relation'] ?? 'has_unknown';
                                    $relationColumn = $prediction['relation_column'] ?? 'unknown';
                                    $relationValue = $prediction['relation_value'] ?? '';
                                    
                                    // Use status from Pipeline 2 dual-algorithm logic
                                    // If Pipeline 2 didn't provide status, fall back to old logic
                                    if (isset($prediction['status'])) {
                                        $status = $prediction['status'];
                                    } else {
                                        $status = ($confidence >= 0.8) ? 'validated' : 'pending_review';
                                    }
                                    
                                    // Get algorithm_used from Pipeline 2 response
                                    $algorithmUsed = $prediction['algorithm_used'] ?? 'csv_classification';

                                    // Create ONE fact per relation
                                    $fact = KnowledgeFact::create([
                                        'source_text' => $tfidfText,
                                        'subject' => $subject,
                                        'relation' => $relation,  // e.g., 'has_population'
                                        'domain' => $domain,
                                        'visibility' => $visibility,
                                        'confidence_score' => $confidence,
                                        'extraction_method' => 'spacy',
                                        'algorithm_used' => $algorithmUsed,
                                        'status' => $status
                                    ]);

                                    // Create ONE fact value for this relation
                                    $valueType = $this->detectValueType($relationValue);
                                    
                                    if ($valueType === 'continuous') {
                                        $numericValue = floatval($relationValue);
                                        FactValue::create([
                                            'parent_type' => 'knowledge_fact',
                                            'parent_id' => $fact->id,
                                            'value_type' => 'continuous',
                                            'value_continuous' => $numericValue,
                                            'value_categorical' => null,
                                            'unit' => $this->guessUnit($relationColumn),
                                            'column_name' => $relationColumn
                                        ]);
                                    } else {
                                        FactValue::create([
                                            'parent_type' => 'knowledge_fact',
                                            'parent_id' => $fact->id,
                                            'value_type' => 'categorical',
                                            'value_continuous' => null,
                                            'value_categorical' => (string)$relationValue,
                                            'unit' => null,
                                            'column_name' => $relationColumn
                                        ]);
                                    }
                                }
                            }
                        } else {
                            \Log::error('Pipeline 2 failed', [
                                'status' => $pipeline2Response->status(),
                                'response' => $pipeline2Response->json()
                            ]);
                        }
                    } catch (\Exception $e) {
                        \Log::error('Pipeline 2 exception', [
                            'error' => $e->getMessage(),
                            'trace' => $e->getTraceAsString()
                        ]);
                    }
                } else {
                    \Log::warning('Invalid structured data', [
                        'headers_count' => count($headers),
                        'rows_count' => count($rows)
                    ]);
                }
            }

            // STEP 4: Always save to document_log table
            $documentLog = DocumentLog::create([
                'filename' => $filename,
                'file_type' => $fileType,
                'routing' => $routing,
                'pages' => $pages,
                'rules_extracted' => $rulesExtracted,
                'facts_extracted' => $factsExtracted,
                'processed_at' => now()
            ]);

            // STEP 5: Return complete response with document tracking
            return response()->json(array_merge(
                $combinedResponse,
                [
                    'document_id' => $documentLog->id,
                    'visibility' => $visibility,
                    'summary' => [
                        'routing' => $routing,
                        'file_type' => $fileType,
                        'pages' => $pages,
                        'rules_extracted' => $rulesExtracted,
                        'facts_extracted' => $factsExtracted
                    ]
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
     * Detect value type: continuous or categorical
     */
    private function detectValueType($value): string
    {
        $strValue = (string)$value;
        // Try to convert to float
        if (is_numeric($strValue)) {
            return 'continuous';
        }
        return 'categorical';
    }

    /**
     * Guess unit based on column header name
     */
    private function guessUnit($columnName): ?string
    {
        $columnLower = strtolower($columnName);
        
        // Common unit patterns
        if (stripos($columnLower, 'population') !== false || stripos($columnLower, 'count') !== false) {
            return 'persons';
        }
        if (stripos($columnLower, 'distance') !== false || stripos($columnLower, 'length') !== false) {
            return 'km';
        }
        if (stripos($columnLower, 'area') !== false) {
            return 'km²';
        }
        if (stripos($columnLower, 'volume') !== false || stripos($columnLower, 'water') !== false) {
            return 'L';
        }
        if (stripos($columnLower, 'weight') !== false || stripos($columnLower, 'mass') !== false) {
            return 'kg';
        }
        if (stripos($columnLower, 'temperature') !== false) {
            return '°C';
        }
        if (stripos($columnLower, 'percentage') !== false || stripos($columnLower, 'percent') !== false) {
            return '%';
        }
        
        return null;
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
