<?php

namespace App\Http\Controllers;

use App\Models\KnowledgeRule;
use Illuminate\Http\Request;

class KnowledgeRuleController extends Controller
{
    public function index(Request $request)
    {
        $user = $request->user();
        
        $query = KnowledgeRule::query();
        
        // If user is public, filter to only public and validated rules
        if (!$user || $user->role === 'public') {
            $query->where('visibility', 'public')
                  ->where('status', 'validated');
        } else {
            // Admin users: by default show both validated and pending_review
            // unless they explicitly filter by status
            if (!$request->has('status') || $request->status === null || $request->status === 'all') {
                $query->whereIn('status', ['validated', 'pending_review']);
            } elseif ($request->status !== 'all') {
                $query->where('status', $request->status);
            }
            
            // Admin users can filter visibility if specified
            if ($request->has('visibility') && $request->visibility !== null && $request->visibility !== 'all') {
                $query->where('visibility', $request->visibility);
            }
        }
        
        // Filter by domain
        if ($request->has('domain') && $request->domain !== null && $request->domain !== 'all') {
            $query->where('domain', $request->domain);
        }
        
        // Filter by status (if provided explicitly)
        if ($request->has('status') && $request->status !== null && $request->status !== 'all') {
            $query->where('status', $request->status);
        }
        
        // Search by source_text
        if ($request->has('search') && !empty($request->search)) {
            $query->where('source_text', 'like', '%' . $request->search . '%');
        }
        
        // Get paginated results (10 per page)
        $rules = $query->orderBy('created_at', 'desc')
                       ->paginate(10);
        
        return response()->json([
            'data' => $rules->items(),
            'current_page' => $rules->currentPage(),
            'last_page' => $rules->lastPage(),
            'total' => $rules->total(),
            'per_page' => $rules->perPage(),
        ]);
    }
}
