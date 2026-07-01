<?php

namespace App\Http\Controllers;

use App\Models\KnowledgeFact;
use App\Models\FactValue;
use Illuminate\Http\Request;

class KnowledgeFactController extends Controller
{
    public function index(Request $request)
    {
        $user = $request->user();
        
        $query = KnowledgeFact::query();
        
        // If user is public, filter to only public and validated facts
        if (!$user || $user->role === 'public') {
            $query->where('visibility', 'public')
                  ->where('status', 'validated');
        } else {
            // Admin users can filter visibility if specified
            if ($request->has('visibility') && $request->visibility !== null && $request->visibility !== 'all') {
                $query->where('visibility', $request->visibility);
            }
        }
        
        // Filter by domain
        if ($request->has('domain') && $request->domain !== null && $request->domain !== 'all') {
            $query->where('domain', $request->domain);
        }
        
        // Filter by status
        if ($request->has('status') && $request->status !== null && $request->status !== 'all') {
            $query->where('status', $request->status);
        }
        
        // Search by subject or relation
        if ($request->has('search') && !empty($request->search)) {
            $searchTerm = $request->search;
            $query->where(function ($q) use ($searchTerm) {
                $q->where('subject', 'like', '%' . $searchTerm . '%')
                  ->orWhere('relation', 'like', '%' . $searchTerm . '%');
            });
        }
        
        // Get paginated results (10 per page)
        $facts = $query->orderBy('created_at', 'desc')
                       ->paginate(10);
        
        // Load values for each fact
        $factIds = collect($facts->items())->pluck('id');
        $values = FactValue::where('parent_type', 'knowledge_fact')
                           ->whereIn('parent_id', $factIds)
                           ->get();
        
        $factsArray = collect($facts->items())->map(function ($fact) use ($values) {
            $fact->values = $values->filter(function ($val) use ($fact) {
                return $val->parent_id === $fact->id && $val->parent_type === 'knowledge_fact';
            })->values();
            return $fact;
        });
        
        return response()->json([
            'data' => $factsArray,
            'current_page' => $facts->currentPage(),
            'last_page' => $facts->lastPage(),
            'total' => $facts->total(),
            'per_page' => $facts->perPage(),
        ]);
    }
}
