<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class KnowledgeRule extends Model
{
    use HasFactory;

    protected $table = 'knowledge_rules';

    protected $fillable = [
        'source_text',
        'domain',
        'visibility',
        'confidence_score',
        'extraction_method',
        'algorithm_used',
        'condition_group_operator',
        'action_group_operator',
        'status',
    ];

    protected $casts = [
        'confidence_score' => 'float',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Get all condition facts for this rule
     */
    public function conditionFacts(): HasMany
    {
        return $this->hasMany(RuleConditionFact::class, 'rule_id');
    }

    /**
     * Get all action facts for this rule
     */
    public function actionFacts(): HasMany
    {
        return $this->hasMany(RuleActionFact::class, 'rule_id');
    }
}
