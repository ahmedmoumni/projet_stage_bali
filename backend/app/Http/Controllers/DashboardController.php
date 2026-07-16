<?php

namespace App\Http\Controllers;

use App\Models\KnowledgeRule;
use App\Models\KnowledgeFact;
use App\Models\DocumentLog;
use Illuminate\Http\Request;

class DashboardController extends Controller
{
    /**
     * Get dashboard statistics
     * GET /api/dashboard
     * 
     * Returns statistics based on user role:
     * - Admin: all items regardless of visibility
     * - Public user: only public items with validated status
     */
    public function index(Request $request)
    {
        $user = $request->user();
        $isAdmin = $user->role === 'admin';

        // Build query constraints based on role
        if ($isAdmin) {
            // Admin sees all items
            $totalRules = KnowledgeRule::count();
            $totalFacts = KnowledgeFact::count();
            $totalValidated = KnowledgeRule::where('status', 'validated')->count() +
                              KnowledgeFact::where('status', 'validated')->count();
            $totalPending = KnowledgeRule::where('status', 'pending_review')->count() +
                           KnowledgeFact::where('status', 'pending_review')->count();
        } else {
            // Public users see only public + validated items
            $totalRules = KnowledgeRule::where('visibility', 'public')
                ->where('status', 'validated')
                ->count();
            
            $totalFacts = KnowledgeFact::where('visibility', 'public')
                ->where('status', 'validated')
                ->count();
            
            $totalValidated = KnowledgeRule::where('visibility', 'public')
                ->where('status', 'validated')
                ->count() +
                KnowledgeFact::where('visibility', 'public')
                ->where('status', 'validated')
                ->count();
            
            $totalPending = 0; // Public users don't see pending items
        }

        $totalDocuments = DocumentLog::count();

        return response()->json([
            'total_rules' => $totalRules,
            'total_facts' => $totalFacts,
            'total_validated' => $totalValidated,
            'total_pending' => $totalPending,
            'total_documents' => $totalDocuments,
        ]);
    }
}
