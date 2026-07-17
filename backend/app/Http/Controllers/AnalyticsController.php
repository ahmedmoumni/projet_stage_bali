<?php

namespace App\Http\Controllers;

use App\Models\DocumentLog;
use App\Models\KnowledgeFact;
use App\Models\KnowledgeRule;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class AnalyticsController extends Controller
{
    protected function authorizeAdmin(Request $request): void
    {
        $user = $request->user();

        if (!$user || $user->role !== 'admin') {
            abort(403, 'Forbidden');
        }
    }

    public function monthly(Request $request): JsonResponse
    {
        $this->authorizeAdmin($request);

        $start = now()->subMonths(11)->startOfMonth();

        $months = collect(range(0, 11))->map(function ($offset) use ($start) {
            return $start->copy()->addMonths($offset)->format('Y-m');
        });

        $ruleCounts = KnowledgeRule::selectRaw("DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as total")
            ->where('created_at', '>=', $start)
            ->groupBy('month')
            ->pluck('total', 'month');

        $factCounts = KnowledgeFact::selectRaw("DATE_FORMAT(created_at, '%Y-%m') as month, COUNT(*) as total")
            ->where('created_at', '>=', $start)
            ->groupBy('month')
            ->pluck('total', 'month');

        $data = $months->map(function ($month) use ($ruleCounts, $factCounts) {
            return [
                'month' => $month,
                'rules' => (int) ($ruleCounts->get($month) ?? 0),
                'facts' => (int) ($factCounts->get($month) ?? 0),
            ];
        })->values();

        return response()->json($data);
    }

    public function methods(Request $request): JsonResponse
    {
        $this->authorizeAdmin($request);

        $ruleExtraction = KnowledgeRule::whereIn('extraction_method', ['spacy', 'llm'])
            ->selectRaw('extraction_method, COUNT(*) as total')
            ->groupBy('extraction_method')
            ->pluck('total', 'extraction_method');

        $factExtraction = KnowledgeFact::whereIn('extraction_method', ['spacy', 'llm'])
            ->selectRaw('extraction_method, COUNT(*) as total')
            ->groupBy('extraction_method')
            ->pluck('total', 'extraction_method');

        $ruleAlgorithm = KnowledgeRule::whereIn('algorithm_used', ['naive_bayes', 'decision_tree'])
            ->selectRaw('algorithm_used, COUNT(*) as total')
            ->groupBy('algorithm_used')
            ->pluck('total', 'algorithm_used');

        $factAlgorithm = KnowledgeFact::whereIn('algorithm_used', ['naive_bayes', 'decision_tree'])
            ->selectRaw('algorithm_used, COUNT(*) as total')
            ->groupBy('algorithm_used')
            ->pluck('total', 'algorithm_used');

        return response()->json([
            'extraction' => [
                'spacy' => (int) ($ruleExtraction->get('spacy') ?? 0) + (int) ($factExtraction->get('spacy') ?? 0),
                'llm' => (int) ($ruleExtraction->get('llm') ?? 0) + (int) ($factExtraction->get('llm') ?? 0),
            ],
            'algorithm' => [
                'naive_bayes' => (int) ($ruleAlgorithm->get('naive_bayes') ?? 0) + (int) ($factAlgorithm->get('naive_bayes') ?? 0),
                'decision_tree' => (int) ($ruleAlgorithm->get('decision_tree') ?? 0) + (int) ($factAlgorithm->get('decision_tree') ?? 0),
            ],
        ]);
    }

    public function documents(Request $request): JsonResponse
    {
        $this->authorizeAdmin($request);

        $pagination = DocumentLog::query()
            ->select([
                'id',
                'filename',
                'file_type',
                'routing',
                'pages',
                'rules_extracted',
                'facts_extracted',
                'processed_at',
            ])
            ->orderBy('processed_at', 'desc')
            ->paginate(10);

        return response()->json($pagination);
    }
}
