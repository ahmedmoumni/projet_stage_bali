<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class RuleConditionFact extends Model
{
    use HasFactory;

    protected $table = 'rule_condition_facts';

    protected $fillable = [
        'rule_id',
        'subject',
        'operator',
        'logical_operator',
        'group_id',
    ];

    /**
     * Get the rule this condition fact belongs to
     */
    public function rule(): BelongsTo
    {
        return $this->belongsTo(KnowledgeRule::class, 'rule_id');
    }

    /**
     * Get all fact values for this condition fact
     */
    public function factValues(): HasMany
    {
        return $this->hasMany(FactValue::class, 'parent_id')
            ->where('parent_type', 'condition_fact');
    }
}
