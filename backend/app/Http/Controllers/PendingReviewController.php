<?php

namespace App\Http\Controllers;

use App\Models\KnowledgeRule;
use App\Models\KnowledgeFact;
use App\Models\FactValue;
use App\Models\RuleConditionFact;
use App\Models\RuleActionFact;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class PendingReviewController extends Controller
{
    /**
     * GET /api/pending
     * Fetch all pending_review items (rules + facts) merged and paginated
     */
    public function index(Request $request)
    {
        // Check admin access
        $user = $request->user();
        if (!$user || $user->role !== 'admin') {
            return response()->json(['message' => 'Unauthorized. Admin access required.'], 403);
        }

        $type = $request->query('type', 'all');
        $domain = $request->query('domain');
        $page = $request->query('page', 1);

        // Get pending rules
        $rulesQuery = KnowledgeRule::where('status', 'pending_review');
        
        // Get pending facts
        $factsQuery = KnowledgeFact::where('status', 'pending_review');

        // Filter by domain
        if ($domain && $domain !== 'all') {
            $rulesQuery->where('domain', $domain);
            $factsQuery->where('domain', $domain);
        }

        // Get data based on type filter
        if ($type === 'rule') {
            $rules = $rulesQuery->get();
            $facts = collect();
        } elseif ($type === 'fact') {
            $rules = collect();
            $facts = $factsQuery->get();
        } else {
            $rules = $rulesQuery->get();
            $facts = $factsQuery->get();
        }

        // Transform rules to include type field
        $rulesData = $rules->map(function ($rule) {
            return [
                'id' => $rule->id,
                'type' => 'rule',
                'source_text' => $rule->source_text,
                'domain' => $rule->domain,
                'visibility' => $rule->visibility,
                'confidence_score' => $rule->confidence_score,
                'extraction_method' => $rule->extraction_method,
                'created_at' => $rule->created_at,
            ];
        });

        // Transform facts to include type field
        $factsData = $facts->map(function ($fact) {
            return [
                'id' => $fact->id,
                'type' => 'fact',
                'source_text' => $fact->source_text,
                'subject' => $fact->subject,
                'relation' => $fact->relation,
                'domain' => $fact->domain,
                'visibility' => $fact->visibility,
                'confidence_score' => $fact->confidence_score,
                'extraction_method' => $fact->extraction_method,
                'created_at' => $fact->created_at,
            ];
        });

        // Merge and sort by created_at descending
        $merged = $rulesData->concat($factsData)
                             ->sortByDesc('created_at')
                             ->values();

        // Manual pagination
        $perPage = 10;
        $total = $merged->count();
        $lastPage = ceil($total / $perPage);
        $offset = ($page - 1) * $perPage;
        $items = $merged->slice($offset, $perPage)->values();

        return response()->json([
            'data' => $items,
            'current_page' => intval($page),
            'last_page' => intval($lastPage),
            'total' => $total,
            'per_page' => $perPage,
        ]);
    }

    /**
     * POST /api/pending/{type}/{id}/approve
     * Approve a pending item and set status to validated
     */
    public function approve(Request $request, $type, $id)
    {
        // Check admin access
        $user = $request->user();
        if (!$user || $user->role !== 'admin') {
            return response()->json(['message' => 'Unauthorized. Admin access required.'], 403);
        }

        if ($type === 'rule') {
            $item = KnowledgeRule::findOrFail($id);
        } elseif ($type === 'fact') {
            $item = KnowledgeFact::findOrFail($id);
        } else {
            return response()->json(['error' => 'Invalid type'], 400);
        }

        // Check that item is pending_review
        if ($item->status !== 'pending_review') {
            return response()->json(['error' => 'Item is not pending review'], 400);
        }

        $item->status = 'validated';
        $item->save();

        return response()->json([
            'message' => 'Item approved successfully',
            'data' => $item,
        ]);
    }

    /**
     * POST /api/pending/{type}/{id}/reject
     * Reject and delete a pending item
     */
    public function reject(Request $request, $type, $id)
    {
        // Check admin access
        $user = $request->user();
        if (!$user || $user->role !== 'admin') {
            return response()->json(['message' => 'Unauthorized. Admin access required.'], 403);
        }

        if ($type === 'rule') {
            $item = KnowledgeRule::findOrFail($id);
            
            // Delete related rows
            RuleConditionFact::where('knowledge_rule_id', $id)->delete();
            RuleActionFact::where('knowledge_rule_id', $id)->delete();
            
            // Delete related fact values
            $conditionIds = DB::table('rule_condition_facts')
                              ->where('knowledge_rule_id', $id)
                              ->pluck('fact_id');
            $actionIds = DB::table('rule_action_facts')
                            ->where('knowledge_rule_id', $id)
                            ->pluck('fact_id');
            
            $allFactIds = $conditionIds->merge($actionIds)->unique();
            foreach ($allFactIds as $factId) {
                FactValue::where('parent_type', 'knowledge_fact')
                         ->where('parent_id', $factId)
                         ->delete();
            }
            
            // Delete the rule
            $item->delete();
            
        } elseif ($type === 'fact') {
            $item = KnowledgeFact::findOrFail($id);
            
            // Delete related fact values
            FactValue::where('parent_type', 'knowledge_fact')
                     ->where('parent_id', $id)
                     ->delete();
            
            // Delete the fact
            $item->delete();
            
        } else {
            return response()->json(['error' => 'Invalid type'], 400);
        }

        return response()->json([
            'message' => 'Item rejected and deleted successfully',
        ]);
    }

    /**
     * PUT /api/pending/{type}/{id}
     * Update a pending item
     */
    public function update(Request $request, $type, $id)
    {
        // Check admin access
        $user = $request->user();
        if (!$user || $user->role !== 'admin') {
            return response()->json(['message' => 'Unauthorized. Admin access required.'], 403);
        }

        $validated = $request->validate([
            'source_text' => 'string',
            'domain' => 'string|nullable',
            'visibility' => 'string|in:public,private',
        ]);

        if ($type === 'rule') {
            $item = KnowledgeRule::findOrFail($id);
        } elseif ($type === 'fact') {
            $item = KnowledgeFact::findOrFail($id);
        } else {
            return response()->json(['error' => 'Invalid type'], 400);
        }

        $item->update($validated);

        return response()->json([
            'message' => 'Item updated successfully',
            'data' => $item,
        ]);
    }
}
