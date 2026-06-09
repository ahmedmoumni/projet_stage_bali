<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class RuleActionFact extends Model
{
    use HasFactory;

    protected $table = 'rule_action_facts';

    protected $fillable = [
        'rule_id',
        'subject',
        'operator',
        'logical_operator',
        'group_id',
    ];

    /**
     * Get the rule this action fact belongs to
     */
    public function rule(): BelongsTo
    {
        return $this->belongsTo(KnowledgeRule::class, 'rule_id');
    }

    /**
     * Get all fact values for this action fact
     */
    public function factValues(): HasMany
    {
        return $this->hasMany(FactValue::class, 'parent_id')
            ->where('parent_type', 'action_fact');
    }
}
